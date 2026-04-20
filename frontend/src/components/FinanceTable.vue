<template>
  <div class="panel">
    <div class="panel-hd">
      <div class="panel-title">
        <span class="accent amber"></span>
        Finance & Accounts
      </div>
      <div class="flex items-center justify-end gap-3">
        <div class="text-right mr-4">
            <div class="text-[10px] text-[var(--qx-text3)] uppercase tracking-wider font-medium">Current Balance</div>
            <div class="text-[18px] font-bold text-[var(--qx-green)] font-mono">{{ formatCurrency(currentBalance) }}</div>
        </div>
        <button class="panel-btn" @click="downloadCSV">Export CSV</button>
        <button class="panel-btn" @click="showAdd = !showAdd">
          {{ showAdd ? '✕ Close' : '+ Add Record' }}
        </button>
      </div>
    </div>

    <transition name="fade">
      <div v-if="showAdd" class="p-4 bg-[var(--qx-bg2)] border-b border-[var(--qx-border)]">
        <form @submit.prevent="addRecord" class="flex gap-3">
          <select v-model="form.type" class="px-2 py-1 rounded bg-[var(--qx-bg1)] border border-[var(--qx-border)] text-[var(--qx-text1)] focus:outline-none text-[12px]">
            <option value="Revenue">Credit (Revenue)</option>
            <option value="Spend">Debit (Expense)</option>
          </select>
          <input 
            v-model.number="form.amount" 
            type="number" 
            required
            placeholder="Amount" 
            class="w-24 px-2 py-1 rounded bg-[var(--qx-bg1)] border border-[var(--qx-border)] text-[var(--qx-text1)] focus:outline-none text-[12px]" 
          />
          <input 
            v-model="form.category" 
            required
            placeholder="Category (e.g. Salary, Rent)" 
            class="w-1/4 px-2 py-1 rounded bg-[var(--qx-bg1)] border border-[var(--qx-border)] text-[var(--qx-text1)] focus:outline-none text-[12px]" 
          />
          <input 
            v-model="form.description" 
            placeholder="Description (Optional)" 
            class="flex-1 px-2 py-1 rounded bg-[var(--qx-bg1)] border border-[var(--qx-border)] text-[var(--qx-text1)] focus:outline-none text-[12px]" 
          />
          <button 
            type="submit" 
            :disabled="isSaving"
            class="px-3 py-1 bg-[var(--qx-green-d)] text-[var(--qx-green)] text-[12px] font-medium rounded hover:bg-[var(--qx-green)] hover:text-white transition-colors disabled:opacity-50"
          >
            {{ isSaving ? 'Saving...' : 'Save' }}
          </button>
        </form>
      </div>
    </transition>

    <div class="panel-bd">
      <table class="tbl">
        <thead>
          <tr>
            <th>Type</th>
            <th>Amount</th>
            <th>Category</th>
            <th>Description</th>
            <th>Date</th>
            <th>Added By</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="rec in records" :key="rec.id">
            <td>
              <span :class="['badge', isIncome(rec.type) ? 'active' : 'leave']">
                {{ rec.type }}
              </span>
            </td>
            <td class="mono font-semibold" :class="isIncome(rec.type) ? 'text-[var(--qx-green)]' : 'text-red-400'">
              {{ isIncome(rec.type) ? '+' : '-' }} {{ formatCurrency(rec.amount) }}
            </td>
            <td>{{ rec.category }}</td>
            <td class="fw text-[var(--qx-text2)]">{{ rec.description || '—' }}</td>
            <td class="mono text-[11px]">{{ fmtDate(rec.date) }}</td>
            <td class="text-[11px]">{{ rec.added_by_name || 'System' }}</td>
          </tr>
          <tr v-if="!records.length">
            <td colspan="6" class="empty-cell py-10 text-center text-[var(--qx-text3)]">No financial records found.</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import api from '../api';

// State Management
const records = ref([]);
const showAdd = ref(false);
const isSaving = ref(false);
const stats = ref({});
const form = ref({
  type: 'Revenue',
  amount: '',
  category: '',
  description: ''
});

// Data Fetching
const fetchRecords = async () => {
  try {
    const response = await api.get('/finance/');
    records.value = response.data;
  } catch (error) {
    console.error('Error fetching financial records:', error);
  }
};

const fetchStats = async () => {
  try {
    const response = await api.get('/dashboard/stats/');
    stats.value = response.data;
  } catch (error) {
    console.error('Error fetching dashboard stats:', error);
  }
};

// Computed
const currentBalance = computed(() => stats.value.current_balance || 0);

const isIncome = (type) => {
  const t = type.toLowerCase();
  return t === 'revenue' || t === 'income' || t === 'credit';
};

// Actions
const addRecord = async () => {
  if (!form.value.amount || !form.value.category) return;
  
  isSaving.value = true;
  try {
    await api.post('/finance/', form.value);
    showAdd.value = false;
    // Reset form
    Object.assign(form.value, { type: 'Revenue', amount: '', category: '', description: '' });
    // Refresh UI
    await Promise.all([fetchRecords(), fetchStats()]);
  } catch (error) {
    alert("Error saving record. Please check your inputs.");
    console.error('Error adding financial record:', error);
  } finally {
    isSaving.value = false;
  }
};

const downloadCSV = async () => {
  try {
    const response = await api.get('/finance/download/', { responseType: 'blob' });
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const a = document.createElement('a');
    a.href = url;
    a.download = `Qmexai_Finance_${new Date().toISOString().split('T')[0]}.csv`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    a.remove();
  } catch (error) {
    console.error('Error downloading CSV:', error);
  }
};

// Formatting Helpers
const formatCurrency = (value) => {
    // Set to INR for Kerala context
    return new Intl.NumberFormat('en-IN', { 
        style: 'currency', 
        currency: 'INR',
        maximumFractionDigits: 0 
    }).format(value);
}

const fmtDate = (dateString) => {
  if (!dateString) return '—';
  const date = new Date(dateString);
  return date.toLocaleDateString('en-GB', {
    day: '2-digit',
    month: 'short',
    year: 'numeric'
  });
};

onMounted(() => {
    fetchRecords();
    fetchStats();
});
</script>

<style scoped>
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>