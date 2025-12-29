import { ref, readonly } from 'vue'
import { adminLogin, adminLogout, getAdminProfile } from '@/api/management'

// 这里的状态在模块被多次 import 时是共享的（单例模式）
const user = ref(JSON.parse(localStorage.getItem('auth_user_info') || 'null'))
const isAuthenticated = ref(!!user.value)

export function useAuthStore() {

  const login = async (credentials) => {
    // credentials 格式: { account, password }
    const data = await adminLogin(credentials)
    // 后端成功返回 AdminProfileSerializer 数据: { id, account, name }
    user.value = data
    isAuthenticated.value = true
    localStorage.setItem('auth_user_info', JSON.stringify(data))
    return data
  }

  const logout = async () => {
    try {
      await adminLogout()
    } finally {
      // 必须确保这两行被执行，且变量是上面定义的全局响应式变量
      user.value = null
      isAuthenticated.value = false
      localStorage.removeItem('auth_user_info')
      localStorage.clear() // 清理所有可能的缓存
    }
  }

  const fetchProfile = async () => {
    try {
      const data = await getAdminProfile()
      user.value = data
      isAuthenticated.value = true
    } catch (error) {
      if (error.status === 401) logout()
    }
  }

  return {
    user: readonly(user),
    isAuthenticated: readonly(isAuthenticated),
    login,
    logout,
    fetchProfile
  }
}
