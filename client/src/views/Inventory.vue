<template>
  <div class="inventory">
    <div class="page-header">
      <p>{{ t('inventory.description') }}</p>
    </div>

    <div v-if="loading" class="loading">{{ t('common.loading') }}</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else>
      <section class="stock-section">
        <div class="section-head">
          <h3>{{ t('inventory.stockLevels') }}</h3>
          <span class="eyebrow">{{ filteredItems.length }} {{ t('inventory.skus') }}</span>
          <div class="search-box">
            <svg class="search-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clip-rule="evenodd" />
            </svg>
            <input
              v-model="searchQuery"
              type="text"
              :placeholder="t('inventory.searchPlaceholder')"
              class="search-input"
            />
            <button
              v-if="searchQuery"
              @click="searchQuery = ''"
              class="clear-search"
              :title="t('inventory.clearSearch')"
            >
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
              </svg>
            </button>
          </div>
        </div>
        <div class="table-container">
          <table>
            <thead>
              <tr>
                <th>{{ t('inventory.table.sku') }}</th>
                <th>{{ t('inventory.table.category') }}</th>
                <th class="align-right">{{ t('inventory.table.quantityOnHand') }}</th>
                <th class="align-right">{{ t('inventory.table.reorderPoint') }}</th>
                <th class="align-right">{{ t('inventory.table.unitCost') }}</th>
                <th class="align-right">{{ t('inventory.table.totalValue') }}</th>
                <th>{{ t('inventory.table.status') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="item in filteredItems"
                :key="item.id"
                class="clickable-row"
                @click="showItemDetail(item)"
              >
                <td>
                  <span class="cell-sku"><b>{{ item.sku }}</b><span>{{ item.location }}</span></span>
                  <span class="cell-name">{{ translateProductName(item.name) }}</span>
                </td>
                <td>{{ translateCategory(item.category) }}</td>
                <td class="align-right">
                  <span :class="['qty', { low: item.quantity_on_hand <= item.reorder_point }]">{{ item.quantity_on_hand }}</span>
                </td>
                <td class="align-right"><span class="num">{{ item.reorder_point }}</span></td>
                <td class="align-right"><span class="num">{{ currencySymbol }}{{ item.unit_cost.toFixed(2) }}</span></td>
                <td class="align-right"><span class="num">{{ currencySymbol }}{{ (item.quantity_on_hand * item.unit_cost).toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2}) }}</span></td>
                <td>
                  <span :class="['badge', getStockStatusClass(item)]">
                    {{ getStockStatus(item) }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
    </div>

    <InventoryDetailModal
      :is-open="showItemModal"
      :inventory-item="selectedItem"
      @close="showItemModal = false"
    />
  </div>
</template>

<script>
import { ref, onMounted, watch, computed } from 'vue'
import { api } from '../api'
import { useFilters } from '../composables/useFilters'
import { useI18n } from '../composables/useI18n'
import InventoryDetailModal from '../components/InventoryDetailModal.vue'

export default {
  name: 'Inventory',
  components: {
    InventoryDetailModal
  },
  setup() {
    const { t, currentCurrency, translateProductName, translateWarehouse } = useI18n()

    const currencySymbol = computed(() => {
      return currentCurrency.value === 'JPY' ? '¥' : '$'
    })

    const loading = ref(true)
    const error = ref(null)
    const items = ref([])
    const searchQuery = ref('')

    // Modal state
    const showItemModal = ref(false)
    const selectedItem = ref(null)

    // Use shared filters
    const { selectedLocation, selectedCategory, getCurrentFilters } = useFilters()

    // Stock status order for sorting (using status keys)
    const STATUS_ORDER = { 'lowStock': 0, 'adequate': 1, 'inStock': 2 }

    // Get stock status key (for sorting and translation)
    const getStockStatusKey = (item) => {
      if (item.quantity_on_hand <= item.reorder_point) {
        return 'lowStock'
      } else if (item.quantity_on_hand <= item.reorder_point * 1.5) {
        return 'adequate'
      } else {
        return 'inStock'
      }
    }

    // Computed property to filter items by search query and sort by stock status
    const filteredItems = computed(() => {
      let filtered = items.value

      // Apply search filter if query exists
      if (searchQuery.value.trim()) {
        const query = searchQuery.value.toLowerCase().trim()
        filtered = filtered.filter(item =>
          item.name.toLowerCase().includes(query)
        )
      }

      // Sort by stock status: Low Stock first, then Adequate, then In Stock
      // Always create a copy to avoid mutating the original array
      return filtered.slice().sort((a, b) => {
        const statusA = getStockStatusKey(a)
        const statusB = getStockStatusKey(b)
        return STATUS_ORDER[statusA] - STATUS_ORDER[statusB]
      })
    })

    const loadInventory = async () => {
      try {
        loading.value = true
        const filters = getCurrentFilters()
        // Inventory doesn't support month/status filters, only warehouse and category
        items.value = await api.getInventory({
          warehouse: filters.warehouse,
          category: filters.category
        })
      } catch (err) {
        error.value = 'Failed to load inventory: ' + err.message
      } finally {
        loading.value = false
      }
    }

    // Watch for filter changes and reload data
    watch([selectedLocation, selectedCategory], () => {
      loadInventory()
    })

    const getStockStatus = (item) => {
      const key = getStockStatusKey(item)
      return t(`status.${key}`)
    }

    const getStockStatusClass = (item) => {
      if (item.quantity_on_hand <= item.reorder_point) {
        return 'danger'
      } else if (item.quantity_on_hand <= item.reorder_point * 1.5) {
        return 'warning'
      } else {
        return 'success'
      }
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

    const showItemDetail = (item) => {
      selectedItem.value = item
      showItemModal.value = true
    }

    onMounted(loadInventory)

    return {
      t,
      loading,
      error,
      items,
      searchQuery,
      filteredItems,
      getStockStatus,
      getStockStatusClass,
      translateCategory,
      showItemModal,
      selectedItem,
      showItemDetail,
      currencySymbol,
      translateProductName,
      translateWarehouse
    }
  }
}
</script>

<style scoped>
.stock-section {
  margin-bottom: var(--s10);
}

.stock-section .section-head {
  flex-wrap: wrap;
}

.align-right {
  text-align: right;
}

.search-box {
  position: relative;
  display: flex;
  align-items: center;
  min-width: 280px;
  margin-left: var(--s5);
  background: var(--surface);
  border: 1px solid var(--rule);
  border-radius: var(--r-sm);
}

.search-box:focus-within {
  border-color: var(--ink);
  box-shadow: var(--ring);
}

.search-icon {
  position: absolute;
  left: var(--s3);
  width: 14px;
  height: 14px;
  color: var(--steel-soft);
  pointer-events: none;
}

.search-input {
  width: 100%;
  padding: 6px var(--s8) 6px var(--s8);
  border: none;
  font-size: var(--t-md);
  color: var(--ink);
  background: transparent;
}

.search-input:focus {
  outline: none;
}

.search-input::placeholder {
  color: var(--steel-soft);
}

.clear-search {
  position: absolute;
  right: var(--s2);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2px;
  color: var(--steel-soft);
  cursor: pointer;
}

.clear-search:hover {
  color: var(--steel);
}

.clear-search svg {
  width: 14px;
  height: 14px;
}

.error {
  padding: var(--s6);
  text-align: center;
  color: var(--signal);
}

.clickable-row {
  cursor: pointer;
}
</style>
