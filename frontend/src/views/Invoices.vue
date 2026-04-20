<template>
  <div class="space-y-8 bg-[#09090b] min-h-screen text-white">
    <header class="flex justify-between items-center">
      <div>
        <h1 class="text-4xl font-bold tracking-tight text-white">Invoices</h1>
        <p class="text-slate-400 mt-1">Manage and generate client billing documents.</p>
      </div>
      <button class="bg-white text-black font-bold px-6 py-3 rounded-xl hover:bg-slate-200 transition-all shadow-xl">
        + Create Invoice
      </button>
    </header>

    <div class="bg-[#121214] border border-white/5 rounded-3xl p-6 shadow-2xl min-h-[400px]">
      <div v-if="loading" class="flex flex-col items-center justify-center py-20 space-y-4">
        <div class="w-10 h-10 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
        <p class="text-slate-500 animate-pulse">Fetching Qmexai Records...</p>
      </div>
      
      <div v-else-if="invoices.length > 0">
        <InvoicesTable :invoices="invoices" />
      </div>

      <div v-else class="flex flex-col items-center justify-center py-20 text-slate-500 italic">
        <svg class="w-16 h-16 mb-4 opacity-20" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M9 12h6m-6 4h6m2 5H7a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5.586a1 1 0 0 1 .707.293l5.414 5.414a1 1 0 0 1 .293.707V19a2 2 0 0 1-2 2z" /></svg>
        No invoices found for this period.
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import apiClient from '../api';
import InvoicesTable from '../components/InvoicesTable.vue';

const invoices = ref([]);
const loading = ref(true);

onMounted(async () => {
  try {
    loading.value = true;
    const res = await apiClient.get('/invoices/');
    invoices.value = res.data;
  } catch (e) {
    console.error("Invoice error", e);
    invoices.value = [];
  } finally {
    // Small delay to ensure smooth transition
    setTimeout(() => { loading.value = false; }, 500);
  }
});
</script>