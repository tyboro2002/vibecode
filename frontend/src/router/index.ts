import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Leaderboard from '../views/Leaderboard.vue'
import Other from '../views/Other.vue'

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
    path: '/other',
    name: 'Other',
    component: Other
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router