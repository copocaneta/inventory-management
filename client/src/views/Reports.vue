<template>
  <div class="reports">
    <div class="page-header">
      <p>View quarterly performance metrics and monthly trends</p>
    </div>

    <div v-if="loading" class="loading">Loading reports...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else>
      <!-- Quarterly Performance -->
      <section class="card">
        <div class="section-head">
          <h3>Quarterly Performance</h3>
        </div>
        <div class="table-container">
          <table class="reports-table">
            <thead>
              <tr>
                <th>Quarter</th>
                <th class="align-right">Total Orders</th>
                <th class="align-right">Total Revenue</th>
                <th class="align-right">Avg Order Value</th>
                <th class="align-right">Fulfillment Rate</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(q, index) in quarterlyData" :key="index">
                <td class="mono-label"><strong>{{ q.quarter }}</strong></td>
                <td class="align-right"><span class="num">{{ q.total_orders }}</span></td>
                <td class="align-right"><span class="num">${{ formatNumber(q.total_revenue) }}</span></td>
                <td class="align-right"><span class="num">${{ formatNumber(q.avg_order_value) }}</span></td>
                <td class="align-right">
                  <span :class="getFulfillmentClass(q.fulfillment_rate)">
                    {{ q.fulfillment_rate }}%
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <!-- Monthly Trends Chart -->
      <section class="card">
        <div class="section-head">
          <h3>Monthly Revenue Trend</h3>
        </div>
        <div class="chart-container">
          <div class="bar-chart">
            <div v-for="(month, index) in monthlyData" :key="index" class="bar-wrapper">
              <div class="bar-container">
                <div
                  class="bar"
                  :class="{ 'bar-max': isMaxRevenue(month.revenue) }"
                  :style="{ height: getBarHeight(month.revenue) + 'px' }"
                  :title="'$' + formatNumber(month.revenue)"
                ></div>
              </div>
              <div class="bar-label">{{ formatMonthShort(month.month) }}</div>
            </div>
          </div>
        </div>
      </section>

      <!-- Month-over-Month Comparison -->
      <section class="card">
        <div class="section-head">
          <h3>Month-over-Month Analysis</h3>
        </div>
        <div class="table-container">
          <table class="reports-table">
            <thead>
              <tr>
                <th>Month</th>
                <th class="align-right">Orders</th>
                <th class="align-right">Revenue</th>
                <th class="align-right">Change</th>
                <th class="align-right">Growth Rate</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(month, index) in monthlyData" :key="index">
                <td class="mono-label"><strong>{{ formatMonth(month.month) }}</strong></td>
                <td class="align-right"><span class="num">{{ month.order_count }}</span></td>
                <td class="align-right"><span class="num">${{ formatNumber(month.revenue) }}</span></td>
                <td class="align-right">
                  <span v-if="index > 0" class="num" :class="getChangeClass(month.revenue, monthlyData[index - 1].revenue)">
                    {{ getChangeValue(month.revenue, monthlyData[index - 1].revenue) }}
                  </span>
                  <span v-else class="num">-</span>
                </td>
                <td class="align-right">
                  <span v-if="index > 0" class="num" :class="getChangeClass(month.revenue, monthlyData[index - 1].revenue)">
                    {{ getGrowthRate(month.revenue, monthlyData[index - 1].revenue) }}
                  </span>
                  <span v-else class="num">-</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <!-- Summary Stats -->
      <section class="stats-grid">
        <div class="stat-card">
          <div class="stat-label">Total Revenue (YTD)</div>
          <div class="stat-value">${{ formatNumber(totalRevenue) }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">Avg Monthly Revenue</div>
          <div class="stat-value">${{ formatNumber(avgMonthlyRevenue) }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">Total Orders (YTD)</div>
          <div class="stat-value">{{ totalOrders }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">Best Performing Quarter</div>
          <div class="stat-value">{{ bestQuarter }}</div>
        </div>
      </section>
    </div>
  </div>
</template>

<script>
import { api } from '../api'

export default {
  name: 'Reports',
  data() {
    return {
      loading: true,
      error: null,
      quarterlyData: [],
      monthlyData: [],
      totalRevenue: 0,
      avgMonthlyRevenue: 0,
      totalOrders: 0,
      bestQuarter: ''
    }
  },
  mounted() {
    console.log('Reports component mounted')
    this.loadData()
  },
  methods: {
    async loadData() {
      console.log('Loading reports data...')
      try {
        this.loading = true

        // Fetch quarterly data
        console.log('Fetching quarterly data...')
        this.quarterlyData = await api.getQuarterlyReport()
        console.log('Quarterly data:', this.quarterlyData)

        // Fetch monthly data
        console.log('Fetching monthly data...')
        this.monthlyData = await api.getMonthlyTrends()
        console.log('Monthly data:', this.monthlyData)

        // Calculate summary stats
        console.log('Calculating summary stats...')
        this.calculateSummaryStats()
        console.log('Summary stats calculated')

      } catch (err) {
        console.log('Error loading reports:', err)
        this.error = 'Failed to load reports: ' + err.message
      } finally {
        this.loading = false
        console.log('Loading complete')
      }
    },

    calculateSummaryStats() {
      // Calculate total revenue
      var total = 0
      for (var i = 0; i < this.monthlyData.length; i++) {
        total = total + this.monthlyData[i].revenue
      }
      this.totalRevenue = total

      // Calculate average monthly revenue
      if (this.monthlyData.length > 0) {
        this.avgMonthlyRevenue = total / this.monthlyData.length
      } else {
        this.avgMonthlyRevenue = 0
      }

      // Calculate total orders
      var orders = 0
      for (var i = 0; i < this.monthlyData.length; i++) {
        orders = orders + this.monthlyData[i].order_count
      }
      this.totalOrders = orders

      // Find best quarter
      var bestQ = ''
      var bestRevenue = 0
      for (var i = 0; i < this.quarterlyData.length; i++) {
        if (this.quarterlyData[i].total_revenue > bestRevenue) {
          bestRevenue = this.quarterlyData[i].total_revenue
          bestQ = this.quarterlyData[i].quarter
        }
      }
      this.bestQuarter = bestQ
    },

    formatNumber(num) {
      console.log('Formatting number:', num)
      // Format number with commas
      var str = num.toString()
      var parts = str.split('.')
      var intPart = parts[0]
      var decPart = parts.length > 1 ? parts[1] : '00'

      var formatted = ''
      var count = 0
      for (var i = intPart.length - 1; i >= 0; i--) {
        if (count > 0 && count % 3 === 0) {
          formatted = ',' + formatted
        }
        formatted = intPart[i] + formatted
        count++
      }

      if (decPart.length === 1) {
        decPart = decPart + '0'
      }
      if (decPart.length > 2) {
        decPart = decPart.substring(0, 2)
      }

      return formatted + '.' + decPart
    },

    formatMonth(monthStr) {
      console.log('Formatting month:', monthStr)
      // Convert YYYY-MM to readable format
      var parts = monthStr.split('-')
      var year = parts[0]
      var month = parts[1]

      var monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
      var monthIndex = parseInt(month) - 1

      return monthNames[monthIndex] + ' ' + year
    },

    // Presentational helper: three-letter month abbreviation for the bar chart
    // x-axis (labels stay horizontal, so the fuller "Mon YYYY" form doesn't fit).
    formatMonthShort(monthStr) {
      var parts = monthStr.split('-')
      var month = parts[1]
      var monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
      var monthIndex = parseInt(month) - 1
      return monthNames[monthIndex]
    },

    // Presentational helper: highlights the single tallest bar in the revenue chart.
    isMaxRevenue(revenue) {
      var maxRevenue = 0
      for (var i = 0; i < this.monthlyData.length; i++) {
        if (this.monthlyData[i].revenue > maxRevenue) {
          maxRevenue = this.monthlyData[i].revenue
        }
      }
      return maxRevenue > 0 && revenue === maxRevenue
    },

    getBarHeight(revenue) {
      console.log('Calculating bar height for revenue:', revenue)
      // Calculate bar height (max height 200px)
      var maxRevenue = 0
      for (var i = 0; i < this.monthlyData.length; i++) {
        if (this.monthlyData[i].revenue > maxRevenue) {
          maxRevenue = this.monthlyData[i].revenue
        }
      }

      if (maxRevenue === 0) {
        return 0
      }

      var height = (revenue / maxRevenue) * 200
      return height
    },

    getFulfillmentClass(rate) {
      if (rate >= 90) {
        return 'badge success'
      } else if (rate >= 75) {
        return 'badge warning'
      } else {
        return 'badge danger'
      }
    },

    getChangeValue(current, previous) {
      var change = current - previous
      if (change > 0) {
        return '+$' + this.formatNumber(change)
      } else if (change < 0) {
        return '-$' + this.formatNumber(Math.abs(change))
      } else {
        return '$0.00'
      }
    },

    getChangeClass(current, previous) {
      var change = current - previous
      if (change > 0) {
        return 'positive-change'
      } else if (change < 0) {
        return 'negative-change'
      } else {
        return ''
      }
    },

    getGrowthRate(current, previous) {
      if (previous === 0) {
        return 'N/A'
      }

      var rate = ((current - previous) / previous) * 100
      var sign = rate > 0 ? '+' : ''

      return sign + rate.toFixed(1) + '%'
    }
  }
}
</script>

<style scoped>
.reports {
  padding: 0;
}

.reports section + section,
.reports .stats-grid {
  margin-top: var(--s10);
}

.align-right {
  text-align: right;
}

.mono-label {
  font-family: var(--mono);
}

.reports-table {
  width: 100%;
  border-collapse: collapse;
}

.reports-table th {
  padding: var(--s3) var(--s4);
  text-align: left;
  font-weight: 600;
  color: var(--steel);
  border-bottom: 1px solid var(--rule-strong);
}

.reports-table td {
  padding: var(--s3) var(--s4);
  border-bottom: 1px solid var(--rule);
}

.reports-table tr:hover {
  background: var(--surface-alt);
}

.chart-container {
  padding: var(--s8) var(--s4);
  min-height: 300px;
}

.bar-chart {
  display: flex;
  align-items: flex-end;
  justify-content: space-around;
  height: 250px;
  gap: var(--s2);
}

.bar-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex: 1;
  max-width: 80px;
}

.bar-container {
  height: 200px;
  display: flex;
  align-items: flex-end;
  width: 100%;
}

.bar {
  width: 100%;
  background: var(--ink);
  border-radius: 2px 2px 0 0;
  transition: background 0.2s;
  cursor: pointer;
}

.bar:hover {
  background: var(--steel);
}

.bar.bar-max {
  background: var(--amber);
}

.bar.bar-max:hover {
  background: var(--steel);
}

.bar-label {
  margin-top: var(--s3);
  font-family: var(--mono);
  font-size: var(--t-xs);
  color: var(--steel-soft);
  letter-spacing: 0.04em;
  text-align: center;
  white-space: nowrap;
}

.positive-change {
  color: var(--mint);
  font-family: var(--mono);
  font-weight: 600;
}

.negative-change {
  color: var(--signal);
  font-family: var(--mono);
  font-weight: 600;
}

.loading {
  text-align: center;
  padding: 3rem;
  color: var(--steel);
}

.error {
  background: var(--signal-soft);
  color: var(--signal);
  padding: var(--s4);
  border-radius: var(--r-md);
  margin: var(--s4) 0;
}
</style>
