<template>
  <div class="home-view">
    <div class="welcome-card">
      <h2>Welcome to Vibe App</h2>
      <p>Choose where you'd like to go:</p>
      <div class="action-buttons">
        <router-link to="/leaderboard" class="action-btn primary">
          📊 View Leaderboard
        </router-link>
        <router-link to="/solve" class="action-btn secondary">
          🎯 Go to Solve Page
        </router-link>
      </div>
    </div>
  </div>
</template>

<style scoped>
.home-view {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  height: 80vh;
  padding-top: 4rem;
}

.welcome-card {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  padding: 3rem;
  text-align: center;
  border: 1px solid rgba(255, 255, 255, 0.2);
  width: 100%;
}

.welcome-card h2 {
  margin: 0 0 1rem 0;
  font-size: 2.5rem;
  font-weight: bold;
  color: white;
}

.welcome-card p {
  margin: 0 0 2rem 0;
  font-size: 1.2rem;
  opacity: 0.9;
  color: white;
}

.action-buttons {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.action-btn {
  padding: 1rem 2rem;
  border: none;
  border-radius: 12px;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  text-align: center;
  text-decoration: none;
  display: block;
}

.action-btn.primary {
  background: linear-gradient(45deg, #4facfe, #00f2fe);
  color: white;
}

.action-btn.secondary {
  background: linear-gradient(45deg, #fa709a, #fee140);
  color: white;
}

.action-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2);
}

@media (max-width: 768px) {
  .welcome-card {
    padding: 2rem;
    margin: 1rem;
  }
  
  .action-buttons {
    gap: 0.8rem;
  }
}
</style>