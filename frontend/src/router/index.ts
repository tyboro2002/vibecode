import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Leaderboard from '../views/Leaderboard.vue'
import Solve from '../views/solve.vue'
import Admin from '../views/Admin.vue'
import { authService } from '@/services/auth'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/leaderboard',
    name: 'Leaderboard',
    component: Leaderboard
  },
  {
    path: '/solve',
    name: 'Solve',
    component: Solve,
    meta: { requiresAuth: true }
  },
  {
    path: '/admin',
    name: 'Admin',
    component: Admin,
    meta: { requiresAuth: true, requiresAdmin: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Global navigation guard for authentication
router.beforeEach(async (to, _from, next) => {
  // Check if route requires authentication
  if (to.meta.requiresAuth) {
    // Use cached auth check (won't make a request if cache is fresh)
    const authStatus = await authService.checkAuth()
    
    if (!authStatus.authenticated) {
      // Store the intended destination
      sessionStorage.setItem('loginReturnUrl', to.fullPath)
      // Redirect to login
      authService.login()
      return
    }

    // Check if route requires admin access (tyboro or runo)
    if (to.meta.requiresAdmin) {
      const username = authStatus.user?.username
      if (!['tyboro', 'runo'].includes(username ?? '')) {
        // Redirect to home if not tyboro or runo
        next('/')
        return
      }
    }
  }
  
  next()
})

export default router