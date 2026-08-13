<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="isOpen && inventoryItem" class="modal-overlay" @click="close">
        <div class="modal-container" @click.stop>
          <div class="modal-header">
            <h3 class="modal-title">Inventory Item Details</h3>
            <button class="close-button" @click="close">
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                <path d="M15 5L5 15M5 5L15 15" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              </svg>
            </button>
          </div>

          <div class="modal-body">
            <div class="item-header">
              <div class="item-title-section">
                <div class="eyebrow">{{ inventoryItem.sku }}</div>
                <h4 class="item-name">{{ translateProductName(inventoryItem.name) }}</h4>
              </div>
              <span class="badge" :class="getStockStatusClass()">
                {{ getStockStatus() }}
              </span>
            </div>

            <div class="stock-summary">
              <div class="summary-card primary">
                <div class="eyebrow">Quantity on Hand</div>
                <div class="summary-value num">{{ inventoryItem.quantity_on_hand }} units</div>
              </div>
              <div class="summary-card" :class="getSummaryCardClass()">
                <div class="eyebrow">Stock Level</div>
                <div class="summary-value num">{{ stockPercentage }}%</div>
                <div class="summary-subtitle">vs. reorder point</div>
              </div>
            </div>

            <div class="info-grid">
              <div class="info-item">
                <div class="eyebrow">Category</div>
                <div class="info-value">{{ inventoryItem.category }}</div>
              </div>

              <div class="info-item">
                <div class="eyebrow">Location</div>
                <div class="info-value">{{ inventoryItem.location }}</div>
              </div>

              <div class="info-item">
                <div class="eyebrow">Reorder Point</div>
                <div class="info-value num">{{ inventoryItem.reorder_point }} units</div>
              </div>

              <div class="info-item">
                <div class="eyebrow">Units Remaining</div>
                <div class="info-value">
                  <span class="num" :class="inventoryItem.quantity_on_hand <= inventoryItem.reorder_point ? 'qty low' : 'qty'">
                    {{ inventoryItem.quantity_on_hand - inventoryItem.reorder_point }} units
                  </span>
                </div>
              </div>

              <div class="info-item">
                <div class="eyebrow">Unit Cost</div>
                <div class="info-value num">{{ currencySymbol }}{{ inventoryItem.unit_cost.toFixed(2) }}</div>
              </div>

              <div class="info-item">
                <div class="eyebrow">Total Value</div>
                <div class="info-value total-value num">
                  {{ currencySymbol }}{{ totalValue.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2}) }}
                </div>
              </div>

              <div class="info-item">
                <div class="eyebrow">Warehouse</div>
                <div class="info-value">{{ translateWarehouse(inventoryItem.warehouse) }}</div>
              </div>

              <div class="info-item">
                <div class="eyebrow">Status</div>
                <div class="info-value">
                  <span :class="['badge', getStockStatusClass()]">
                    {{ getStockStatus() }}
                  </span>
                </div>
              </div>
            </div>
          </div>

          <div class="modal-footer">
            <button class="btn-secondary" @click="close">Close</button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from '../composables/useI18n'

const { currentCurrency, translateProductName, translateWarehouse } = useI18n()

const currencySymbol = computed(() => {
  return currentCurrency.value === 'JPY' ? '¥' : '$'
})

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false
  },
  inventoryItem: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['close'])

const totalValue = computed(() => {
  if (!props.inventoryItem) return 0
  return props.inventoryItem.quantity_on_hand * props.inventoryItem.unit_cost
})

const stockPercentage = computed(() => {
  if (!props.inventoryItem || props.inventoryItem.reorder_point === 0) return 0
  return Math.round((props.inventoryItem.quantity_on_hand / props.inventoryItem.reorder_point) * 100)
})

const close = () => {
  emit('close')
}

const getStockStatus = () => {
  if (!props.inventoryItem) return 'Unknown'
  if (props.inventoryItem.quantity_on_hand <= props.inventoryItem.reorder_point) {
    return 'Low Stock'
  } else if (props.inventoryItem.quantity_on_hand <= props.inventoryItem.reorder_point * 1.5) {
    return 'Adequate'
  } else {
    return 'In Stock'
  }
}

const getStockStatusClass = () => {
  const status = getStockStatus()
  if (status === 'Low Stock') return 'danger'
  if (status === 'Adequate') return 'warning'
  return 'success'
}

const getSummaryCardClass = () => {
  const status = getStockStatus()
  if (status === 'Low Stock') return 'danger-card'
  if (status === 'Adequate') return 'warning-card'
  return 'success-card'
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(16, 20, 24, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--s4);
  z-index: 2000;
}

.modal-container {
  background: var(--surface);
  border: 1px solid var(--rule-strong);
  border-radius: var(--r-sm);
  box-shadow: var(--e-3);
  width: 100%;
  max-width: 700px;
  max-height: 90vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.modal-header {
  padding: var(--s5) var(--s6);
  border-bottom: 1px solid var(--rule);
  display: flex;
  align-items: center;
  gap: var(--s4);
}

.modal-title {
  font-family: var(--display);
  font-size: var(--t-lg);
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--ink);
}

.close-button {
  margin-left: auto;
  display: grid;
  place-items: center;
  width: 28px;
  height: 28px;
  border-radius: var(--r-sm);
  color: var(--steel);
  transition: background 0.12s ease, color 0.12s ease;
}

.close-button:hover {
  background: var(--surface-alt);
  color: var(--ink);
}

.modal-body {
  flex: 1;
  overflow-y: auto;
  padding: var(--s6);
}

.item-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--s4);
  padding-bottom: var(--s5);
  border-bottom: 1px solid var(--rule);
  margin-bottom: var(--s5);
}

.item-title-section {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: var(--s2);
}

.item-name {
  font-family: var(--display);
  font-size: var(--t-xl);
  font-weight: 700;
  color: var(--ink);
}

.stock-summary {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--s4);
  margin-bottom: var(--s6);
}

.summary-card {
  padding: var(--s4);
  border-radius: var(--r-sm);
  border: 1px solid var(--rule-strong);
  background: var(--surface-alt);
  display: flex;
  flex-direction: column;
  gap: var(--s2);
}

.summary-card.success-card {
  background: var(--mint-soft);
  border-color: var(--mint);
}

.summary-card.warning-card {
  background: var(--amber-soft);
  border-color: var(--amber);
}

.summary-card.danger-card {
  background: var(--signal-soft);
  border-color: var(--signal);
}

.summary-value {
  font-size: var(--t-2xl);
  font-weight: 700;
  color: var(--ink);
}

.summary-subtitle {
  font-size: var(--t-sm);
  color: var(--steel);
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--s5);
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: var(--s2);
}

.info-value {
  font-size: var(--t-base);
  color: var(--ink);
  font-weight: 500;
}

.info-value.total-value {
  font-size: var(--t-lg);
  color: var(--ink);
  font-weight: 700;
}

.modal-footer {
  padding: var(--s5) var(--s6);
  border-top: 1px solid var(--rule);
  display: flex;
  justify-content: flex-end;
  gap: var(--s3);
}

.btn-secondary {
  padding: 8px var(--s4);
  border: 1px solid var(--rule-strong);
  border-radius: var(--r-sm);
  background: var(--surface);
  color: var(--ink);
  font-size: var(--t-md);
  font-weight: 500;
  cursor: pointer;
  transition: border-color 0.12s ease;
}

.btn-secondary:hover {
  border-color: var(--ink);
}

.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.16s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-active .modal-container,
.modal-leave-active .modal-container {
  transition: transform 0.16s ease;
}

.modal-enter-from .modal-container,
.modal-leave-to .modal-container {
  transform: translateY(4px);
}
</style>
