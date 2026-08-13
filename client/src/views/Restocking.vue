<template>
  <div class="restocking">
    <div class="page-header">
      <h2>{{ t('restocking.title') }}</h2>
      <p>{{ t('restocking.description') }}</p>
    </div>

    <div v-if="loading" class="loading">{{ t('common.loading') }}</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else>
      <div v-if="successInfo" class="success-banner">
        <div class="success-title">
          {{ t('restocking.success.title', { number: successInfo.restock_number }) }}
        </div>
        <div class="success-detail">
          {{ t('restocking.success.detail', {
            count: successInfo.items.length,
            total: formatCurrency(successInfo.total_cost, currentCurrency),
            date: formatDate(successInfo.expected_delivery)
          }) }}
        </div>
        <router-link to="/orders" class="success-link">
          {{ t('restocking.success.viewInOrders') }}
        </router-link>
      </div>

      <div class="card budget-card">
        <div class="budget-header">
          <div class="budget-label">{{ t('restocking.budget.label') }}</div>
          <div class="budget-value">{{ formatCurrency(budget, currentCurrency) }}</div>
        </div>
        <input
          type="range"
          class="budget-slider"
          :min="budgetMin"
          :max="budgetMax"
          :step="budgetStep"
          v-model.number="budget"
        />
        <div v-if="budget >= budgetMax" class="budget-covers-all">
          {{ t('restocking.budget.coversAll') }}
        </div>
        <div class="budget-stats">
          <div class="budget-stat">
            <div class="budget-stat-label">{{ t('restocking.budget.allocated') }}</div>
            <div class="budget-stat-value">{{ formatCurrency(allocated, currentCurrency) }}</div>
          </div>
          <div class="budget-stat">
            <div class="budget-stat-label">{{ t('restocking.budget.remaining') }}</div>
            <div class="budget-stat-value">{{ formatCurrency(remaining, currentCurrency) }}</div>
          </div>
          <div class="budget-stat">
            <div class="budget-stat-label">{{ t('restocking.budget.selectedItems') }}</div>
            <div class="budget-stat-value">{{ selectedCount }}</div>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="card-header">
          <h3 class="card-title">{{ t('restocking.table.title') }}</h3>
        </div>
        <div class="table-container">
          <table>
            <thead>
              <tr>
                <th>{{ t('restocking.table.include') }}</th>
                <th>{{ t('restocking.table.sku') }}</th>
                <th>{{ t('restocking.table.itemName') }}</th>
                <th>{{ t('restocking.table.trend') }}</th>
                <th>{{ t('restocking.table.forecastedDemand') }}</th>
                <th>{{ t('restocking.table.gap') }}</th>
                <th>{{ t('restocking.table.quantity') }}</th>
                <th>{{ t('restocking.table.unitCost') }}</th>
                <th>{{ t('restocking.table.lineCost') }}</th>
                <th>{{ t('restocking.table.leadTime') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="row in rankedRows"
                :key="row.item_sku"
                :class="{ 'row-selected': selectedSkus.has(row.item_sku), 'row-muted': !selectedSkus.has(row.item_sku) }"
              >
                <td>
                  <input
                    type="checkbox"
                    :checked="selectedSkus.has(row.item_sku)"
                    @change="toggleSelection(row.item_sku)"
                  />
                </td>
                <td><strong>{{ row.item_sku }}</strong></td>
                <td>
                  {{ row.item_name }}
                  <span v-if="!selectedSkus.has(row.item_sku)" class="badge over-budget-tag">
                    {{ t('restocking.overBudget') }}
                  </span>
                </td>
                <td>
                  <span :class="['badge', row.trend]">
                    {{ t(`trends.${row.trend}`) }}
                  </span>
                </td>
                <td>{{ row.forecasted_demand }}</td>
                <td>{{ row.gap > 0 ? '+' : '' }}{{ row.gap }}</td>
                <td>{{ row.forecasted_demand }}</td>
                <!-- Unit cost needs cents: rounding to whole dollars makes qty * unit price
                     visibly not match the line cost shown next to it. -->
                <td>{{ formatCurrencyWithDecimals(row.unit_cost, currentCurrency, 2) }}</td>
                <td>{{ formatCurrency(row.line_cost, currentCurrency) }}</td>
                <td>{{ t('restocking.days', { count: row.lead_time_days }) }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="place-order-row">
          <div v-if="submitError" class="error submit-error">{{ submitError }}</div>
          <button
            class="place-order-btn"
            :disabled="selectedCount === 0 || placing"
            @click="placeOrder"
          >
            {{ placing ? t('restocking.placingOrder') : t('restocking.placeOrder') }}
          </button>
          <span v-if="selectedCount === 0" class="nothing-selected-hint">
            {{ t('restocking.nothingSelected') }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch, onMounted } from 'vue'
import { api } from '../api'
import { useI18n } from '../composables/useI18n'
import { formatCurrency, formatCurrencyWithDecimals } from '../utils/currency'

// This view intentionally ignores the global filter bar (warehouse/category/month/status).
// Demand forecasts carry no warehouse or category dimension, so applying those filters
// here would silently do nothing and mislead the user - App.vue hides the FilterBar on
// this route for the same reason.
export default {
  name: 'Restocking',
  setup() {
    const { t, currentCurrency, currentLocale } = useI18n()

    const loading = ref(true)
    const error = ref(null)
    const forecasts = ref([])

    const budget = ref(0)
    const budgetMin = ref(0)
    const budgetMax = ref(0)
    const budgetStep = ref(1)

    // Manual checkbox overrides, keyed by item_sku -> boolean. When present, this wins
    // over the greedy auto-selection for that row.
    const manualOverrides = ref({})

    const placing = ref(false)
    const submitError = ref(null)
    const successInfo = ref(null)

    // Per-line derivation: order quantity mirrors forecasted demand, line cost is
    // forecasted demand * unit cost, gap is how far forecast is from current demand.
    const enrichedForecasts = computed(() => {
      return forecasts.value.map(f => ({
        ...f,
        line_cost: f.forecasted_demand * f.unit_cost,
        gap: f.forecasted_demand - f.current_demand
      }))
    })

    // Urgency ranking: increasing trend first (demand is growing, restock most urgent),
    // then stable, then decreasing (demand shrinking, least urgent to restock ahead of).
    // Within a trend, larger demand gap first since it represents the bigger shortfall.
    // Tiebreak on id so equal-urgency rows keep a stable order and the table never
    // visibly jitters when values are equal.
    const trendOrder = { increasing: 0, stable: 1, decreasing: 2 }
    const rankedRows = computed(() => {
      return [...enrichedForecasts.value].sort((a, b) => {
        const trendDiff = trendOrder[a.trend] - trendOrder[b.trend]
        if (trendDiff !== 0) return trendDiff
        const gapDiff = b.gap - a.gap
        if (gapDiff !== 0) return gapDiff
        return a.id - b.id
      })
    })

    // Greedy budget allocation, skip-and-continue: walk the urgency-ranked list and take
    // any item whose line cost still fits in the remaining budget. If an item doesn't
    // fit, skip it (don't stop) so a single expensive urgent item can't block cheaper,
    // less urgent items further down the list from being funded.
    const greedySelection = computed(() => {
      const selected = new Set()
      let remainingBudget = budget.value
      for (const row of rankedRows.value) {
        if (row.line_cost <= remainingBudget) {
          selected.add(row.item_sku)
          remainingBudget -= row.line_cost
        }
      }
      return selected
    })

    // Effective selection: manual checkbox overrides win over the greedy default,
    // until the slider moves and resets them (see watch below).
    const selectedSkus = computed(() => {
      const result = new Set()
      for (const row of rankedRows.value) {
        const override = manualOverrides.value[row.item_sku]
        const isSelected = override !== undefined ? override : greedySelection.value.has(row.item_sku)
        if (isSelected) result.add(row.item_sku)
      }
      return result
    })

    const toggleSelection = (sku) => {
      const isCurrentlySelected = selectedSkus.value.has(sku)
      manualOverrides.value = { ...manualOverrides.value, [sku]: !isCurrentlySelected }
    }

    const allocated = computed(() => {
      return rankedRows.value
        .filter(row => selectedSkus.value.has(row.item_sku))
        .reduce((sum, row) => sum + row.line_cost, 0)
    })

    const remaining = computed(() => budget.value - allocated.value)
    const selectedCount = computed(() => selectedSkus.value.size)

    // Moving the slider recomputes the greedy selection from scratch and discards any
    // manual checkbox edits - a budget change invalidates the assumptions the user's
    // manual picks were made under, so silently keeping stale overrides would be more
    // surprising than resetting them.
    watch(budget, () => {
      manualOverrides.value = {}
    })

    const formatDate = (dateString) => {
      const date = new Date(dateString)
      if (isNaN(date.getTime())) return dateString
      const locale = currentLocale.value === 'ja' ? 'ja-JP' : 'en-US'
      return date.toLocaleDateString(locale, { year: 'numeric', month: 'short', day: 'numeric' })
    }

    const roundToCleanStep = (rawStep) => {
      if (rawStep <= 0) return 1
      const magnitude = Math.pow(10, Math.floor(Math.log10(rawStep)))
      return Math.max(1, Math.round(rawStep / magnitude) * magnitude)
    }

    const loadForecasts = async () => {
      try {
        loading.value = true
        error.value = null
        const data = await api.getDemandForecasts()
        forecasts.value = data

        const totalCost = data.reduce((sum, f) => sum + f.forecasted_demand * f.unit_cost, 0)
        budgetMin.value = 0
        budgetMax.value = totalCost
        budgetStep.value = roundToCleanStep(totalCost / 100)
        budget.value = Math.round(totalCost * 0.5)
      } catch (err) {
        error.value = 'Failed to load demand forecasts: ' + err.message
      } finally {
        loading.value = false
      }
    }

    const placeOrder = async () => {
      submitError.value = null
      successInfo.value = null
      placing.value = true
      try {
        const items = rankedRows.value
          .filter(row => selectedSkus.value.has(row.item_sku))
          .map(row => ({ item_sku: row.item_sku, quantity: row.forecasted_demand }))

        const order = await api.createRestockOrder({ budget: budget.value, items })
        successInfo.value = order
        manualOverrides.value = {}
      } catch (err) {
        submitError.value = t('restocking.error') + (err.response?.data?.detail ? ': ' + err.response.data.detail : '')
      } finally {
        placing.value = false
      }
    }

    onMounted(loadForecasts)

    return {
      t,
      currentCurrency,
      loading,
      error,
      budget,
      budgetMin,
      budgetMax,
      budgetStep,
      rankedRows,
      selectedSkus,
      toggleSelection,
      allocated,
      remaining,
      selectedCount,
      placing,
      submitError,
      successInfo,
      placeOrder,
      formatCurrency,
      formatCurrencyWithDecimals,
      formatDate
    }
  }
}
</script>

<style scoped>
.budget-card {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.budget-header {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
}

.budget-label {
  font-size: 0.875rem;
  font-weight: 600;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.budget-value {
  font-size: 1.75rem;
  font-weight: 700;
  color: #0f172a;
}

.budget-slider {
  width: 100%;
  accent-color: #2563eb;
}

.budget-covers-all {
  font-size: 0.875rem;
  color: #059669;
  font-weight: 600;
}

.budget-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
  padding-top: 0.5rem;
  border-top: 1px solid #f1f5f9;
}

.budget-stat-label {
  font-size: 0.75rem;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 0.25rem;
}

.budget-stat-value {
  font-size: 1.125rem;
  font-weight: 700;
  color: #0f172a;
}

.row-selected {
  background: #f0fdf4;
}

.row-muted {
  opacity: 0.55;
}

.over-budget-tag {
  margin-left: 0.5rem;
  background: #fef2f2;
  color: #991b1b;
}

.success-banner {
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
  border-radius: 8px;
  padding: 1rem 1.25rem;
  margin-bottom: 1.25rem;
}

.success-title {
  font-weight: 700;
  color: #065f46;
  margin-bottom: 0.25rem;
}

.success-detail {
  color: #166534;
  font-size: 0.875rem;
  margin-bottom: 0.5rem;
}

.success-link {
  color: #2563eb;
  font-weight: 600;
  text-decoration: none;
  font-size: 0.875rem;
}

.success-link:hover {
  text-decoration: underline;
}

.place-order-row {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-top: 1.25rem;
  padding-top: 1rem;
  border-top: 1px solid #f1f5f9;
}

.place-order-btn {
  background: #2563eb;
  color: white;
  border: none;
  border-radius: 8px;
  padding: 0.625rem 1.5rem;
  font-size: 0.938rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s ease;
}

.place-order-btn:hover:not(:disabled) {
  background: #1d4ed8;
}

.place-order-btn:disabled {
  background: #cbd5e1;
  cursor: not-allowed;
}

.nothing-selected-hint {
  color: #64748b;
  font-size: 0.875rem;
}

.submit-error {
  margin: 0;
}
</style>
