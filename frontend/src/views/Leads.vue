<template>
  <div class="space-y-8">
    <header class="flex justify-between items-end">
      <div>
        <h1 class="text-4xl font-bold tracking-tight text-white">Leads Management</h1>
        <p class="text-slate-400 mt-1">Acquisition pipeline for Qmexai Digital.</p>
      </div>
      <div class="bg-[#121214] border border-white/5 px-6 py-3 rounded-2xl shadow-xl">
        <span class="text-[10px] text-blue-400 uppercase font-black tracking-widest">Live Pipeline</span>
        <div class="text-2xl font-bold text-white">{{ leads.length }} <span class="text-sm font-normal text-slate-500">Entities</span></div>
      </div>
    </header>

    <div class="bg-[#121214] border border-white/5 rounded-3xl p-6 shadow-2xl transition-all hover:border-white/10">
      <LeadsTable :leads="leads" @refresh="fetchLeads" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import apiClient from '../api';
import LeadsTable from '../components/LeadsTable.vue';

const leads = ref([]);

const fetchLeads = async () => {
  try {
    const res = await apiClient.get('/leads/');
    leads.value = res.data;
  } catch (e) {
    console.error("Leads fetch error:", e);
    leads.value = [];
  }
};

onMounted(fetchLeads);
</script>