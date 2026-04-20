<template>
  <div class="space-y-8">
    <header class="flex justify-between items-center">
      <div>
        <h1 class="text-4xl font-bold tracking-tight text-white">Daily Tasks</h1>
        <p class="text-slate-400 mt-1">Individual and team task synchronization.</p>
      </div>
      <button @click="showAdd = true" 
        class="bg-white text-black font-bold px-6 py-3 rounded-xl hover:bg-slate-200 transition-all flex items-center gap-2 shadow-xl">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M12 4v16m8-8H4" /></svg>
        Assign Task
      </button>
    </header>

    <div class="bg-[#121214] border border-white/5 rounded-3xl p-6 shadow-2xl">
      <TasksTable :tasks="tasks" />
    </div>

    <AddTaskModal v-if="showAdd" @close="showAdd = false" @created="fetchTasks" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import apiClient from '../api';
import TasksTable from '../components/TasksTable.vue';
import AddTaskModal from '../components/AddTaskModal.vue';

const tasks = ref([]);
const showAdd = ref(false);

const fetchTasks = async () => {
  try {
    const res = await apiClient.get('/tasks/');
    tasks.value = res.data;
  } catch (e) {
    tasks.value = [];
  }
};

onMounted(fetchTasks);
</script>