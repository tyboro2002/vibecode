<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'

interface TestCase {
  id: number
  problem_id: number
  problem_name: string
  input_data: any
  expected_output: string
  is_public: boolean
}

interface Problem {
  id: number
  name: string
  points: number
  assignment: string
}

const tests = ref<TestCase[]>([])
const problems = ref<Problem[]>([])
const isLoading = ref(true)
const errorMessage = ref('')
const filterProblemId = ref<number | null>(null)
const filterPublic = ref<boolean | null>(null)
const editingTest = ref<number | null>(null)
const editingProblem = ref<number | null>(null)
const activeTab = ref<'tests' | 'problems'>('tests')
const creatingTest = ref(false)
const editForm = ref({
  input_data: '',
  expected_output: '',
  is_public: true
})
const newTestForm = ref({
  problem_id: null as number | null,
  input_data: '',
  expected_output: '',
  is_public: true
})
const problemEditForm = ref({
  name: '',
  points: 0,
  assignment: ''
})

const fetchAllTests = async () => {
  try {
    isLoading.value = true
    errorMessage.value = ''
    
    const response = await fetch('http://localhost:8000/api/tests/all/')
    const data = await response.json()
    
    if (data.success) {
      tests.value = data.tests
    } else {
      errorMessage.value = data.error || 'Failed to load tests'
    }
  } catch (error) {
    errorMessage.value = 'Failed to connect to the backend. Make sure the server is running.'
    console.error('Error fetching tests:', error)
  } finally {
    isLoading.value = false
  }
}

const fetchAllProblems = async () => {
  try {
    isLoading.value = true
    errorMessage.value = ''
    
    const response = await fetch('http://localhost:8000/api/problems/all/')
    const data = await response.json()
    
    if (data.success) {
      problems.value = data.problems
    } else {
      errorMessage.value = data.error || 'Failed to load problems'
    }
  } catch (error) {
    errorMessage.value = 'Failed to connect to the backend. Make sure the server is running.'
    console.error('Error fetching problems:', error)
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  fetchAllTests()
  fetchAllProblems()
})

const filteredTests = computed(() => {
  let result = tests.value
  
  if (filterProblemId.value !== null) {
    result = result.filter(t => t.problem_id === filterProblemId.value)
  }
  
  if (filterPublic.value !== null) {
    result = result.filter(t => t.is_public === filterPublic.value)
  }
  
  return result
})

const uniqueProblems = computed(() => {
  const problemMap = new Map<number, string>()
  tests.value.forEach(test => {
    if (!problemMap.has(test.problem_id)) {
      problemMap.set(test.problem_id, test.problem_name)
    }
  })
  return Array.from(problemMap.entries()).map(([id, name]) => ({ id, name }))
})

const clearFilters = () => {
  filterProblemId.value = null
  filterPublic.value = null
}

const toggleVisibility = async (test: TestCase) => {
  try {
    const response = await fetch(`http://localhost:8000/api/tests/${test.id}/`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
      body: JSON.stringify({
        is_public: !test.is_public
      })
    })

    const data = await response.json()

    if (data.success) {
      // Update the test in the local array
      const index = tests.value.findIndex(t => t.id === test.id)
      if (index !== -1 && tests.value[index]) {
        tests.value[index].is_public = data.test.is_public
      }
    } else {
      errorMessage.value = data.error || 'Failed to update test visibility'
    }
  } catch (error) {
    errorMessage.value = 'Failed to connect to the backend'
    console.error('Error toggling visibility:', error)
  }
}

const startEditing = (test: TestCase) => {
  editingTest.value = test.id
  editForm.value = {
    input_data: JSON.stringify(test.input_data),
    expected_output: test.expected_output,
    is_public: test.is_public
  }
}

const cancelEditing = () => {
  editingTest.value = null
}

const saveEdit = async (testId: number) => {
  try {
    let parsedInputData
    try {
      parsedInputData = JSON.parse(editForm.value.input_data)
    } catch (e) {
      errorMessage.value = 'Invalid JSON format for input data'
      return
    }

    const response = await fetch(`http://localhost:8000/api/tests/${testId}/`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
      body: JSON.stringify({
        input_data: parsedInputData,
        expected_output: editForm.value.expected_output,
        is_public: editForm.value.is_public
      })
    })

    const data = await response.json()

    if (data.success) {
      // Update the test in the local array
      const index = tests.value.findIndex(t => t.id === testId)
      if (index !== -1) {
        tests.value[index] = data.test
      }
      editingTest.value = null
      errorMessage.value = ''
    } else {
      errorMessage.value = data.error || 'Failed to update test'
    }
  } catch (error) {
    errorMessage.value = 'Failed to connect to the backend'
    console.error('Error saving test:', error)
  }
}

const startCreatingTest = () => {
  creatingTest.value = true
  newTestForm.value = {
    problem_id: filterProblemId.value,
    input_data: '',
    expected_output: '',
    is_public: true
  }
}

const cancelCreatingTest = () => {
  creatingTest.value = false
}

const createTest = async () => {
  try {
    if (!newTestForm.value.problem_id) {
      errorMessage.value = 'Please select a problem'
      return
    }

    let parsedInputData
    try {
      parsedInputData = JSON.parse(newTestForm.value.input_data)
    } catch (e) {
      errorMessage.value = 'Invalid JSON format for input data'
      return
    }

    const response = await fetch('http://localhost:8000/api/tests/create/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
      body: JSON.stringify({
        problem_id: newTestForm.value.problem_id,
        input_data: parsedInputData,
        expected_output: newTestForm.value.expected_output,
        is_public: newTestForm.value.is_public
      })
    })

    const data = await response.json()

    if (data.success) {
      tests.value.push(data.test)
      creatingTest.value = false
      errorMessage.value = ''
    } else {
      errorMessage.value = data.error || 'Failed to create test'
    }
  } catch (error) {
    errorMessage.value = 'Failed to connect to the backend'
    console.error('Error creating test:', error)
  }
}

const deleteTest = async (testId: number) => {
  if (!confirm('Are you sure you want to delete this test case? This action cannot be undone.')) {
    return
  }

  try {
    const response = await fetch(`http://localhost:8000/api/tests/${testId}/delete/`, {
      method: 'DELETE',
      credentials: 'include'
    })

    const data = await response.json()

    if (data.success) {
      const index = tests.value.findIndex(t => t.id === testId)
      if (index !== -1) {
        tests.value.splice(index, 1)
      }
      errorMessage.value = ''
    } else {
      errorMessage.value = data.error || 'Failed to delete test'
    }
  } catch (error) {
    errorMessage.value = 'Failed to connect to the backend'
    console.error('Error deleting test:', error)
  }
}

const startEditingProblem = (problem: Problem) => {
  editingProblem.value = problem.id
  problemEditForm.value = {
    name: problem.name,
    points: problem.points,
    assignment: problem.assignment
  }
}

const cancelEditingProblem = () => {
  editingProblem.value = null
}

const saveProblemEdit = async (problemId: number) => {
  try {
    const response = await fetch(`http://localhost:8000/api/problems/${problemId}/`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
      body: JSON.stringify({
        name: problemEditForm.value.name,
        points: problemEditForm.value.points,
        assignment: problemEditForm.value.assignment
      })
    })

    const data = await response.json()

    if (data.success) {
      // Update the problem in the local array
      const index = problems.value.findIndex(p => p.id === problemId)
      if (index !== -1) {
        problems.value[index] = data.problem
      }
      editingProblem.value = null
      errorMessage.value = ''
    } else {
      errorMessage.value = data.error || 'Failed to update problem'
    }
  } catch (error) {
    errorMessage.value = 'Failed to connect to the backend'
    console.error('Error saving problem:', error)
  }
}
</script>

<script lang="ts">
export default {
  name: 'Admin'
}
</script>

<template>
  <div class="admin-container">
    <div class="admin-content">
      <div class="header-section">
        <h1 class="page-title">🔧 Admin Panel</h1>
        <p class="page-subtitle">Management Dashboard</p>
      </div>

      <!-- Error Message -->
      <div v-if="errorMessage" class="error-message">
        ⚠️ {{ errorMessage }}
      </div>

      <!-- Tab Navigation -->
      <div class="tab-navigation">
        <button 
          @click="activeTab = 'tests'" 
          :class="{ active: activeTab === 'tests' }"
          class="tab-btn"
        >
          🧪 Test Cases
        </button>
        <button 
          @click="activeTab = 'problems'" 
          :class="{ active: activeTab === 'problems' }"
          class="tab-btn"
        >
          📝 Problems
        </button>
      </div>

      <!-- Tests Tab -->
      <div v-if="activeTab === 'tests'">
        <!-- Filters -->
        <div class="filters-section">
        <div class="filter-group">
          <label for="problem-filter">Filter by Problem:</label>
          <select id="problem-filter" v-model.number="filterProblemId">
            <option :value="null">All Problems</option>
            <option v-for="problem in uniqueProblems" :key="problem.id" :value="problem.id">
              {{ problem.name }}
            </option>
          </select>
        </div>

        <div class="filter-group">
          <label for="visibility-filter">Filter by Visibility:</label>
          <select id="visibility-filter" v-model="filterPublic">
            <option :value="null">All Tests</option>
            <option :value="true">Public Only</option>
            <option :value="false">Hidden Only</option>
          </select>
        </div>

        <button @click="clearFilters" class="clear-filters-btn">Clear Filters</button>
        <button @click="fetchAllTests" :disabled="isLoading" class="refresh-btn">
          <span v-if="isLoading">🔄 Loading...</span>
          <span v-else>🔄 Refresh</span>
        </button>
        <button @click="startCreatingTest" class="create-btn">➕ Create New Test</button>
      </div>

      <!-- Stats -->
      <div class="stats-section">
        <div class="stat-card">
          <div class="stat-value">{{ filteredTests.length }}</div>
          <div class="stat-label">Total Tests</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ filteredTests.filter((t: { is_public: any; }) => t.is_public).length }}</div>
          <div class="stat-label">Public Tests</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ filteredTests.filter((t: { is_public: any; }) => !t.is_public).length }}</div>
          <div class="stat-label">Hidden Tests</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ uniqueProblems.length }}</div>
          <div class="stat-label">Problems</div>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="isLoading" class="loading-container">
        <div class="loading-spinner">🔄 Loading test cases...</div>
      </div>

      <!-- Create New Test Form -->
      <div v-else-if="creatingTest" class="create-test-form">
        <h3>Create New Test Case</h3>
        <div class="form-row">
          <label>Problem:</label>
          <select v-model.number="newTestForm.problem_id" required>
            <option :value="null">Select a problem</option>
            <option v-for="problem in uniqueProblems" :key="problem.id" :value="problem.id">
              {{ problem.name }}
            </option>
          </select>
        </div>
        <div class="form-row">
          <label>Input Data (JSON):</label>
          <textarea v-model="newTestForm.input_data" class="edit-textarea-large" placeholder='{"param": "value"}' required></textarea>
        </div>
        <div class="form-row">
          <label>Expected Output:</label>
          <textarea v-model="newTestForm.expected_output" class="edit-textarea-large" placeholder="Expected output" required></textarea>
        </div>
        <div class="form-row">
          <label class="visibility-toggle">
            <input type="checkbox" v-model="newTestForm.is_public">
            <span>{{ newTestForm.is_public ? '👁️ Public' : '🔒 Hidden' }}</span>
          </label>
        </div>
        <div class="form-actions">
          <button @click="createTest" class="save-btn">💾 Create Test</button>
          <button @click="cancelCreatingTest" class="cancel-btn">❌ Cancel</button>
        </div>
      </div>

      <!-- Tests List -->
      <div v-else class="tests-list">
        <div class="list-header">
          <span>ID</span>
          <span>Problem</span>
          <span>Input</span>
          <span>Expected Output</span>
          <span>Visibility</span>
          <span>Actions</span>
        </div>

        <div v-for="test in filteredTests" :key="test.id" class="test-item">
          <template v-if="editingTest === test.id">
            <!-- Edit Mode -->
            <div class="test-id">{{ test.id }}</div>
            <div class="test-problem">{{ test.problem_name }}</div>
            <div class="test-input edit-mode">
              <textarea v-model="editForm.input_data" class="edit-textarea" placeholder="JSON input data"></textarea>
            </div>
            <div class="test-output edit-mode">
              <textarea v-model="editForm.expected_output" class="edit-textarea" placeholder="Expected output"></textarea>
            </div>
            <div class="test-visibility">
              <label class="visibility-toggle">
                <input type="checkbox" v-model="editForm.is_public">
                <span>{{ editForm.is_public ? '👁️ Public' : '🔒 Hidden' }}</span>
              </label>
            </div>
            <div class="test-actions">
              <button @click="saveEdit(test.id)" class="save-btn">💾 Save</button>
              <button @click="cancelEditing" class="cancel-btn">❌ Cancel</button>
            </div>
          </template>
          <template v-else>
            <!-- View Mode -->
            <div class="test-id">{{ test.id }}</div>
            <div class="test-problem">{{ test.problem_name }}</div>
            <div class="test-input">
              <code>{{ JSON.stringify(test.input_data) }}</code>
            </div>
            <div class="test-output">
              <code>{{ test.expected_output }}</code>
            </div>
            <div class="test-visibility">
              <button @click="toggleVisibility(test)" class="visibility-btn" :class="test.is_public ? 'btn-public' : 'btn-hidden'">
                {{ test.is_public ? '👁️ Public' : '🔒 Hidden' }}
              </button>
            </div>
            <div class="test-actions">
              <button @click="startEditing(test)" class="edit-btn">✏️ Edit</button>
              <button @click="deleteTest(test.id)" class="delete-btn">🗑️ Delete</button>
            </div>
          </template>
        </div>

        <div v-if="filteredTests.length === 0" class="empty-state">
          <p>No test cases found with current filters.</p>
        </div>
      </div>
      </div>

      <!-- Problems Tab -->
      <div v-if="activeTab === 'problems'">
        <!-- Stats -->
        <div class="stats-section">
          <div class="stat-card">
            <div class="stat-value">{{ problems.length }}</div>
            <div class="stat-label">Total Problems</div>
          </div>
          <div class="stat-card">
            <div class="stat-value">{{ problems.reduce((sum: number, p: Problem) => sum + p.points, 0) }}</div>
            <div class="stat-label">Total Points</div>
          </div>
        </div>

        <!-- Loading State -->
        <div v-if="isLoading" class="loading-container">
          <div class="loading-spinner">🔄 Loading problems...</div>
        </div>

        <!-- Problems List -->
        <div v-else class="problems-list">
          <div v-for="problem in problems" :key="problem.id" class="problem-card">
            <template v-if="editingProblem === problem.id">
              <!-- Edit Mode -->
              <div class="problem-edit-form">
                <div class="form-row">
                  <label>Problem Name:</label>
                  <input v-model="problemEditForm.name" type="text" class="edit-input" placeholder="Problem name">
                </div>
                <div class="form-row">
                  <label>Points:</label>
                  <input v-model.number="problemEditForm.points" type="number" class="edit-input" placeholder="Points">
                </div>
                <div class="form-row full-width">
                  <label>Assignment Text (Markdown):</label>
                  <textarea v-model="problemEditForm.assignment" class="edit-textarea-large" placeholder="Problem description in Markdown"></textarea>
                </div>
                <div class="form-actions">
                  <button @click="saveProblemEdit(problem.id)" class="save-btn">💾 Save Changes</button>
                  <button @click="cancelEditingProblem" class="cancel-btn">❌ Cancel</button>
                </div>
              </div>
            </template>
            <template v-else>
              <!-- View Mode -->
              <div class="problem-header">
                <h3>{{ problem.name }}</h3>
                <div class="problem-meta">
                  <span class="problem-id">ID: {{ problem.id }}</span>
                  <span class="problem-points">{{ problem.points }} pts</span>
                  <button @click="startEditingProblem(problem)" class="edit-btn">✏️ Edit</button>
                </div>
              </div>
              <div class="problem-assignment">
                <div class="assignment-preview">{{ problem.assignment.substring(0, 200) }}{{ problem.assignment.length > 200 ? '...' : '' }}</div>
              </div>
            </template>
          </div>

          <div v-if="problems.length === 0" class="empty-state">
            <p>No problems found.</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.admin-container {
  min-height: calc(100vh - 100px);
  padding: 2rem;
  overflow-y: auto;
}

.admin-content {
  max-width: 1400px;
  margin: 0 auto;
}

.header-section {
  text-align: center;
  margin-bottom: 2rem;
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
  margin: 0;
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

.tab-navigation {
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;
  justify-content: center;
}

.tab-btn {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: white;
  padding: 0.75rem 2rem;
  border-radius: 10px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 1rem;
}

.tab-btn:hover {
  background: rgba(255, 255, 255, 0.15);
  transform: translateY(-2px);
}

.tab-btn.active {
  background: linear-gradient(45deg, #4facfe, #00f2fe);
  border-color: rgba(79, 172, 254, 0.5);
  box-shadow: 0 4px 12px rgba(79, 172, 254, 0.3);
}

.filters-section {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 15px;
  padding: 1.5rem;
  margin-bottom: 2rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
  align-items: flex-end;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  flex: 1;
  min-width: 200px;
}

.filter-group label {
  color: white;
  font-weight: 600;
  font-size: 0.9rem;
}

.filter-group select {
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  padding: 0.75rem;
  color: white;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.filter-group select:focus {
  outline: none;
  border-color: #4facfe;
  background: rgba(0, 0, 0, 0.4);
}

.filter-group select option {
  background: #1a1a2e;
  color: white;
}

.clear-filters-btn,
.refresh-btn,
.create-btn {
  background: linear-gradient(45deg, #4facfe, #00f2fe);
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  height: fit-content;
}

.clear-filters-btn {
  background: linear-gradient(45deg, #ff6b6b, #ee5a52);
}

.create-btn {
  background: linear-gradient(45deg, #43e97b, #38f9d7);
}

.clear-filters-btn:hover,
.refresh-btn:hover:not(:disabled),
.create-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(79, 172, 254, 0.3);
}

.refresh-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.stats-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 15px;
  padding: 1.5rem;
  text-align: center;
}

.stat-value {
  font-size: 2.5rem;
  font-weight: bold;
  color: #4facfe;
  margin-bottom: 0.5rem;
}

.stat-label {
  font-size: 1rem;
  color: rgba(255, 255, 255, 0.8);
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

.tests-list {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 15px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.list-header {
  display: grid;
  grid-template-columns: 60px 200px 1fr 1fr 120px 150px;
  background: rgba(0, 0, 0, 0.3);
  padding: 1rem;
  font-weight: bold;
  color: white;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  gap: 1rem;
}

.test-item {
  display: grid;
  grid-template-columns: 60px 200px 1fr 1fr 120px 150px;
  padding: 1rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  color: white;
  gap: 1rem;
  transition: all 0.2s ease;
  align-items: center;
}

.test-item:hover {
  background: rgba(255, 255, 255, 0.05);
}

.test-item:last-child {
  border-bottom: none;
}

.test-id {
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  color: #4facfe;
}

.test-problem {
  display: flex;
  align-items: center;
  font-size: 0.9rem;
  word-break: break-word;
}

.test-input,
.test-output {
  display: flex;
  align-items: center;
}

.test-input code,
.test-output code {
  background: rgba(0, 0, 0, 0.3);
  padding: 0.5rem;
  border-radius: 6px;
  font-size: 0.85rem;
  word-break: break-all;
  max-width: 100%;
  overflow-x: auto;
  display: block;
}

.test-visibility {
  display: flex;
  align-items: center;
  justify-content: center;
}

.badge-public,
.badge-hidden {
  padding: 0.4rem 0.8rem;
  border-radius: 999px;
  font-size: 0.85rem;
  font-weight: 600;
}

.badge-public {
  background: rgba(67, 233, 123, 0.2);
  border: 1px solid rgba(67, 233, 123, 0.5);
  color: #43e97b;
}

.badge-hidden {
  background: rgba(255, 193, 7, 0.2);
  border: 1px solid rgba(255, 193, 7, 0.5);
  color: #ffc107;
}

.test-actions {
  display: flex;
  gap: 0.5rem;
  justify-content: center;
  align-items: center;
}

.visibility-btn,
.edit-btn,
.delete-btn,
.save-btn,
.cancel-btn {
  padding: 0.4rem 0.8rem;
  border-radius: 8px;
  font-size: 0.85rem;
  font-weight: 600;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.visibility-btn {
  width: 100%;
}

.btn-public {
  background: rgba(67, 233, 123, 0.2);
  border: 1px solid rgba(67, 233, 123, 0.5);
  color: #43e97b;
}

.btn-public:hover {
  background: rgba(67, 233, 123, 0.3);
  transform: translateY(-1px);
}

.btn-hidden {
  background: rgba(255, 193, 7, 0.2);
  border: 1px solid rgba(255, 193, 7, 0.5);
  color: #ffc107;
}

.btn-hidden:hover {
  background: rgba(255, 193, 7, 0.3);
  transform: translateY(-1px);
}

.edit-btn {
  background: rgba(79, 172, 254, 0.2);
  border: 1px solid rgba(79, 172, 254, 0.5);
  color: #4facfe;
}

.edit-btn:hover {
  background: rgba(79, 172, 254, 0.3);
  transform: translateY(-1px);
}

.delete-btn {
  background: rgba(255, 107, 107, 0.2);
  border: 1px solid rgba(255, 107, 107, 0.5);
  color: #ff6b6b;
}

.delete-btn:hover {
  background: rgba(255, 107, 107, 0.3);
  transform: translateY(-1px);
}

.save-btn {
  background: rgba(67, 233, 123, 0.2);
  border: 1px solid rgba(67, 233, 123, 0.5);
  color: #43e97b;
}

.save-btn:hover {
  background: rgba(67, 233, 123, 0.3);
  transform: translateY(-1px);
}

.cancel-btn {
  background: rgba(255, 107, 107, 0.2);
  border: 1px solid rgba(255, 107, 107, 0.5);
  color: #ff6b6b;
}

.cancel-btn:hover {
  background: rgba(255, 107, 107, 0.3);
  transform: translateY(-1px);
}

.edit-mode {
  padding: 0;
}

.edit-textarea {
  width: 100%;
  min-height: 60px;
  background: rgba(0, 0, 0, 0.4);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 6px;
  padding: 0.5rem;
  color: white;
  font-family: 'Courier New', monospace;
  font-size: 0.85rem;
  resize: vertical;
}

.edit-textarea:focus {
  outline: none;
  border-color: #4facfe;
  background: rgba(0, 0, 0, 0.5);
}

.visibility-toggle {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  user-select: none;
}

.visibility-toggle input[type="checkbox"] {
  cursor: pointer;
}

.visibility-toggle span {
  font-size: 0.85rem;
  font-weight: 600;
}

.create-test-form {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 15px;
  padding: 2rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
  margin-bottom: 2rem;
}

.create-test-form h3 {
  color: white;
  margin-bottom: 1.5rem;
  font-size: 1.5rem;
}

.create-test-form .form-row {
  margin-bottom: 1.5rem;
}

.create-test-form .form-row label {
  display: block;
  color: white;
  font-weight: 600;
  margin-bottom: 0.5rem;
}

.create-test-form .form-row select,
.create-test-form .form-row textarea {
  width: 100%;
  background: rgba(0, 0, 0, 0.4);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  padding: 0.75rem;
  color: white;
  font-size: 1rem;
}

.create-test-form .form-row select:focus,
.create-test-form .form-row textarea:focus {
  outline: none;
  border-color: #4facfe;
  background: rgba(0, 0, 0, 0.5);
}

.create-test-form .form-row select option {
  background: #1a1a2e;
  color: white;
}

.create-test-form .form-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-start;
}

.problems-list {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.problem-card {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 15px;
  padding: 1.5rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
  transition: all 0.2s ease;
}

.problem-card:hover {
  background: rgba(255, 255, 255, 0.12);
  border-color: rgba(255, 255, 255, 0.3);
}

.problem-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.problem-header h3 {
  color: white;
  margin: 0;
  font-size: 1.3rem;
  flex: 1;
}

.problem-meta {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.problem-id {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.9rem;
}

.problem-points {
  background: rgba(67, 233, 123, 0.2);
  border: 1px solid rgba(67, 233, 123, 0.5);
  color: #43e97b;
  padding: 0.4rem 0.8rem;
  border-radius: 999px;
  font-size: 0.9rem;
  font-weight: 600;
}

.problem-assignment {
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.95rem;
  line-height: 1.6;
}

.assignment-preview {
  background: rgba(0, 0, 0, 0.2);
  padding: 1rem;
  border-radius: 8px;
  border-left: 3px solid #4facfe;
  font-family: monospace;
  white-space: pre-wrap;
}

.problem-edit-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-row {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-row.full-width {
  grid-column: 1 / -1;
}

.form-row label {
  color: white;
  font-weight: 600;
  font-size: 0.9rem;
}

.edit-input {
  background: rgba(0, 0, 0, 0.4);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  padding: 0.75rem;
  color: white;
  font-size: 1rem;
}

.edit-input:focus {
  outline: none;
  border-color: #4facfe;
  background: rgba(0, 0, 0, 0.5);
}

.edit-textarea-large {
  width: 100%;
  min-height: 300px;
  background: rgba(0, 0, 0, 0.4);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  padding: 1rem;
  color: white;
  font-family: 'Courier New', monospace;
  font-size: 0.9rem;
  resize: vertical;
  line-height: 1.6;
}

.edit-textarea-large:focus {
  outline: none;
  border-color: #4facfe;
  background: rgba(0, 0, 0, 0.5);
}

.form-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 1rem;
}

.empty-state {
  text-align: center;
  padding: 3rem;
  color: rgba(255, 255, 255, 0.6);
  font-style: italic;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

@media (max-width: 1200px) {
  .list-header,
  .test-item {
    grid-template-columns: 60px 150px 1fr 1fr 100px 120px;
    font-size: 0.9rem;
  }

  .test-actions {
    flex-direction: column;
  }
}

@media (max-width: 768px) {
  .admin-container {
    padding: 1rem;
  }

  .page-title {
    font-size: 2rem;
  }

  .filters-section {
    flex-direction: column;
  }

  .filter-group {
    min-width: 100%;
  }

  .list-header {
    display: none;
  }

  .test-item {
    grid-template-columns: 1fr;
    gap: 0.5rem;
    padding: 1rem;
  }

  .test-id::before {
    content: 'ID: ';
    font-weight: normal;
    color: rgba(255, 255, 255, 0.7);
  }

  .test-problem::before {
    content: 'Problem: ';
    font-weight: bold;
    color: rgba(255, 255, 255, 0.7);
    margin-right: 0.5rem;
  }
}
</style>
