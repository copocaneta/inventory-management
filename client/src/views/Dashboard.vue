<template>
  <div class="dashboard">
    <div v-if="loading" class="loading">{{ t('common.loading') }}</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else class="dash-sections">

      <!-- Shortages: signature element -->
      <section class="shortages-section">
        <div class="section-head">
          <h3>Shortages</h3>
          <span class="eyebrow">{{ backlogItems.length }} open</span>
          <span class="section-note">Committed to orders you cannot fill today.</span>
        </div>
        <div class="shortages">
          <article
            class="label-card"
            v-for="item in backlogItems"
            :key="item.id"
            @click="showBacklogDetail(item)"
          >
            <div class="label-strip">
              <div class="label-sku">
                <b>{{ item.item_sku }}</b>
                <span>{{ translateProductName(item.item_name) }}</span>
              </div>
            </div>
            <div class="label-body">
              <div class="short-row">
                <div class="short-fig">
                  <span class="eyebrow">Short by</span>
                  <b>{{ item.quantity_needed - item.quantity_available }}</b>
                </div>
                <div class="short-meta">
                  <b>{{ item.order_id }}</b><br>
                  {{ item.days_delayed }} days late
                </div>
              </div>
              <div class="fill-track"><div class="fill-bar" :style="{ width: fillPct(item) + '%' }"></div></div>
              <div class="fill-legend">
                <span>{{ item.quantity_available }} on hand</span>
                <span>{{ item.quantity_needed }} needed</span>
              </div>
            </div>
            <div class="label-foot">
              <span class="badge" :class="item.priority">{{ translatePriority(item.priority) }}</span>
              <button
                class="label-act"
                @click.stop="item.purchase_order_id ? viewPO(item) : openPOModal(item)"
              >
                {{ item.purchase_order_id ? 'View purchase order' : 'Raise purchase order' }}
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9"><path d="M5 12h14M13 6l6 6-6 6"/></svg>
              </button>
            </div>
          </article>
        </div>
      </section>

      <!-- KPIs -->
      <section class="kpi-section">
        <div class="section-head">
          <h3>{{ t('dashboard.kpi.title') }}</h3>
        </div>
        <div class="kpi-grid">
          <div class="kpi-card">
            <div class="kpi-label">{{ t('dashboard.kpi.inventoryTurnover') }}</div>
            <div class="kpi-value">4.2</div>
            <div class="kpi-goal">{{ t('dashboard.kpi.goal') }}: 4.5 (-6.67%)</div>
            <div class="kpi-progress-bar">
              <div class="kpi-progress danger" style="width: 93.33%"></div>
            </div>
          </div>

          <div class="kpi-card">
            <div class="kpi-label">{{ t('dashboard.kpi.ordersFulfilled') }}</div>
            <div class="kpi-value">{{ ordersData.fulfilled }}</div>
            <div class="kpi-goal">{{ t('dashboard.kpi.goal') }}: {{ ordersData.goal }} ({{ calculatePercentage(ordersData.fulfilled, ordersData.goal) }}%)</div>
            <div class="kpi-progress-bar">
              <div
                class="kpi-progress"
                :class="{ success: ordersData.fulfilled >= ordersData.goal, danger: ordersData.fulfilled < ordersData.goal }"
                :style="{ width: calculatePercentage(ordersData.fulfilled, ordersData.goal) + '%' }"
              ></div>
            </div>
          </div>

          <div class="kpi-card">
            <div class="kpi-label">{{ t('dashboard.kpi.orderFillRate') }}</div>
            <div class="kpi-value">{{ fillRate }}%</div>
            <div class="kpi-goal">{{ t('dashboard.kpi.goal') }}: 95% ({{ fillRate - 95 > 0 ? '+' : '' }}{{ (fillRate - 95).toFixed(2) }}%)</div>
            <div class="kpi-progress-bar">
              <div
                class="kpi-progress"
                :class="{ success: fillRate >= 95, danger: fillRate < 95 }"
                :style="{ width: (fillRate / 95 * 100) + '%' }"
              ></div>
            </div>
          </div>

          <div class="kpi-card">
            <div class="kpi-label">{{ t(selectedPeriod === 'all' ? 'dashboard.kpi.revenueYTD' : 'dashboard.kpi.revenueMTD') }}</div>
            <div class="kpi-value">{{ formatCurrency(Math.round(summary.total_orders_value), selectedCurrency) }}</div>
            <div class="kpi-goal">{{ t('dashboard.kpi.goal') }}: {{ formatCurrency(revenueGoal, selectedCurrency) }} ({{ summary.total_orders_value > revenueGoal ? '+' : '' }}{{ ((summary.total_orders_value / revenueGoal - 1) * 100).toFixed(1) }}%)</div>
            <div class="kpi-progress-bar">
              <div
                class="kpi-progress"
                :class="{ success: summary.total_orders_value >= revenueGoal, danger: summary.total_orders_value < revenueGoal }"
                :style="{ width: Math.min((summary.total_orders_value / revenueGoal * 100), 100) + '%' }"
              ></div>
            </div>
          </div>

          <div class="kpi-card">
            <div class="kpi-label">{{ t('dashboard.kpi.avgProcessingTime') }}</div>
            <div class="kpi-value">2.8</div>
            <div class="kpi-goal">{{ t('dashboard.kpi.goal') }}: 3.0 (-6.67%)</div>
            <div class="kpi-progress-bar">
              <div class="kpi-progress success" style="width: 93.33%"></div>
            </div>
          </div>
        </div>
      </section>

      <!-- Charts -->
      <section class="performance-section">
        <div class="section-head">
          <h3>{{ t('dashboard.summary.title') }}</h3>
        </div>
        <div class="charts-grid">
          <!-- Order Health Dashboard -->
          <div class="card chart-card">
            <div class="card-header">
              <h3 class="card-title">{{ t('dashboard.orderHealth.title') }}</h3>
            </div>
            <div class="chart-content">
              <div class="order-health-container">
                <div class="order-health-chart">
                  <svg viewBox="0 0 200 200" class="donut-svg-compact">
                    <circle cx="100" cy="100" r="65" fill="none" class="ring-track" stroke-width="25"/>
                    <circle cx="100" cy="100" r="65" fill="none" class="ring-mint" stroke-width="25"
                      :stroke-dasharray="`${getCircleSegment(statusData.delivered)} 408`"
                      stroke-dashoffset="0" transform="rotate(-90 100 100)"/>
                    <circle cx="100" cy="100" r="65" fill="none" class="ring-steel" stroke-width="25"
                      :stroke-dasharray="`${getCircleSegment(statusData.shipped)} 408`"
                      :stroke-dashoffset="`-${getCircleSegment(statusData.delivered)}`"
                      transform="rotate(-90 100 100)"/>
                    <circle cx="100" cy="100" r="65" fill="none" class="ring-amber" stroke-width="25"
                      :stroke-dasharray="`${getCircleSegment(statusData.processing)} 408`"
                      :stroke-dashoffset="`-${getCircleSegment(statusData.delivered) + getCircleSegment(statusData.shipped)}`"
                      transform="rotate(-90 100 100)"/>
                    <circle cx="100" cy="100" r="65" fill="none" class="ring-signal" stroke-width="25"
                      :stroke-dasharray="`${getCircleSegment(statusData.backordered)} 408`"
                      :stroke-dashoffset="`-${getCircleSegment(statusData.delivered) + getCircleSegment(statusData.shipped) + getCircleSegment(statusData.processing)}`"
                      transform="rotate(-90 100 100)"/>
                    <text x="100" y="90" text-anchor="middle" class="donut-center-label">{{ t('dashboard.orderHealth.total') }}</text>
                    <text x="100" y="120" text-anchor="middle" class="donut-center-value">{{ orderHealthMetrics.totalOrders }}</text>
                  </svg>
                  <div class="donut-legend-compact">
                    <div class="legend-item-compact"><span class="legend-dot dot-mint"></span>{{ t('status.delivered') }}</div>
                    <div class="legend-item-compact"><span class="legend-dot dot-steel"></span>{{ t('status.shipped') }}</div>
                    <div class="legend-item-compact"><span class="legend-dot dot-amber"></span>{{ t('status.processing') }}</div>
                    <div class="legend-item-compact"><span class="legend-dot dot-signal"></span>{{ t('status.backordered') }}</div>
                  </div>
                </div>

                <div class="order-health-metrics">
                  <div class="health-metric">
                    <div class="health-metric-label">{{ t('dashboard.orderHealth.revenue') }}</div>
                    <div class="health-metric-value">{{ formatCurrency(orderHealthMetrics.totalValue, selectedCurrency) }}</div>
                  </div>
                  <div class="health-metric">
                    <div class="health-metric-label">{{ t('dashboard.orderHealth.avgOrderValue') }}</div>
                    <div class="health-metric-value">{{ formatCurrency(orderHealthMetrics.avgOrderValue, selectedCurrency) }}</div>
                  </div>
                  <div class="health-metric">
                    <div class="health-metric-label">{{ t('dashboard.orderHealth.onTimeRate') }}</div>
                    <div class="health-metric-value" :class="{ 'metric-good': orderHealthMetrics.onTimeRate >= 90, 'metric-warning': orderHealthMetrics.onTimeRate < 90 && orderHealthMetrics.onTimeRate >= 75, 'metric-bad': orderHealthMetrics.onTimeRate < 75 }">
                      {{ orderHealthMetrics.onTimeRate.toFixed(1) }}%
                    </div>
                  </div>
                  <div class="health-metric">
                    <div class="health-metric-label">{{ t('dashboard.orderHealth.avgFulfillmentDays') }}</div>
                    <div class="health-metric-value">{{ orderHealthMetrics.avgFulfillmentDays.toFixed(1) }}</div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Inventory by Category -->
          <div class="card chart-card">
            <div class="card-header">
              <h3 class="card-title">{{ t('dashboard.inventoryValue.title') }}</h3>
            </div>
            <div class="chart-content">
              <div class="horizontal-bar-chart" v-if="categoryData.length > 0">
                <div v-for="cat in categoryData" :key="cat.name" class="h-bar-item">
                  <div class="h-bar-label">{{ translateCategory(cat.name) }}</div>
                  <div class="h-bar-container">
                    <div
                      class="h-bar"
                      :class="{ 'is-peak': cat.value === maxCategoryValue }"
                      :style="{ width: (cat.value / maxCategoryValue * 100) + '%' }"
                    >
                      <span class="h-bar-value">{{ selectedCurrency === 'JPY' ? formatCurrency(cat.value, selectedCurrency) : `$${(cat.value / 1000).toFixed(1)}K` }}</span>
                    </div>
                  </div>
                </div>
              </div>
              <div v-else class="no-data">{{ t('dashboard.inventoryShortages.noData') }}</div>
            </div>
          </div>
        </div>
      </section>

      <!-- Top Products -->
      <section class="top-products-section">
        <div class="section-head">
          <h3>{{ t('dashboard.topProducts.title') }}</h3>
        </div>
        <div class="card">
          <div class="table-container">
            <table>
              <thead>
                <tr>
                  <th>{{ t('dashboard.topProducts.product') }}</th>
                  <th>{{ t('dashboard.topProducts.category') }}</th>
                  <th>{{ t('dashboard.topProducts.unitsOrdered') }}</th>
                  <th>{{ t('dashboard.topProducts.revenue') }}</th>
                  <th>{{ t('dashboard.topProducts.firstOrder') }}</th>
                  <th>{{ t('dashboard.topProducts.stockStatus') }}</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="item in topProducts"
                  :key="item.sku"
                  class="clickable-row"
                  @click="showProductDetail(item)"
                >
                  <td>
                    <span class="cell-sku"><b>{{ item.sku }}</b></span>
                    <span class="cell-name">{{ translateProductName(item.name) }}</span>
                  </td>
                  <td>{{ translateCategory(item.category) }}</td>
                  <td class="num">{{ item.unitsOrdered }}</td>
                  <td class="num"><strong>{{ formatCurrency(item.revenue, selectedCurrency) }}</strong></td>
                  <td>{{ formatDate(item.firstOrderDate) }}</td>
                  <td>
                    <span :class="['badge', getStockBadge(item.stockLevel)]">
                      {{ translateStockLevel(item.stockLevel) }}
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </section>

    </div>

    <ProductDetailModal
      :is-open="showProductModal"
      :product="selectedProduct"
      @close="showProductModal = false"
    />

    <BacklogDetailModal
      :is-open="showBacklogModal"
      :backlog-item="selectedBacklogItem"
      @close="showBacklogModal = false"
    />

    <PurchaseOrderModal
      :is-open="showPOModal"
      :backlog-item="selectedBacklogForPO"
      :mode="poModalMode"
      @close="showPOModal = false"
      @po-created="handlePOCreated"
    />
  </div>
</template>

<script>
import { ref, onMounted, computed, watch } from 'vue'
import { api } from '../api'
import { useFilters } from '../composables/useFilters'
import { useI18n } from '../composables/useI18n'
import { formatCurrency } from '../utils/currency'
import ProductDetailModal from '../components/ProductDetailModal.vue'
import BacklogDetailModal from '../components/BacklogDetailModal.vue'

export default {
  name: 'Dashboard',
  components: {
    ProductDetailModal,
    BacklogDetailModal,
  },
  setup() {
    const { t, currentCurrency, translateProductName, translateWarehouse } = useI18n()
    const loading = ref(true)
    const error = ref(null)
    const summary = ref({})
    const allOrders = ref([])
    const inventoryItems = ref([])

    // Modal state
    const showProductModal = ref(false)
    const selectedProduct = ref(null)
    const showBacklogModal = ref(false)
    const selectedBacklogItem = ref(null)
    const showPOModal = ref(false)
    const selectedBacklogForPO = ref(null)
    const poModalMode = ref('create')

    // Use shared filters
    const {
      selectedPeriod,
      selectedLocation,
      selectedCategory,
      selectedStatus,
      getCurrentFilters
    } = useFilters()

    const ordersData = ref({ fulfilled: 187, goal: 200 })
    const fillRate = ref(96.8)

    const revenueGoal = computed(() => {
      // $800K per month, so if looking at all months (12 months), goal is 12 * 800K = 9.6M
      const monthlyGoal = 800000
      if (selectedPeriod.value === 'all') {
        return monthlyGoal * 12 // $9,600,000 for the full year
      }
      return monthlyGoal // $800,000 for a single month
    })

    const revenueGoalDisplay = computed(() => {
      if (revenueGoal.value >= 1000000) {
        return `$${(revenueGoal.value / 1000000).toFixed(1)}M`
      }
      return `$${(revenueGoal.value / 1000).toFixed(0)}K`
    })

    const statusData = computed(() => {
      const counts = { delivered: 0, shipped: 0, processing: 0, backordered: 0 }
      allOrders.value.forEach(order => {
        const status = order.status.toLowerCase()
        if (counts[status] !== undefined) counts[status]++
      })
      return counts
    })

    const orderHealthMetrics = computed(() => {
      const totalOrders = allOrders.value.length
      const totalValue = allOrders.value.reduce((sum, order) => sum + (order.total_value || 0), 0)
      const avgOrderValue = totalOrders > 0 ? totalValue / totalOrders : 0

      // Calculate on-time delivery rate (delivered orders that arrived on or before expected date)
      const deliveredOrders = allOrders.value.filter(o => o.status.toLowerCase() === 'delivered')
      const onTimeDeliveries = deliveredOrders.filter(o => {
        if (o.actual_delivery && o.expected_delivery) {
          return new Date(o.actual_delivery) <= new Date(o.expected_delivery)
        }
        return false
      }).length
      const onTimeRate = deliveredOrders.length > 0 ? (onTimeDeliveries / deliveredOrders.length) * 100 : 0

      // Calculate average fulfillment speed (days from order to delivery for delivered orders)
      let totalDays = 0
      let countWithDates = 0
      deliveredOrders.forEach(o => {
        if (o.order_date && o.actual_delivery) {
          const orderDate = new Date(o.order_date)
          const deliveryDate = new Date(o.actual_delivery)
          const days = Math.round((deliveryDate - orderDate) / (1000 * 60 * 60 * 24))
          totalDays += days
          countWithDates++
        }
      })
      const avgFulfillmentDays = countWithDates > 0 ? totalDays / countWithDates : 0

      return {
        totalOrders,
        totalValue,
        avgOrderValue,
        onTimeRate,
        avgFulfillmentDays
      }
    })

    const categoryData = computed(() => {
      // Group inventory by category and calculate values
      // Filter inventory items to only include those with orders in the selected period
      const categoryMap = {}

      // Use a single neutral slate/gray color for all categories
      const singleColor = '#64748b' // Neutral slate gray color

      // Get SKUs from orders in the filtered time period
      const orderedSkus = new Set()
      allOrders.value.forEach(order => {
        if (order.items) {
          order.items.forEach(item => {
            orderedSkus.add(item.sku)
          })
        }
      })

      // Only include inventory items that have orders in the selected period
      // If no period is selected (all), include all inventory items
      const itemsToInclude = selectedPeriod.value === 'all'
        ? inventoryItems.value
        : inventoryItems.value.filter(item => orderedSkus.has(item.sku))

      itemsToInclude.forEach(item => {
        const cat = item.category.toLowerCase()
        if (!categoryMap[cat]) {
          categoryMap[cat] = {
            name: item.category,
            value: 0,
            color: singleColor,
            category: cat,
            count: 0
          }
        }
        categoryMap[cat].value += item.quantity_on_hand * item.unit_cost
        categoryMap[cat].count += 1
      })

      return Object.values(categoryMap)
    })

    const maxCategoryValue = computed(() => {
      if (categoryData.value.length === 0) return 1
      return Math.max(...categoryData.value.map(c => c.value))
    })

    const orderTrendData = computed(() => {
      // Group orders by month from the actual data
      const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

      // Initialize all months with 0 orders
      const monthMap = {}
      monthNames.forEach(month => {
        monthMap[month] = { month, orders: 0 }
      })

      // Count orders for each month
      if (Array.isArray(allOrders.value)) {
        allOrders.value.forEach(order => {
          if (order && order.order_date) {
            const date = new Date(order.order_date)
            const monthIndex = date.getMonth()
            // Check if monthIndex is valid (0-11)
            if (!isNaN(monthIndex) && monthIndex >= 0 && monthIndex <= 11) {
              const monthName = monthNames[monthIndex]
              monthMap[monthName].orders++
            }
          }
        })
      }

      // Return all months in order
      return monthNames.map(month => monthMap[month])
    })

    const maxOrderCount = computed(() => {
      if (orderTrendData.value.length === 0) return 10
      const max = Math.max(...orderTrendData.value.map(d => d.orders))
      // Round up to nearest 10 for cleaner axis, minimum 10
      return Math.max(10, Math.ceil(max / 10) * 10)
    })

    const topProducts = computed(() => {
      // Calculate top products from filtered order data
      const productMap = {}

      // allOrders is already filtered by API based on: month, warehouse, category, status
      allOrders.value.forEach(order => {
        if (order.items) {
          order.items.forEach(item => {
            const sku = item.sku

            // Find matching inventory item to get full product details
            // Note: inventoryItems is also filtered by API based on: warehouse, category
            const invItem = inventoryItems.value.find(i => i.sku === sku)

            // Skip products that don't match current inventory filters
            // (e.g., if filtering by warehouse A, don't show products from warehouse B)
            if (!invItem && (selectedLocation.value !== 'all' || selectedCategory.value !== 'all')) {
              return // Skip this product as it doesn't match inventory filters
            }

            if (!productMap[sku]) {
              productMap[sku] = {
                name: item.name,
                sku: sku,
                category: invItem?.category || 'Unknown',
                warehouse: invItem?.warehouse || 'Unknown',
                unitsOrdered: 0,
                revenue: 0,
                stockLevel: invItem ? (invItem.quantity_on_hand > invItem.reorder_point ? 'In Stock' : 'Low Stock') : 'Unknown',
                firstOrderDate: order.order_date
              }
            } else {
              // Update to EARLIEST order date (to show January at top when selecting All Months)
              if (order.order_date && (!productMap[sku].firstOrderDate || order.order_date < productMap[sku].firstOrderDate)) {
                productMap[sku].firstOrderDate = order.order_date
              }
            }
            productMap[sku].unitsOrdered += item.quantity
            productMap[sku].revenue += item.quantity * item.unit_price
          })
        }
      })

      // Convert to array, sort by first order date (earliest first = January at top), then by revenue, and take top 12
      return Object.values(productMap)
        .sort((a, b) => {
          // Sort by first order date (earliest first)
          // This ensures products first ordered in January appear before those first ordered in December
          const dateA = new Date(a.firstOrderDate || '9999-12-31')
          const dateB = new Date(b.firstOrderDate || '9999-12-31')
          if (dateA.getTime() !== dateB.getTime()) {
            return dateA.getTime() - dateB.getTime() // Earlier dates come first
          }
          // If dates are equal, sort by revenue (highest first)
          return b.revenue - a.revenue
        })
        .slice(0, 12)
    })

    const allBacklogItems = ref([])

    // Filter backlog based on inventory filters
    const backlogItems = computed(() => {
      if (selectedLocation.value === 'all' && selectedCategory.value === 'all') {
        return allBacklogItems.value
      }

      // Get SKUs of items that match the filters
      const validSkus = new Set(inventoryItems.value.map(item => item.sku))
      return allBacklogItems.value.filter(b => validSkus.has(b.item_sku))
    })

    const loadData = async () => {
      try {
        loading.value = true
        const filters = getCurrentFilters()

        const [summaryData, ordersData, inventoryData, backlogData] = await Promise.all([
          api.getDashboardSummary(filters),
          api.getOrders(filters),
          api.getInventory(filters),
          api.getBacklog()
        ])

        summary.value = summaryData
        allOrders.value = ordersData
        inventoryItems.value = inventoryData
        allBacklogItems.value = backlogData
      } catch (err) {
        error.value = 'Failed to load dashboard data: ' + err.message
      } finally {
        loading.value = false
      }
    }

    const calculatePercentage = (value, goal) => {
      return ((value / goal) * 100).toFixed(2)
    }

    // Compute total orders once for efficiency
    const totalOrders = computed(() => {
      return statusData.value.delivered + statusData.value.shipped +
             statusData.value.processing + statusData.value.backordered
    })

    const getCircleSegment = (value) => {
      return totalOrders.value > 0 ? (value / totalOrders.value) * 440 : 0
    }

    const getStockBadge = (level) => {
      if (level === 'In Stock') return 'success'
      if (level === 'Low Stock') return 'warning'
      return 'danger'
    }

    const translateCategory = (category) => {
      const categoryMap = {
        'Circuit Boards': t('categories.circuitBoards'),
        'Sensors': t('categories.sensors'),
        'Actuators': t('categories.actuators'),
        'Controllers': t('categories.controllers'),
        'Power Supplies': t('categories.powerSupplies')
      }
      return categoryMap[category] || category
    }

    const translateStockLevel = (stockLevel) => {
      const stockMap = {
        'In Stock': t('status.inStock'),
        'Low Stock': t('status.lowStock')
      }
      return stockMap[stockLevel] || stockLevel
    }

    const translatePriority = (priority) => {
      const priorityMap = {
        'high': t('priority.high'),
        'medium': t('priority.medium'),
        'low': t('priority.low'),
        'High': t('priority.high'),
        'Medium': t('priority.medium'),
        'Low': t('priority.low')
      }
      return priorityMap[priority] || priority
    }

    const formatDate = (dateString) => {
      if (!dateString) return '-'
      const { currentLocale } = useI18n()
      const locale = currentLocale.value === 'ja' ? 'ja-JP' : 'en-US'
      const date = new Date(dateString)
      return date.toLocaleDateString(locale, { month: 'short', day: 'numeric', year: 'numeric' })
    }

    const showProductDetail = (product) => {
      selectedProduct.value = product
      showProductModal.value = true
    }

    const showBacklogDetail = (item) => {
      selectedBacklogItem.value = item
      showBacklogModal.value = true
    }

    const openPOModal = (item) => {
      selectedBacklogForPO.value = item
      poModalMode.value = 'create'
      showPOModal.value = true
    }

    const viewPO = (item) => {
      selectedBacklogForPO.value = item
      poModalMode.value = 'view'
      showPOModal.value = true
    }

    const handlePOCreated = (poData) => {
      // Update the backlog item with the new PO ID
      const item = allBacklogItems.value.find(b => b.id === poData.backlog_item_id)
      if (item) {
        item.purchase_order_id = poData.id
        item.purchase_order = poData
      }
      showPOModal.value = false
    }

    // Fill percentage for a backlog item's on-hand vs needed quantity (visual only)
    const fillPct = (item) => {
      if (!item.quantity_needed) return 0
      return Math.min(100, (item.quantity_available / item.quantity_needed) * 100)
    }

    // Watch for filter changes and reload data
    watch([selectedPeriod, selectedLocation, selectedCategory, selectedStatus], () => {
      loadData()
    })

    onMounted(loadData)

    return {
      t,
      loading,
      error,
      summary,
      ordersData,
      fillRate,
      statusData,
      orderHealthMetrics,
      categoryData,
      maxCategoryValue,
      orderTrendData,
      maxOrderCount,
      topProducts,
      backlogItems,
      calculatePercentage,
      getCircleSegment,
      getStockBadge,
      translateCategory,
      translateStockLevel,
      translatePriority,
      formatDate,
      revenueGoal,
      revenueGoalDisplay,
      showProductModal,
      selectedProduct,
      showProductDetail,
      showBacklogModal,
      selectedBacklogItem,
      showBacklogDetail,
      selectedPeriod,
      selectedCurrency: currentCurrency,
      formatCurrency,
      Math,
      translateProductName,
      translateWarehouse,
      showPOModal,
      selectedBacklogForPO,
      poModalMode,
      openPOModal,
      viewPO,
      handlePOCreated,
      fillPct
    }
  }
}
</script>

<style scoped>
.dash-sections {
  display: flex;
  flex-direction: column;
  gap: var(--s10);
}

/* ---------- shortages: label stock ---------- */

.shortages {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(272px, 1fr));
  gap: var(--s4);
}

.label-card {
  background: var(--surface);
  border: 1px solid var(--rule-strong);
  border-radius: var(--r-sm);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  cursor: pointer;
  transition: border-color 0.14s ease, transform 0.14s ease;
}

.label-card:hover {
  border-color: var(--ink);
  transform: translateY(-1px);
}

.label-strip {
  border-bottom: 1px dashed var(--rule-strong);
  background: linear-gradient(180deg, #fff, var(--surface-alt));
}

.label-sku {
  padding: 11px var(--s4) 9px;
}

.label-sku b {
  display: block;
  font-family: var(--mono);
  font-size: 15px;
  font-weight: 600;
  letter-spacing: 0.02em;
}

.label-sku span {
  display: block;
  margin-top: 2px;
  font-size: var(--t-sm);
  letter-spacing: 0.04em;
  text-transform: uppercase;
  color: var(--steel);
}

.label-body {
  padding: var(--s4);
  display: flex;
  flex-direction: column;
  gap: var(--s3);
}

.short-row {
  display: flex;
  align-items: flex-end;
  gap: var(--s4);
}

.short-fig b {
  font-family: var(--mono);
  font-size: 30px;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
  color: var(--signal);
  line-height: 1;
}

.short-fig .eyebrow {
  display: block;
  margin-bottom: 5px;
}

.short-meta {
  margin-left: auto;
  text-align: right;
  font-family: var(--mono);
  font-size: var(--t-sm);
  color: var(--steel);
  line-height: 1.6;
}

.short-meta b {
  color: var(--ink);
  font-weight: 600;
}

.fill-track {
  height: 5px;
  background: #efede8;
  border-radius: 99px;
  overflow: hidden;
}

.fill-bar {
  height: 100%;
  background: var(--signal);
  border-radius: 99px;
}

.fill-legend {
  display: flex;
  justify-content: space-between;
  font-family: var(--mono);
  font-size: 11px;
  color: var(--steel);
}

.label-foot {
  margin-top: auto;
  padding: 10px var(--s4);
  border-top: 1px solid var(--rule);
  display: flex;
  align-items: center;
  gap: var(--s3);
}

.label-act {
  margin-left: auto;
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: var(--t-md);
  font-weight: 500;
  color: var(--ink);
  background: none;
  border: none;
  padding: 0;
  cursor: pointer;
}

.label-act svg {
  width: 13px;
  height: 13px;
}

.label-act:hover {
  color: var(--signal);
}

/* ---------- KPI strip ---------- */

.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  background: var(--surface);
  border: 1px solid var(--rule);
  border-radius: var(--r-sm);
}

.kpi-card {
  padding: var(--s5);
  border-right: 1px solid var(--rule);
}

.kpi-card:last-child {
  border-right: none;
}

.kpi-label {
  display: block;
  font-family: var(--mono);
  font-size: var(--t-xs);
  font-weight: 500;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--steel-soft);
  margin-bottom: var(--s3);
}

.kpi-value {
  font-family: var(--mono);
  font-variant-numeric: tabular-nums;
  font-size: 26px;
  font-weight: 600;
  line-height: 1;
  letter-spacing: -0.01em;
  color: var(--ink);
  margin-bottom: var(--s2);
}

.kpi-goal {
  font-size: var(--t-sm);
  color: var(--steel);
  margin-bottom: var(--s3);
}

.kpi-progress-bar {
  width: 100%;
  height: 4px;
  background: #efede8;
  border-radius: 99px;
  overflow: hidden;
}

.kpi-progress {
  height: 100%;
  background: var(--ink);
  border-radius: 99px;
  transition: width 0.6s ease;
}

.kpi-progress.success {
  background: var(--mint);
}

.kpi-progress.danger {
  background: var(--signal);
}

/* ---------- charts ---------- */

.charts-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--s5);
}

.chart-content {
  padding: var(--s4) 0 0;
}

.order-health-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--s6);
  align-items: center;
  min-height: 220px;
}

.order-health-chart {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: var(--s4);
}

.donut-svg-compact {
  width: 190px;
  height: 190px;
}

.ring-track {
  stroke: var(--rule);
}

.ring-mint {
  stroke: var(--mint);
}

.ring-steel {
  stroke: var(--steel);
}

.ring-amber {
  stroke: var(--amber);
}

.ring-signal {
  stroke: var(--signal);
}

.donut-center-label {
  font-family: var(--mono);
  font-size: 10px;
  fill: var(--steel-soft);
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.1em;
}

.donut-center-value {
  font-family: var(--mono);
  font-size: 32px;
  fill: var(--ink);
  font-weight: 600;
}

.donut-legend-compact {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--s2) var(--s5);
}

.legend-item-compact {
  display: flex;
  align-items: center;
  gap: var(--s2);
  font-size: var(--t-md);
  color: var(--steel);
  font-weight: 500;
}

.legend-dot {
  width: 9px;
  height: 9px;
  border-radius: 2px;
}

.dot-mint { background: var(--mint); }
.dot-steel { background: var(--steel); }
.dot-amber { background: var(--amber); }
.dot-signal { background: var(--signal); }

.order-health-metrics {
  display: flex;
  flex-direction: column;
  gap: var(--s5);
  justify-content: center;
  align-items: center;
}

.health-metric {
  display: flex;
  flex-direction: column;
  gap: 3px;
  text-align: center;
  width: 100%;
}

.health-metric-label {
  font-family: var(--mono);
  font-size: var(--t-xs);
  color: var(--steel-soft);
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.1em;
}

.health-metric-value {
  font-family: var(--mono);
  font-variant-numeric: tabular-nums;
  font-size: 22px;
  font-weight: 600;
  color: var(--ink);
  letter-spacing: -0.01em;
}

.metric-good {
  color: var(--mint);
}

.metric-warning {
  color: var(--amber-ink);
}

.metric-bad {
  color: var(--signal);
}

.horizontal-bar-chart {
  display: flex;
  flex-direction: column;
  gap: var(--s5);
}

.h-bar-item {
  display: flex;
  align-items: center;
  gap: var(--s4);
}

.h-bar-label {
  width: 120px;
  min-width: 120px;
  font-size: var(--t-md);
  font-weight: 600;
  color: var(--steel);
  flex-shrink: 0;
}

.h-bar-container {
  flex: 1;
  height: 30px;
  background: var(--surface-alt);
  border-radius: var(--r-sm);
  overflow: hidden;
}

.h-bar {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding-right: var(--s3);
  transition: width 0.6s ease;
  background: var(--ink);
}

.h-bar.is-peak {
  background: var(--amber);
}

.h-bar-value {
  font-family: var(--mono);
  font-size: var(--t-sm);
  font-weight: 700;
  color: #fff;
}

.no-data {
  padding: var(--s8);
  text-align: center;
  color: var(--steel-soft);
  font-size: var(--t-md);
}

.clickable-row {
  cursor: pointer;
}
</style>
