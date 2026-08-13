<template>
  <div class="orders">
    <div class="page-header">
      <p>{{ t('orders.description') }}</p>
    </div>

    <div v-if="loading" class="loading">{{ t('common.loading') }}</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else>
      <section class="stats-grid">
        <div class="stat-card success">
          <div class="stat-label">{{ t('status.delivered') }}</div>
          <div class="stat-value">{{ getOrdersByStatus('Delivered').length }}</div>
        </div>
        <div class="stat-card info">
          <div class="stat-label">{{ t('status.shipped') }}</div>
          <div class="stat-value">{{ getOrdersByStatus('Shipped').length }}</div>
        </div>
        <div class="stat-card warning">
          <div class="stat-label">{{ t('status.processing') }}</div>
          <div class="stat-value">{{ getOrdersByStatus('Processing').length }}</div>
        </div>
        <div class="stat-card danger">
          <div class="stat-label">{{ t('status.backordered') }}</div>
          <div class="stat-value">{{ getOrdersByStatus('Backordered').length }}</div>
        </div>
      </section>

      <!--
        Restock orders (procurement, inbound, no customer) are deliberately kept in
        their own ref/table separate from sales `orders` (outbound revenue to a
        customer). Merging them would corrupt getOrdersByStatus()/stat cards above,
        which must only ever count sales orders, and would incorrectly apply the
        warehouse/category/status/period filters (restock orders have none of those
        dimensions).
      -->
      <section class="card">
        <div class="section-head">
          <h3>{{ t('orders.submittedOrders') }}</h3>
          <span class="section-note">{{ restockOrders.length }}</span>
        </div>
        <div v-if="restockError" class="error">{{ restockError }}</div>
        <div v-else-if="restockOrders.length === 0" class="submitted-orders-empty">
          {{ t('orders.submittedOrdersEmpty') }}
        </div>
        <div v-else class="table-container">
          <table class="orders-table">
            <thead>
              <tr>
                <th class="col-order-number">{{ t('orders.submittedTable.restockNumber') }}</th>
                <th class="col-items">{{ t('orders.submittedTable.items') }}</th>
                <th class="col-value">{{ t('orders.submittedTable.totalCost') }}</th>
                <th class="col-date">{{ t('orders.submittedTable.submitted') }}</th>
                <th class="col-date">{{ t('orders.submittedTable.leadTime') }}</th>
                <th class="col-date">{{ t('orders.submittedTable.expectedDelivery') }}</th>
                <th class="col-status">{{ t('orders.submittedTable.status') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="order in restockOrders" :key="order.id || order.restock_number">
                <td class="col-order-number num">{{ order.restock_number }}</td>
                <td class="col-items">
                  <details class="items-details">
                    <summary class="items-summary">
                      {{ t('orders.itemsCount', { count: order.items.length }) }}
                    </summary>
                    <div class="items-dropdown">
                      <div v-for="item in order.items" :key="item.item_sku" class="item-entry">
                        <span class="item-name">{{ translateProductName(item.item_name) }}</span>
                        <!-- Unit cost needs cents here even though totals elsewhere on this
                             page round to whole dollars: rounding a per-unit price hides real
                             cents and makes qty * unit price look inconsistent with total_cost. -->
                        <span class="item-meta">{{ t('orders.quantity') }}: {{ item.quantity }} @ {{ formatCurrencyWithDecimals(item.unit_cost, currentCurrency, 2) }}</span>
                        <span class="item-meta">{{ t('orders.submittedTable.leadTime') }}: {{ t('orders.leadTimeDays', { count: item.lead_time_days }) }}</span>
                      </div>
                    </div>
                  </details>
                </td>
                <td class="col-value num">{{ formatCurrency(order.total_cost, currentCurrency) }}</td>
                <td class="col-date num">{{ formatDate(order.submitted_date) }}</td>
                <!-- order.lead_time_days is the MAX across item lead times, not an
                     average: the order isn't complete until the slowest item lands -->
                <td class="col-date">{{ t('orders.leadTimeDays', { count: order.lead_time_days }) }}</td>
                <td class="col-date num">{{ formatDate(order.expected_delivery) }}</td>
                <td class="col-status">
                  <span class="badge info">{{ t('status.submitted') }}</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <section class="card">
        <div class="section-head">
          <h3>{{ t('orders.allOrders') }}</h3>
          <span class="section-note">{{ orders.length }}</span>
        </div>
        <div class="table-container">
          <table class="orders-table">
            <thead>
              <tr>
                <th class="col-order-number">{{ t('orders.table.orderNumber') }}</th>
                <th class="col-customer">{{ t('orders.table.customer') }}</th>
                <th class="col-items">{{ t('orders.table.items') }}</th>
                <th class="col-status">{{ t('orders.table.status') }}</th>
                <th class="col-date">{{ t('orders.table.orderDate') }}</th>
                <th class="col-date">{{ t('orders.table.expectedDelivery') }}</th>
                <th class="col-value">{{ t('orders.table.totalValue') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="order in orders" :key="order.id">
                <td class="col-order-number num">{{ order.order_number }}</td>
                <td class="col-customer">{{ translateCustomerName(order.customer) }}</td>
                <td class="col-items">
                  <details class="items-details">
                    <summary class="items-summary">
                      {{ t('orders.itemsCount', { count: order.items.length }) }}
                    </summary>
                    <div class="items-dropdown">
                      <div v-for="(item, idx) in order.items" :key="idx" class="item-entry">
                        <span class="item-name">{{ translateProductName(item.name) }}</span>
                        <span class="item-meta">{{ t('orders.quantity') }}: {{ item.quantity }} @ {{ currencySymbol }}{{ item.unit_price }}</span>
                      </div>
                    </div>
                  </details>
                </td>
                <td class="col-status">
                  <span :class="['badge', getOrderStatusClass(order.status)]">
                    {{ t(`status.${order.status.toLowerCase()}`) }}
                  </span>
                </td>
                <td class="col-date num">{{ formatDate(order.order_date) }}</td>
                <td class="col-date num">{{ formatDate(order.expected_delivery) }}</td>
                <td class="col-value num">{{ currencySymbol }}{{ order.total_value.toLocaleString() }}</td>
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
import { formatCurrency, formatCurrencyWithDecimals } from '../utils/currency'

export default {
  name: 'Orders',
  setup() {
    const { t, currentCurrency, translateProductName, translateCustomerName } = useI18n()

    const currencySymbol = computed(() => {
      return currentCurrency.value === 'JPY' ? '¥' : '$'
    })
    const loading = ref(true)
    const error = ref(null)
    const orders = ref([])

    // Restock orders (procurement) are kept separate from sales `orders` (revenue).
    // See template comment above the Submitted Orders card for why.
    const restockOrders = ref([])
    const restockError = ref(null)

    // Use shared filters
    const {
      selectedPeriod,
      selectedLocation,
      selectedCategory,
      selectedStatus,
      getCurrentFilters
    } = useFilters()

    const loadOrders = async () => {
      try {
        loading.value = true
        const filters = getCurrentFilters()
        const fetchedOrders = await api.getOrders(filters)

        // Sort orders by order_date (earliest first)
        orders.value = fetchedOrders.sort((a, b) => {
          const dateA = new Date(a.order_date)
          const dateB = new Date(b.order_date)
          return dateA - dateB
        })
      } catch (err) {
        error.value = 'Failed to load orders: ' + err.message
      } finally {
        loading.value = false
      }
    }

    // Watch for filter changes and reload data
    watch([selectedPeriod, selectedLocation, selectedCategory, selectedStatus], () => {
      loadOrders()
    })

    // Restock orders have no warehouse/category/status/period dimension, so they
    // are not part of the global filters watch above and are loaded once on mount.
    const loadRestockOrders = async () => {
      try {
        restockOrders.value = await api.getRestockOrders()
      } catch (err) {
        // Keep this failure independent so the All Orders table still renders
        restockError.value = 'Failed to load submitted orders: ' + err.message
      }
    }

    const getOrdersByStatus = (status) => {
      return orders.value.filter(order => order.status === status)
    }

    const getOrderStatusClass = (status) => {
      const statusMap = {
        'Delivered': 'success',
        'Shipped': 'info',
        'Processing': 'warning',
        'Backordered': 'danger'
      }
      return statusMap[status] || 'info'
    }

    const formatDate = (dateString) => {
      const { currentLocale } = useI18n()
      const locale = currentLocale.value === 'ja' ? 'ja-JP' : 'en-US'
      return new Date(dateString).toLocaleDateString(locale, {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      })
    }

    onMounted(() => {
      loadOrders()
      loadRestockOrders()
    })

    return {
      t,
      loading,
      error,
      orders,
      restockOrders,
      restockError,
      getOrdersByStatus,
      getOrderStatusClass,
      formatDate,
      formatCurrency,
      formatCurrencyWithDecimals,
      currentCurrency,
      currencySymbol,
      translateProductName,
      translateCustomerName
    }
  }
}
</script>

<style scoped>
section + section {
  margin-top: var(--s10);
}

/* Fixed table layout to prevent column shifting */
.orders-table {
  table-layout: fixed;
  width: 100%;
}

/* Column widths */
.col-order-number {
  width: 130px;
}

.col-customer {
  width: 180px;
}

.col-items {
  width: 200px;
}

.col-status {
  width: 130px;
}

.col-date {
  width: 140px;
}

.col-value {
  width: 120px;
}

.col-value,
.col-date {
  text-align: right;
}

/* Items details styling */
.items-details {
  position: relative;
}

.items-summary {
  cursor: pointer;
  font-family: var(--mono);
  font-size: var(--t-sm);
  color: var(--steel);
  list-style: none;
  user-select: none;
  display: inline-block;
}

.items-summary::-webkit-details-marker {
  display: none;
}

.items-summary::before {
  content: '▶';
  display: inline-block;
  margin-right: 0.375rem;
  font-size: 0.75rem;
  transition: transform 0.2s;
}

.items-details[open] .items-summary::before {
  transform: rotate(90deg);
}

.items-summary:hover {
  color: var(--ink);
}

/* Dropdown container */
.items-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  margin-top: var(--s2);
  background: var(--surface-alt);
  border: 1px solid var(--rule);
  border-top: 1px solid var(--rule);
  border-radius: var(--r-sm);
  padding: var(--s3);
  z-index: 10;
  min-width: 300px;
  max-width: 400px;
}

.item-entry {
  display: flex;
  flex-direction: column;
  gap: var(--s1);
  padding: var(--s2);
  border-bottom: 1px solid var(--rule);
}

.item-entry:last-child {
  border-bottom: none;
}

.item-name {
  font-size: var(--t-md);
  font-weight: 500;
  color: var(--ink);
}

.item-meta {
  font-size: var(--t-sm);
  color: var(--steel);
}

.submitted-orders-empty {
  padding: var(--s12) var(--s6);
  text-align: center;
  color: var(--steel);
  font-size: var(--t-md);
}
</style>
