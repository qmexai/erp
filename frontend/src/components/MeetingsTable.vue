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
      <div v-if="error" class="mx-6 mb-4 rounded-xl border border-rose-500/20 bg-rose-500/10 px-4 py-3 text-sm text-rose-300">
        {{ error }}
        <button type="button" class="ml-3 font-semibold text-rose-200 underline" @click="fetchMeetings">Retry</button>
      </div>
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
          <tr
            v-for="meeting in meetings"
            :key="meeting.id"
            class="group cursor-pointer hover:bg-white/[0.04] transition-colors"
            tabindex="0"
            role="button"
            @click="openMeetingDetails(meeting)"
            @keydown.enter="openMeetingDetails(meeting)"
          >
            <td class="px-6 py-4 whitespace-nowrap text-sm font-semibold text-white">
              {{ meeting.title }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-slate-400">
              {{ meeting.agenda || 'No agenda provided' }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-slate-300 font-mono">
              {{ formatDateTime(meeting.start_time) }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
              <div class="flex items-center -space-x-2">
                <div v-for="(participant, index) in meeting.participants_details || meeting.participants" :key="index" class="relative group/user">
                  <div class="w-8 h-8 rounded-full bg-slate-800 border-2 border-[#121214] flex items-center justify-center text-[10px] font-black text-blue-400 group-hover/user:text-white transition-colors shadow-lg">
                    {{ getSafeInitials(participant) }}
                  </div>
                  <span class="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 w-max px-2 py-1 bg-slate-900 border border-white/10 text-white text-[10px] rounded-lg opacity-0 group-hover/user:opacity-100 transition-opacity pointer-events-none z-50">
                    {{ getParticipantName(participant) }}
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

  <div
    v-if="selectedMeeting"
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/75 p-4 backdrop-blur-sm"
    role="dialog"
    aria-modal="true"
    aria-labelledby="meeting-details-title"
    @click.self="closeMeetingDetails"
  >
    <div class="w-full max-w-xl overflow-hidden rounded-3xl border border-white/10 bg-[#121214] shadow-2xl">
      <div class="flex items-start justify-between border-b border-white/10 px-6 py-5">
        <div>
          <p class="text-[10px] font-black uppercase tracking-[0.2em] text-blue-400">Meeting details</p>
          <h2 id="meeting-details-title" class="mt-1 text-2xl font-bold text-white">
            {{ selectedMeeting.title }}
          </h2>
        </div>
        <button
          type="button"
          class="rounded-lg px-3 py-1 text-2xl leading-none text-slate-400 transition hover:bg-white/10 hover:text-white"
          aria-label="Close meeting details"
          @click="closeMeetingDetails"
        >
          &times;
        </button>
      </div>

      <div class="space-y-5 px-6 py-6">
        <div class="grid gap-3 sm:grid-cols-2">
          <div class="rounded-xl border border-white/10 bg-white/[0.03] p-4">
            <p class="detail-label">Date & time</p>
            <p class="detail-value">{{ formatFullDateTime(selectedMeeting.start_time) }}</p>
          </div>
          <div class="rounded-xl border border-white/10 bg-white/[0.03] p-4">
            <p class="detail-label">Status</p>
            <span :class="['meeting-status', selectedMeeting.is_approved ? 'meeting-status--approved' : 'meeting-status--pending']">
              {{ selectedMeeting.is_approved ? 'Approved' : 'Pending approval' }}
            </span>
          </div>
        </div>

        <div>
          <p class="detail-label">Agenda</p>
          <p class="mt-2 whitespace-pre-wrap text-sm leading-6 text-slate-300">
            {{ selectedMeeting.agenda || 'No agenda provided.' }}
          </p>
        </div>

        <div>
          <p class="detail-label">Host</p>
          <p class="mt-2 text-sm text-slate-300">{{ getParticipantName(selectedMeeting.host_details || selectedMeeting.host) }}</p>
        </div>

        <div>
          <p class="detail-label">Participants</p>
          <div class="mt-2 flex flex-wrap gap-2">
            <span
              v-for="(participant, index) in selectedMeeting.participants_details || selectedMeeting.participants"
              :key="index"
              class="rounded-full border border-blue-400/20 bg-blue-400/10 px-3 py-1.5 text-xs text-blue-200"
            >
              {{ getParticipantName(participant) }}
            </span>
            <span v-if="!(selectedMeeting.participants_details || selectedMeeting.participants || []).length" class="text-sm text-slate-500">
              No participants added.
            </span>
          </div>
        </div>

        <a
          v-if="selectedMeeting.google_meet_link"
          :href="selectedMeeting.google_meet_link"
          target="_blank"
          rel="noopener noreferrer"
          class="inline-flex items-center rounded-xl bg-blue-600 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-blue-500"
        >
          Open meeting link
        </a>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import apiClient from '../api';

const meetings = ref([]);
const loading = ref(true);
const error = ref('');
const selectedMeeting = ref(null);

const fetchMeetings = async () => {
  try {
    loading.value = true;
    error.value = '';
    const response = await apiClient.get('/meetings/');
    // Ensure we always have an array to prevent .length errors
    meetings.value = Array.isArray(response.data) ? response.data : [];
  } catch (caughtError) {
    console.error('Error fetching meetings:', caughtError.response?.data || caughtError);
    meetings.value = [];
    error.value = caughtError.response?.data?.detail || 'Unable to load meetings. Please try again.';
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

const formatFullDateTime = (dateStr) => {
  if (!dateStr) return 'Time not set';
  return new Date(dateStr).toLocaleString('en-IN', {
    weekday: 'long',
    day: 'numeric',
    month: 'long',
    year: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
    hour12: true,
  });
};

const getParticipantName = (user) => {
  if (typeof user === 'string') return user;
  return user?.name || [user?.first_name, user?.last_name].filter(Boolean).join(' ') || user?.email || 'Unknown user';
};

const getSafeInitials = (user) => {
  // Handles strings or objects (e.g. { name: "Muhsin" })
  const name = getParticipantName(user);
  if (!name || typeof name !== 'string') return '??';
  
  const parts = name.trim().split(' ');
  if (parts.length === 1) return parts[0].substring(0, 2).toUpperCase();
  return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
};

const openMeetingDetails = (meeting) => {
  selectedMeeting.value = meeting;
};

const closeMeetingDetails = () => {
  selectedMeeting.value = null;
};

onMounted(fetchMeetings);

defineExpose({
  fetchMeetings
});
</script>

<style scoped>
.detail-label {
  color: #64748b;
  font-size: 10px;
  font-weight: 800;
  letter-spacing: .16em;
  text-transform: uppercase;
}

.detail-value {
  margin-top: 8px;
  color: #e2e8f0;
  font-size: 13px;
  line-height: 1.5;
}

.meeting-status {
  display: inline-flex;
  margin-top: 8px;
  border-radius: 999px;
  padding: 5px 10px;
  font-size: 11px;
  font-weight: 700;
}

.meeting-status--approved {
  background: rgba(16, 185, 129, .12);
  color: #6ee7b7;
}

.meeting-status--pending {
  background: rgba(245, 158, 11, .12);
  color: #fcd34d;
}
</style>