<script setup lang="ts">
import { useRoute } from 'vue-router'

const route = useRoute()
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
          to="/other" 
          :class="{ active: route.name === 'Other' }"
          class="nav-btn"
        >
          Other Page
        </router-link>
      </nav>
    </header>

    <!-- Main Content -->
    <main class="main-content">
      <router-view />
    </main>
  </div>
</template>

<style scoped>
.app {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
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
}

.app-title {
  margin: 0;
  font-size: 1.8rem;
  font-weight: bold;
  background: linear-gradient(45deg, #fff, #f0f0ff);
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
</style>
