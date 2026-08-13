<template>
  <div class="restocking">
    <div class="page-header">
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

      <section class="section">
        <div class="section-head">
          <h3>{{ t('restocking.budget.label') }}</h3>
          <span v-if="budget >= totalCost" class="section-note budget-covers-all">
            {{ t('restocking.budget.coversAll') }}
          </span>
        </div>
        <div class="card budget-card">
          <div class="budget-header">
            <div class="eyebrow">{{ t('restocking.budget.label') }}</div>
            <div class="budget-value num">{{ formatCurrency(budget, currentCurrency) }}</div>
          </div>
          <input
            type="range"
            class="budget-slider"
            :min="budgetMin"
            :max="budgetMax"
            :step="budgetStep"
            v-model.number="budget"
          />
          <!-- Compare against the actual basket total, not the rounded-up budgetMax, since
               budgetMax is padded to the next step multiple and could be reached before the
               basket is actually fully covered. -->
          <div class="budget-stats stats-grid">
            <div class="stat-card">
              <div class="stat-label">{{ t('restocking.budget.allocated') }}</div>
              <div class="stat-value num">{{ formatCurrency(allocated, currentCurrency) }}</div>
            </div>
            <div class="stat-card">
              <div class="stat-label">{{ t('restocking.budget.remaining') }}</div>
              <div class="stat-value num" :class="{ 'value-negative': remaining < 0 }">
                {{ formatCurrency(remaining, currentCurrency) }}
              </div>
            </div>
            <div class="stat-card">
              <div class="stat-label">{{ t('restocking.budget.selectedItems') }}</div>
              <div class="stat-value num">{{ selectedCount }}</div>
            </div>
          </div>
        </div>
      </section>

      <section class="section">
        <div class="section-head">
          <h3>{{ t('restocking.table.title') }}</h3>
        </div>
        <div class="card">
          <div class="table-container">
            <table>
              <thead>
                <tr>
                  <th>{{ t('restocking.table.include') }}</th>
                  <th>{{ t('restocking.table.sku') }}</th>
                  <th>{{ t('restocking.table.trend') }}</th>
                  <th class="num">{{ t('restocking.table.forecastedDemand') }}</th>
                  <th class="num">{{ t('restocking.table.gap') }}</th>
                  <th class="num">{{ t('restocking.table.quantity') }}</th>
                  <th class="num">{{ t('restocking.table.unitCost') }}</th>
                  <th class="num">{{ t('restocking.table.lineCost') }}</th>
                  <th>{{ t('restocking.table.leadTime') }}</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="row in rankedRows"
                  :key="row.item_sku"
                  :class="{
                    'row-selected': selectedSkus.has(row.item_sku),
                    'row-muted': !selectedSkus.has(row.item_sku),
                    'row-over-budget': !greedySelection.has(row.item_sku)
                  }"
                >
                  <td>
                    <input
                      type="checkbox"
                      :checked="selectedSkus.has(row.item_sku)"
                      @change="toggleSelection(row.item_sku)"
                    />
                  </td>
                  <td>
                    <span class="cell-sku"><b>{{ row.item_sku }}</b></span>
                    <span class="cell-name">
                      {{ row.item_name }}
                      <!-- Tag reflects affordability (greedySelection), not the checkbox state
                           (selectedSkus). A row the user unchecked but the budget could still
                           afford is not "over budget" - it's muted, tag-free. A row the user
                           manually checked despite it not fitting the greedy walk is genuinely
                           over budget once added, so the tag still applies. -->
                      <span v-if="!greedySelection.has(row.item_sku)" class="badge danger over-budget-tag">
                        {{ t('restocking.overBudget') }}
                      </span>
                    </span>
                  </td>
                  <td>
                    <span :class="['badge', row.trend]">
                      {{ t(`trends.${row.trend}`) }}
                    </span>
                  </td>
                  <td class="num">{{ row.forecasted_demand }}</td>
                  <td class="num">{{ row.gap > 0 ? '+' : '' }}{{ row.gap }}</td>
                  <td class="num">{{ row.forecasted_demand }}</td>
                  <!-- Unit cost needs cents: rounding to whole dollars makes qty * unit price
                       visibly not match the line cost shown next to it. -->
                  <td class="num">{{ formatCurrencyWithDecimals(row.unit_cost, currentCurrency, 2) }}</td>
                  <td class="num">{{ formatCurrency(row.line_cost, currentCurrency) }}</td>
                  <td class="lead-time">{{ t('restocking.days', { count: row.lead_time_days }) }}</td>
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
      </section>
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
    // Actual sum of every line cost in the basket. budgetMax is rounded UP to a step
    // multiple (see loadForecasts) so the slider thumb can land on it, which means
    // budgetMax can overshoot the real total - this is the true "covers everything" line.
    const totalCost = ref(0)

    // Manual checkbox overrides, keyed by item_sku -> boolean. When present, this wins
    // over the greedy auto-selection for that row.
    const manualOverrides = ref({})

    // True right after a successful submit, before the user expresses any new intent
    // (moving the slider or toggling a row). While true, the table must show nothing
    // selected and Place Order must stay disabled, so a second click can't silently
    // resubmit the same basket as a duplicate order.
    const justSubmitted = ref(false)

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
    // until the slider moves and resets them (see watch below). Right after a submit,
    // force this to empty regardless of overrides/greedy result, so the basket can't
    // silently snap back to "everything checked" and enable a duplicate submit.
    const selectedSkus = computed(() => {
      if (justSubmitted.value) return new Set()
      const result = new Set()
      for (const row of rankedRows.value) {
        const override = manualOverrides.value[row.item_sku]
        const isSelected = override !== undefined ? override : greedySelection.value.has(row.item_sku)
        if (isSelected) result.add(row.item_sku)
      }
      return result
    })

    const toggleSelection = (sku) => {
      // Toggling a checkbox is a fresh intent, so it both clears the post-submit lock
      // and applies the toggle in the same action.
      justSubmitted.value = false
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
      // Moving the slider is also a fresh intent, so it clears the post-submit lock
      // the same way a checkbox toggle does.
      justSubmitted.value = false
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

        const total = data.reduce((sum, f) => sum + f.forecasted_demand * f.unit_cost, 0)
        totalCost.value = total
        budgetMin.value = 0
        // A range input only lands on min + n*step, so if budgetMax were the raw total,
        // the thumb could never actually reach it. Compute the clean step first, then
        // round the max UP to the next whole multiple of that step so the far right of
        // the track always exists and always covers the full basket.
        const step = roundToCleanStep(total / 100)
        budgetStep.value = step
        budgetMax.value = Math.ceil(total / step) * step
        // Snap the 50% default to a step multiple too, so the thumb position and the
        // displayed figure agree on first paint instead of disagreeing until the user drags.
        budget.value = Math.round((total * 0.5) / step) * step
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
        // Clear the selection outright rather than just discarding overrides: overrides
        // alone fall back to the greedy set, which would instantly re-check every row
        // and leave Place Order enabled with an identical basket - a second click would
        // silently submit a duplicate order. justSubmitted forces the table to show zero
        // selected until the user expresses a new intent (slider move or checkbox toggle).
        manualOverrides.value = {}
        justSubmitted.value = true
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
      totalCost,
      rankedRows,
      greedySelection,
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
.section {
  margin-bottom: var(--s10);
}

.section:last-child {
  margin-bottom: 0;
}

.budget-card {
  display: flex;
  flex-direction: column;
  gap: var(--s5);
}

.budget-header {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
}

.budget-value {
  font-size: var(--t-2xl);
  font-weight: 600;
  color: var(--ink);
}

.budget-slider {
  -webkit-appearance: none;
  appearance: none;
  width: 100%;
  height: 6px;
  background: var(--rule);
  border-radius: 99px;
  outline: none;
}

.budget-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 18px;
  height: 18px;
  border-radius: var(--r-sm);
  background: var(--ink);
  border: 2px solid var(--surface);
  box-shadow: var(--e-1);
  cursor: pointer;
}

.budget-slider::-moz-range-thumb {
  width: 18px;
  height: 18px;
  border-radius: var(--r-sm);
  background: var(--ink);
  border: 2px solid var(--surface);
  cursor: pointer;
}

.budget-slider:focus-visible {
  box-shadow: var(--ring);
}

.budget-covers-all {
  font-weight: 600;
  color: var(--mint);
}

.budget-stats {
  margin-bottom: 0;
}

.value-negative {
  color: var(--signal);
}

.row-selected {
  background: var(--surface-alt);
}

.row-muted {
  opacity: 0.55;
}

.row-over-budget {
  background: var(--signal-soft);
}

.over-budget-tag {
  margin-left: var(--s2);
}

.success-banner {
  background: var(--mint-soft);
  border: 1px solid var(--mint);
  border-radius: var(--r-sm);
  padding: var(--s4) var(--s5);
  margin-bottom: var(--s5);
}

.success-title {
  font-weight: 700;
  color: var(--ink);
  margin-bottom: var(--s1);
}

.success-detail {
  color: var(--steel);
  font-size: var(--t-md);
  margin-bottom: var(--s2);
}

.success-link {
  color: var(--info);
  font-weight: 600;
  text-decoration: none;
  font-size: var(--t-md);
}

.success-link:hover {
  text-decoration: underline;
}

.place-order-row {
  display: flex;
  align-items: center;
  gap: var(--s4);
  margin-top: var(--s5);
  padding-top: var(--s4);
  border-top: 1px solid var(--rule);
}

.place-order-btn {
  background: var(--ink);
  color: var(--paper);
  border-radius: var(--r-sm);
  padding: 10px var(--s5);
  font-weight: 600;
  font-size: var(--t-md);
  cursor: pointer;
  transition: background 0.2s ease;
}

.place-order-btn:hover:not(:disabled) {
  background: var(--steel);
}

.place-order-btn:disabled {
  background: var(--rule-strong);
  color: var(--surface);
  cursor: not-allowed;
}

.nothing-selected-hint {
  color: var(--steel);
  font-size: var(--t-md);
}

.submit-error {
  margin: 0;
}

.lead-time {
  font-family: var(--mono);
  color: var(--steel);
}

input[type='checkbox'] {
  accent-color: var(--ink);
}
</style>
