<template>
  <div v-if="show" class="fixed inset-0 z-50 flex items-center justify-center bg-black/60" @click.self="$emit('close')">
    <div class="bg-[#18181b] rounded-2xl p-8 w-full max-w-lg border border-white/10 shadow-xl">
      <h2 class="text-xl font-bold text-white mb-4">Convert Lead to Project</h2>
      <p class="text-gray-400 mb-2">
        You are about to convert the lead for <strong class="text-white">{{ lead.client_name }}</strong> from <strong class="text-white">{{ lead.company_name }}</strong> into a new project.
      </p>
      <p class="text-gray-400 mb-6">
        Please confirm or add the services required for this new project.
      </p>
      <form @submit.prevent="handleConvert" class="space-y-4">
        <div>
          <label for="services" class="block text-sm font-medium text-gray-300 mb-1">Services Needed</label>
          <input
            id="services"
            v-model="services"
            placeholder="e.g., Web Development, SEO, Marketing"
            class="w-full px-3 py-2 rounded bg-[#23232b] border border-white/10 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            required
          />
          <p class="text-xs text-gray-500 mt-1">Separate multiple services with a comma.</p>
        </div>
        <div class="flex justify-end gap-4 pt-4">
          <button type="button" @click="$emit('close')" class="px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-lg transition-colors">Cancel</button>
          <button type="submit" class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors">Confirm Conversion</button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue';
import apiClient from '../api';

const props = defineProps({
  show: Boolean,
  lead: Object,
});

const emit = defineEmits(['close', 'converted']);

const services = ref('');

// When the lead prop changes, update the services field
watch(() => props.lead, (newLead) => {
  if (newLead && newLead.services_needed) {
    services.value = Array.isArray(newLead.services_needed)
      ? newLead.services_needed.join(', ')
      : newLead.services_needed;
  } else {
    services.value = '';
  }
});

const handleConvert = async () => {
  if (!props.lead) return;

  try {
    const servicesArray = services.value.split(',').map(s => s.trim()).filter(s => s);
    await apiClient.post(`/leads/${props.lead.id}/convert_to_project/`, {
      services_needed: servicesArray,
    });
    emit('converted');
    emit('close');
  } catch (error) {
    console.error('Failed to convert lead to project:', error);
    // Optionally, show an error message to the user
  }
};
</script>
