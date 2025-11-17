<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'
import { ref, onMounted, watch } from 'vue'
import { authService, type User } from '@/services/auth'

const route = useRoute()
const router = useRouter()

const currentUser = ref<User | null>(null)
const isAuthenticated = ref(false)
const isLoggingOut = ref(false)

// Check auth status
async function checkAuth() {
  const authStatus = await authService.checkAuth()
  isAuthenticated.value = authStatus.authenticated
  currentUser.value = authStatus.user || null
}

// Get Zeus avatar URL from user data
function getAvatarUrl(user: User | null): string | null {
  if (user) {
    // Use picture URL from Zeus if available
    return user.picture || null
  }
  return null
}

// Logout handler
async function handleLogout() {
  if (isLoggingOut.value) return
  
  isLoggingOut.value = true
  const success = await authService.logout()
  
  if (success) {
    currentUser.value = null
    isAuthenticated.value = false
    // Redirect to home after logout
    router.push('/')
  }
  
  isLoggingOut.value = false
}

// Login handler
function handleLogin() {
  authService.login()
}

// Check auth on mount and when route changes
onMounted(() => {
  checkAuth()
})

watch(() => route.query.login, (newValue) => {
  if (newValue === 'success') {
    checkAuth()
  }
})
</script>

<template>
  <div class="app">
    <!-- Navigation Header -->
    <header class="nav-header">
      <h1 class="app-title">Vibe App</h1>
      
      <nav class="nav-menu">
        <router-link 
          to="/" 
          :class="{ active: route.name === 'Home' }"
          class="nav-btn"
        >
          Home
        </router-link>
        <router-link 
          to="/leaderboard" 
          :class="{ active: route.name === 'Leaderboard' }"
          class="nav-btn"
        >
          Leaderboard
        </router-link>
        <router-link 
          to="/solve"
          :class="{ active: route.name === 'Solve' }"
          class="nav-btn"
        >
          Solver
        </router-link>
        <router-link 
          v-if="isAuthenticated && (currentUser?.username === 'tyboro' || currentUser?.username === 'runo')"
          to="/admin"
          :class="{ active: route.name === 'Admin' }"
          class="nav-btn admin-btn"
        >
          🔧 Admin
        </router-link>
      </nav>

      <!-- User Info / Auth Section -->
      <div class="auth-section">
        <div v-if="isAuthenticated && currentUser" class="user-info">
          <div class="user-badge">
            <div class="user-icon">
              <img 
                v-if="getAvatarUrl(currentUser)" 
                :src="getAvatarUrl(currentUser)!" 
                :alt="currentUser.username" 
                class="user-avatar-img"
              />
              <span v-else>👤</span>
            </div>
            <div class="user-details">
              <span class="user-name">{{ currentUser.name || currentUser.username }}</span>
              <span class="user-username">@{{ currentUser.username }}</span>
            </div>
          </div>
          <button 
            @click="handleLogout" 
            :disabled="isLoggingOut"
            class="logout-btn"
          >
            <span v-if="isLoggingOut">Logging out...</span>
            <span v-else>🚪 Logout</span>
          </button>
        </div>
        <button 
          v-else 
          @click="handleLogin"
          class="login-btn"
        >
          🔐 Login
        </button>
      </div>
    </header>

    <!-- Main Content -->
    <main class="main-content">
      <router-view />
    </main>
  </div>
</template>

<style scoped>
.app {
  background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
  color: white;
}

.nav-header {
  background: rgba(0, 0, 0, 0.2);
  backdrop-filter: blur(10px);
  padding: 1rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  gap: 2rem;
  flex-wrap: wrap;
}

.app-title {
  margin: 0;
  font-size: 1.8rem;
  font-weight: bold;
  background: linear-gradient(45deg, #fff, #e0f0ff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.nav-menu {
  display: flex;
  gap: 1rem;
}

.nav-btn {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: 500;
  text-decoration: none;
  display: block;
}

.nav-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: translateY(-2px);
}

.nav-btn.active {
  background: rgba(255, 255, 255, 0.3);
  border-color: rgba(255, 255, 255, 0.5);
}

.nav-btn.admin-btn {
  background: linear-gradient(45deg, #ff6b6b, #ffa500);
  border-color: rgba(255, 165, 0, 0.5);
}

.nav-btn.admin-btn:hover {
  background: linear-gradient(45deg, #ff5252, #ff8c00);
}

.auth-section {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.user-badge {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 10px;
  padding: 0.5rem 1rem;
}

.user-icon {
  font-size: 1.3rem;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 35px;
  height: 35px;
  background: rgba(79, 172, 254, 0.3);
  border-radius: 50%;
  overflow: hidden;
  flex-shrink: 0;
}

.user-avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 50%;
}

.user-details {
  display: flex;
  flex-direction: column;
  gap: 0.1rem;
}

.user-name {
  color: white;
  font-weight: 600;
  font-size: 0.9rem;
  line-height: 1.2;
}

.user-username {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.75rem;
  line-height: 1.2;
}

.logout-btn {
  background: linear-gradient(45deg, #ff6b6b, #ee5a52);
  color: white;
  border: none;
  padding: 0.6rem 1.2rem;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.9rem;
  white-space: nowrap;
}

.logout-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(255, 107, 107, 0.4);
}

.logout-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.login-btn {
  background: linear-gradient(45deg, #4facfe, #00f2fe);
  color: white;
  border: none;
  padding: 0.6rem 1.5rem;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.9rem;
  white-space: nowrap;
}

.login-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(79, 172, 254, 0.4);
}

/* Responsive styles */
@media (max-width: 1024px) {
  .nav-header {
    flex-direction: column;
    gap: 1rem;
    padding: 1rem;
  }

  .app-title {
    font-size: 1.5rem;
  }

  .nav-menu {
    width: 100%;
    justify-content: center;
  }

  .auth-section {
    width: 100%;
    justify-content: center;
  }
}

@media (max-width: 768px) {
  .nav-menu {
    flex-direction: column;
    width: 100%;
  }

  .nav-btn {
    text-align: center;
  }

  .user-badge {
    padding: 0.4rem 0.8rem;
  }

  .user-icon {
    width: 30px;
    height: 30px;
    font-size: 1.1rem;
  }

  .user-name {
    font-size: 0.85rem;
  }

  .user-username {
    font-size: 0.7rem;
  }

  .logout-btn,
  .login-btn {
    padding: 0.5rem 1rem;
    font-size: 0.85rem;
  }
}

@media (max-width: 480px) {
  .user-info {
    flex-direction: column;
    width: 100%;
  }

  .user-badge {
    width: 100%;
    justify-content: center;
  }

  .logout-btn {
    width: 100%;
  }
}
</style>
