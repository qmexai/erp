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
  <div class="p-4 sm:p-6">
    <div class="flex items-center justify-between">
      <h1 class="text-2xl font-semibold text-gray-900">Leave Requests</h1>
      <button @click="showRequestLeaveModal = true" class="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2.5 rounded-xl font-semibold transition-all shadow-lg shadow-blue-500/20">
        Request Leave
      </button>
    </div>
    <div class="mt-8">
      <LeaveRequestsTable ref="leaveRequestsTable" />
    </div>
    <RequestLeaveModal 
      :show="showRequestLeaveModal" 
      @close="showRequestLeaveModal = false"
      @leave-request-submitted="handleLeaveRequestSubmitted"
    />
  </div>
</template>
