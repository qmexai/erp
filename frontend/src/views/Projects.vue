<template>
  <div class="space-y-8">
    <header class="flex justify-between items-center">
      <div>
        <h1 class="text-4xl font-bold tracking-tight text-white">Project Matrix</h1>
        <p class="text-slate-400 mt-1">Status of all Qmexai digital assets.</p>
      </div>
      <div v-if="auth.user?.role === 'CEO' || auth.user?.role === 'HR'" class="bg-violet-600/10 border border-violet-500/20 px-6 py-3 rounded-2xl">
        <span class="text-[10px] text-violet-400 uppercase font-black tracking-widest">Active Operations</span>
        <div class="text-2xl font-bold text-white">{{ projects.length }}</div>
      </div>
    </header>

    <div class="bg-[#121214] border border-white/5 rounded-3xl p-6 shadow-2xl">
      <ProjectsTable :projects="projects" @refresh="fetchProjects" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useAuthStore } from '../stores/auth';
import apiClient from '../api';
import ProjectsTable from '../components/ProjectsTable.vue';

const auth = useAuthStore();
const projects = ref([]);

const fetchProjects = async () => {
  try {
    const res = await apiClient.get('/projects/');
    projects.value = res.data;
  } catch (e) {
    projects.value = [];
  }
};

onMounted(fetchProjects);
</script>