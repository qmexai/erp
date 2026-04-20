<template>
  <div v-if="show" class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
    <div class="bg-[#18181b] rounded-2xl p-8 w-full max-w-lg border border-white/10 shadow-xl">
      <h2 class="text-xl font-bold text-white mb-6">Create a New Task</h2>
      <form @submit.prevent="submitTask" class="space-y-4">
        <input v-model="form.title" placeholder="Task Title" class="w-full px-4 py-3 rounded-lg bg-[#23232b] border border-white/10 text-white focus:outline-none focus:ring-2 focus:ring-blue-500 transition" required />
        <textarea v-model="form.description" placeholder="Description" rows="3" class="w-full px-4 py-3 rounded-lg bg-[#23232b] border border-white/10 text-white focus:outline-none focus:ring-2 focus:ring-blue-500 transition" />
        
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="text-xs text-slate-400 mb-1 block">Assign To</label>
            <select v-model="form.assigned_to_id" class="w-full px-3 py-3 rounded-lg bg-[#23232b] border border-white/10 text-white appearance-none focus:outline-none focus:ring-2 focus:ring-blue-500 transition">
              <option v-for="user in users" :key="user.id" :value="user.id">{{ user.email }}</option>
            </select>
          </div>
          <div>
            <label class="text-xs text-slate-400 mb-1 block">Due Date</label>
            <input v-model="form.due_date" type="date" class="w-full px-3 py-3 rounded-lg bg-[#23232b] border border-white/10 text-white appearance-none focus:outline-none focus:ring-2 focus:ring-blue-500 transition" />
          </div>
        </div>

        <div class="flex justify-end gap-4 pt-4">
          <button type="button" @click="$emit('close')" class="px-6 py-2.5 bg-gray-700/50 text-slate-300 font-semibold rounded-lg hover:bg-gray-700/80 transition">Cancel</button>
          <button type="submit" :disabled="isSubmitting" class="px-6 py-2.5 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-500 disabled:opacity-50 transition">
            <span v-if="isSubmitting">Creating...</span>
            <span v-else>Create Task</span>
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import api from '../api';
import { useAuthStore } from '../stores/auth';

const props = defineProps({ show: Boolean });
const emit = defineEmits(['close', 'created']);

const auth = useAuthStore();
const users = ref([]);
const isSubmitting = ref(false);

const form = ref({
  title: '',
  description: '',
  assigned_to_id: null,
  due_date: ''
});

// Set default assigned_to_id when auth store is ready
watch(() => auth.user, (newUser) => {
  if (newUser) {
    form.value.assigned_to_id = newUser.id;
  }
}, { immediate: true });


const fetchUsers = async () => {
  try {
    const response = await api.get('/users/');
    users.value = response.data;
  } catch (error) {
    console.error('Error fetching users:', error);
  }
};

const submitTask = async () => {
  if (isSubmitting.value) return;
  isSubmitting.value = true;
  try {
    await api.post('/tasks/', form.value);
    emit('created');
    emit('close');
  } catch (error) {
    console.error('Error creating task:', error.response?.data || error);
    // Optionally, show an error message to the user
  } finally {
    isSubmitting.value = false;
  }
};

onMounted(() => {
  fetchUsers();
});
</script>
