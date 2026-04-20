<template>
  <div class="space-y-8 min-h-screen bg-[#09090b] text-white">
    <header class="grid grid-cols-1 lg:grid-cols-3 gap-6 items-center">
      <div>
        <h1 class="text-4xl font-bold tracking-tight text-white">Finance</h1>
        <p class="text-slate-400 mt-1">Real-time revenue & expense tracking.</p>
      </div>
      
      <div class="bg-blue-600/5 border border-blue-500/20 p-5 rounded-2xl flex justify-between items-center shadow-lg">
        <div>
          <span class="text-[10px] text-blue-400 uppercase font-black tracking-widest">Total Balance</span>
          <div class="text-3xl font-bold text-white">₹{{ currentBalance.toLocaleString() }}</div>
        </div>
        <div class="h-12 w-12 bg-blue-600 rounded-xl flex items-center justify-center shadow-lg shadow-blue-500/20">
          <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 1.343-3 3s1.343 3 3 3 3-1.343 3-3-1.343-3-3-3zM12 8V7m0 1v1m0 0a4 4 0 100 8 4 4 0 000-8z" /></svg>
        </div>
      </div>

      <div class="bg-[#121214] border border-white/5 p-5 rounded-2xl flex items-center justify-center gap-4">
        <input v-model="filterFrom" type="date" class="bg-[#09090b] border border-white/10 rounded-lg p-2 text-xs text-white focus:border-blue-500 transition-all outline-none" />
        <span class="text-slate-600 font-bold">→</span>
        <input v-model="filterTo" type="date" class="bg-[#09090b] border border-white/10 rounded-lg p-2 text-xs text-white focus:border-blue-500 transition-all outline-none" />
      </div>
    </header>
    
    <div class="bg-[#121214] border border-white/5 rounded-3xl p-6 shadow-2xl overflow-hidden">
      <div class="overflow-x-auto">
        <FinanceTable :records="filteredRecords" class="text-white w-full" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import apiClient from '../api';
import FinanceTable from '../components/FinanceTable.vue';

const records = ref([]);
const filterFrom = ref('');
const filterTo = ref('');

// Logic for the requested Date Filter
const filteredRecords = computed(() => {
  if (!filterFrom.value || !filterTo.value) return records.value;
  const start = new Date(filterFrom.value);
  const end = new Date(filterTo.value);
  return records.value.filter(record => {
    const d = new Date(record.date);
    return d >= start && d <= end;
  });
});

const currentBalance = computed(() => {
  return records.value.reduce((acc, curr) => 
    curr.type === 'Revenue' ? acc + Number(curr.amount) : acc - Number(curr.amount), 0
  );
});

onMounted(async () => {
  try {
    const res = await apiClient.get('/finance/');
    records.value = res.data;
  } catch (e) {
    console.error("Finance load error", e);
    records.value = [];
  }
});
</script>