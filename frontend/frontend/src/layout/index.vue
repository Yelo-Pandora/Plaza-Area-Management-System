<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import Navbar from './components/Navbar.vue'
import Sidebar from './components/Sidebar.vue'
import AppMain from './components/AppMain.vue'

const router = useRouter()

const projectName = '广场区域管理系统'
const username = ref('')

onMounted(() => {
  username.value = localStorage.getItem('auth_user') || ''
})

function handleLogout() {
  localStorage.removeItem('auth_user')
  username.value = ''
  router.push({ name: 'Login' })
}
</script>

<template>
  <div class="layout-container">
    <Navbar :project-name="projectName" :username="username" @logout="handleLogout" />
    <div class="layout-body">
      <Sidebar class="layout-sidebar" />
      <AppMain class="layout-main" />
    </div>
  </div>
</template>

<style scoped>
.layout-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
}

.layout-body {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.layout-sidebar {
  width: 220px;
  border-right: 1px solid #e5e7eb;
  background-color: #f9fafb;
}

.layout-main {
  flex: 1;
  overflow: auto;
  background-color: #ffffff;
}
</style>


