<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/views/login&register/useAuthStore'
import Navbar from './components/Navbar.vue'
import Sidebar from './components/Sidebar.vue'
import AppMain from './components/AppMain.vue'

const router = useRouter()
const { user, logout } = useAuthStore()

const projectName = '广场区域管理系统'
const username = ref('')

async function handleLogout() {
  if (confirm('确定要退出登录吗？')) {
    try {
      // 1. 调用注销接口
      await logout()
    } catch (error) {
      console.warn('后端注销请求失败，但我们将继续清理本地状态', error)
    } finally {
      // 2. 无论后端接口成功与否，强制跳转到登录页
      // 使用 replace 防止用户点击浏览器后退键回到系统
      router.replace('/login').then(() => {
        // 3. 额外保险：跳转后刷新一下页面，清除所有内存中的 Vue 状态
      window.location.href = '/login' // 强制浏览器重定向
      })
    }
  }
}
</script>

<template>
  <div class="layout-container">
    <Navbar
      :project-name="projectName"
      :username="user?.name || user?.account || '管理员'"
      @logout="handleLogout"
    />
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


