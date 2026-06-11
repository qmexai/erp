<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md" @click.self="$emit('close')">
    <div class="relative w-full max-w-lg bg-[#121214] border border-white/10 shadow-2xl rounded-3xl">
      <div class="p-8">
        <h3 class="text-2xl font-bold text-white tracking-tight">Schedule a New Meeting</h3>
        <p class="text-slate-400 text-sm mt-1">Organize your team's next sync-up.</p>

        <form @submit.prevent="submitMeeting" class="mt-8 space-y-6">
          <div>
            <label class="block text-[10px] font-black text-slate-500 uppercase tracking-widest mb-2">Meeting Title</label>
            <input type="text" v-model="meeting.title" placeholder="e.g., Q2 Project Kick-off" class="w-full bg-black/40 border border-white/10 rounded-xl py-3 px-4 text-white focus:border-blue-500/50 outline-none transition-all">
          </div>

          <div>
            <label class="block text-[10px] font-black text-slate-500 uppercase tracking-widest mb-2">Agenda</label>
            <textarea v-model="meeting.agenda" placeholder="Topics to be discussed..." rows="3" class="w-full bg-black/40 border border-white/10 rounded-xl py-3 px-4 text-white focus:border-blue-500/50 outline-none transition-all"></textarea>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label class="block text-[10px] font-black text-slate-500 uppercase tracking-widest mb-2">Start Time</label>
              <input type="datetime-local" v-model="meeting.start_time" class="w-full bg-black/40 border border-white/10 rounded-xl py-3 px-4 text-white focus:border-blue-500/50 outline-none transition-all">
            </div>
            <div>
              <label class="block text-[10px] font-black text-slate-500 uppercase tracking-widest mb-2">Google Meet Link</label>
              <input type="url" v-model="meeting.google_meet_link" placeholder="https://meet.google.com/..." class="w-full bg-black/40 border border-white/10 rounded-xl py-3 px-4 text-white focus:border-blue-500/50 outline-none transition-all">
            </div>
          </div>

          <div>
            <label class="block text-[10px] font-black text-slate-500 uppercase tracking-widest mb-2">Participants</label>
            <div class="w-full h-48 bg-black/40 border border-white/10 rounded-xl p-3 text-white overflow-y-auto">
              <div v-for="user in users" :key="user.id" class="flex items-center space-x-3 p-2 rounded-lg hover:bg-white/10 transition-colors">
                <input type="checkbox" :id="'user-' + user.id" :value="user.id" v-model="meeting.participants" class="form-checkbox h-5 w-5 text-blue-600 bg-gray-800 border-gray-600 rounded focus:ring-blue-500">
                <label :for="'user-' + user.id" class="text-sm flex items-center gap-2">
                  {{ user.email }}
                  <span v-if="isUserOnLeave(user.id)" class="px-2 py-0.5 rounded text-[10px] bg-red-500/20 text-red-400 font-bold uppercase tracking-widest">On Leave</span>
                </label>
              </div>
            </div>
          </div>

          <div class="flex gap-4 pt-4">
            <button type="button" @click="$emit('close')" class="flex-1 py-4 bg-white/5 text-slate-400 font-bold rounded-2xl hover:bg-white/10 transition-all">
              Cancel
            </button>
            <button type="submit" :disabled="isSubmitting" class="flex-1 py-4 bg-blue-600 text-white font-bold rounded-2xl hover:bg-blue-500 shadow-lg shadow-blue-600/30 transition-all disabled:opacity-50">
              <span v-if="isSubmitting">Scheduling...</span>
              <span v-else>Schedule Meeting</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '../api';

const emit = defineEmits(['close', 'meeting-created']);

const users = ref([]);
const leaves = ref([]);

const meeting = ref({
  title: '',
  agenda: '',
  start_time: '',
  google_meet_link: '',
  participants: [],
});
const isSubmitting = ref(false);

onMounted(async () => {
  try {
    const [usersRes, leavesRes] = await Promise.all([
        api.get('/users/'),
        api.get('/leave-requests/')
    ]);
    users.value = usersRes.data;
    // Only care about approved leaves
    leaves.value = leavesRes.data.filter(l => l.status === 'Approved');
  } catch (error) {
    console.error('Error fetching data:', error);
  }
});

const isUserOnLeave = (userId) => {
    if (!meeting.value.start_time) return false;
    const mTime = new Date(meeting.value.start_time).getTime();
    
    return leaves.value.some(l => {
        const empId = typeof l.employee === 'object' ? l.employee.id : l.employee;
        if (empId !== userId) return false;
        
        const lStart = new Date(l.start_date).getTime();
        const lEnd = new Date(l.end_date).getTime() + 86400000; // End of the day
        return mTime >= lStart && mTime <= lEnd;
    });
};

const submitMeeting = async () => {
  isSubmitting.value = true;
  try {
    const payload = {
      ...meeting.value,
      start_time: new Date(meeting.value.start_time).toISOString(),
    };
    const response = await api.post('/meetings/', payload);
    emit('meeting-created', response.data);
    emit('close');
  } catch (error) {
    console.error('Error creating meeting:', error.response?.data || error);
  } finally {
    isSubmitting.value = false;
  }
};
</script>
<style scoped>
.form-checkbox {
  appearance: none;
  -webkit-appearance: none;
  height: 1.25rem;
  width: 1.25rem;
  border: 2px solid #4A5568;
  border-radius: 0.375rem;
  display: inline-block;
  position: relative;
  cursor: pointer;
  transition: all 0.2s;
}

.form-checkbox:checked {
  background-color: #4299E1;
  border-color: #4299E1;
}

.form-checkbox:checked::after {
  content: '✔';
  font-size: 0.8rem;
  color: white;
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}
</style>