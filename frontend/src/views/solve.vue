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
type TestResult = {
  test_id: number
  input: any
  expected: string
  actual: string
  passed: boolean
  is_public: boolean
}

const inputText = ref('')
const displayText = ref('Your processed text will appear here when you submit...')
const isLoading = ref(false)
const errorMessage = ref('')
const problems = ref<Problem[]>([])
const selectedProblem = ref<Problem | null>(null)
const solvedProblemIds = ref<number[]>([])
const testResults = ref<TestResult[]>([])
const totalTests = ref(0)
const passedTests = ref(0)
const showResults = ref(false)
const showOnlyFailed = ref(false)
const selectedCode = ref('')
const selectionStart = ref(0)
const selectionEnd = ref(0)

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
    const response = await fetch('http://192.168.0.107:8000/api/problems/all', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
    })

    const data = await response.json()
    problems.value = data.problems || []
    selectedProblem.value = problems.value[0] ?? null

    // Fetch solved problems
    try {
      const solvedResponse = await fetch('http://192.168.0.107:8000/api/problems/solved/', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
      })
      const solvedData = await solvedResponse.json()
      if (solvedData.success) {
        solvedProblemIds.value = solvedData.solved_problem_ids || []
      }
    } catch (error) {
      console.log('User not authenticated or error fetching solved problems:', error)
    }
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
    // Try to find the textarea within the py-code-block component
    let editorElement = document.querySelector('#script textarea') as HTMLTextAreaElement
    
    // If not found, try common selectors for code editors
    if (!editorElement) {
      editorElement = document.querySelector('py-code-block textarea') as HTMLTextAreaElement
    }
    if (!editorElement) {
      editorElement = document.querySelector('.editor textarea') as HTMLTextAreaElement
    }
    
    let hasSelection = false
    let codeToSend = pyCode.value
    
    if (editorElement) {
      hasSelection = editorElement.selectionStart !== editorElement.selectionEnd
      
      if (hasSelection) {
        selectedCode.value = editorElement.value.substring(editorElement.selectionStart, editorElement.selectionEnd)
        selectionStart.value = editorElement.selectionStart
        selectionEnd.value = editorElement.selectionEnd
        codeToSend = selectedCode.value
      }
    } else {
      // Fallback: check if there's a window selection (for contenteditable)
      const selection = window.getSelection()
      if (selection && selection.toString().length > 0) {
        const selectedText = selection.toString()
        const codeIndex = pyCode.value.indexOf(selectedText)
        if (codeIndex !== -1) {
          hasSelection = true
          selectedCode.value = selectedText
          selectionStart.value = codeIndex
          selectionEnd.value = codeIndex + selectedText.length
          codeToSend = selectedText
        }
      }
    }

    if (!selectedProblem.value) {
      errorMessage.value = 'Please select a problem first.'
      isLoading.value = false
      return
    }

    const response = await fetch('http://192.168.0.107:8000/api/submit/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include', // Include authentication cookies
      body: JSON.stringify({
        prompt: inputText.value,
        code: codeToSend,
        problem_id: selectedProblem.value.id,
      })
    })

    const data = await response.json()

    if (data.success) {
      if (hasSelection) {
        // Replace only the selected portion
        const before = pyCode.value.substring(0, selectionStart.value)
        const after = pyCode.value.substring(selectionEnd.value)
        pyCode.value = before + data.generated_code + after
      } else {
        // Replace entire code
        pyCode.value = data.generated_code
      }
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

// Format input parameters for display
const formatInputParams = (input: any): string => {
  if (!Array.isArray(input)) {
    return String(input)
  }
  
  // Format each element, preserving nested arrays and removing quotes from strings
  const formatValue = (val: any): string => {
    if (typeof val === 'string') {
      return val
    }
    return JSON.stringify(val)
  }
  
  return input.map(formatValue).join(',')
}

// Test function to send code to test endpoint
const testCode = async () => {
  if (!selectedProblem.value) {
    errorMessage.value = 'Please select a problem first.'
    return
  }

  if (!pyCode.value.trim()) {
    errorMessage.value = 'Please write some code before testing.'
    return
  }

  isLoading.value = true
  errorMessage.value = ''

  try {
    const response = await fetch('http://192.168.0.107:8000/api/test/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
      body: JSON.stringify({
        problem_id: selectedProblem.value.id,
        submission: pyCode.value,
      })
    })

    const data = await response.json()

    if (data.success) {
      testResults.value = data.results || []
      totalTests.value = data.total_tests || 0
      passedTests.value = data.passed_tests || 0
      showResults.value = true
      
      if (data.submission_correct) {
        displayText.value = '✅ All test cases passed! Your solution is correct.'
        
        // Add the problem to solved list if not already there
        if (selectedProblem.value && !solvedProblemIds.value.includes(selectedProblem.value.id as number)) {
          solvedProblemIds.value.push(selectedProblem.value.id as number)
        }
      } else {
        displayText.value = '❌ Some test cases failed. Please review your code and try again.'
      }
    } else {
      errorMessage.value = data.error || 'An error occurred while testing the code.'
    }

  } catch (error) {
    errorMessage.value = 'Failed to connect to the backend. Make sure the server is running.'
    console.error('Error:', error)
  } finally {
    isLoading.value = false
  }
}

const selectProblem = (p: Problem) => {
  selectedProblem.value = p
  // Reset code and test results when switching problems
  pyCode.value = ''
  inputText.value = ''
  testResults.value = []
  totalTests.value = 0
  passedTests.value = 0
  showResults.value = false
  showOnlyFailed.value = false
  errorMessage.value = ''
}

const assignmentHtml = computed(() => {
  const md = selectedProblem.value?.assignment || ''
  const html = marked.parse(md)
  return DOMPurify.sanitize(html)
})

const filteredTestResults = computed(() => {
  if (showOnlyFailed.value) {
    return testResults.value.filter(result => !result.passed)
  }
  return testResults.value
})
</script>

<template>
  <div class="other-container">
    <div class="split-layout">
      <div class="problems-panel">
        <li v-for="(problem, index) in problems" :key="index" class="left-list" :class="{ selected: selectedProblem?.id === problem.id, solved: solvedProblemIds.includes(problem.id) }" @click="selectProblem(problem)">
          <span class="left-list-name">
            <span v-if="solvedProblemIds.includes(problem.id)" class="solved-icon">✅</span>
            {{ problem.name }}
          </span>
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

            <div class="test-controls">
              <button @click="testCode" :disabled="isLoading || !selectedProblem" class="test-btn">
                <span v-if="isLoading">⏳ Testing...</span>
                <span v-else>🧪 Test Solution</span>
              </button>
            </div>

            <!-- Test Results Section -->
            <div v-if="showResults" class="results-section">
              <div class="results-header">
                <h3>Test Results</h3>
                <div class="results-summary">
                  <button 
                    @click="showOnlyFailed = !showOnlyFailed" 
                    class="filter-btn"
                    :class="{ active: showOnlyFailed }"
                  >
                    {{ showOnlyFailed ? '📋 Show All' : '❌ Failed Only' }}
                  </button>
                  <span class="summary-badge" :class="passedTests === totalTests ? 'success' : 'partial'">
                    {{ passedTests }} / {{ totalTests }} passed
                  </span>
                </div>
              </div>
              
              <div class="results-list">
                <div v-if="filteredTestResults.length === 0" class="no-results">
                  {{ showOnlyFailed ? '🎉 No failed tests!' : 'No test results available.' }}
                </div>
                <div v-for="(result, index) in filteredTestResults" :key="index" class="result-card" :class="result.passed ? 'passed' : 'failed'">
                  <div class="result-header">
                    <span class="result-status">{{ result.passed ? '✅' : '❌' }}</span>
                    <span class="result-label">Test #{{ index + 1 }}{{ result.is_public ? '' : ' 🔒' }}</span>
                  </div>
                  
                  <div v-if="result.is_public" class="result-details">
                    <div class="result-row">
                      <code class="result-value input-call">function_name({{ formatInputParams(result.input) }})</code>
                    </div>
                    <div class="result-row">
                      <span class="result-key">Expected:</span>
                      <code class="result-value expected">{{ result.expected }}</code>
                    </div>
                    <div class="result-row">
                      <span class="result-key">Got:</span>
                      <code class="result-value" :class="result.passed ? 'correct' : 'incorrect'">{{ result.actual }}</code>
                    </div>
                  </div>
                  <div v-else class="result-details">
                    <div class="hidden-test-message">
                      <span class="lock-icon">🔒</span>
                      <span>Hidden test case - {{ result.passed ? 'Passed' : 'Failed' }}</span>
                    </div>
                  </div>
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

.left-list.selected {
  background: rgba(79, 172, 254, 0.25);
  border-color: rgba(79, 172, 254, 0.5);
  box-shadow: 0 4px 12px rgba(79, 172, 254, 0.3);
}

.left-list.selected:hover {
  background: rgba(79, 172, 254, 0.3);
  border-color: rgba(79, 172, 254, 0.6);
}

.left-list.solved {
  background: rgba(67, 233, 123, 0.15);
  border-color: rgba(67, 233, 123, 0.35);
}

.left-list.solved:hover {
  background: rgba(67, 233, 123, 0.2);
  border-color: rgba(67, 233, 123, 0.45);
}

.left-list.solved.selected {
  background: linear-gradient(135deg, rgba(67, 233, 123, 0.2), rgba(79, 172, 254, 0.25));
  border-color: rgba(79, 172, 254, 0.5);
}

.solved-icon {
  margin-right: 0.5rem;
  font-size: 1rem;
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

.test-btn {
  background: linear-gradient(45deg, #43e97b, #38f9d7);
  color: white;
  border: none;
  padding: 0.8rem 1.5rem;
  border-radius: 10px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  width: 100%;
  margin-top: 1rem;
}

.test-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(67, 233, 123, 0.3);
}

.test-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.test-controls {
  margin-top: auto;
}

.results-section {
  margin-top: 1.5rem;
  max-height: 400px;
  overflow-y: auto;
}

.results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.results-header h3 {
  color: white;
  margin: 0;
  font-size: 1.3rem;
}

.results-summary {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.filter-btn {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: rgba(255, 255, 255, 0.8);
  padding: 0.4rem 0.8rem;
  border-radius: 8px;
  font-weight: 600;
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.filter-btn:hover {
  background: rgba(255, 255, 255, 0.15);
  border-color: rgba(255, 255, 255, 0.3);
}

.filter-btn.active {
  background: rgba(255, 107, 107, 0.2);
  border-color: rgba(255, 107, 107, 0.5);
  color: #ff6b6b;
}

.summary-badge {
  padding: 0.4rem 0.8rem;
  border-radius: 8px;
  font-weight: 600;
  font-size: 0.9rem;
}

.summary-badge.success {
  background: rgba(67, 233, 123, 0.2);
  border: 1px solid rgba(67, 233, 123, 0.5);
  color: #43e97b;
}

.summary-badge.partial {
  background: rgba(255, 193, 7, 0.2);
  border: 1px solid rgba(255, 193, 7, 0.5);
  color: #ffc107;
}

.results-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.no-results {
  text-align: center;
  padding: 2rem;
  color: rgba(255, 255, 255, 0.6);
  font-size: 1rem;
  font-style: italic;
}

.result-card {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  padding: 1rem;
  transition: all 0.2s ease;
  overflow: hidden;
}

.result-card.passed {
  border-left: 3px solid #43e97b;
}

.result-card.failed {
  border-left: 3px solid #ff6b6b;
}

.result-card:hover {
  background: rgba(255, 255, 255, 0.08);
}

.result-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
}

.result-status {
  font-size: 1.2rem;
}

.result-label {
  color: rgba(255, 255, 255, 0.9);
  font-weight: 600;
  font-size: 0.95rem;
}

.result-details {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.result-row {
  display: flex;
  gap: 0.75rem;
  align-items: flex-start;
}

.result-key {
  color: rgba(255, 255, 255, 0.7);
  font-weight: 600;
  min-width: 70px;
  font-size: 0.9rem;
}

.result-value {
  background: rgba(0, 0, 0, 0.3);
  padding: 0.3rem 0.6rem;
  border-radius: 6px;
  color: rgba(255, 255, 255, 0.95);
  font-family: 'Courier New', monospace;
  font-size: 0.85rem;
  flex: 1;
  word-break: break-all;
}

.result-value.input-call {
  width: 100%;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.result-value.expected {
  border: 1px solid rgba(100, 181, 246, 0.3);
}

.result-value.correct {
  border: 1px solid rgba(67, 233, 123, 0.3);
  color: #43e97b;
}

.result-value.incorrect {
  border: 1px solid rgba(255, 107, 107, 0.3);
  color: #ff6b6b;
}

.hidden-test-message {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  color: rgba(255, 255, 255, 0.7);
  font-style: italic;
  font-size: 0.9rem;
}

.lock-icon {
  font-size: 1.1rem;
  opacity: 0.8;
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