<script setup lang="ts">
import { ref, onMounted } from 'vue'

interface LeaderboardEntry {
  rank: number
  name: string
  score: number
  avatar: string
}

const leaderboardData = ref<LeaderboardEntry[]>([])
const isLoading = ref(true)
const errorMessage = ref('')

const fetchLeaderboard = async () => {
  try {
    isLoading.value = true
    errorMessage.value = ''
    
    const response = await fetch('http://localhost:8000/api/leaderboard/')
    const data = await response.json()
    
    if (data.success) {
      leaderboardData.value = data.leaderboard
    } else {
      errorMessage.value = data.error || 'Failed to load leaderboard data'
    }
  } catch (error) {
    errorMessage.value = 'Failed to connect to the backend. Make sure the server is running.'
    console.error('Error fetching leaderboard:', error)
  } finally {
    isLoading.value = false
  }
}

// Fetch data when component mounts
onMounted(fetchLeaderboard)
</script>

<template>
  <div class="leaderboard-container">
    <div class="leaderboard-content">
      <div class="header-section">
        <h1 class="page-title">🏆 Leaderboard</h1>
        <p class="page-subtitle">Top performers from our database</p>
        <button @click="fetchLeaderboard" :disabled="isLoading" class="refresh-btn">
          <span v-if="isLoading">🔄 Loading...</span>
          <span v-else>🔄 Refresh</span>
        </button>
      </div>

      <!-- Error Message -->
      <div v-if="errorMessage" class="error-message">
        ⚠️ {{ errorMessage }}
      </div>

      <!-- Loading State -->
      <div v-if="isLoading && !errorMessage" class="loading-container">
        <div class="loading-spinner">
          🔄 Loading leaderboard data...
        </div>
      </div>

      <!-- Leaderboard Content -->
      <div v-else-if="leaderboardData.length > 0">
        <!-- Top 3 Podium -->
        <div class="podium-section">
          <div class="podium">
            <!-- Second Place -->
            <div v-if="leaderboardData[1]" class="podium-item second-place">
              <div class="avatar">{{ leaderboardData[1].avatar }}</div>
              <div class="rank-badge silver">2</div>
              <h3>{{ leaderboardData[1].name }}</h3>
              <p class="score">{{ leaderboardData[1].score.toLocaleString() }}</p>
            </div>
            
            <!-- First Place -->
            <div v-if="leaderboardData[0]" class="podium-item first-place">
              <div class="avatar">{{ leaderboardData[0].avatar }}</div>
              <div class="rank-badge gold">1</div>
              <h3>{{ leaderboardData[0].name }}</h3>
              <p class="score">{{ leaderboardData[0].score.toLocaleString() }}</p>
              <div class="crown">👑</div>
            </div>
            
            <!-- Third Place -->
            <div v-if="leaderboardData[2]" class="podium-item third-place">
              <div class="avatar">{{ leaderboardData[2].avatar }}</div>
              <div class="rank-badge bronze">3</div>
              <h3>{{ leaderboardData[2].name }}</h3>
              <p class="score">{{ leaderboardData[2].score.toLocaleString() }}</p>
            </div>
          </div>
        </div>

        <!-- Rest of Leaderboard -->
        <div class="leaderboard-list" v-if="leaderboardData.length > 3">
          <div class="list-header">
            <span>Rank</span>
            <span>Player</span>
            <span>Score</span>
          </div>
          
          <div 
            v-for="player in leaderboardData.slice(3)" 
            :key="player.rank"
            class="list-item"
          >
            <div class="rank-col">
              <span class="rank-number">{{ player.rank }}</span>
            </div>
            <div class="player-col">
              <span class="player-avatar">{{ player.avatar }}</span>
              <span class="player-name">{{ player.name }}</span>
            </div>
            <div class="score-col">
              <span class="player-score">{{ player.score.toLocaleString() }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else-if="!isLoading" class="empty-state">
        <h2>📊 No Data Available</h2>
        <p>No leaderboard entries found. Try refreshing or contact an administrator.</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.leaderboard-container {
  min-height: calc(100vh - 100px);
  padding: 2rem;
  overflow-y: auto;
}

.leaderboard-content {
  max-width: 1200px;
  margin: 0 auto;
}

.header-section {
  text-align: center;
  margin-bottom: 3rem;
}

.page-title {
  font-size: 3rem;
  font-weight: bold;
  color: white;
  margin: 0 0 0.5rem 0;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.page-subtitle {
  font-size: 1.2rem;
  color: rgba(255, 255, 255, 0.8);
  margin: 0 0 1rem 0;
}

.refresh-btn {
  background: linear-gradient(45deg, #4facfe, #00f2fe);
  color: white;
  border: none;
  padding: 0.8rem 1.5rem;
  border-radius: 10px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-top: 1rem;
}

.refresh-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(79, 172, 254, 0.3);
}

.refresh-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.error-message {
  background: rgba(255, 107, 107, 0.2);
  border: 1px solid rgba(255, 107, 107, 0.5);
  color: #ff6b6b;
  padding: 1rem;
  border-radius: 12px;
  margin-bottom: 2rem;
  text-align: center;
  font-weight: 500;
}

.loading-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 300px;
}

.loading-spinner {
  font-size: 1.5rem;
  color: #4facfe;
  animation: pulse 2s infinite;
}

.empty-state {
  text-align: center;
  padding: 4rem 2rem;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.empty-state h2 {
  color: white;
  margin-bottom: 1rem;
}

.empty-state p {
  color: rgba(255, 255, 255, 0.8);
}

/* Podium Section */
.podium-section {
  margin-bottom: 3rem;
}

.podium {
  display: flex;
  justify-content: center;
  align-items: end;
  gap: 1rem;
  margin-bottom: 2rem;
}

.podium-item {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  padding: 2rem 1.5rem;
  text-align: center;
  border: 2px solid rgba(255, 255, 255, 0.2);
  position: relative;
  transition: all 0.3s ease;
  min-width: 180px;
}

.podium-item:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
}

.first-place {
  order: 2;
  margin-top: -20px;
  border-color: #FFD700;
  background: linear-gradient(135deg, rgba(255, 215, 0, 0.2), rgba(255, 255, 255, 0.1));
}

.second-place {
  order: 1;
  border-color: #C0C0C0;
  background: linear-gradient(135deg, rgba(192, 192, 192, 0.2), rgba(255, 255, 255, 0.1));
}

.third-place {
  order: 3;
  border-color: #CD7F32;
  background: linear-gradient(135deg, rgba(205, 127, 50, 0.2), rgba(255, 255, 255, 0.1));
}

.avatar {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.rank-badge {
  position: absolute;
  top: -10px;
  right: -10px;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 1.2rem;
  border: 3px solid white;
}

.rank-badge.gold {
  background: linear-gradient(135deg, #FFD700, #FFA500);
  color: #333;
}

.rank-badge.silver {
  background: linear-gradient(135deg, #C0C0C0, #A0A0A0);
  color: #333;
}

.rank-badge.bronze {
  background: linear-gradient(135deg, #CD7F32, #8B4513);
  color: white;
}

.crown {
  position: absolute;
  top: -25px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 2rem;
  animation: bounce 2s infinite;
}

@keyframes bounce {
  0%, 20%, 50%, 80%, 100% {
    transform: translateX(-50%) translateY(0);
  }
  40% {
    transform: translateX(-50%) translateY(-10px);
  }
  60% {
    transform: translateX(-50%) translateY(-5px);
  }
}

.podium-item h3 {
  color: white;
  margin: 0.5rem 0;
  font-size: 1.3rem;
  font-weight: 600;
}

.podium-item .score {
  color: #4facfe;
  font-size: 1.4rem;
  font-weight: bold;
  margin: 0;
}

/* Leaderboard List */
.leaderboard-list {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.list-header {
  display: grid;
  grid-template-columns: 80px 1fr 120px;
  background: rgba(0, 0, 0, 0.3);
  padding: 1.5rem;
  font-weight: bold;
  font-size: 1.1rem;
  color: white;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.list-item {
  display: grid;
  grid-template-columns: 80px 1fr 120px;
  padding: 1.2rem 1.5rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  transition: all 0.3s ease;
  color: white;
}

.list-item:hover {
  background: rgba(255, 255, 255, 0.1);
}

.list-item:last-child {
  border-bottom: none;
}

.rank-col {
  display: flex;
  align-items: center;
  justify-content: center;
}

.rank-number {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  width: 35px;
  height: 35px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 1rem;
}

.player-col {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.player-avatar {
  font-size: 1.8rem;
}

.player-name {
  font-weight: 500;
  font-size: 1.1rem;
}

.score-col {
  display: flex;
  align-items: center;
  justify-content: flex-end;
}

.player-score {
  color: #4facfe;
  font-weight: bold;
  font-size: 1.1rem;
}

/* Responsive Design */
@media (max-width: 1024px) {
  .leaderboard-container {
    padding: 1.5rem;
  }
  
  .podium {
    flex-direction: column;
    align-items: center;
  }
  
  .first-place,
  .second-place,
  .third-place {
    order: initial;
    margin-top: 0;
    margin-bottom: 1rem;
  }
  
  .podium-item {
    min-width: 250px;
  }
}

@media (max-width: 768px) {
  .leaderboard-container {
    padding: 1rem;
  }
  
  .page-title {
    font-size: 2.5rem;
  }
  
  .podium-item {
    padding: 1.5rem 1rem;
    min-width: 200px;
  }
  
  .list-header,
  .list-item {
    grid-template-columns: 60px 1fr 100px;
    padding: 1rem;
  }
  
  .player-name {
    font-size: 1rem;
  }
  
  .player-score {
    font-size: 1rem;
  }
}

@media (max-width: 480px) {
  .header-section {
    margin-bottom: 2rem;
  }
  
  .podium-section {
    margin-bottom: 2rem;
  }
  
  .podium-item {
    min-width: 160px;
    padding: 1rem;
  }
  
  .avatar {
    font-size: 2.5rem;
  }
  
  .podium-item h3 {
    font-size: 1.1rem;
  }
  
  .podium-item .score {
    font-size: 1.2rem;
  }
}
</style>