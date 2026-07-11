import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { public: true }
  },
  {
    path: '/share/:code',
    name: 'Share',
    component: () => import('@/views/Share.vue'),
    meta: { public: true }
  },
  // 管理员路由
  {
    path: '/admin',
    component: () => import('@/layout/AdminLayout.vue'),
    redirect: '/admin/dashboard',
    meta: { requiresAdmin: true },
    children: [
      { path: 'dashboard', name: 'AdminDashboard', component: () => import('@/views/AdminDashboard.vue') },
      { path: 'trips', name: 'AdminTrips', component: () => import('@/views/AdminTrips.vue') },
      { path: 'users', name: 'AdminUsers', component: () => import('@/views/Users.vue') },
      { path: 'resources', name: 'AdminResources', component: () => import('@/views/Resources.vue') },
      { path: 'templates', name: 'AdminTemplates', component: () => import('@/views/Templates.vue') },
      { path: 'reviews', name: 'AdminReviews', component: () => import('@/views/AdminReviews.vue') }
    ]
  },
  // 普通用户路由
  {
    path: '/',
    component: () => import('@/layout/AppLayout.vue'),
    redirect: '/dashboard',
    meta: { requiresPlanner: true },
    children: [
      { path: 'dashboard', name: 'Dashboard', component: () => import('@/views/Dashboard.vue') },
      { path: 'trips', name: 'Trips', component: () => import('@/views/trips/TripList.vue') },
      { path: 'trips/:id', name: 'TripDetail', component: () => import('@/views/trips/TripDetail.vue') },
      { path: 'templates', name: 'Templates', component: () => import('@/views/Templates.vue') },
      { path: 'ai', name: 'AI', component: () => import('@/views/AI.vue') }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach(async (to, from, next) => {
  // 公开页面直接放行
  if (to.meta.public) return next()

  const token = localStorage.getItem('token')
  if (!token) return next('/login')

  // 需要获取用户信息来判断角色
  const userStore = useUserStore()
  if (!userStore.user) {
    await userStore.fetchUser()
  }

  // 获取用户失败（token 无效等）
  if (!userStore.user) {
    return next('/login')
  }

  const isAdmin = userStore.isAdmin

  // 管理员访问普通用户页面 -> 重定向到管理后台
  if (to.matched.some(r => r.meta.requiresPlanner) && isAdmin) {
    return next('/admin')
  }

  // 普通用户访问管理员页面 -> 重定向到用户首页
  if (to.matched.some(r => r.meta.requiresAdmin) && !isAdmin) {
    return next('/dashboard')
  }

  next()
})

export default router
