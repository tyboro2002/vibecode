<script setup lang="ts">
import {ref, onMounted} from 'vue'

const inputText = ref('')
const displayText = ref('Your processed text will appear here when you submit...')
const isLoading = ref(false)
const errorMessage = ref('')
const problems = ref([])

// Fetch the problems from the backend on component mount
onMounted(async () => {
  try {
    const response = await fetch('http://localhost:8000/api/problems/all', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
    })

    const data = await response.json()
    problems.value = data.problems || []
    // for dev
    // problems.value = [
    //   "The Jumbled Jumper",
    //   "Sortocalypse",
    //   "The Shuffle Shuffle",
    //   "Whack-a-Number",
    //   "The Mischief Sort",
    //   "Random Access Chaos",
    //   "The Out-of-Place Race",
    //   "Sort of Confused",
    //   "HodgePodge Heap",
    //   "Disorderly Conduct",
    //   "The Misplaced Parade",
    // ];

  } catch (error) {
    console.error('Error fetching problems:', error)
  }
})

// Submit function to send text to backend
const submitText = async () => {
  if (!inputText.value.trim()) {
    errorMessage.value = 'Please enter some text before submitting.'
    return
  }

  isLoading.value = true
  errorMessage.value = ''

  try {
    const response = await fetch('http://localhost:8000/api/submit/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include', // Include authentication cookies
      body: JSON.stringify({
        prompt: inputText.value,
        code: ""
      })
    })

    const data = await response.json()

    displayText.value = data.generated_code
  } catch (error) {
    errorMessage.value = 'Failed to connect to the backend. Make sure the server is running.'
    displayText.value = 'Connection error. Please check if the backend server is running.'
    console.error('Error:', error)
  } finally {
    isLoading.value = false
  }
}

// Clear function
const clearText = () => {
  inputText.value = ''
  displayText.value = 'Your processed text will appear here when you submit...'
  errorMessage.value = ''
}
</script>

<template>
  <div class="other-container">
    <div class="split-layout">
      <div>
        <li v-for="(problem, index) in problems" :key="index" class="left-list">
          <router-link
              style="color: white"
              :to="`/solve/${problem.id}`"
          >
            {{ problem.name }}
          </router-link>

          <span class="left-list-points">{{ problem.points }}</span>
        </li>
      </div>
      <!-- Left Side - Input Field -->
      <div class="input-section">
        <div class="input-card">
          <h2>✍️ Text Input</h2>
          <p>Type something and click submit to send it to the backend for processing!</p>

          <div v-if="errorMessage" class="error-message">
            ⚠️ {{ errorMessage }}
          </div>

          <div class="input-group">
            <label for="textInput" class="input-label">Enter your text:</label>
            <textarea
                id="textInput"
                v-model="inputText"
                class="text-input"
                placeholder="Start typing here..."
                rows="10"
            ></textarea>
          </div>

          <div class="input-controls">
            <button @click="submitText" :disabled="isLoading" class="submit-btn">
              <span v-if="isLoading">⏳ Processing...</span>
              <span v-else>📤 Submit Text</span>
            </button>
            <button @click="clearText" :disabled="isLoading" class="clear-btn">
              🗑️ Clear Text
            </button>
            <div class="char-count">
              Characters: {{ inputText.length }}
            </div>
          </div>

          <div class="quick-actions">
            <h3>Quick Insert:</h3>
            <div class="action-buttons">
              <button @click="inputText += 'Hello World! '" class="action-btn">
                👋 Hello
              </button>
              <button @click="inputText += 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. '"
                      class="action-btn">
                📝 Lorem
              </button>
              <button @click="inputText += '🎉🚀⭐💫 '" class="action-btn">
                ✨ Emojis
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Right Side - Text Display -->
      <div class="display-section">
        <div class="display-card">
          <h2>📄 Backend Response</h2>
          <p>Processed response from the backend</p>

          <div class="text-display">
            <div class="display-content" :class="{ 'loading': isLoading }">
              <div v-if="isLoading" class="loading-spinner">
                🔄 Processing your text...
              </div>
              <div v-else>
                {{ displayText }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>

.left-list-points {
  margin-left: 1rem;
  color: rgba(255, 255, 255, 0.7);
  font-weight: 600;
  text-align: right;
  min-width: 2rem;
}

.left-list {
  list-style: none;
  margin: 0;
  padding: 5px;
  text-align: left;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.other-container {
  padding: 2rem;
  overflow-y: auto;
}

.split-layout {
  display: grid;
  grid-template-columns: 200px 1fr 1fr;
  gap: 15px;
  max-width: 1400px;
  margin: 0 auto;
  height: calc(100vh - 140px);
}

/* Left Side - Input Section */
.input-section {
  display: flex;
  flex-direction: column;
}

.input-card {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  padding: 2rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
  height: 100%;
  display: flex;
  flex-direction: column;
}

.input-card h2 {
  color: white;
  margin: 0 0 0.5rem 0;
  font-size: 2rem;
  font-weight: bold;
}

.input-card p {
  color: rgba(255, 255, 255, 0.8);
  margin: 0 0 1rem 0;
  font-size: 1.1rem;
}

.error-message {
  background: rgba(255, 107, 107, 0.2);
  border: 1px solid rgba(255, 107, 107, 0.5);
  color: #ff6b6b;
  padding: 0.8rem;
  border-radius: 8px;
  margin-bottom: 1rem;
  font-weight: 500;
}

.input-group {
  flex: 1;
  display: flex;
  flex-direction: column;
  margin-bottom: 1.5rem;
}

.input-label {
  color: white;
  font-weight: 600;
  margin-bottom: 0.5rem;
  font-size: 1.1rem;
}

.text-input {
  flex: 1;
  background: rgba(255, 255, 255, 0.1);
  border: 2px solid rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  padding: 1rem;
  color: white;
  font-size: 1rem;
  font-family: inherit;
  resize: none;
  transition: all 0.3s ease;
  min-height: 200px;
}

.text-input:focus {
  outline: none;
  border-color: #4facfe;
  background: rgba(255, 255, 255, 0.15);
  box-shadow: 0 0 0 3px rgba(79, 172, 254, 0.2);
}

.text-input::placeholder {
  color: rgba(255, 255, 255, 0.5);
}

.input-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.submit-btn {
  background: linear-gradient(45deg, #4facfe, #00f2fe);
  color: white;
  border: none;
  padding: 0.8rem 1.5rem;
  border-radius: 10px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.submit-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(79, 172, 254, 0.3);
}

.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.clear-btn {
  background: linear-gradient(45deg, #ff6b6b, #ee5a52);
  color: white;
  border: none;
  padding: 0.8rem 1.5rem;
  border-radius: 10px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.clear-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(255, 107, 107, 0.3);
}

.clear-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.char-count {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.9rem;
  font-weight: 500;
}

.quick-actions h3 {
  color: white;
  margin: 0 0 1rem 0;
  font-size: 1.2rem;
}

.action-buttons {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.action-btn {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
  padding: 0.5rem 1rem;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.9rem;
}

.action-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: translateY(-1px);
}

/* Right Side - Display Section */
.display-section {
  display: flex;
  flex-direction: column;
}

.display-card {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  padding: 2rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
  height: 100%;
  display: flex;
  flex-direction: column;
}

.display-card h2 {
  color: white;
  margin: 0 0 0.5rem 0;
  font-size: 2rem;
  font-weight: bold;
}

.display-card p {
  color: rgba(255, 255, 255, 0.8);
  margin: 0 0 2rem 0;
  font-size: 1.1rem;
}

.text-display {
  flex: 1;
  background: rgba(0, 0, 0, 0.2);
  border: 2px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 1.5rem;
  overflow-y: auto;
}

.display-content {
  color: white;
  font-size: 1.1rem;
  line-height: 1.6;
  white-space: pre-wrap;
  word-wrap: break-word;
  min-height: 100px;
}

.display-content.loading {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 200px;
}

.loading-spinner {
  font-size: 1.2rem;
  color: #4facfe;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

/* Responsive Design */
@media (max-width: 1024px) {
  .split-layout {
    grid-template-columns: 1fr;
    gap: 1.5rem;
    height: auto;
  }

  .input-card,
  .display-card {
    height: auto;
    min-height: 400px;
  }
}

@media (max-width: 768px) {
  .other-container {
    padding: 1rem;
  }

  .input-card,
  .display-card {
    padding: 1.5rem;
  }

  .input-card h2,
  .display-card h2 {
    font-size: 1.8rem;
  }

  .action-buttons {
    justify-content: center;
  }

  .input-controls {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }

  .submit-btn,
  .clear-btn {
    width: 100%;
  }
}

@media (max-width: 480px) {
  .split-layout {
    gap: 1rem;
  }

  .input-card,
  .display-card {
    padding: 1rem;
  }

  .text-input {
    min-height: 150px;
  }
}
</style>