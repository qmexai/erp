<template>
  <div class="panel">
    <div class="panel-hd flex-col items-start gap-4 md:flex-row md:items-center">
      <div class="panel-title">
        <span class="accent violet"></span>
        Task Management
      </div>
      
      <div class="flex items-center justify-between w-full md:w-auto gap-4">
        <!-- Tabs -->
        <div class="flex gap-2">
          <button 
            @click="activeTab = 'my_tasks'" 
            :class="['panel-btn', activeTab === 'my_tasks' ? 'bg-[var(--qx-bg2)] text-[var(--qx-text1)] border-[var(--qx-border2)]' : '']">
            My Tasks
          </button>
          <button 
            @click="activeTab = 'assigned_tasks'" 
            :class="['panel-btn', activeTab === 'assigned_tasks' ? 'bg-[var(--qx-bg2)] text-[var(--qx-text1)] border-[var(--qx-border2)]' : '']">
            Assigned by Me
          </button>
        </div>

        <button @click="showAddTaskModal = true" class="panel-btn text-[var(--qx-blue)] font-medium border-[var(--qx-blue-d)] hover:bg-[var(--qx-blue-d)]">
          + Add Task
        </button>
      </div>
    </div>

    <!-- Tasks Table -->
    <div class="panel-bd !p-0 overflow-x-auto">
      <table class="tbl w-full m-0">
        <thead>
          <tr>
            <th class="w-12 text-center pl-4">Status</th>
            <th>Title</th>
            <th v-if="activeTab === 'my_tasks'">Assigned By</th>
            <th v-if="activeTab === 'assigned_tasks'">Assigned To</th>
            <th>Project</th>
            <th>Due Date</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="task in tasks" :key="task.id" :class="task.completed ? 'opacity-60' : ''">
            <td class="text-center pl-4">
              <input type="checkbox" v-model="task.completed" @change="toggleComplete(task)" 
                class="cursor-pointer w-4 h-4 rounded border-[var(--qx-border)] bg-[var(--qx-bg1)] checked:bg-[var(--qx-blue)] transition-colors mt-1" />
            </td>
            <td :class="['fw', task.completed ? 'line-through text-[var(--qx-text3)]' : '']">{{ task.title }}</td>
            <td v-if="activeTab === 'my_tasks'">{{ task.assigned_by?.name || task.assigned_by?.email || '—' }}</td>
            <td v-if="activeTab === 'assigned_tasks'">{{ task.assigned_to?.name || task.assigned_to?.email || '—' }}</td>
            <td>
              <span v-if="task.project" class="badge active">{{ task.project?.name }}</span>
              <span v-else class="text-[var(--qx-text3)] text-xs">—</span>
            </td>
            <td class="mono" :class="isOverdue(task.due_date) && !task.completed ? 'text-[var(--qx-red)] font-semibold' : ''">
              {{ formatDate(task.due_date) || '—' }}
            </td>
          </tr>
          <tr v-if="tasks.length === 0">
            <td colspan="6" class="empty-cell text-center p-8">No tasks found. Get to work!</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Add Task Modal -->
    <AddTaskModal 
      v-if="showAddTaskModal"
      :show="showAddTaskModal" 
      :users="users"
      :projects="projects"
      @close="showAddTaskModal = false" 
      @task-added="handleTaskAdded" 
    />
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import apiClient from '../api';
import AddTaskModal from './AddTaskModal.vue';
import { fmtDateShort as formatDate } from '../utils/formatters';

const tasks = ref([]);
const users = ref([]);
const projects = ref([]);
const showAddTaskModal = ref(false);
const activeTab = ref('my_tasks'); // 'my_tasks' or 'assigned_tasks'

const fetchTasks = async () => {
  try {
    const view = activeTab.value === 'my_tasks' ? 'assigned_to_me' : 'assigned_by_me';
    const response = await apiClient.get(`/tasks/?view=${view}`);
    tasks.value = response.data;
  } catch (error) {
    console.error('Error fetching tasks:', error);
  }
};

const fetchUsers = async () => {
  try {
    const response = await apiClient.get('/users/');
    users.value = response.data.results || response.data;
  } catch (error) {
    console.error('Error fetching users:', error);
  }
};

const fetchProjects = async () => {
  try {
    const response = await apiClient.get('/projects/');
    projects.value = response.data;
  } catch (error) {
    console.error('Error fetching projects:', error);
  }
};

const toggleComplete = async (task) => {
  try {
    const response = await apiClient.patch(`/tasks/${task.id}/toggle_complete/`);
    // Update the task in the local list with the response from the server
    const index = tasks.value.findIndex(t => t.id === task.id);
    if (index !== -1) {
      tasks.value[index] = response.data;
    }
  } catch (error) {
    console.error('Error updating task status:', error);
    // Revert the checkbox state on failure
    task.completed = !task.completed;
  }
};

const handleTaskAdded = () => {
  showAddTaskModal.value = false;
  fetchTasks(); // Refresh the list after a task is added
};

// Fetch tasks when the component mounts and when the active tab changes
onMounted(() => {
  fetchTasks();
  fetchUsers();
  fetchProjects();
});

const isOverdue = (dateStr) => {
  if (!dateStr) return false;
  return new Date(dateStr) < new Date(new Date().setHours(0,0,0,0));
};

watch(activeTab, fetchTasks);
</script>

<style scoped>
</style>

