<template>
  <div class="auth-container">
    <!-- Show loading state -->
    <div v-if="loading" class="loading">
      Checking authentication...
    </div>

    <!-- Show login button if not authenticated -->
    <div v-else-if="!authenticated" class="login-section">
      <h2>Login Required</h2>
      <p>Please login with your Zeus account to continue</p>
      <button @click="handleLogin" class="login-button">
        Login with Zeus
      </button>
    </div>

    <!-- Show user info if authenticated -->
    <div v-else class="user-section">
      <div class="user-info">
        <div class="user-badge">
          <div class="user-avatar">
            <img 
              v-if="user?.picture" 
              :src="user.picture" 
              :alt="user.username" 
              class="avatar-img"
            />
            <span v-else>👤</span>
          </div>
          <span class="user-name">{{ user?.name || user?.username }}</span>
        </div>
        <button @click="handleLogout" class="logout-button">
          Logout
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { authService, type User } from '@/services/auth';

const authenticated = ref(false);
const loading = ref(true);
const user = ref<User | null>(null);

async function checkAuth() {
  loading.value = true;
  try {
    const response = await authService.checkAuth();
    authenticated.value = response.authenticated;
    user.value = response.user || null;
  } catch (error) {
    console.error('Failed to check auth:', error);
    authenticated.value = false;
  } finally {
    loading.value = false;
  }
}

function handleLogin() {
  authService.login();
}

async function handleLogout() {
  const success = await authService.logout();
  if (success) {
    authenticated.value = false;
    user.value = null;
  }
}

onMounted(() => {
  checkAuth();
});
</script>

<style scoped>
.auth-container {
  padding: 1rem;
}

.loading {
  text-align: center;
  padding: 2rem;
  color: #666;
}

.login-section {
  text-align: center;
  padding: 2rem;
  background: #f5f5f5;
  border-radius: 8px;
}

.login-section h2 {
  margin-bottom: 1rem;
  color: #333;
}

.login-section p {
  margin-bottom: 1.5rem;
  color: #666;
}

.login-button {
  background: #007bff;
  color: white;
  padding: 0.75rem 2rem;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  transition: background 0.2s;
}

.login-button:hover {
  background: #0056b3;
}

.user-section {
  padding: 1rem;
}

.user-info {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: white;
  padding: 1rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.user-badge {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.user-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f0f0f0;
  flex-shrink: 0;
}

.avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.user-name {
  font-weight: 500;
  color: #333;
}

.logout-button {
  background: #dc3545;
  color: white;
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.2s;
}

.logout-button:hover {
  background: #c82333;
}
</style>
