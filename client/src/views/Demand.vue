<template>
  <div class="demand">
    <div class="page-header">
      <p>{{ t('demand.description') }}</p>
    </div>

    <div v-if="loading" class="loading">{{ t('common.loading') }}</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else>
      <section class="trend-strip">
        <div class="trend-cell trend-increasing">
          <div class="trend-cell-head">
            <svg class="trend-icon" viewBox="0 0 12 12" width="12" height="12" aria-hidden="true">
              <path d="M2 9 L6 3 L10 9" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" />
            </svg>
            <span class="eyebrow">{{ t('demand.increasingDemand') }}</span>
          </div>
          <div class="trend-count num">{{ getForecastsByTrend('increasing').length }}</div>
          <div class="trend-items">
            <div v-for="item in getForecastsByTrend('increasing').slice(0, 5)" :key="item.id" class="trend-item">
              <span class="item-name">{{ item.item_name }}</span>
              <span class="item-change num">+{{ getChangePercent(item) }}%</span>
            </div>
            <div v-if="getForecastsByTrend('increasing').length > 5" class="more-items">
              +{{ getForecastsByTrend('increasing').length - 5 }} {{ t('demand.more') }}
            </div>
          </div>
        </div>

        <div class="trend-cell trend-stable">
          <div class="trend-cell-head">
            <svg class="trend-icon" viewBox="0 0 12 12" width="12" height="12" aria-hidden="true">
              <path d="M2 6 L10 6" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" />
            </svg>
            <span class="eyebrow">{{ t('demand.stableDemand') }}</span>
          </div>
          <div class="trend-count num">{{ getForecastsByTrend('stable').length }}</div>
          <div class="trend-items">
            <div v-for="item in getForecastsByTrend('stable').slice(0, 5)" :key="item.id" class="trend-item">
              <span class="item-name">{{ item.item_name }}</span>
              <span class="item-change num">{{ getChangePercent(item) }}%</span>
            </div>
            <div v-if="getForecastsByTrend('stable').length > 5" class="more-items">
              +{{ getForecastsByTrend('stable').length - 5 }} {{ t('demand.more') }}
            </div>
          </div>
        </div>

        <div class="trend-cell trend-decreasing">
          <div class="trend-cell-head">
            <svg class="trend-icon" viewBox="0 0 12 12" width="12" height="12" aria-hidden="true">
              <path d="M2 3 L6 9 L10 3" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" />
            </svg>
            <span class="eyebrow">{{ t('demand.decreasingDemand') }}</span>
          </div>
          <div class="trend-count num">{{ getForecastsByTrend('decreasing').length }}</div>
          <div class="trend-items">
            <div v-for="item in getForecastsByTrend('decreasing').slice(0, 5)" :key="item.id" class="trend-item">
              <span class="item-name">{{ item.item_name }}</span>
              <span class="item-change num">{{ getChangePercent(item) }}%</span>
            </div>
            <div v-if="getForecastsByTrend('decreasing').length > 5" class="more-items">
              +{{ getForecastsByTrend('decreasing').length - 5 }} {{ t('demand.more') }}
            </div>
          </div>
        </div>
      </section>

      <section>
        <div class="section-head">
          <h3>{{ t('demand.demandForecasts') }}</h3>
        </div>
        <div class="table-container">
          <table>
            <thead>
              <tr>
                <th>{{ t('demand.table.sku') }}</th>
                <th>{{ t('demand.table.currentDemand') }}</th>
                <th>{{ t('demand.table.forecastedDemand') }}</th>
                <th>{{ t('demand.table.change') }}</th>
                <th>{{ t('demand.table.trend') }}</th>
                <th>{{ t('demand.table.period') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="forecast in forecasts" :key="forecast.id">
                <td>
                  <span class="cell-sku"><b>{{ forecast.item_sku }}</b></span>
                  <span class="cell-name">{{ forecast.item_name }}</span>
                </td>
                <td class="num">{{ forecast.current_demand }}</td>
                <td class="num"><strong>{{ forecast.forecasted_demand }}</strong></td>
                <td>
                  <span class="num" :style="{ color: getChangeColor(forecast) }">
                    {{ getChangePercent(forecast) }}%
                  </span>
                </td>
                <td>
                  <span :class="['badge', forecast.trend]">
                    {{ t(`trends.${forecast.trend}`) }}
                  </span>
                </td>
                <td>{{ translatePeriod(forecast.period) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, watch, computed } from 'vue'
import { api } from '../api'
import { useFilters } from '../composables/useFilters'
import { useI18n } from '../composables/useI18n'

export default {
  name: 'Demand',
  setup() {
    const { t } = useI18n()
    const loading = ref(true)
    const error = ref(null)
    const allForecasts = ref([])
    const inventoryItems = ref([])

    // Use shared filters
    const { selectedLocation, selectedCategory, getCurrentFilters } = useFilters()

    // Filter forecasts based on inventory filters
    const forecasts = computed(() => {
      if (selectedLocation.value === 'all' && selectedCategory.value === 'all') {
        return allForecasts.value
      }

      // Get SKUs of items that match the filters
      const validSkus = new Set(inventoryItems.value.map(item => item.sku))
      return allForecasts.value.filter(f => validSkus.has(f.item_sku))
    })

    const loadForecasts = async () => {
      try {
        loading.value = true
        const filters = getCurrentFilters()

        const [forecastsData, inventoryData] = await Promise.all([
          api.getDemandForecasts(),
          api.getInventory({
            warehouse: filters.warehouse,
            category: filters.category
          })
        ])

        allForecasts.value = forecastsData
        inventoryItems.value = inventoryData
      } catch (err) {
        error.value = 'Failed to load demand forecasts: ' + err.message
      } finally {
        loading.value = false
      }
    }

    // Watch for filter changes and reload data
    watch([selectedLocation, selectedCategory], () => {
      loadForecasts()
    })

    const getForecastsByTrend = (trend) => {
      return forecasts.value.filter(f => f.trend === trend)
    }

    const getChangePercent = (forecast) => {
      const change = ((forecast.forecasted_demand - forecast.current_demand) / forecast.current_demand * 100).toFixed(1)
      return change > 0 ? `+${change}` : change
    }

    const getChangeColor = (forecast) => {
      const change = forecast.forecasted_demand - forecast.current_demand
      const changePercent = Math.abs((change / forecast.current_demand) * 100)

      // If change is within ±2%, consider it stable and show blue
      if (changePercent <= 2) {
        return '#3b82f6' // Blue for stable
      }

      if (change > 0) return '#10b981' // Green for increasing
      if (change < 0) return '#ef4444' // Red for decreasing
      return '#3b82f6' // Blue for no change
    }

    const translatePeriod = (period) => {
      // Period values like "Next 3 months", "Q1 2025", "30 days", etc.
      const { currentLocale } = useI18n()
      if (currentLocale.value === 'ja') {
        return period
          .replace(/Next\s+/i, '次の')
          .replace(/\s+months/i, 'か月')
          .replace(/\s+month/i, 'か月')
          .replace(/\s+days/i, '日間')
          .replace(/\s+day/i, '日')
          .replace('Q1', '第1四半期')
          .replace('Q2', '第2四半期')
          .replace('Q3', '第3四半期')
          .replace('Q4', '第4四半期')
      }
      return period
    }

    onMounted(loadForecasts)

    return {
      t,
      loading,
      error,
      forecasts,
      getForecastsByTrend,
      getChangePercent,
      getChangeColor,
      translatePeriod
    }
  }
}
</script>

<style scoped>
/* Trend strip: one outer border, 1px dividers between cells — same
   register as the global .stats-grid, but each cell also carries a
   short item list beneath its count. */
.trend-strip {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  background: var(--surface);
  border: 1px solid var(--rule);
  border-radius: var(--r-sm);
  margin-bottom: var(--s10);
}

.trend-cell {
  padding: var(--s5);
  border-right: 1px solid var(--rule);
}

.trend-cell:last-child {
  border-right: none;
}

.trend-cell-head {
  display: flex;
  align-items: center;
  gap: var(--s2);
  margin-bottom: var(--s3);
}

.trend-icon {
  flex-shrink: 0;
}

.trend-count {
  font-size: 26px;
  font-weight: 600;
  line-height: 1;
  margin-bottom: var(--s4);
}

.trend-increasing .trend-icon,
.trend-increasing .trend-count { color: var(--mint); }

.trend-stable .trend-icon,
.trend-stable .trend-count { color: var(--steel); }

.trend-decreasing .trend-icon,
.trend-decreasing .trend-count { color: var(--signal); }

.trend-items {
  display: flex;
  flex-direction: column;
  gap: var(--s2);
  padding-top: var(--s3);
  border-top: 1px solid var(--rule);
}

.trend-item {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: var(--s3);
}

.item-name {
  font-size: var(--t-sm);
  color: var(--ink);
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.item-change {
  font-size: var(--t-sm);
  font-weight: 600;
  flex-shrink: 0;
}

.trend-increasing .item-change { color: var(--mint); }
.trend-stable .item-change { color: var(--steel); }
.trend-decreasing .item-change { color: var(--signal); }

.more-items {
  font-size: var(--t-xs);
  color: var(--steel-soft);
  text-align: center;
  padding-top: var(--s1);
}
</style>
