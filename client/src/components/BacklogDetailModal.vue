<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="isOpen && backlogItem" class="modal-overlay" @click="close">
        <div class="modal-container" @click.stop>
          <div class="modal-header">
            <h3 class="modal-title">Inventory Shortage Details</h3>
            <button class="close-button" @click="close">
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                <path d="M15 5L5 15M5 5L15 15" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              </svg>
            </button>
          </div>

          <div class="modal-body">
            <div class="shortage-header">
              <div class="shortage-title-section">
                <div class="eyebrow">{{ backlogItem.item_sku }}</div>
                <h4 class="item-name">{{ translateProductName(backlogItem.item_name) }}</h4>
              </div>
              <span class="badge" :class="backlogItem.priority">
                {{ backlogItem.priority }} Priority
              </span>
            </div>

            <div class="shortage-summary">
              <div class="summary-card danger">
                <div class="eyebrow">Shortage Amount</div>
                <div class="summary-value num">{{ shortage }} units</div>
              </div>
              <div class="summary-card warning">
                <div class="eyebrow">Days Delayed</div>
                <div class="summary-value num">{{ backlogItem.days_delayed }} days</div>
              </div>
            </div>

            <div class="info-grid">
              <div class="info-item">
                <div class="eyebrow">Order ID</div>
                <div class="info-value num">{{ backlogItem.order_id }}</div>
              </div>

              <div class="info-item">
                <div class="eyebrow">Item SKU</div>
                <div class="info-value">
                  <span class="cell-sku"><b>{{ backlogItem.item_sku }}</b></span>
                </div>
              </div>

              <div class="info-item">
                <div class="eyebrow">Quantity Needed</div>
                <div class="info-value num">{{ backlogItem.quantity_needed }} units</div>
              </div>

              <div class="info-item">
                <div class="eyebrow">Quantity Available</div>
                <div class="info-value num">{{ backlogItem.quantity_available }} units</div>
              </div>

              <div class="info-item">
                <div class="eyebrow">Expected Date</div>
                <div class="info-value">{{ formatDate(backlogItem.expected_date) }}</div>
              </div>

              <div class="info-item">
                <div class="eyebrow">Status</div>
                <div class="info-value">
                  <span class="badge danger">Backordered</span>
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

const { translateProductName } = useI18n()

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false
  },
  backlogItem: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['close'])

const shortage = computed(() => {
  if (!props.backlogItem) return 0
  return props.backlogItem.quantity_needed - props.backlogItem.quantity_available
})

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

.shortage-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--s4);
  padding-bottom: var(--s5);
  border-bottom: 1px solid var(--rule);
  margin-bottom: var(--s5);
}

.shortage-title-section {
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

.shortage-summary {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--s4);
  margin-bottom: var(--s6);
}

.summary-card {
  padding: var(--s4);
  border-radius: var(--r-sm);
  border: 1px solid var(--rule-strong);
  display: flex;
  flex-direction: column;
  gap: var(--s2);
}

.summary-card.danger {
  background: var(--signal-soft);
  border-color: var(--signal);
}

.summary-card.warning {
  background: var(--amber-soft);
  border-color: var(--amber);
}

.summary-value {
  font-size: var(--t-2xl);
  font-weight: 700;
  color: var(--ink);
}

.summary-card.danger .summary-value {
  color: var(--signal);
}

.summary-card.warning .summary-value {
  color: var(--amber-ink);
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
