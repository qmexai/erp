<template>
  <div class="bg-[#121214] border border-white/5 rounded-3xl p-6 shadow-2xl transition-all hover:border-white/10 min-h-[300px]">
    <header class="mb-6 flex justify-between items-center">
      <h3 class="text-xl font-bold text-white tracking-tight flex items-center gap-2">
        <span class="w-1.5 h-6 bg-blue-500 rounded-full shadow-[0_0_10px_rgba(59,130,246,0.5)]"></span>
        Upcoming Meetings
      </h3>
    </header>

    <div v-if="loading" class="flex flex-col items-center justify-center py-20 space-y-4">
      <div class="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
      <p class="text-[10px] font-black text-slate-500 uppercase tracking-[0.2em]">Syncing Calendar...</p>
    </div>

    <div v-else class="overflow-x-auto">
      <table class="min-w-full">
        <thead>
          <tr class="border-b border-white/5">
            <th scope="col" class="px-6 py-4 text-left text-[10px] font-black text-slate-500 uppercase tracking-[0.2em]">Title</th>
            <th scope="col" class="px-6 py-4 text-left text-[10px] font-black text-slate-500 uppercase tracking-[0.2em]">Agenda</th>
            <th scope="col" class="px-6 py-4 text-left text-[10px] font-black text-slate-500 uppercase tracking-[0.2em]">Date & Time</th>
            <th scope="col" class="px-6 py-4 text-left text-[10px] font-black text-slate-500 uppercase tracking-[0.2em]">Participants</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-white/5">
          <tr v-for="meeting in meetings" :key="meeting.id" class="group hover:bg-white/[0.02] transition-colors">
            <td class="px-6 py-4 whitespace-nowrap text-sm font-semibold text-white">
              {{ meeting.title }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-slate-400">
              {{ meeting.agenda }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-slate-300 font-mono">
              {{ formatDateTime(meeting.date_time) }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
              <div class="flex items-center -space-x-2">
                <div v-for="(participant, index) in meeting.participants" :key="index" class="relative group/user">
                  <div class="w-8 h-8 rounded-full bg-slate-800 border-2 border-[#121214] flex items-center justify-center text-[10px] font-black text-blue-400 group-hover/user:text-white transition-colors shadow-lg">
                    {{ getSafeInitials(participant) }}
                  </div>
                  <span class="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 w-max px-2 py-1 bg-slate-900 border border-white/10 text-white text-[10px] rounded-lg opacity-0 group-hover/user:opacity-100 transition-opacity pointer-events-none z-50">
                    {{ typeof participant === 'string' ? participant : participant.name }}
                  </span>
                </div>
              </div>
            </td>
          </tr>
          <tr v-if="meetings.length === 0">
            <td colspan="4" class="px-6 py-12 text-center text-slate-500 italic text-sm">
              No meetings scheduled for this week.
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import apiClient from '../api';

const meetings = ref([]);
const loading = ref(true);

const fetchMeetings = async () => {
  try {
    loading.value = true;
    const response = await apiClient.get('/meetings/');
    // Ensure we always have an array to prevent .length errors
    meetings.value = Array.isArray(response.data) ? response.data : [];
  } catch (error) {
    console.error('Error fetching meetings:', error);
    meetings.value = [];
  } finally {
    // Small timeout for smooth UI transition
    setTimeout(() => { loading.value = false; }, 300);
  }
};

const formatDateTime = (dateStr) => {
  if (!dateStr) return 'TBD';
  const date = new Date(dateStr);
  return date.toLocaleString('en-IN', {
    day: '2-digit',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit',
    hour12: true
  });
};

const getSafeInitials = (user) => {
  // Handles strings or objects (e.g. { name: "Muhsin" })
  const name = typeof user === 'string' ? user : (user?.name || user?.username || '');
  if (!name || typeof name !== 'string') return '??';
  
  const parts = name.trim().split(' ');
  if (parts.length === 1) return parts[0].substring(0, 2).toUpperCase();
  return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
};

onMounted(fetchMeetings);

defineExpose({
  fetchMeetings
});
</script>