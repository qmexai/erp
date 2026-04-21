<template>
  <div class="panel">
    <div class="panel-hd flex-col items-start gap-4 md:flex-row md:items-center">
      <div class="panel-title">
        <span class="accent blue"></span>
        Meetings & Calendar
      </div>
      <button class="panel-btn" @click="showAdd = !showAdd">
        + Schedule
      </button>
    </div>

    <div v-if="showAdd" class="p-4 bg-[var(--qx-bg2)] border-b border-[var(--qx-border)]">
      <form @submit.prevent="addMeeting">
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 mb-3">
          <input v-model="form.title" placeholder="Meeting Title" class="w-full px-2 py-1.5 rounded bg-[var(--qx-bg1)] border border-[var(--qx-border)] text-[var(--qx-text1)] focus:outline-none text-[13px]" />
          <input v-model="form.start_time" type="datetime-local" class="w-full px-2 py-1.5 rounded bg-[var(--qx-bg1)] border border-[var(--qx-border)] text-[var(--qx-text1)] focus:outline-none text-[13px] " />
          <input v-model="form.participants" placeholder="Emails (comma separated)" class="w-full px-2 py-1.5 rounded bg-[var(--qx-bg1)] border border-[var(--qx-border)] text-[var(--qx-text1)] focus:outline-none text-[13px]" />
        </div>
        <button type="submit" class="px-4 py-1.5 bg-[var(--qx-blue-d)] text-[var(--qx-blue)] text-[12px] font-medium rounded hover:bg-[var(--qx-blue)] hover:text-white transition-colors">Submit</button>
      </form>
    </div>

    <div class="panel-bd !p-0 overflow-x-auto">
      <table class="tbl w-full m-0">
        <thead>
          <tr>
            <th class="pl-4">Title</th>
            <th>Start Time</th>
            <th>Participants</th>
            <th>Approved</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="meeting in meetings" :key="meeting.id">
            <td class="fw pl-4">{{ meeting.title }}</td>
            <td class="mono">{{ formatDateTime(meeting.start_time) }}</td>
            <td>
              <div v-if="meeting.participants" class="flex flex-wrap gap-1">
                <span v-for="p in meeting.participants" :key="p" class="bg-[var(--qx-bg3)] text-[var(--qx-text2)] px-1.5 py-0.5 rounded text-[10px]">
                  {{ p }}
                </span>
              </div>
            </td>
            <td>
              <span :class="['badge', meeting.is_approved ? 'active' : 'pending']">
                {{ meeting.is_approved ? 'Yes' : 'Pending' }}
              </span>
            </td>
          </tr>
          <tr v-if="!meetings?.length">
            <td colspan="4" class="empty-cell text-center p-8">No upcoming meetings.</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useAuthStore } from '../stores/auth';

const auth = useAuthStore();
const meetings = ref([]);
const showAdd = ref(false);
const form = ref({
  title: '',
  start_time: '',
  participants: ''
});

const fetchMeetings = async () => {
  const backendUrl = import.meta.env.VITE_API_URL || 'https://erp-e1ax.onrender.com';
  const res = await fetch(`${backendUrl}/api/meetings/`, {
    headers: { Authorization: `Bearer ${auth.token}` }
  });
  meetings.value = await res.json();
};

const addMeeting = async () => {
  const payload = { ...form.value, participants: form.value.participants.split(',').map(s => s.trim()) };
  const backendUrl = import.meta.env.VITE_API_URL || 'https://erp-e1ax.onrender.com';
  await fetch(`${backendUrl}/api/meetings/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${auth.token}`
    },
    body: JSON.stringify(payload)
  });
  showAdd.value = false;
  Object.assign(form.value, { title: '', start_time: '', participants: '' });
  fetchMeetings();
};

const formatDateTime = (dateStr) => {
  if (!dateStr) return '';
  return new Date(dateStr).toLocaleString('en-IN', {
    month: 'short', day: 'numeric',
    hour: 'numeric', minute: '2-digit', hour12: true
  });
};

onMounted(fetchMeetings);
</script>

<style scoped>
</style>

