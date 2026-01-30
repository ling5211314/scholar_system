import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  {
    path: '/',
    name: 'Chat',
    component: () => import('@/views/Chat.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/Register.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/navigator',
    name: 'Navigator',
    component: () => import('@/views/Navigator.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/papers',
    name: 'Papers',
    component: () => import('@/views/Papers.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/login'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()

  // 如果需要认证但未登录，跳转到登录页
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/login')
  }
  // 如果已登录但访问登录/注册页，跳转到首页
  else if ((to.name === 'Login' || to.name === 'Register') && authStore.isAuthenticated) {
    next('/')
  }
  // 其他情况正常跳转
  else {
    next()
  }
})

export default router
