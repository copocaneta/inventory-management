<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="isOpen && product" class="modal-overlay" @click="close">
        <div class="modal-container" @click.stop>
          <div class="modal-header">
            <h3 class="modal-title">Product Details</h3>
            <button class="close-button" @click="close">
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                <path d="M15 5L5 15M5 5L15 15" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              </svg>
            </button>
          </div>

          <div class="modal-body">
            <div class="product-header">
              <div class="product-title-section">
                <div class="eyebrow">{{ product.sku }}</div>
                <h4 class="product-name">{{ product.name }}</h4>
              </div>
              <span class="badge" :class="getStockBadgeClass(product.stockLevel)">
                {{ product.stockLevel }}
              </span>
            </div>

            <div class="info-grid">
              <div class="info-item">
                <div class="eyebrow">Category</div>
                <div class="info-value">{{ product.category }}</div>
              </div>

              <div class="info-item">
                <div class="eyebrow">Warehouse</div>
                <div class="info-value">{{ product.warehouse }}</div>
              </div>

              <div class="info-item">
                <div class="eyebrow">Units Ordered</div>
                <div class="info-value num">{{ product.unitsOrdered }}</div>
              </div>

              <div class="info-item">
                <div class="eyebrow">Total Revenue</div>
                <div class="info-value num">{{ currencySymbol }}{{ product.revenue.toLocaleString() }}</div>
              </div>

              <div class="info-item">
                <div class="eyebrow">Current Stock</div>
                <div class="info-value num">{{ product.quantityOnHand }} units</div>
              </div>

              <div class="info-item">
                <div class="eyebrow">Reorder Point</div>
                <div class="info-value num">{{ product.reorderPoint }} units</div>
              </div>

              <div class="info-item">
                <div class="eyebrow">First Order Date</div>
                <div class="info-value">{{ formatDate(product.firstOrderDate) }}</div>
              </div>

              <div class="info-item">
                <div class="eyebrow">Stock Status</div>
                <div class="info-value">
                  <span :class="['badge', getStockBadgeClass(product.stockLevel)]">
                    {{ product.stockLevel }}
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

const { currentCurrency } = useI18n()

const currencySymbol = computed(() => {
  return currentCurrency.value === 'JPY' ? '¥' : '$'
})

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false
  },
  product: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['close'])

const close = () => {
  emit('close')
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

const getStockBadgeClass = (stockLevel) => {
  if (stockLevel === 'In Stock') return 'success'
  if (stockLevel === 'Low Stock') return 'warning'
  if (stockLevel === 'Out of Stock') return 'danger'
  return 'info'
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

.product-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--s4);
  padding-bottom: var(--s5);
  border-bottom: 1px solid var(--rule);
  margin-bottom: var(--s6);
}

.product-title-section {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: var(--s2);
}

.product-name {
  font-family: var(--display);
  font-size: var(--t-xl);
  font-weight: 700;
  color: var(--ink);
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
