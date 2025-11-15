<script setup lang="ts">
import {ref, onMounted, onBeforeMount, computed} from 'vue'
// Vue Python editor and runtime
import { usePython } from 'usepython'
import { PyStatus, PyCodeBlock } from 'vuepython'
import 'vuepython/style.css'
import 'highlight.js/styles/stackoverflow-dark.css'
import { marked } from 'marked'
import DOMPurify from 'dompurify'

type Problem = { id: string | number; name: string; points: number; assignment?: string }

const inputText = ref('')
const displayText = ref('Your processed text will appear here when you submit...')
const isLoading = ref(false)
const errorMessage = ref('')
const problems = ref<Problem[]>([])
const selectedProblem = ref<Problem | null>(null)

// Python runtime and example code for the editor
const py = usePython()
const pyCode = ref(
  ``
  // `print('starting python script')\n` +
  // `a = 1\n` +
  // `b = 2\n` +
  // `print('finished python script')\n` +
  // `c = a + b\n` +
  // `# return value\n` +
  // `c\n` + 
  // `for i in range(0,10):\n` +
  // `\tprint(i)`

)

onBeforeMount(async () => {
  await py.load()
})

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
    selectedProblem.value = problems.value[0] ?? null
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
        code: pyCode.value,
      })
    })

    const data = await response.json()

    if (data.success) {
      pyCode.value = data.generated_code
    } else {
      errorMessage.value = data.error || 'An error occurred while processing the text.'
      // pyCode.value = 'Error processing text. Please try again.'
    }

  } catch (error) {
    errorMessage.value = 'Failed to connect to the backend. Make sure the server is running.'
    // pyCode.value = 'Connection error. Please check if the backend server is running.'
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

const selectProblem = (p: Problem) => {
  selectedProblem.value = p
}

const assignmentHtml = computed(() => {
  const md = selectedProblem.value?.assignment || ''
  const html = marked.parse(md)
  return DOMPurify.sanitize(html)
})
</script>

<template>
  <div class="other-container">
    <div class="split-layout">
      <div class="problems-panel">
        <li v-for="(problem, index) in problems" :key="index" class="left-list" @click="selectProblem(problem)">
          <span class="left-list-name">{{ problem.name }}</span>
          <span class="left-list-points">{{ problem.points }}</span>
        </li>
      </div>
      <!-- Left Side - Problem Description -->
      <div class="input-section">
        <div class="input-card">
          <div class="problem-header" v-if="selectedProblem">
            <h2>{{ selectedProblem.name }}</h2>
            <span class="problem-points-badge">{{ selectedProblem.points }} pts</span>
          </div>
          
          <div class="text-display">
            <div class="display-content markdown-content" v-html="assignmentHtml" style="max-height: 300px; overflow-y: auto;"></div>
          </div>

          <div v-if="errorMessage" class="error-message">
            ⚠️ {{ errorMessage }}
          </div>

          <div class="input-group" style="min-width: 40%;">
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
        </div>
      </div>

      <!-- Right Side - Python Editor -->
      <div class="display-section">
        <div class="display-card">
          <h2>Python Editor</h2>

            <div class="text-display">
              <div class="display-content no-padding">
                <div class="editor-status"><py-status :py="py" /></div>
                <py-code-block id="script" :py="py" :code="pyCode" :controls="false" />
              </div>
            </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>

.left-list-points {
  color: #fff;
  font-weight: 600;
  text-align: right;
  min-width: 2.25rem;
  background: rgba(255, 255, 255, 0.15);
  border: 1px solid rgba(255, 255, 255, 0.25);
  padding: 0.2rem 0.6rem;
  border-radius: 999px;
}

.left-list {
  list-style: none;
  margin: 0;
  padding: 0.6rem 0.75rem;
  text-align: left;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.18);
  border-radius: 12px;
  transition: transform 0.18s ease, box-shadow 0.18s ease, border-color 0.18s ease, background 0.18s ease;
}

.left-list:hover {
  transform: translateY(-2px);
  border-color: rgba(255, 255, 255, 0.35);
  background: rgba(255, 255, 255, 0.12);
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.25);
}

.left-list {
  cursor: pointer;
}

.left-list-name {
  color: #fff;
  font-weight: 600;
  word-wrap: break-word;
  overflow-wrap: break-word;
  flex: 1;
  max-width: 70%;
}

.problems-panel {
  display: flex;
  flex-direction: column;
  gap: 8px;
  overflow-y: auto;
  overflow-x: hidden;
  max-height: 100vh;
  padding-right: 4px;
}

.problem-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1rem;
}

.problem-points-badge {
  color: #fff;
  font-weight: 700;
  background: rgba(255, 255, 255, 0.15);
  border: 1px solid rgba(255, 255, 255, 0.25);
  padding: 0.35rem 0.75rem;
  border-radius: 999px;
  font-size: 0.95rem;
}

.markdown-content {
  overflow: auto;
  text-align: left;
}

.markdown-content h1,
.markdown-content h2,
.markdown-content h3 {
  color: #fff;
  margin: 5.6rem 0;
  text-align: left;
}

.markdown-content p {
  color: rgba(255, 255, 255, 0.9);
  text-align: left;
}

.markdown-content ul,
.markdown-content ol {
  padding-left: 1.2rem;
}

.markdown-content code {
  background: rgba(255, 255, 255, 0.15);
  padding: 0.15rem 0.35rem;
  border-radius: 6px;
}

.markdown-content pre {
  background: #0b1220;
  border: 1px solid rgba(255, 255, 255, 0.12);
  padding: 0.75rem;
  border-radius: 10px;
  overflow: auto;
}

.other-container {
  padding: 2rem;
  overflow-y: auto;
}

.split-layout {
  display: grid;
  grid-template-columns: 200px minmax(35%, 1fr) minmax(45%, 1fr);
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
  display: flex;
  flex-direction: column;
  overflow: hidden; /* let inner editor manage scrolling */
}

.display-content {
  color: white;
  font-size: 1.1rem;
  line-height: 1.6;
  white-space: pre-wrap;
  word-wrap: break-word;
  min-height: 0; /* allow flex child (editor) to grow */
}

.display-content.loading {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 200px;
}

.display-content.no-padding {
  padding: 0;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.loading-spinner {
  font-size: 1.2rem;
  color: #4facfe;
  animation: pulse 2s infinite;
}

.pythonpad-iframe {
  width: 100%;
  height: 600px;
  border: none;
  border-radius: 8px;
  background: #111;
}

/* Controls hidden via :controls="false" on <py-code-block> */

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

/* Python editor theming (ensure dark background + readable text) */
:deep(.pycode-block),
:deep(.pycode-block .code-editor),
:deep(.pycode-block pre),
:deep(.pycode-block code),
:deep(.hljs) {
  background-color: #0f172a !important; /* slate-900 */
  color: #e5e7eb !important; /* gray-200 */
}

/* Force left alignment inside the editor */
:deep(.pycode-block),
:deep(.pycode-block .code-editor),
:deep(.pycode-block pre),
:deep(.pycode-block code),
:deep(.hljs) {
  text-align: left !important;
}

:deep(.pycode-block .code-editor) {
  justify-content: flex-start !important;
  align-items: flex-start !important;
  flex: 1 1 auto !important;
  min-height: 0 !important;
  overflow: auto !important;
}

/* Make the embedded editor fill the container */
:deep(py-code-block),
:deep(.pycode-block) {
  width: 100% !important;
  height: 100% !important;
  display: flex !important;
  flex-direction: column !important;
}

:deep(.pycode-block pre),
:deep(.pycode-block code),
:deep(.hljs) {
  width: 100% !important;
  height: 100% !important;
}

/* Optional: tweak borders and selection for better contrast */
:deep(.pycode-block .code-editor) {
  border-color: rgba(255, 255, 255, 0.15) !important;
}

/* Remove white focus border/outline when clicking editor */
:deep(.pycode-block .code-editor:focus),
:deep(.pycode-block .code-editor:focus-visible),
:deep(.pycode-block pre:focus),
:deep(.pycode-block pre:focus-visible),
:deep(.pycode-block code:focus),
:deep(.pycode-block code:focus-visible),
:deep(.hljs:focus),
:deep(.hljs:focus-visible) {
  outline: none !important;
  box-shadow: none !important;
  border-color: rgba(255, 255, 255, 0.15) !important;
}

/* In case the container itself receives focus */
.text-display:focus,
.display-content:focus {
  outline: none !important;
  box-shadow: none !important;
}

/* If the editor renders a textarea (.code-block), style it too */
:deep(textarea.code-block) {
  border: none;
  /* Hide the textarea's own scrollbar so only the editor container scrolls */
  overflow: hidden !important;
  resize: none !important;
  /* Cross-browser scrollbar hiding */
  scrollbar-width: none; /* Firefox */
  -ms-overflow-style: none; /* IE 10+ */
}

:deep(textarea.code-block::-webkit-scrollbar) {
  display: none; /* Chrome/Safari */
  width: 0;
  height: 0;
}

:deep(textarea.code-block:focus),
:deep(textarea.code-block:focus-visible) {
  outline: none !important;
  box-shadow: none !important;
  border-color: rgba(255, 255, 255, 0.15) !important;
}

:deep(.hljs ::selection),
:deep(.pycode-block ::selection) {
  background: rgba(79, 172, 254, 0.35) !important;
  color: #fff !important;
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