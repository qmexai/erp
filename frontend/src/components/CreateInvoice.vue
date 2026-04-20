<template>
  <div class="fixed inset-0 flex items-center justify-center bg-black bg-opacity-70 z-50">
    <div class="bg-[#18181b] p-8 rounded-xl w-full max-w-3xl border border-white/10">
      <h2 class="text-2xl font-bold mb-6 text-white">Create New Invoice</h2>
      <form @submit.prevent="submitInvoice">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          <select v-model="invoice.project" class="w-full px-3 py-2 rounded bg-[#23232b] border border-white/10 text-white" required>
            <option disabled value="">Select a Project</option>
            <option v-for="project in projects" :key="project.id" :value="project.id">{{ project.name }}</option>
          </select>
          <input v-model="invoice.invoice_number" placeholder="Invoice Number" class="w-full px-3 py-2 rounded bg-[#23232b] border border-white/10 text-white" required />
          <input v-model="invoice.due_date" type="date" placeholder="Due Date" class="w-full px-3 py-2 rounded bg-[#23232b] border border-white/10 text-white" required />
        </div>

        <h3 class="text-lg font-semibold mt-6 mb-2 text-white">Line Items</h3>
        <div v-for="(item, index) in invoice.line_items" :key="index" class="flex gap-2 mb-2 items-center">
          <input v-model="item.description" placeholder="Description" class="w-full px-3 py-2 rounded bg-[#23232b] border border-white/10 text-white" />
          <input v-model.number="item.quantity" type="number" placeholder="Qty" class="w-24 px-3 py-2 rounded bg-[#23232b] border border-white/10 text-white" />
          <input v-model.number="item.unit_price" type="number" placeholder="Price" class="w-32 px-3 py-2 rounded bg-[#23232b] border border-white/10 text-white" />
          <button @click.prevent="removeLineItem(index)" class="text-red-500">&times;</button>
        </div>
        <button @click.prevent="addLineItem" class="text-blue-400 mt-2">+ Add Line Item</button>

        <div class="flex justify-end gap-4 mt-8">
          <button type="button" @click="$emit('close')" class="px-4 py-2 bg-gray-700 text-white rounded-lg">Cancel</button>
          <button type="submit" class="px-4 py-2 bg-blue-600 text-white rounded-lg">Create Invoice</button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import apiClient from '../api'; // Import the new API client

const emit = defineEmits(['close', 'invoice-created']);
const projects = ref([]);

const invoice = ref({
  project: '',
  invoice_number: `INV-${Date.now()}`,
  due_date: '',
  line_items: [{ description: '', quantity: 1, unit_price: 0 }]
});

const fetchProjects = async () => {
  try {
    const response = await apiClient.get('/projects/');
    projects.value = response.data;
  } catch (error) {
    console.error('Error fetching projects:', error);
  }
};

const addLineItem = () => {
  invoice.value.line_items.push({ description: '', quantity: 1, unit_price: 0 });
};

const removeLineItem = (index) => {
  invoice.value.line_items.splice(index, 1);
};

const submitInvoice = async () => {
  try {
    // First, create the invoice
    const invoicePayload = {
      project: invoice.value.project,
      invoice_number: invoice.value.invoice_number,
      due_date: invoice.value.due_date,
      status: 'Draft',
    };
    const invoiceRes = await apiClient.post('/invoices/', invoicePayload);
    const createdInvoice = invoiceRes.data;

    // Then, create the line items for that invoice
    for (const item of invoice.value.line_items) {
      const lineItemPayload = {
        invoice: createdInvoice.id,
        ...item
      };
      await apiClient.post('/lineitems/', lineItemPayload);
    }
    
    emit('invoice-created');
    emit('close');
  } catch (error) {
    console.error('Error creating invoice:', error);
    alert('Failed to create invoice.');
  }
};

onMounted(fetchProjects);
</script>
