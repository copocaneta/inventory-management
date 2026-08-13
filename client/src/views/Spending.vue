<template>
  <div class="spending">
    <div class="page-header">
      <p>{{ t('finance.description') }}</p>
    </div>

    <div v-if="loading" class="loading">{{ t('common.loading') }}</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else>
      <!-- Revenue & Financial KPIs -->
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-label">{{ t('finance.totalRevenue') }}</div>
          <div class="stat-value">{{ formatCurrency(revenueMetrics.totalRevenue) }}</div>
          <div class="stat-change positive">
            <span class="change-icon">↑</span>
            {{ t('finance.fromOrders', { count: revenueMetrics.orderCount }) }}
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-label">{{ t('finance.totalCosts') }}</div>
          <div class="stat-value">{{ formatCurrency(totalCosts) }}</div>
          <div class="stat-meta">{{ t('finance.costBreakdown') }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">{{ t('finance.netProfit') }}</div>
          <div class="stat-value">{{ formatCurrency(netProfit) }}</div>
          <div class="stat-meta">{{ profitMargin }}% {{ t('finance.margin') }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">{{ t('finance.avgOrderValue') }}</div>
          <div class="stat-value">{{ formatCurrency(revenueMetrics.avgOrderValue) }}</div>
          <div class="stat-meta">{{ t('finance.perOrderRevenue') }}</div>
        </div>
      </div>

      <!-- Monthly Revenue vs Cost Chart -->
      <section class="section-block">
        <div class="section-head">
          <h3>{{ t('finance.revenueVsCosts.title') }}</h3>
          <div class="chart-legend section-note">
            <span class="legend-item"><span class="legend-dot revenue-color"></span>{{ t('finance.revenueVsCosts.revenue') }}</span>
            <span class="legend-item"><span class="legend-dot cost-color"></span>{{ t('finance.revenueVsCosts.costs') }}</span>
          </div>
        </div>
        <div class="card">
          <div class="chart-container">
            <div class="bar-chart">
              <div class="y-axis">
                <span>{{ currencySymbol }}{{ maxRevenueValue }}K</span>
                <span>{{ currencySymbol }}{{ Math.round(maxRevenueValue * 0.75) }}K</span>
                <span>{{ currencySymbol }}{{ Math.round(maxRevenueValue * 0.5) }}K</span>
                <span>{{ currencySymbol }}{{ Math.round(maxRevenueValue * 0.25) }}K</span>
                <span>{{ currencySymbol }}0</span>
              </div>
              <div class="chart-area">
                <div v-for="month in monthlyRevenue" :key="month.month" class="bar-group-revenue">
                  <div class="revenue-bars">
                    <div
                      class="revenue-bar"
                      :class="{ 'bar-accent': month.revenue === Math.max(...monthlyRevenue.map(m => m.revenue)) }"
                      :style="{ height: getRevenueBarHeight(month.revenue) + '%' }"
                      :title="`Revenue: ${currencySymbol}${month.revenue.toLocaleString()}`"
                    ></div>
                    <div class="cost-bar" :style="{ height: getRevenueBarHeight(month.costs) + '%' }" :title="`Costs: ${currencySymbol}${month.costs.toLocaleString()}`"></div>
                  </div>
                  <span class="bar-label">{{ translateMonth(month.month) }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Monthly Cost Flow Chart -->
      <section class="section-block">
        <div class="section-head">
          <h3>{{ t('finance.monthlyCostFlow.title') }}</h3>
          <div class="chart-legend section-note">
            <span class="legend-item"><span class="legend-dot procurement"></span>{{ t('finance.monthlyCostFlow.procurement') }}</span>
            <span class="legend-item"><span class="legend-dot operational"></span>{{ t('finance.monthlyCostFlow.operational') }}</span>
            <span class="legend-item"><span class="legend-dot labor"></span>{{ t('finance.monthlyCostFlow.labor') }}</span>
            <span class="legend-item"><span class="legend-dot overhead"></span>{{ t('finance.monthlyCostFlow.overhead') }}</span>
          </div>
        </div>
        <div class="card">
          <div class="chart-container">
            <div class="bar-chart">
              <div class="y-axis">
                <span>{{ currencySymbol }}25K</span>
                <span>{{ currencySymbol }}20K</span>
                <span>{{ currencySymbol }}15K</span>
                <span>{{ currencySymbol }}10K</span>
                <span>{{ currencySymbol }}5K</span>
                <span>{{ currencySymbol }}0</span>
              </div>
              <div class="chart-area">
                <div v-for="month in monthlySpending" :key="month.month" class="bar-group">
                  <div class="stacked-bar" @click="showCostDetail(month)">
                    <div class="bar-segment procurement" :style="{ height: getBarHeight(month.procurement) + '%' }" :title="`Procurement: ${currencySymbol}${month.procurement.toLocaleString()}`"></div>
                    <div class="bar-segment operational" :style="{ height: getBarHeight(month.operational) + '%' }" :title="`Operational: ${currencySymbol}${month.operational.toLocaleString()}`"></div>
                    <div class="bar-segment labor" :style="{ height: getBarHeight(month.labor) + '%' }" :title="`Labor: ${currencySymbol}${month.labor.toLocaleString()}`"></div>
                    <div class="bar-segment overhead" :style="{ height: getBarHeight(month.overhead) + '%' }" :title="`Overhead: ${currencySymbol}${month.overhead.toLocaleString()}`"></div>
                  </div>
                  <span class="bar-label">{{ translateMonth(month.month) }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <div class="two-column-grid">
        <!-- Category Spending Breakdown -->
        <section class="section-block">
          <div class="section-head">
            <h3>{{ t('finance.categorySpending.title') }}</h3>
          </div>
          <div class="card">
            <div class="category-list">
              <div v-for="category in categorySpending" :key="category.category" class="category-item">
                <div class="category-info">
                  <div class="category-name">{{ translateCategory(category.category) }}</div>
                  <div class="category-amount num">{{ currencySymbol }}{{ category.amount.toLocaleString() }}</div>
                </div>
                <div class="category-bar-container">
                  <div
                    class="category-bar"
                    :class="{ 'bar-accent': category.percentage === Math.max(...categorySpending.map(c => c.percentage)) }"
                    :style="{ width: category.percentage + '%' }"
                  ></div>
                </div>
                <div class="category-meta">
                  <span class="percentage">{{ category.percentage }}% {{ t('finance.categorySpending.ofTotal') }}</span>
                  <span class="change num" :class="{ positive: category.change > 0, negative: category.change < 0 }">
                    {{ category.change > 0 ? '+' : '' }}{{ category.change }}%
                  </span>
                </div>
              </div>
            </div>
          </div>
        </section>

        <!-- Recent Transactions -->
        <section class="section-block">
          <div class="section-head">
            <h3>{{ t('finance.transactions.title') }}</h3>
          </div>
          <div class="card transactions-card">
            <div class="table-container transactions-table-container">
              <table>
                <thead>
                  <tr>
                    <th>{{ t('finance.transactions.id') }}</th>
                    <th>{{ t('finance.transactions.description') }}</th>
                    <th>{{ t('finance.transactions.vendor') }}</th>
                    <th>{{ t('finance.transactions.date') }}</th>
                    <th class="text-right">{{ t('finance.transactions.amount') }}</th>
                  </tr>
                </thead>
                <tbody>
                  <tr
                    v-for="transaction in recentTransactions"
                    :key="transaction.id"
                    class="clickable-row"
                    @click="handleTransactionClick(transaction)"
                  >
                    <td class="transaction-id">{{ transaction.id.toString().padStart(3, '0') }}</td>
                    <td class="transaction-description">{{ transaction.description }}</td>
                    <td class="transaction-vendor">{{ transaction.vendor }}</td>
                    <td class="transaction-date">{{ formatDateShort(transaction.date) }}</td>
                    <td class="transaction-amount num text-right">{{ currencySymbol }}{{ transaction.amount.toLocaleString() }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </section>
      </div>
    </div>

    <CostDetailModal
      :is-open="showCostModal"
      :cost-data="selectedCostData"
      @close="showCostModal = false"
    />
  </div>
</template>

<script>
import { ref, onMounted, watch, computed } from 'vue'
import { api } from '../api'
import { useFilters } from '../composables/useFilters'
import { useI18n } from '../composables/useI18n'
import { formatCurrency as formatCurrencyUtil } from '../utils/currency'
import CostDetailModal from '../components/CostDetailModal.vue'

export default {
  name: 'Spending',
  components: {
    CostDetailModal
  },
  setup() {
    const { t, currentCurrency } = useI18n()
    const loading = ref(true)
    const error = ref(null)
    const allMonthlySpending = ref([])
    const allCategorySpending = ref([])
    const allTransactions = ref([])
    const summaryData = ref({})
    const allOrders = ref([])

    // Modal state
    const showCostModal = ref(false)
    const selectedCostData = ref(null)

    // Use shared filters
    const { selectedPeriod, getCurrentFilters } = useFilters()

    // Monthly spending chart always shows all months (not filtered)
    const monthlySpending = computed(() => {
      return allMonthlySpending.value
    })

    // Filtered monthly spending for summary calculations only
    const filteredMonthlySpending = computed(() => {
      if (selectedPeriod.value === 'all') {
        return allMonthlySpending.value
      }

      // Extract month name from YYYY-MM format
      const monthMap = {
        '01': 'Jan', '02': 'Feb', '03': 'Mar', '04': 'Apr',
        '05': 'May', '06': 'Jun', '07': 'Jul', '08': 'Aug',
        '09': 'Sep', '10': 'Oct', '11': 'Nov', '12': 'Dec'
      }
      const selectedMonth = monthMap[selectedPeriod.value.split('-')[1]]
      return allMonthlySpending.value.filter(m => m.month === selectedMonth)
    })

    const categorySpending = computed(() => {
      return allCategorySpending.value
    })

    const recentTransactions = computed(() => {
      if (selectedPeriod.value === 'all') {
        return allTransactions.value
      }
      // Filter transactions by selected month
      return allTransactions.value.filter(t => {
        const transactionMonth = new Date(t.date).toISOString().slice(0, 7)
        return transactionMonth === selectedPeriod.value
      })
    })

    const summary = computed(() => {
      // Recalculate summary based on filteredMonthlySpending (not the chart data)
      if (filteredMonthlySpending.value.length === 0) {
        return summaryData.value
      }

      const totals = filteredMonthlySpending.value.reduce((acc, month) => ({
        procurement: acc.procurement + month.procurement,
        operational: acc.operational + month.operational,
        labor: acc.labor + month.labor,
        overhead: acc.overhead + month.overhead
      }), { procurement: 0, operational: 0, labor: 0, overhead: 0 })

      return {
        total_procurement_cost: totals.procurement,
        total_operational_cost: totals.operational,
        total_labor_cost: totals.labor,
        total_overhead: totals.overhead,
        procurement_change: summaryData.value.procurement_change || 0,
        operational_change: summaryData.value.operational_change || 0,
        labor_change: summaryData.value.labor_change || 0,
        overhead_change: summaryData.value.overhead_change || 0
      }
    })

    // Filtered orders based on selected period
    const filteredOrders = computed(() => {
      if (selectedPeriod.value === 'all') {
        return allOrders.value
      }

      // Filter orders by selected month
      return allOrders.value.filter(order => {
        const orderMonth = new Date(order.order_date).toISOString().slice(0, 7)
        return orderMonth === selectedPeriod.value
      })
    })

    // Revenue metrics from filtered orders
    const revenueMetrics = computed(() => {
      const totalRevenue = filteredOrders.value.reduce((sum, order) => sum + (order.total_value || 0), 0)
      const orderCount = filteredOrders.value.length
      const avgOrderValue = orderCount > 0 ? totalRevenue / orderCount : 0

      return {
        totalRevenue,
        orderCount,
        avgOrderValue,
        revenueGrowth: 15.3 // Placeholder - could calculate from historical data
      }
    })

    // Total costs from summary
    const totalCosts = computed(() => {
      return summary.value.total_procurement_cost +
             summary.value.total_operational_cost +
             summary.value.total_labor_cost +
             summary.value.total_overhead
    })

    // Net profit
    const netProfit = computed(() => {
      return revenueMetrics.value.totalRevenue - totalCosts.value
    })

    // Profit margin percentage
    const profitMargin = computed(() => {
      if (revenueMetrics.value.totalRevenue === 0) return 0
      return ((netProfit.value / revenueMetrics.value.totalRevenue) * 100).toFixed(1)
    })

    // Monthly revenue data for chart
    const monthlyRevenue = computed(() => {
      const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

      // Initialize all months
      const revenueByMonth = monthNames.map(month => ({
        month,
        revenue: 0,
        costs: 0
      }))

      // Calculate revenue from orders
      allOrders.value.forEach(order => {
        const orderDate = new Date(order.order_date)
        const monthIndex = orderDate.getMonth()
        if (monthIndex >= 0 && monthIndex < 12) {
          revenueByMonth[monthIndex].revenue += order.total_value || 0
        }
      })

      // Add costs from spending data
      allMonthlySpending.value.forEach(spending => {
        const monthIndex = monthNames.indexOf(spending.month)
        if (monthIndex >= 0) {
          revenueByMonth[monthIndex].costs = spending.procurement + spending.operational + spending.labor + spending.overhead
        }
      })

      return revenueByMonth
    })

    // Max value for chart scaling
    const maxRevenueValue = computed(() => {
      const maxRevenue = Math.max(...monthlyRevenue.value.map(m => m.revenue))
      const maxCost = Math.max(...monthlyRevenue.value.map(m => m.costs))
      const max = Math.max(maxRevenue, maxCost)
      return Math.ceil(max / 1000) // Return in K
    })

    const loadData = async () => {
      try {
        loading.value = true
        const [summaryRes, monthlyRes, categoryRes, transactionsRes, ordersRes] = await Promise.all([
          api.getSpendingSummary(),
          api.getMonthlySpending(),
          api.getCategorySpending(),
          api.getTransactions(),
          api.getOrders()
        ])

        summaryData.value = summaryRes
        allMonthlySpending.value = monthlyRes
        allCategorySpending.value = categoryRes
        allTransactions.value = transactionsRes
        allOrders.value = ordersRes
      } catch (err) {
        error.value = 'Failed to load financial data: ' + err.message
      } finally {
        loading.value = false
      }
    }

    // Watch for period filter changes
    watch([selectedPeriod], () => {
      // Data will automatically update via computed properties
    })

    const formatCurrency = (value) => {
      return formatCurrencyUtil(value, currentCurrency.value)
    }

    const currencySymbol = computed(() => {
      return currentCurrency.value === 'JPY' ? '¥' : '$'
    })

    const getBarHeight = (value) => {
      const maxValue = 25000
      return (value / maxValue) * 100
    }

    const getRevenueBarHeight = (value) => {
      const maxValue = maxRevenueValue.value * 1000
      return (value / maxValue) * 100
    }

    const formatDate = (dateString) => {
      return new Date(dateString).toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric'
      })
    }

    const formatDateShort = (dateString) => {
      const date = new Date(dateString)
      const month = (date.getMonth() + 1).toString().padStart(2, '0')
      const day = date.getDate().toString().padStart(2, '0')
      const year = date.getFullYear().toString().slice(-2)
      return `${month}/${day}/${year}`
    }

    const translateMonth = (month) => {
      const monthMap = {
        'Jan': t('months.jan'),
        'Feb': t('months.feb'),
        'Mar': t('months.mar'),
        'Apr': t('months.apr'),
        'May': t('months.may'),
        'Jun': t('months.jun'),
        'Jul': t('months.jul'),
        'Aug': t('months.aug'),
        'Sep': t('months.sep'),
        'Oct': t('months.oct'),
        'Nov': t('months.nov'),
        'Dec': t('months.dec')
      }
      return monthMap[month] || month
    }

    const translateCategory = (category) => {
      // First try spending categories
      const spendingCategoryMap = {
        'Raw Materials': t('spendingCategories.rawMaterials'),
        'Components': t('spendingCategories.components'),
        'Equipment': t('spendingCategories.equipment'),
        'Consumables': t('spendingCategories.consumables')
      }

      // Then try product categories
      const productCategoryMap = {
        'Circuit Boards': t('categories.circuitBoards'),
        'Sensors': t('categories.sensors'),
        'Actuators': t('categories.actuators'),
        'Controllers': t('categories.controllers'),
        'Power Supplies': t('categories.powerSupplies')
      }

      return spendingCategoryMap[category] || productCategoryMap[category] || category
    }

    const handleTransactionClick = (transaction) => {
      console.log('Transaction clicked:', transaction)
      alert(`Transaction Details:\n\nID: ${transaction.id}\nDescription: ${transaction.description}\nVendor: ${transaction.vendor}\nDate: ${formatDateShort(transaction.date)}\nAmount: $${transaction.amount.toLocaleString()}`)
    }

    const showCostDetail = (monthData) => {
      selectedCostData.value = monthData
      showCostModal.value = true
    }

    onMounted(loadData)

    return {
      t,
      loading,
      error,
      summary,
      monthlySpending,
      categorySpending,
      recentTransactions,
      revenueMetrics,
      totalCosts,
      netProfit,
      profitMargin,
      monthlyRevenue,
      maxRevenueValue,
      formatCurrency,
      currencySymbol,
      getBarHeight,
      getRevenueBarHeight,
      formatDate,
      formatDateShort,
      translateMonth,
      translateCategory,
      handleTransactionClick,
      showCostModal,
      selectedCostData,
      showCostDetail,
      Math
    }
  }
}
</script>

<style scoped>
.stat-change {
  margin-top: var(--s3);
  font-family: var(--mono);
  font-size: var(--t-sm);
  display: flex;
  align-items: center;
  gap: var(--s1);
}

.stat-change.positive {
  color: var(--mint);
}

.stat-change.negative {
  color: var(--signal);
}

.change-icon {
  font-weight: 700;
}

.stat-meta {
  margin-top: var(--s2);
  font-family: var(--mono);
  font-size: var(--t-sm);
  color: var(--steel);
}

/* ---------- sections ---------- */

.section-block {
  margin-bottom: var(--s10);
}

.section-block:last-child {
  margin-bottom: 0;
}

.section-block .card {
  margin-bottom: 0;
}

.chart-legend {
  display: flex;
  gap: var(--s5);
}

.legend-item {
  display: flex;
  align-items: center;
  gap: var(--s2);
  font-family: var(--mono);
  font-size: var(--t-sm);
  color: var(--steel);
}

.legend-dot {
  width: 8px;
  height: 8px;
  border-radius: 2px;
}

.legend-dot.procurement { background: var(--ink); }
.legend-dot.operational { background: var(--steel); }
.legend-dot.labor { background: var(--steel-soft); }
.legend-dot.overhead { background: var(--rule-strong); }
.legend-dot.revenue-color { background: var(--ink); }
.legend-dot.cost-color { background: var(--steel); }

/* ---------- revenue vs cost chart ---------- */

.bar-group-revenue {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex: 1;
  height: 100%;
}

.revenue-bars {
  width: 100%;
  max-width: 80px;
  display: flex;
  gap: 6px;
  justify-content: center;
  align-items: flex-end;
  height: 100%;
  padding-bottom: var(--s6);
}

.revenue-bar, .cost-bar {
  width: 50%;
  max-width: 30px;
  border-radius: var(--r-sm) var(--r-sm) 0 0;
  transition: opacity 0.15s ease;
  cursor: pointer;
  min-height: 4px;
}

.revenue-bar {
  background: var(--ink);
}

.revenue-bar.bar-accent {
  background: var(--amber);
}

.cost-bar {
  background: var(--steel);
}

.revenue-bar:hover, .cost-bar:hover {
  opacity: 0.8;
}

/* ---------- shared bar chart shell ---------- */

.chart-container {
  padding: var(--s5) 0;
}

.bar-chart {
  display: flex;
  gap: var(--s6);
  height: 350px;
}

.y-axis {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding-right: var(--s4);
  font-family: var(--mono);
  font-size: var(--t-xs);
  color: var(--steel-soft);
  border-right: 1px solid var(--rule);
}

.chart-area {
  flex: 1;
  display: flex;
  align-items: flex-end;
  justify-content: space-around;
  gap: var(--s2);
}

/* ---------- monthly cost flow (stacked) ---------- */

.bar-group {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex: 1;
  height: 100%;
}

.stacked-bar {
  width: 100%;
  max-width: 60px;
  display: flex;
  flex-direction: column-reverse;
  align-items: stretch;
  height: 100%;
  padding-bottom: var(--s6);
  cursor: pointer;
  transition: opacity 0.2s ease;
}

.stacked-bar:hover {
  opacity: 0.85;
}

.bar-segment {
  width: 100%;
  transition: opacity 0.15s ease;
  cursor: pointer;
  display: block;
}

.bar-segment:first-child {
  border-radius: 0 0 var(--r-sm) var(--r-sm);
}

.bar-segment:last-child {
  border-radius: var(--r-sm) var(--r-sm) 0 0;
}

.bar-segment.procurement { background: var(--ink); }
.bar-segment.operational { background: var(--steel); }
.bar-segment.labor { background: var(--steel-soft); }
.bar-segment.overhead { background: var(--rule-strong); }

.bar-segment:hover {
  opacity: 0.8;
}

.bar-label {
  margin-top: var(--s2);
  font-family: var(--mono);
  font-size: var(--t-xs);
  font-weight: 500;
  color: var(--steel-soft);
}

/* ---------- layout ---------- */

.two-column-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(450px, 1fr));
  gap: var(--s6);
}

/* ---------- category spending ---------- */

.category-list {
  display: flex;
  flex-direction: column;
  gap: var(--s6);
}

.category-item {
  display: flex;
  flex-direction: column;
  gap: var(--s2);
}

.category-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.category-name {
  font-weight: 600;
  color: var(--ink);
}

.category-amount {
  font-weight: 600;
  font-size: var(--t-lg);
  color: var(--ink);
}

.category-bar-container {
  width: 100%;
  height: 8px;
  background: var(--surface-alt);
  border: 1px solid var(--rule);
  border-radius: var(--r-sm);
  overflow: hidden;
}

.category-bar {
  height: 100%;
  background: var(--steel);
  transition: width 0.6s ease;
}

.category-bar.bar-accent {
  background: var(--amber);
}

.category-meta {
  display: flex;
  justify-content: space-between;
  font-size: var(--t-sm);
}

.percentage {
  color: var(--steel);
}

.change {
  font-weight: 600;
}

.change.positive {
  color: var(--mint);
}

.change.negative {
  color: var(--signal);
}

/* ---------- transactions ---------- */

.transactions-card {
  display: flex;
  flex-direction: column;
}

.transactions-table-container {
  overflow-y: auto;
  max-height: 400px;
}

.transactions-table-container thead {
  position: sticky;
  top: 0;
  background: var(--surface);
  z-index: 1;
}

.clickable-row {
  cursor: pointer;
}

.transaction-id {
  font-family: var(--mono);
  font-size: var(--t-sm);
  color: var(--steel);
}

.transaction-description {
  font-weight: 500;
  color: var(--ink);
}

.transaction-vendor {
  color: var(--steel);
}

.transaction-date {
  font-size: var(--t-sm);
  color: var(--steel);
}

.transaction-amount {
  font-weight: 600;
  color: var(--ink);
}

.text-right {
  text-align: right;
}
</style>
