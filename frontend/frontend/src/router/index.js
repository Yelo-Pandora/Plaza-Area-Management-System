import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/views/login&register/useAuthStore'

// 懒加载页面视图
const LoginView = () => import('../views/login&register/Login.vue')
const Layout = () => import('../layout/index.vue')
const MapEditorView = () => import('../views/map-editor/index.vue')
const EventManagementView = () => import('../views/event-management/index.vue')
const AreaManagementView = () => import('../views/area-management/index.vue')
const FacilityManagementView = () => import('../views/facility-management/index.vue')

function isAuthenticated() {
  return !!localStorage.getItem('auth_user')
}

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'Login',
      component: LoginView
    },
    {
      path: '/',
      component: Layout,
      children: [
        {
          path: '',
          redirect: '/map-editor'
        },
        {
          path: '/map-editor',
          name: 'MapEditor',
          component: MapEditorView
        },
        {
          path: '/event-management',
          name: 'EventManagement',
          component: EventManagementView
        },
        {
          path: '/area-management',
          name: 'AreaManagement',
          component: AreaManagementView
        },
        {
          path: '/facility-management',
          name: 'FacilityManagement',
          component: FacilityManagementView
        }
      ]
    }
  ]
})

// 路由守卫：未登录只能访问 /login
router.beforeEach((to, from, next) => {
  const { isAuthenticated } = useAuthStore()

  // 1. 如果去的是登录页，直接放行
  if (to.name === 'Login') {
    if (isAuthenticated.value) {
      next('/')
    } else {
      next()
    }
    return
  }

  // 2. 访问其他页面，未登录则强制去登录页
  if (!isAuthenticated.value) {
    next({ name: 'Login' })
  } else {
    next()
  }
})

export default router


