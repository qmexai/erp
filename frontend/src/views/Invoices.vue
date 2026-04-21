<template>
  <div class="space-y-8 bg-[#09090b] min-h-screen text-white p-8">
    <header class="flex justify-between items-center">
      <div>
        <h1 class="text-4xl font-bold tracking-tight text-white">Invoices</h1>
        <p class="text-slate-400 mt-1">Manage and generate client billing documents.</p>
      </div>
      <button 
        @click="handleCreateInvoice"
        :disabled="creating"
        class="bg-white text-black font-bold px-6 py-3 rounded-xl hover:bg-slate-200 disabled:opacity-50 transition-all shadow-xl"
      >
        {{ creating ? 'Creating...' : '+ Create Invoice' }}
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
        <svg class="w-16 h-16 mb-4 opacity-20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path d="M9 12h6m-6 4h6m2 5H7a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5.586a1 1 0 0 1 .707.293l5.414 5.414a1 1 0 0 1 .293.707V19a2 2 0 0 1-2 2z" />
        </svg>
        No invoices found. Click "Create" to start.
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
const creating = ref(false);

const fetchInvoices = async () => {
  try {
    loading.value = true;
    // Added trailing slash to match Django standard
    const res = await apiClient.get('/invoices/');
    // If you use pagination, it's res.data.results. Otherwise res.data
    invoices.value = res.data.results || res.data;
  } catch (e) {
    console.error("Invoice fetch error:", e);
  } finally {
    loading.value = false;
  }
};

const handleCreateInvoice = async () => {
  try {
    creating.value = true;
    
    // IMPORTANT: In your models.py, 'project' and 'due_date' are required.
    // Ensure at least one project exists in your DB before running this.
    const payload = {
      project: 1, // ID of an existing project
      due_date: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0], // 7 days from now
      status: 'Unpaid',
      total_amount: 0.00
    };

    const res = await apiClient.post('/invoices/', payload);
    
    // Add the new invoice to the list and notify user
    invoices.value.unshift(res.data);
    alert("Invoice Generated! You can now add line items in the table.");
  } catch (e) {
    console.error("Creation Error:", e.response?.data || e.message);
    alert("Failed to create invoice. Make sure a Project with ID 1 exists.");
  } finally {
    creating.value = false;
  }
};

onMounted(fetchInvoices);
</script>