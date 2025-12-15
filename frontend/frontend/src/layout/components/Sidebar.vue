<script setup>
import { useRoute, useRouter } from 'vue-router'
import { computed } from 'vue'

const router = useRouter()
const route = useRoute()

const menus = [
  { path: '/map-editor', label: '地图编辑器' },
  { path: '/event-management', label: '活动管理' },
  { path: '/area-management', label: '区域管理' },
  { path: '/facility-management', label: '设施管理' }
]

const activePath = computed(() => route.path)

function handleClick(path) {
  if (path !== route.path) {
    router.push(path)
  }
}
</script>

<template>
  <aside class="sidebar">
    <nav class="sidebar-nav">
      <div
        v-for="item in menus"
        :key="item.path"
        class="sidebar-item"
        :class="{ 'sidebar-item--active': activePath === item.path }"
        @click="handleClick(item.path)"
      >
        <span>{{ item.label }}</span>
      </div>
    </nav>
  </aside>
</template>

<style scoped>
.sidebar {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.sidebar-nav {
  padding: 12px 0;
}

.sidebar-item {
  padding: 10px 16px;
  cursor: pointer;
  font-size: 14px;
  color: #374151;
}

.sidebar-item:hover {
  background-color: #e5e7eb;
}

.sidebar-item--active {
  background-color: #111827;
  color: #f9fafb;
}
</style>


