<template>
  <div class="filters-bar">
    <div class="filters-container">
      <div class="filter-group" :class="{ 'is-set': selectedPeriod !== 'all' }">
        <label>{{ t('filters.timePeriod') }}</label>
        <select v-model="selectedPeriod" class="filter-select">
          <option value="all">{{ t('filters.allMonths') }}</option>
          <option value="2025-01">{{ t('months.january') }}</option>
          <option value="2025-02">{{ t('months.february') }}</option>
          <option value="2025-03">{{ t('months.march') }}</option>
          <option value="2025-04">{{ t('months.april') }}</option>
          <option value="2025-05">{{ t('months.may') }}</option>
          <option value="2025-06">{{ t('months.june') }}</option>
          <option value="2025-07">{{ t('months.july') }}</option>
          <option value="2025-08">{{ t('months.august') }}</option>
          <option value="2025-09">{{ t('months.september') }}</option>
          <option value="2025-10">{{ t('months.october') }}</option>
          <option value="2025-11">{{ t('months.november') }}</option>
          <option value="2025-12">{{ t('months.december') }}</option>
        </select>
      </div>

      <div class="filter-group" :class="{ 'is-set': selectedLocation !== 'all' }">
        <label>{{ t('filters.location') }}</label>
        <select v-model="selectedLocation" class="filter-select">
          <option value="all">{{ t('filters.all') }}</option>
          <option value="San Francisco">{{ t('warehouses.sanFrancisco') }}</option>
          <option value="London">{{ t('warehouses.london') }}</option>
          <option value="Tokyo">{{ t('warehouses.tokyo') }}</option>
        </select>
      </div>

      <div class="filter-group" :class="{ 'is-set': selectedCategory !== 'all' }">
        <label>{{ t('filters.category') }}</label>
        <select v-model="selectedCategory" class="filter-select">
          <option value="all">{{ t('filters.all') }}</option>
          <option value="circuit boards">{{ t('categories.circuitBoards') }}</option>
          <option value="sensors">{{ t('categories.sensors') }}</option>
          <option value="actuators">{{ t('categories.actuators') }}</option>
          <option value="controllers">{{ t('categories.controllers') }}</option>
          <option value="power supplies">{{ t('categories.powerSupplies') }}</option>
        </select>
      </div>

      <div class="filter-group" :class="{ 'is-set': selectedStatus !== 'all' }">
        <label>{{ t('filters.orderStatus') }}</label>
        <select v-model="selectedStatus" class="filter-select">
          <option value="all">{{ t('filters.all') }}</option>
          <option value="delivered">{{ t('status.delivered') }}</option>
          <option value="shipped">{{ t('status.shipped') }}</option>
          <option value="processing">{{ t('status.processing') }}</option>
          <option value="backordered">{{ t('status.backordered') }}</option>
        </select>
      </div>

      <button
        class="reset-filters-btn"
        @click="resetFilters"
        :disabled="!hasActiveFilters"
        title="Reset all filters"
      >
        Clear filters
      </button>
    </div>
  </div>
</template>

<script>
import { useFilters } from '../composables/useFilters'
import { useI18n } from '../composables/useI18n'

export default {
  name: 'FilterBar',
  setup() {
    const {
      selectedPeriod,
      selectedLocation,
      selectedCategory,
      selectedStatus,
      hasActiveFilters,
      resetFilters
    } = useFilters()

    const { t } = useI18n()

    return {
      t,
      selectedPeriod,
      selectedLocation,
      selectedCategory,
      selectedStatus,
      hasActiveFilters,
      resetFilters
    }
  }
}
</script>

<style scoped>
.filters-bar {
  margin-top: var(--s4);
}

.filters-container {
  display: flex;
  align-items: center;
  gap: var(--s2);
  flex-wrap: wrap;
}

.filter-group {
  display: inline-flex;
  align-items: center;
  gap: var(--s2);
  padding: 6px 10px;
  background: var(--surface);
  border: 1px solid var(--rule);
  border-radius: var(--r-sm);
  font-size: var(--t-md);
  color: var(--ink);
  transition: border-color 0.12s ease;
}

.filter-group:hover {
  border-color: var(--rule-strong);
}

.filter-group:focus-within {
  border-color: var(--ink);
  box-shadow: var(--ring);
}

.filter-group.is-set {
  border-color: var(--ink);
}

.filter-group label {
  font-family: var(--mono);
  font-size: var(--t-xs);
  font-weight: 500;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--steel-soft);
  white-space: nowrap;
}

.filter-select {
  border: none;
  background: none;
  font: inherit;
  color: inherit;
  padding: 0;
  cursor: pointer;
  outline: none;
}

.reset-filters-btn {
  margin-left: auto;
  font-size: var(--t-md);
  color: var(--steel);
  border: none;
  border-bottom: 1px solid var(--rule-strong);
  padding-bottom: 1px;
  background: none;
  border-radius: 0;
  cursor: pointer;
}

.reset-filters-btn:hover:not(:disabled) {
  color: var(--ink);
  border-color: var(--ink);
}

.reset-filters-btn:disabled {
  opacity: 0.4;
  cursor: default;
}
</style>
