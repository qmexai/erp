<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md overflow-y-auto" @click.self="$emit('close')">
    <div class="relative w-full max-w-4xl bg-[#121214] border border-white/10 shadow-2xl rounded-3xl overflow-hidden my-8">
      
      <div class="px-8 pt-8 pb-4">
        <h3 class="text-2xl font-bold text-white tracking-tight">Create New Invoice</h3>
        <p class="text-slate-400 text-sm">Draft a professional billing document for Qmexai clients.</p>
      </div>

      <div class="p-8">
        <form @submit.prevent="submitInvoice" class="space-y-8">
          
          <div class="grid grid-cols-1 md:grid-cols-2 gap-8 bg-white/[0.02] p-6 rounded-2xl border border-white/5">
            <div>
              <label class="block text-[10px] font-black text-slate-500 uppercase tracking-widest mb-2">Project</label>
              <select v-model="invoice.project" class="w-full bg-black/40 border border-white/10 rounded-xl py-3 px-4 text-white focus:border-blue-500/50 outline-none transition-all appearance-none">
                <option disabled value="" class="bg-[#121214]">Select a Project</option>
                <option v-for="project in projects" :key="project.id" :value="project.id" class="bg-[#121214]">
                  {{ project.name }}
                </option>
              </select>
            </div>
            <div>
              <label class="block text-[10px] font-black text-slate-500 uppercase tracking-widest mb-2">Due Date</label>
              <input type="date" v-model="invoice.due_date" class="w-full bg-black/40 border border-white/10 rounded-xl py-3 px-4 text-white focus:border-blue-500/50 outline-none transition-all">
            </div>
          </div>

          <div v-if="!createdInvoice">
            <div>
              <div class="flex justify-between items-center mb-4">
                <h4 class="text-xs font-black text-slate-500 uppercase tracking-widest">Line Items</h4>
                <button type="button" @click="addLineItem" class="text-xs font-bold text-blue-400 hover:text-blue-300 transition-colors">+ Add Item</button>
              </div>

              <div class="space-y-3">
                <div v-for="(item, index) in invoice.line_items_data" :key="index" class="grid grid-cols-12 gap-3 items-center bg-white/[0.02] p-3 rounded-xl border border-white/5 group">
                  <div class="col-span-6">
                    <input type="text" v-model="item.description" placeholder="Service description" class="w-full bg-transparent border-none text-sm text-white focus:ring-0 placeholder:text-slate-600">
                  </div>
                  <div class="col-span-2">
                    <input type="number" v-model.number="item.quantity" placeholder="Qty" class="w-full bg-black/20 border border-white/10 rounded-lg py-1.5 px-2 text-sm text-white text-center">
                  </div>
                  <div class="col-span-2">
                    <input type="number" v-model.number="item.unit_price" placeholder="Price" class="w-full bg-black/20 border border-white/10 rounded-lg py-1.5 px-2 text-sm text-white text-right">
                  </div>
                  <div class="col-span-1 text-right text-xs font-bold text-slate-300">
                    {{ (item.quantity * item.unit_price).toFixed(2) }}
                  </div>
                  <div class="col-span-1 text-center">
                    <button type="button" @click="removeLineItem(index)" class="text-slate-600 hover:text-red-500 transition-colors">&times;</button>
                  </div>
                </div>
              </div>
            </div>

            <div class="flex justify-end pt-6 border-t border-white/5">
              <div class="w-full max-w-xs space-y-3">
                <div class="flex justify-between text-sm text-slate-400">
                  <span>Subtotal</span>
                  <span class="text-white font-mono">₹{{ subTotal.toFixed(2) }}</span>
                </div>
                <div class="flex justify-between items-center text-sm text-slate-400">
                  <span>Discount (%)</span>
                  <input type="number" v-model.number="invoice.discount" class="w-16 bg-black/40 border border-white/10 rounded-lg py-1 px-2 text-right text-xs text-white">
                </div>
                <div class="flex justify-between pt-3 border-t border-white/5">
                  <span class="text-lg font-bold text-white">Total Amount</span>
                  <span class="text-lg font-bold text-blue-400 font-mono">₹{{ totalAmount.toFixed(2) }}</span>
                </div>
              </div>
            </div>
          </div>

          <div v-if="createdInvoice" class="text-center p-8 bg-green-900/20 rounded-2xl border border-green-500/20">
            <h4 class="text-xl font-bold text-green-400">Invoice Created Successfully!</h4>
            <p class="text-slate-400 mt-2">Invoice <span class="font-bold text-white">{{ createdInvoice.invoice_number }}</span> has been generated.</p>
            <div class="mt-6 flex justify-center gap-4">
              <button @click="downloadInvoicePDF" class="px-6 py-3 bg-blue-600 text-white font-bold rounded-xl hover:bg-blue-500 shadow-lg shadow-blue-600/30 transition-all">
                Download PDF
              </button>
              <button @click="$emit('close')" class="px-6 py-3 bg-white/5 text-slate-400 font-bold rounded-xl hover:bg-white/10 transition-all">
                Close
              </button>
            </div>
          </div>

          <div v-if="!createdInvoice" class="flex gap-4 pt-4">
            <button type="button" @click="$emit('close')" class="flex-1 py-4 bg-white/5 text-slate-400 font-bold rounded-2xl hover:bg-white/10 transition-all">
              Cancel
            </button>
            <button type="submit" :disabled="isSubmitting" class="flex-1 py-4 bg-blue-600 text-white font-bold rounded-2xl hover:bg-blue-500 shadow-lg shadow-blue-600/30 transition-all disabled:opacity-50">
              <span v-if="isSubmitting">Creating...</span>
              <span v-else>Create Invoice</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import api from '../api';

const emit = defineEmits(['close', 'invoice-created']);

const projects = ref([]);
const invoice = ref({
  project: '',
  issue_date: new Date().toISOString().slice(0, 10),
  due_date: '',
  status: 'Draft',
  discount: 0,
  line_items_data: [
    { description: '', quantity: 1, unit_price: 0 },
  ],
});

const createdInvoice = ref(null);
const isSubmitting = ref(false);

onMounted(async () => {
  try {
    const response = await api.get('/projects/');
    projects.value = response.data;
  } catch (error) {
    console.error('Error fetching projects:', error);
  }
});

const subTotal = computed(() => {
  return invoice.value.line_items_data.reduce((acc, item) => {
    return acc + (item.quantity * item.unit_price);
  }, 0);
});

const totalAmount = computed(() => {
  const discountAmount = subTotal.value * (invoice.value.discount / 100);
  return subTotal.value - discountAmount;
});

const addLineItem = () => {
  invoice.value.line_items_data.push({ description: '', quantity: 1, unit_price: 0 });
};

const removeLineItem = (index) => {
  if (invoice.value.line_items_data.length > 1) {
    invoice.value.line_items_data.splice(index, 1);
  }
};

const submitInvoice = async () => {
  isSubmitting.value = true;
  const payload = {
    ...invoice.value,
    sub_total: subTotal.value,
    total_amount: totalAmount.value,
  };
  try {
    const response = await api.post('/invoices/', payload);
    createdInvoice.value = response.data;
    emit('invoice-created', response.data);
  } catch (error) {
    console.error('Error creating invoice:', error.response?.data || error);
  } finally {
    isSubmitting.value = false;
  }
};

const downloadInvoicePDF = async () => {
  if (!createdInvoice.value) return;
  try {
    const response = await api.get(`/invoices/${createdInvoice.value.id}/download-pdf/`, {
      responseType: 'blob', // Important for file downloads
    });
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `invoice_${createdInvoice.value.invoice_number}.pdf`);
    document.body.appendChild(link);
    link.click();
    link.remove();
  } catch (error) {
    console.error('Error downloading invoice PDF:', error);
  }
};
</script>