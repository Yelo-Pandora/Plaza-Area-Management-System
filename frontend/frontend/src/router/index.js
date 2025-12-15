import { createRouter, createWebHistory } from 'vue-router'

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

// 简单路由守卫：未登录只能访问 /login
router.beforeEach((to, from, next) => {
  if (to.name === 'Login') {
    if (isAuthenticated()) {
      next({ path: '/' })
    } else {
      next()
    }
    return
  }

  if (!isAuthenticated()) {
    next({ name: 'Login', query: { redirect: to.fullPath } })
  } else {
    next()
  }
})

export default router


