<template>
  <div v-if="show" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md overflow-y-auto" @click.self="close">
    <div class="relative w-full max-w-md bg-[#121214] border border-white/10 shadow-2xl rounded-3xl overflow-hidden transform transition-all">
      
      <div class="px-8 pt-8 pb-4 text-center">
        <h3 class="text-2xl font-bold text-white tracking-tight">Request Leave</h3>
        <p class="text-slate-400 text-sm mt-1">Submit your time-off request for CEO approval.</p>
      </div>

      <div class="px-8 py-6">
        <form @submit.prevent="submitLeaveRequest" class="space-y-5">
          <div>
            <label for="leave_type" class="block text-[10px] font-black text-slate-500 uppercase tracking-widest mb-2 text-left">Leave Type</label>
            <select v-model="leaveRequest.leave_type" id="leave_type" class="w-full bg-black/40 border border-white/10 rounded-xl py-3 px-4 text-white focus:border-blue-500/50 outline-none transition-all appearance-none cursor-pointer">
              <option class="bg-[#121214]">SICK</option>
              <option class="bg-[#121214]">CASUAL</option>
              <option class="bg-[#121214]">EMERGENCY</option>
              <option class="bg-[#121214]">STUDY</option>
              <option class="bg-[#121214]">MATERNITY</option>
              <option class="bg-[#121214]">PATERNITY</option>
              <option class="bg-[#121214]">OTHER</option>
            </select>
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div>
              <label for="start_date" class="block text-[10px] font-black text-slate-500 uppercase tracking-widest mb-2 text-left">Start Date</label>
              <input type="date" v-model="leaveRequest.start_date" id="start_date" class="w-full bg-black/40 border border-white/10 rounded-xl py-3 px-4 text-white focus:border-blue-500/50 outline-none transition-all">
            </div>
            <div>
              <label for="end_date" class="block text-[10px] font-black text-slate-500 uppercase tracking-widest mb-2 text-left">End Date</label>
              <input type="date" v-model="leaveRequest.end_date" id="end_date" class="w-full bg-black/40 border border-white/10 rounded-xl py-3 px-4 text-white focus:border-blue-500/50 outline-none transition-all">
            </div>
          </div>

          <div>
            <label for="reason" class="block text-[10px] font-black text-slate-500 uppercase tracking-widest mb-2 text-left">Reason for Leave</label>
            <textarea v-model="leaveRequest.reason" id="reason" rows="3" placeholder="Provide a brief explanation..." class="w-full bg-black/40 border border-white/10 rounded-xl py-3 px-4 text-white focus:border-blue-500/50 outline-none transition-all resize-none placeholder:text-slate-600"></textarea>
          </div>

          <div class="pt-4 space-y-3">
            <button type="submit" class="w-full py-4 bg-blue-600 text-white font-bold rounded-2xl hover:bg-blue-500 shadow-lg shadow-blue-600/20 transition-all">
              Submit Request
            </button>
            <button type="button" @click="close" class="w-full py-4 bg-white/5 text-slate-400 font-bold rounded-2xl hover:bg-white/10 transition-all">
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import api from '../api';
import { useAuthStore } from '../stores/auth';

const props = defineProps({
  show: Boolean,
});

const emit = defineEmits(['close', 'leave-request-submitted']);

const authStore = useAuthStore();

const leaveRequest = ref({
  leave_type: 'SICK',
  start_date: '',
  end_date: '',
  reason: '',
});

const close = () => {
  emit('close');
};

const submitLeaveRequest = async () => {
  if (!authStore.user) {
    console.error("User not logged in");
    return;
  }
  try {
    const response = await api.post('/leave-requests/', {
      ...leaveRequest.value,
      employee: authStore.user.id,
    });
    emit('leave-request-submitted');
    close();
  } catch (error) {
    console.error('Error submitting leave request:', error.response?.data || error);
  }
};
</script>