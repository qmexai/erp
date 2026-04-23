<template>
  <div class="panel">
    <div class="panel-hd">
      <div class="panel-title">
        <span class="accent indigo"></span>
        Invoices
      </div>
      <button class="panel-btn" @click="showCreateInvoiceModal = true">
        + Create Invoice
      </button>
    </div>

    <div class="panel-bd">
      <table class="tbl">
        <thead>
          <tr>
            <th>Invoice #</th>
            <th>Project</th>
            <th>Issue Date</th>
            <th>Due Date</th>
            <th>Status</th>
            <th>Total</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="invoice in invoices" :key="invoice.id">
            <td class="mono font-semibold">{{ invoice.invoice_number }}</td>
            <td class="font-medium text-[var(--qx-text1)]">{{ invoice.project_name }}</td>
            <td class="mono text-[12px]">{{ invoice.issue_date }}</td>
            <td class="mono text-[12px]">{{ invoice.due_date }}</td>
            <td>
              <select 
                v-model="invoice.status" 
                @change="handleStatusChange(invoice, $event)"
                class="px-2 py-1 rounded text-[11px] font-bold uppercase tracking-wider cursor-pointer outline-none transition-colors border"
                :class="{
                  'bg-green-500/10 text-green-400 border-green-500/20': invoice.status === 'Paid',
                  'bg-yellow-500/10 text-yellow-400 border-yellow-500/20': invoice.status === 'Unpaid' || invoice.status === 'Draft' || invoice.status === 'Sent',
                  'bg-red-500/10 text-red-400 border-red-500/20': invoice.status === 'Overdue'
                }"
              >
                <option value="Draft" class="bg-[var(--qx-bg1)] text-[var(--qx-text1)]">Draft</option>
                <option value="Unpaid" class="bg-[var(--qx-bg1)] text-[var(--qx-text1)]">Unpaid</option>
                <option value="Paid" class="bg-[var(--qx-bg1)] text-[var(--qx-text1)]">Paid</option>
                <option value="Overdue" class="bg-[var(--qx-bg1)] text-[var(--qx-text1)]">Overdue</option>
              </select>
            </td>
            <td class="mono font-bold text-[var(--qx-green)]">{{ formatCurrency(invoice.total_amount || 0) }}</td>
            <td>
              <button @click="viewInvoice(invoice)" class="text-[12px] text-blue-400 hover:text-blue-300 mr-3">View</button>
            </td>
          </tr>
          <tr v-if="invoices.length === 0">
             <td colspan="7" class="py-8 text-center text-[var(--qx-text3)]">No invoices found.</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Create Invoice Modal -->
    <CreateInvoiceModal v-if="showCreateInvoiceModal" @close="showCreateInvoiceModal = false" @invoice-created="handleInvoiceCreated" />
    
    <!-- View/Edit Invoice Modal -->
    <div v-if="showViewModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
      <div class="bg-[var(--qx-bg1)] p-6 rounded-xl w-[500px] border border-[var(--qx-border)] shadow-2xl">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-bold text-[var(--qx-text1)]">Invoice Details</h3>
          <button @click="closeViewModal" class="text-gray-400 hover:text-white">&times;</button>
        </div>
        
        <div class="space-y-4" v-if="viewingInvoice">
          <div class="grid grid-cols-2 gap-4">
             <div>
               <label class="block text-xs font-semibold mb-1 text-[var(--qx-text2)] uppercase">Invoice #</label>
               <div class="text-[var(--qx-text1)] font-mono">{{ viewingInvoice.invoice_number }}</div>
             </div>
             <div>
               <label class="block text-xs font-semibold mb-1 text-[var(--qx-text2)] uppercase">Status</label>
               <div class="text-[var(--qx-text1)] font-bold">{{ viewingInvoice.status }}</div>
             </div>
          </div>
          <div>
            <label class="block text-xs font-semibold mb-1 text-[var(--qx-text2)] uppercase">Project</label>
            <div class="text-[var(--qx-text1)]">{{ viewingInvoice.project_name }}</div>
          </div>
          <div class="grid grid-cols-2 gap-4">
             <div>
               <label class="block text-xs font-semibold mb-1 text-[var(--qx-text2)] uppercase">Issue Date</label>
               <input v-model="viewingInvoice.issue_date" type="date" class="w-full px-2 py-1 rounded bg-[var(--qx-bg2)] border border-[var(--qx-border)] focus:border-[var(--qx-green)] focus:outline-none text-[var(--qx-text1)] text-sm" />
             </div>
             <div>
               <label class="block text-xs font-semibold mb-1 text-[var(--qx-text2)] uppercase">Due Date</label>
               <input v-model="viewingInvoice.due_date" type="date" class="w-full px-2 py-1 rounded bg-[var(--qx-bg2)] border border-[var(--qx-border)] focus:border-[var(--qx-green)] focus:outline-none text-[var(--qx-text1)] text-sm" />
             </div>
          </div>
          
          <div class="mt-4 pt-4 border-t border-[var(--qx-border)]">
             <label class="block text-xs font-semibold mb-1 text-[var(--qx-text2)] uppercase">Total Amount</label>
             <div class="text-xl font-bold text-[var(--qx-green)]">{{ formatCurrency(viewingInvoice.total_amount) }}</div>
             <div v-if="viewingInvoice.status === 'Paid'" class="mt-2 text-xs text-gray-400">Paid via: {{ viewingInvoice.payment_method }}<br>Txn ID: {{ viewingInvoice.transaction_id || 'N/A' }}</div>
          </div>
        </div>

        <div class="flex justify-end gap-3 mt-6">
          <button @click="closeViewModal" class="px-4 py-2 bg-[var(--qx-bg3)] hover:bg-[var(--qx-bg4)] rounded text-sm text-[var(--qx-text2)] transition-colors">Close</button>
          <button @click="saveInvoiceUpdates" :disabled="isSaving" class="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded text-sm font-medium transition-colors disabled:opacity-50">
             {{ isSaving ? 'Saving...' : 'Save Updates' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Payment Modal -->
    <div v-if="showPaymentModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
      <div class="bg-[var(--qx-bg1)] p-6 rounded-xl w-96 border border-[var(--qx-border)] shadow-2xl">
        <h3 class="text-lg font-bold mb-4 text-[var(--qx-text1)]">Record Payment</h3>
        <p class="text-xs text-[var(--qx-text3)] mb-4">Invoice: <span class="font-mono">{{ selectedInvoice?.invoice_number }}</span></p>
        
        <div class="mb-4">
          <label class="block text-xs font-semibold mb-1 text-[var(--qx-text2)] uppercase tracking-wide">Payment Method</label>
          <select v-model="paymentForm.method" class="w-full px-3 py-2 rounded bg-[var(--qx-bg2)] border border-[var(--qx-border)] focus:border-[var(--qx-green)] focus:outline-none text-[var(--qx-text1)] text-sm">
            <option value="Bank Transfer">Bank Transfer</option>
            <option value="UPI">UPI</option>
            <option value="Cash">Cash</option>
            <option value="Credit Card">Credit Card</option>
            <option value="Other">Other</option>
          </select>
        </div>
        <div class="mb-8">
          <label class="block text-xs font-semibold mb-1 text-[var(--qx-text2)] uppercase tracking-wide">Transaction ID</label>
          <input v-model="paymentForm.transaction_id" type="text" class="w-full px-3 py-2 rounded bg-[var(--qx-bg2)] border border-[var(--qx-border)] focus:border-[var(--qx-green)] focus:outline-none text-[var(--qx-text1)] text-sm font-mono placeholder:font-sans" placeholder="Enter Txn ID" />
        </div>
        <div class="flex justify-end gap-3">
          <button @click="cancelPayment" class="px-4 py-2 bg-[var(--qx-bg3)] hover:bg-[var(--qx-bg4)] rounded text-sm text-[var(--qx-text2)] transition-colors">Cancel</button>
          <button @click="confirmPayment" :disabled="isSaving" class="px-4 py-2 bg-[var(--qx-green-d)] hover:bg-[var(--qx-green)] text-[var(--qx-green)] hover:text-white rounded text-sm font-medium transition-colors disabled:opacity-50">
             {{ isSaving ? 'Saving...' : 'Save Payment' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '../api';
import CreateInvoiceModal from './CreateInvoiceModal.vue';
import { formatCurrency } from '../utils/formatters';

const invoices = ref([]);
const showCreateInvoiceModal = ref(false);
const showPaymentModal = ref(false);
const showViewModal = ref(false);
const selectedInvoice = ref(null);
const viewingInvoice = ref(null);
const previousStatus = ref('');
const isSaving = ref(false);

const paymentForm = ref({
  method: 'Bank Transfer',
  transaction_id: ''
});

const checkAndSetOverdue = async (invoice) => {
    if (invoice.status === 'Paid') return;
    
    const today = new Date();
    // Normalize to midnight for accurate day comparison
    today.setHours(0, 0, 0, 0); 
    
    const dueDate = new Date(invoice.due_date);
    if (dueDate < today && invoice.status !== 'Overdue') {
        invoice.status = 'Overdue';
        try {
            await api.patch(`/invoices/${invoice.id}/`, { status: 'Overdue' });
        } catch (e) {
            console.error('Failed to update overdue status', e);
        }
    } else if (dueDate >= today && invoice.status === 'Overdue') {
        invoice.status = 'Unpaid';
        try {
            await api.patch(`/invoices/${invoice.id}/`, { status: 'Unpaid' });
        } catch (e) {
            console.error('Failed to update status', e);
        }
    }
    // Map Sent/Pending to Unpaid visually internally if needed, though choice is Unpaid
    if (invoice.status === 'Sent' || invoice.status === 'Pending') {
         invoice.status = 'Unpaid';
    }
};

const fetchInvoices = async () => {
  try {
    const response = await api.get('/invoices/');
    // Auto-update overdue states on load
    invoices.value = response.data.map(inv => {
        if(inv.status === 'Sent' || inv.status === 'Pending') inv.status = 'Unpaid';
        return inv;
    });
    
    // Check overdue statuses concurrently
    await Promise.all(invoices.value.map(inv => checkAndSetOverdue(inv)));
    
  } catch (error) {
    console.error('Error fetching invoices:', error);
  }
};

const handleInvoiceCreated = (newInvoice) => {
  if (newInvoice.status === 'Sent' || newInvoice.status === 'Pending') newInvoice.status = 'Unpaid';
  checkAndSetOverdue(newInvoice);
  invoices.value.unshift(newInvoice);
  showCreateInvoiceModal.value = false;
};

const handleStatusChange = async (invoice, event) => {
    const newStatus = event.target.value;
    
    if (newStatus === 'Paid') {
        // Stop default change momentarily, open modal
        invoice.status = previousStatus.value || invoice.status;
        if(invoice.status === 'Paid') invoice.status = 'Unpaid'; // fallback if was already paid somehow
        selectedInvoice.value = invoice;
        previousStatus.value = invoice.status;
        paymentForm.value = { method: 'Bank Transfer', transaction_id: '' };
        showPaymentModal.value = true;
    } else {
        // Just save normally
        try {
            await api.patch(`/invoices/${invoice.id}/`, { status: newStatus });
        } catch (error) {
            alert('Failed to update status');
            console.error(error);
        }
    }
};

const cancelPayment = () => {
    if (selectedInvoice.value) {
        selectedInvoice.value.status = previousStatus.value;
    }
    showPaymentModal.value = false;
    selectedInvoice.value = null;
};

const confirmPayment = async () => {
    if (!selectedInvoice.value) return;
    
    isSaving.value = true;
    try {
        await api.patch(`/invoices/${selectedInvoice.value.id}/`, {
            status: 'Paid',
            payment_method: paymentForm.value.method,
            transaction_id: paymentForm.value.transaction_id
        });
        
        selectedInvoice.value.status = 'Paid';
        showPaymentModal.value = false;
        selectedInvoice.value = null;
    } catch (error) {
        alert('Error saving payment details.');
        console.error(error);
    } finally {
        isSaving.value = false;
    }
};

const viewInvoice = (invoice) => {
  viewingInvoice.value = JSON.parse(JSON.stringify(invoice));
  showViewModal.value = true;
};

const closeViewModal = () => {
    showViewModal.value = false;
    viewingInvoice.value = null;
};

const saveInvoiceUpdates = async () => {
    if(!viewingInvoice.value) return;
    isSaving.value = true;
    try {
        await api.patch(`/invoices/${viewingInvoice.value.id}/`, {
            issue_date: viewingInvoice.value.issue_date,
            due_date: viewingInvoice.value.due_date
        });
        
        const idx = invoices.value.findIndex(i => i.id === viewingInvoice.value.id);
        if (idx !== -1) invoices.value[idx] = { ...viewingInvoice.value };
        
        closeViewModal();
    } catch(e) {
        alert("Failed to update invoice");
        console.error(e);
    } finally {
        isSaving.value = false;
    }
};

onMounted(() => {
    fetchInvoices();
});
</script>
