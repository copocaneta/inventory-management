<template>
  <div class="shell" :class="{ 'is-collapsed': sidebarCollapsed, 'drawer-open': drawerOpen }">
    <div
      v-if="drawerOpen"
      class="sidebar-backdrop"
      @click="drawerOpen = false"
    ></div>

    <aside class="sidebar">
      <div class="brand">
        <span class="brand-mark">{{ t('nav.companyName') }}</span>
        <span class="brand-sub">{{ t('nav.subtitle') }}</span>
      </div>

      <nav class="nav-group">
        <span class="nav-group-label eyebrow">{{ t('nav.groupFloor') }}</span>

        <router-link to="/" exact-active-class="is-active" class="nav-link" :title="t('nav.overview')">
          <svg width="17" height="17" viewBox="0 0 17 17" fill="none" stroke="currentColor" stroke-width="1.6">
            <rect x="2" y="2" width="5.5" height="5.5" rx="0.5" />
            <rect x="9.5" y="2" width="5.5" height="5.5" rx="0.5" />
            <rect x="2" y="9.5" width="5.5" height="5.5" rx="0.5" />
            <rect x="9.5" y="9.5" width="5.5" height="5.5" rx="0.5" />
          </svg>
          <span>{{ t('nav.overview') }}</span>
        </router-link>

        <router-link to="/inventory" active-class="is-active" class="nav-link" :title="t('nav.inventory')">
          <svg width="17" height="17" viewBox="0 0 17 17" fill="none" stroke="currentColor" stroke-width="1.6">
            <path d="M8.5 2L14.5 5.25V11.75L8.5 15L2.5 11.75V5.25L8.5 2Z" stroke-linejoin="round" />
            <path d="M2.5 5.25L8.5 8.5L14.5 5.25" stroke-linejoin="round" />
            <path d="M8.5 8.5V15" />
          </svg>
          <span>{{ t('nav.inventory') }}</span>
        </router-link>

        <router-link to="/orders" active-class="is-active" class="nav-link" :title="t('nav.orders')">
          <svg width="17" height="17" viewBox="0 0 17 17" fill="none" stroke="currentColor" stroke-width="1.6">
            <rect x="3.5" y="3" width="10" height="12" rx="1" />
            <rect x="6" y="1.75" width="5" height="2.5" rx="0.5" />
            <path d="M6 8H11" stroke-linecap="round" />
            <path d="M6 10.75H11" stroke-linecap="round" />
            <path d="M6 13.5H9" stroke-linecap="round" />
          </svg>
          <span>{{ t('nav.orders') }}</span>
        </router-link>
      </nav>

      <nav class="nav-group">
        <span class="nav-group-label eyebrow">{{ t('nav.groupAnalysis') }}</span>

        <router-link to="/spending" active-class="is-active" class="nav-link" :title="t('nav.finance')">
          <svg width="17" height="17" viewBox="0 0 17 17" fill="none" stroke="currentColor" stroke-width="1.6">
            <path d="M8.5 1.75V15.25" stroke-linecap="round" />
            <path d="M11.75 4.5C11.75 3.25 10.25 2.75 8.5 2.75C6.75 2.75 5.25 3.5 5.25 4.85C5.25 7.75 11.75 6.25 11.75 9.15C11.75 10.5 10.25 11.25 8.5 11.25C6.75 11.25 5.25 10.75 5.25 9.5" stroke-linecap="round" />
          </svg>
          <span>{{ t('nav.finance') }}</span>
        </router-link>

        <router-link to="/demand" active-class="is-active" class="nav-link" :title="t('nav.demandForecast')">
          <svg width="17" height="17" viewBox="0 0 17 17" fill="none" stroke="currentColor" stroke-width="1.6">
            <path d="M2 12.5L6.5 8L9.5 11L15 5.5" stroke-linecap="round" stroke-linejoin="round" />
            <path d="M11 5.5H15V9.5" stroke-linecap="round" stroke-linejoin="round" />
          </svg>
          <span>{{ t('nav.demandForecast') }}</span>
        </router-link>

        <router-link to="/restocking" active-class="is-active" class="nav-link" :title="t('nav.restocking')">
          <svg width="17" height="17" viewBox="0 0 17 17" fill="none" stroke="currentColor" stroke-width="1.6">
            <rect x="2" y="7" width="10" height="7.5" rx="0.5" stroke-linejoin="round" />
            <path d="M2 7L7 4L12 7" stroke-linecap="round" stroke-linejoin="round" />
            <path d="M13.5 2V9" stroke-linecap="round" />
            <path d="M11 6.5L13.5 9L16 6.5" stroke-linecap="round" stroke-linejoin="round" />
          </svg>
          <span>{{ t('nav.restocking') }}</span>
        </router-link>

        <router-link to="/reports" active-class="is-active" class="nav-link" :title="t('nav.reports')">
          <svg width="17" height="17" viewBox="0 0 17 17" fill="none" stroke="currentColor" stroke-width="1.6">
            <path d="M4.5 1.75H10.5L13 4.25V15.25H4.5V1.75Z" stroke-linejoin="round" />
            <path d="M10.5 1.75V4.25H13" stroke-linejoin="round" />
            <path d="M6.5 8H11" stroke-linecap="round" />
            <path d="M6.5 10.5H11" stroke-linecap="round" />
            <path d="M6.5 13H9" stroke-linecap="round" />
          </svg>
          <span>{{ t('nav.reports') }}</span>
        </router-link>
      </nav>

      <div class="sidebar-foot">
        <ProfileMenu
          @show-profile-details="showProfileDetails = true"
          @show-tasks="showTasks = true"
        />
        <LanguageSwitcher />
        <button
          class="collapse-toggle"
          @click="toggleSidebar"
          :aria-label="sidebarCollapsed ? t('nav.expandSidebar') : t('nav.collapseSidebar')"
          :title="sidebarCollapsed ? t('nav.expandSidebar') : t('nav.collapseSidebar')"
        >
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.6">
            <rect x="2" y="2.5" width="12" height="11" rx="1" />
            <path d="M6.5 2.5V13.5" />
          </svg>
        </button>
      </div>
    </aside>

    <div class="main">
      <div class="page-head">
        <button
          class="page-hamburger"
          @click="drawerOpen = !drawerOpen"
          :aria-label="t('nav.openMenu')"
          :aria-expanded="drawerOpen"
        >
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.75">
            <path d="M3 5.5H17" stroke-linecap="round" />
            <path d="M3 10H17" stroke-linecap="round" />
            <path d="M3 14.5H17" stroke-linecap="round" />
          </svg>
        </button>
        <h1 class="page-title">{{ pageTitle }}</h1>
        <!-- Restocking ignores all global filters (no warehouse/category/month/status
             dimension on demand forecasts), so showing a FilterBar there would be a
             control that silently does nothing - worse than no control at all. -->
        <FilterBar v-if="$route.path !== '/restocking'" />
      </div>
      <main class="content">
        <router-view />
      </main>
    </div>

    <ProfileDetailsModal
      :is-open="showProfileDetails"
      @close="showProfileDetails = false"
    />

    <TasksModal
      :is-open="showTasks"
      :tasks="tasks"
      @close="showTasks = false"
      @add-task="addTask"
      @delete-task="deleteTask"
      @toggle-task="toggleTask"
    />
  </div>
</template>

<script>
import { ref, onMounted, onBeforeUnmount, computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import { api } from './api'
import { useAuth } from './composables/useAuth'
import { useI18n } from './composables/useI18n'
import FilterBar from './components/FilterBar.vue'
import ProfileMenu from './components/ProfileMenu.vue'
import ProfileDetailsModal from './components/ProfileDetailsModal.vue'
import TasksModal from './components/TasksModal.vue'
import LanguageSwitcher from './components/LanguageSwitcher.vue'

export default {
  name: 'App',
  components: {
    FilterBar,
    ProfileMenu,
    ProfileDetailsModal,
    TasksModal,
    LanguageSwitcher
  },
  setup() {
    const { currentUser } = useAuth()
    const { t } = useI18n()
    const route = useRoute()
    const showProfileDetails = ref(false)
    const showTasks = ref(false)
    const apiTasks = ref([])

    const sidebarCollapsed = ref(localStorage.getItem('app-sidebar-collapsed') === 'true')
    const toggleSidebar = () => {
      sidebarCollapsed.value = !sidebarCollapsed.value
      localStorage.setItem('app-sidebar-collapsed', String(sidebarCollapsed.value))
    }

    const drawerOpen = ref(false)
    const handleDrawerKeydown = (event) => {
      if (event.key === 'Escape') {
        drawerOpen.value = false
      }
    }
    watch(drawerOpen, (isOpen) => {
      if (isOpen) {
        window.addEventListener('keydown', handleDrawerKeydown)
      } else {
        window.removeEventListener('keydown', handleDrawerKeydown)
      }
    })
    watch(() => route.path, () => {
      drawerOpen.value = false
    })
    onBeforeUnmount(() => {
      window.removeEventListener('keydown', handleDrawerKeydown)
    })

    const pageTitleMap = {
      '/': () => t('nav.overview'),
      '/inventory': () => t('nav.inventory'),
      '/orders': () => t('nav.orders'),
      '/spending': () => t('nav.finance'),
      '/demand': () => t('nav.demandForecast'),
      '/restocking': () => t('nav.restocking'),
      '/reports': () => t('nav.reports')
    }
    const pageTitle = computed(() => {
      const resolver = pageTitleMap[route.path]
      return resolver ? resolver() : ''
    })

    // Merge mock tasks from currentUser with API tasks
    const tasks = computed(() => {
      return [...currentUser.value.tasks, ...apiTasks.value]
    })

    const loadTasks = async () => {
      try {
        apiTasks.value = await api.getTasks()
      } catch (err) {
        console.error('Failed to load tasks:', err)
      }
    }

    const addTask = async (taskData) => {
      try {
        const newTask = await api.createTask(taskData)
        // Add new task to the beginning of the array
        apiTasks.value.unshift(newTask)
      } catch (err) {
        console.error('Failed to add task:', err)
      }
    }

    const deleteTask = async (taskId) => {
      try {
        // Check if it's a mock task (from currentUser)
        const isMockTask = currentUser.value.tasks.some(t => t.id === taskId)

        if (isMockTask) {
          // Remove from mock tasks
          const index = currentUser.value.tasks.findIndex(t => t.id === taskId)
          if (index !== -1) {
            currentUser.value.tasks.splice(index, 1)
          }
        } else {
          // Remove from API tasks
          await api.deleteTask(taskId)
          apiTasks.value = apiTasks.value.filter(t => t.id !== taskId)
        }
      } catch (err) {
        console.error('Failed to delete task:', err)
      }
    }

    const toggleTask = async (taskId) => {
      try {
        // Check if it's a mock task (from currentUser)
        const mockTask = currentUser.value.tasks.find(t => t.id === taskId)

        if (mockTask) {
          // Toggle mock task status
          mockTask.status = mockTask.status === 'pending' ? 'completed' : 'pending'
        } else {
          // Toggle API task
          const updatedTask = await api.toggleTask(taskId)
          const index = apiTasks.value.findIndex(t => t.id === taskId)
          if (index !== -1) {
            apiTasks.value[index] = updatedTask
          }
        }
      } catch (err) {
        console.error('Failed to toggle task:', err)
      }
    }

    onMounted(loadTasks)

    return {
      t,
      pageTitle,
      sidebarCollapsed,
      toggleSidebar,
      drawerOpen,
      showProfileDetails,
      showTasks,
      tasks,
      addTask,
      deleteTask,
      toggleTask
    }
  }
}
</script>

<style scoped>
.shell {
  display: grid;
  grid-template-columns: var(--sidebar-w) 1fr;
  min-height: 100vh;
}

.sidebar {
  position: sticky;
  top: 0;
  height: 100vh;
  display: flex;
  flex-direction: column;
  gap: var(--s6);
  padding: var(--s6) 0 var(--s4);
  background: var(--surface);
  border-right: 1px solid var(--rule);
  overflow-y: auto;
}

.brand {
  padding: 0 var(--s5);
}

.brand-mark {
  display: inline-flex;
  align-items: center;
  gap: var(--s2);
  font-family: var(--display);
  font-weight: 700;
  font-size: 19px;
  letter-spacing: 0.02em;
  text-transform: uppercase;
}

.brand-mark::before {
  content: '';
  width: 5px;
  height: 19px;
  background: var(--amber);
  border-radius: 1px;
}

.brand-sub {
  display: block;
  margin-top: var(--s2);
  padding-left: 13px;
  font-family: var(--mono);
  font-size: var(--t-xs);
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--steel-soft);
}

.nav-group {
  display: flex;
  flex-direction: column;
  gap: 2px;
  padding: 0 var(--s3);
}

.nav-group-label {
  padding: 0 var(--s3) var(--s2);
}

.nav-link {
  position: relative;
  display: flex;
  align-items: center;
  gap: var(--s3);
  padding: 9px var(--s3);
  border-radius: var(--r-sm);
  color: var(--steel);
  font-size: 13.5px;
  font-weight: 500;
  transition: background 0.12s ease, color 0.12s ease;
}

.nav-link svg {
  flex-shrink: 0;
}

.nav-link:hover {
  background: #f2f0ec;
  color: var(--ink);
}

.nav-link.is-active {
  background: var(--amber-soft);
  color: var(--ink);
  font-weight: 600;
}

.nav-link.is-active::before {
  content: '';
  position: absolute;
  left: -12px;
  top: 7px;
  bottom: 7px;
  width: 3px;
  background: var(--amber);
  border-radius: 0 2px 2px 0;
}

.sidebar-foot {
  margin-top: auto;
  padding: var(--s4) var(--s5) 0;
  display: flex;
  flex-direction: column;
  gap: var(--s3);
  border-top: 1px solid var(--rule);
}

.collapse-toggle {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  align-self: flex-start;
  width: 32px;
  height: 32px;
  border-radius: var(--r-sm);
  color: var(--steel);
  transition: background 0.12s ease, color 0.12s ease;
}

.collapse-toggle:hover {
  background: #f2f0ec;
  color: var(--ink);
}

.main {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.page-head {
  position: sticky;
  top: 0;
  z-index: 20;
  background: var(--paper);
  border-bottom: 1px solid var(--rule);
  padding: var(--s6) var(--s8) var(--s4);
}

.page-title {
  font-family: var(--display);
  font-size: var(--t-2xl);
  font-weight: 700;
  line-height: 1;
  letter-spacing: -0.005em;
  text-transform: uppercase;
  margin-bottom: var(--s4);
}

.content {
  padding: var(--s8);
  max-width: var(--content-max);
  width: 100%;
}

/* ---------- collapsed rail ---------- */

.shell.is-collapsed {
  --sidebar-w: var(--sidebar-w-rail);
}

.is-collapsed .nav-link {
  justify-content: center;
  padding: 9px;
  margin: 0 var(--s1);
}

.is-collapsed .nav-link span,
.is-collapsed .brand-sub,
.is-collapsed .nav-group-label {
  display: none;
}

/* In the rail the wordmark has nowhere to go, so it reduces to the amber tick
   from .brand-mark::before. font-size:0 drops the text without dropping the
   pseudo-element, which carries its own width and height. */
.is-collapsed .brand {
  display: flex;
  justify-content: center;
  padding: 0;
}

.is-collapsed .brand-mark {
  font-size: 0;
  gap: 0;
}

.page-hamburger {
  display: none;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  margin-right: var(--s3);
  border-radius: var(--r-sm);
  color: var(--steel);
  transition: background 0.12s ease, color 0.12s ease;
}

.page-hamburger:hover {
  background: #f2f0ec;
  color: var(--ink);
}

/* ---------- responsive: 861px - 1200px, forced icon rail ---------- */

@media (max-width: 1200px) and (min-width: 861px) {
  .shell {
    --sidebar-w: var(--sidebar-w-rail);
  }

  .nav-link {
    justify-content: center;
    padding: 9px;
    margin: 0 var(--s1);
  }

  .nav-link span,
  .brand-sub,
  .nav-group-label {
    display: none;
  }

  .brand {
    display: flex;
    justify-content: center;
    padding: 0;
  }

  .brand-mark {
    font-size: 0;
    gap: 0;
  }

  .collapse-toggle {
    display: none;
  }

  .sidebar-foot {
    flex-direction: column;
    gap: var(--s2);
  }
}

/* ---------- responsive: below 860px, off-canvas drawer ---------- */

@media (max-width: 860px) {
  .shell {
    grid-template-columns: 1fr;
    --sidebar-w: 248px;
  }

  .sidebar {
    position: fixed;
    top: 0;
    left: 0;
    bottom: 0;
    width: var(--sidebar-w);
    height: 100vh;
    transform: translateX(-100%);
    transition: transform 0.2s ease;
    z-index: 300;
  }

  .shell.drawer-open .sidebar {
    transform: translateX(0);
  }

  /* the drawer always shows full labels, even if the rail preference is stored */
  .shell.is-collapsed .sidebar .nav-link {
    justify-content: flex-start;
    padding: 9px var(--s3);
    margin: 0;
  }

  .shell.is-collapsed .sidebar .nav-link span,
  .shell.is-collapsed .sidebar .brand-sub,
  .shell.is-collapsed .sidebar .nav-group-label {
    display: revert;
  }

  .sidebar-backdrop {
    position: fixed;
    inset: 0;
    background: rgba(16, 20, 24, 0.45);
    z-index: 290;
  }

  .collapse-toggle,
  .shell.is-collapsed .collapse-toggle {
    display: none;
  }

  .page-hamburger {
    display: inline-flex;
  }

  .page-head,
  .content {
    padding-left: var(--s5);
    padding-right: var(--s5);
  }
}
</style>
