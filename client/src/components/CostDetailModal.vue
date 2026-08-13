<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="isOpen && costData" class="modal-overlay" @click="close">
        <div class="modal-container" @click.stop>
          <div class="modal-header">
            <h3 class="modal-title">{{ costData.month }} Cost Breakdown</h3>
            <button class="close-button" @click="close">
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                <path d="M15 5L5 15M5 5L15 15" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              </svg>
            </button>
          </div>

          <div class="modal-body">
            <div class="cost-summary">
              <div class="summary-card total">
                <div class="eyebrow">Total Costs</div>
                <div class="summary-value num">{{ currencySymbol }}{{ totalCosts.toLocaleString() }}</div>
              </div>
            </div>

            <div class="cost-breakdown">
              <div class="cost-item">
                <div class="cost-header">
                  <div class="cost-info">
                    <div class="eyebrow">Procurement</div>
                    <div class="cost-amount num">{{ currencySymbol }}{{ costData.procurement.toLocaleString() }}</div>
                  </div>
                  <div class="cost-percentage num">{{ getProcurementPercentage() }}%</div>
                </div>
              </div>

              <div class="cost-item">
                <div class="cost-header">
                  <div class="cost-info">
                    <div class="eyebrow">Operational</div>
                    <div class="cost-amount num">{{ currencySymbol }}{{ costData.operational.toLocaleString() }}</div>
                  </div>
                  <div class="cost-percentage num">{{ getOperationalPercentage() }}%</div>
                </div>
              </div>

              <div class="cost-item">
                <div class="cost-header">
                  <div class="cost-info">
                    <div class="eyebrow">Labor</div>
                    <div class="cost-amount num">{{ currencySymbol }}{{ costData.labor.toLocaleString() }}</div>
                  </div>
                  <div class="cost-percentage num">{{ getLaborPercentage() }}%</div>
                </div>
              </div>

              <div class="cost-item">
                <div class="cost-header">
                  <div class="cost-info">
                    <div class="eyebrow">Overhead</div>
                    <div class="cost-amount num">{{ currencySymbol }}{{ costData.overhead.toLocaleString() }}</div>
                  </div>
                  <div class="cost-percentage num">{{ getOverheadPercentage() }}%</div>
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
  costData: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['close'])

const totalCosts = computed(() => {
  if (!props.costData) return 0
  return props.costData.procurement + props.costData.operational +
         props.costData.labor + props.costData.overhead
})

const getProcurementPercentage = () => {
  if (!props.costData || totalCosts.value === 0) return 0
  return ((props.costData.procurement / totalCosts.value) * 100).toFixed(1)
}

const getOperationalPercentage = () => {
  if (!props.costData || totalCosts.value === 0) return 0
  return ((props.costData.operational / totalCosts.value) * 100).toFixed(1)
}

const getLaborPercentage = () => {
  if (!props.costData || totalCosts.value === 0) return 0
  return ((props.costData.labor / totalCosts.value) * 100).toFixed(1)
}

const getOverheadPercentage = () => {
  if (!props.costData || totalCosts.value === 0) return 0
  return ((props.costData.overhead / totalCosts.value) * 100).toFixed(1)
}

const close = () => {
  emit('close')
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
  max-width: 600px;
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

.cost-summary {
  margin-bottom: var(--s6);
}

.summary-card {
  padding: var(--s5);
  border-radius: var(--r-sm);
  border: 1px solid var(--rule-strong);
  background: var(--surface-alt);
  display: flex;
  flex-direction: column;
  gap: var(--s2);
}

.summary-value {
  font-size: var(--t-2xl);
  font-weight: 700;
  color: var(--ink);
}

.cost-breakdown {
  display: flex;
  flex-direction: column;
  gap: var(--s3);
}

.cost-item {
  padding: var(--s4);
  border-radius: var(--r-sm);
  border: 1px solid var(--rule);
}

.cost-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--s4);
}

.cost-info {
  display: flex;
  flex-direction: column;
  gap: var(--s2);
}

.cost-amount {
  font-size: var(--t-lg);
  font-weight: 700;
  color: var(--ink);
}

.cost-percentage {
  font-size: var(--t-md);
  color: var(--steel);
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
