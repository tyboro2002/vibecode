<script setup lang="ts">
import { ref, onMounted } from 'vue'

interface LeaderboardEntry {
  id: number
  rank: number
  name: string
  score: number
  avatar?: string  // Emoji fallback
  avatar_url?: string  // Zeus profile picture URL
}

interface SolvedProblem {
  id: number
  name: string
  points: number
}

interface UserSolvedData {
  user_name: string
  total_score: number
  solved_problems: SolvedProblem[]
  total_points_from_problems: number
  problems_solved_count: number
}

const leaderboardData = ref<LeaderboardEntry[]>([])
const isLoading = ref(true)
const errorMessage = ref('')
const showModal = ref(false)
const modalLoading = ref(false)
const selectedUserData = ref<UserSolvedData | null>(null)

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

const fetchUserSolvedProblems = async (userId: number, userName: string) => {
  try {
    modalLoading.value = true
    showModal.value = true
    selectedUserData.value = null
    
    const response = await fetch(`http://localhost:8000/api/users/${userId}/solved-problems/`)
    const data = await response.json()
    
    if (data.success) {
      selectedUserData.value = data
    } else {
      console.error('Failed to load user solved problems:', data.error)
      selectedUserData.value = {
        user_name: userName,
        total_score: 0,
        solved_problems: [],
        total_points_from_problems: 0,
        problems_solved_count: 0
      }
    }
  } catch (error) {
    console.error('Error fetching user solved problems:', error)
    selectedUserData.value = {
      user_name: userName,
      total_score: 0,
      solved_problems: [],
      total_points_from_problems: 0,
      problems_solved_count: 0
    }
  } finally {
    modalLoading.value = false
  }
}

const closeModal = () => {
  showModal.value = false
  selectedUserData.value = null
}
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
              <div class="avatar">
                <img v-if="leaderboardData[1].avatar_url" :src="leaderboardData[1].avatar_url" :alt="leaderboardData[1].name" class="avatar-img" />
                <span v-else>{{ leaderboardData[1].avatar }}</span>
              </div>
              <div class="rank-badge silver">2</div>
              <h3 class="clickable-name" @click="fetchUserSolvedProblems(leaderboardData[1].id, leaderboardData[1].name)">{{ leaderboardData[1].name }}</h3>
              <p class="score">{{ leaderboardData[1].score.toLocaleString() }}</p>
            </div>
            
            <!-- First Place -->
            <div v-if="leaderboardData[0]" class="podium-item first-place">
              <div class="avatar">
                <img v-if="leaderboardData[0].avatar_url" :src="leaderboardData[0].avatar_url" :alt="leaderboardData[0].name" class="avatar-img" />
                <span v-else>{{ leaderboardData[0].avatar }}</span>
              </div>
              <div class="rank-badge gold">1</div>
              <h3 class="clickable-name" @click="fetchUserSolvedProblems(leaderboardData[0].id, leaderboardData[0].name)">{{ leaderboardData[0].name }}</h3>
              <p class="score">{{ leaderboardData[0].score.toLocaleString() }}</p>
              <div class="crown">👑</div>
            </div>
            
            <!-- Third Place -->
            <div v-if="leaderboardData[2]" class="podium-item third-place">
              <div class="avatar">
                <img v-if="leaderboardData[2].avatar_url" :src="leaderboardData[2].avatar_url" :alt="leaderboardData[2].name" class="avatar-img" />
                <span v-else>{{ leaderboardData[2].avatar }}</span>
              </div>
              <div class="rank-badge bronze">3</div>
              <h3 class="clickable-name" @click="fetchUserSolvedProblems(leaderboardData[2].id, leaderboardData[2].name)">{{ leaderboardData[2].name }}</h3>
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
              <span class="player-avatar">
                <img v-if="player.avatar_url" :src="player.avatar_url" :alt="player.name" class="avatar-img-small" />
                <span v-else>{{ player.avatar }}</span>
              </span>
              <span class="player-name clickable-name" @click="fetchUserSolvedProblems(player.id, player.name)">{{ player.name }}</span>
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

    <!-- Modal for User's Solved Problems -->
    <div v-if="showModal" class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2>🏆 {{ selectedUserData?.user_name || 'User' }}'s Solved Problems</h2>
          <button class="close-btn" @click="closeModal">✕</button>
        </div>
        
        <div v-if="modalLoading" class="modal-loading">
          <div class="loading-spinner">🔄 Loading...</div>
        </div>
        
        <div v-else-if="selectedUserData" class="modal-body">
          <div class="stats-summary">
            <div class="stat-card">
              <div class="stat-value">{{ selectedUserData.problems_solved_count }}</div>
              <div class="stat-label">Problems Solved</div>
            </div>
            <div class="stat-card">
              <div class="stat-value">{{ selectedUserData.total_points_from_problems }}</div>
              <div class="stat-label">Points Earned</div>
            </div>
            <div class="stat-card">
              <div class="stat-value">{{ selectedUserData.total_score }}</div>
              <div class="stat-label">Total Score</div>
            </div>
          </div>
          
          <div v-if="selectedUserData.solved_problems.length > 0" class="problems-list">
            <h3>Solved Problems:</h3>
            <div v-for="problem in selectedUserData.solved_problems" :key="problem.id" class="problem-item">
              <span class="problem-name">{{ problem.name }}</span>
              <span class="problem-points">{{ problem.points }} pts</span>
            </div>
          </div>
          
          <div v-else class="no-problems">
            <p>No problems solved yet. Keep practicing! 💪</p>
          </div>
        </div>
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
  width: 80px;
  height: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 1rem auto;
}

.avatar-img {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  object-fit: cover;
  border: 3px solid rgba(255, 255, 255, 0.3);
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
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
}

.avatar-img-small {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid rgba(255, 255, 255, 0.3);
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

.clickable-name {
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
}

.clickable-name:hover {
  color: #4facfe;
  text-decoration: underline;
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(5px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.2s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.modal-content {
  background: linear-gradient(135deg, rgba(30, 30, 60, 0.95), rgba(20, 20, 40, 0.95));
  border-radius: 20px;
  padding: 2rem;
  max-width: 600px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
  border: 2px solid rgba(79, 172, 254, 0.3);
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
  animation: slideUp 0.3s ease;
}

@keyframes slideUp {
  from {
    transform: translateY(50px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 2px solid rgba(255, 255, 255, 0.1);
}

.modal-header h2 {
  color: white;
  margin: 0;
  font-size: 1.5rem;
}

.close-btn {
  background: rgba(255, 107, 107, 0.2);
  border: 1px solid rgba(255, 107, 107, 0.5);
  color: #ff6b6b;
  width: 35px;
  height: 35px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 1.2rem;
  transition: all 0.2s ease;
}

.close-btn:hover {
  background: rgba(255, 107, 107, 0.3);
  transform: scale(1.1);
}

.modal-loading {
  text-align: center;
  padding: 3rem;
  color: #4facfe;
  font-size: 1.2rem;
}

.modal-body {
  color: white;
}

.stats-summary {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 1rem;
  text-align: center;
}

.stat-value {
  font-size: 2rem;
  font-weight: bold;
  color: #4facfe;
  margin-bottom: 0.5rem;
}

.stat-label {
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.7);
}

.problems-list h3 {
  color: white;
  margin-bottom: 1rem;
  font-size: 1.2rem;
}

.problem-item {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  padding: 0.75rem 1rem;
  margin-bottom: 0.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  transition: all 0.2s ease;
}

.problem-item:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(79, 172, 254, 0.3);
}

.problem-name {
  color: rgba(255, 255, 255, 0.9);
  font-size: 0.95rem;
  flex: 1;
}

.problem-points {
  color: #43e97b;
  font-weight: bold;
  background: rgba(67, 233, 123, 0.2);
  padding: 0.25rem 0.75rem;
  border-radius: 999px;
  font-size: 0.85rem;
}

.no-problems {
  text-align: center;
  padding: 2rem;
  color: rgba(255, 255, 255, 0.6);
  font-style: italic;
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

  .stats-summary {
    grid-template-columns: 1fr;
    gap: 0.75rem;
  }

  .modal-content {
    width: 95%;
    padding: 1.5rem;
  }

  .modal-header h2 {
    font-size: 1.2rem;
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