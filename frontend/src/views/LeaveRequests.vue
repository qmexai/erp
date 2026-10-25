<script setup>
import { ref } from 'vue';
import LeaveRequestsTable from '../components/LeaveRequestsTable.vue';
import RequestLeaveModal from '../components/RequestLeaveModal.vue';

const showRequestLeaveModal = ref(false);
const leaveRequestsTable = ref(null);

const handleLeaveRequestSubmitted = () => {
  if (leaveRequestsTable.value) {
    leaveRequestsTable.value.fetchLeaveRequests();
  }
};
</script>

<template>
  <div class="min-h-full p-4 text-white sm:p-6">
    <div class="flex flex-col items-start justify-between gap-4 sm:flex-row sm:items-center">
      <div>
        <p class="text-[10px] font-bold uppercase tracking-[0.18em] text-blue-400">People operations</p>
        <h1 class="mt-1 text-2xl font-semibold text-white">Leave Requests</h1>
        <p class="mt-1 text-sm text-slate-400">Submit and track your time-off requests.</p>
      </div>
      <button @click="showRequestLeaveModal = true" class="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2.5 rounded-xl font-semibold transition-all shadow-lg shadow-blue-500/20">
        Request Leave
      </button>
    </div>
    <div class="mt-6">
      <LeaveRequestsTable ref="leaveRequestsTable" />
    </div>
    <RequestLeaveModal 
      :show="showRequestLeaveModal" 
      @close="showRequestLeaveModal = false"
      @leave-request-submitted="handleLeaveRequestSubmitted"
    />
  </div>
</template>
