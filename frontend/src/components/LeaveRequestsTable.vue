<template>
  <div class="panel-bd !p-0 overflow-x-auto">
    <table class="tbl w-full m-0">
      <thead>
        <tr>
          <th class="pl-4">Employee</th>
          <th>Start Date</th>
          <th>End Date</th>
          <th>Reason</th>
          <th>Status</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="request in leaveRequests" :key="request.id">
            <td class="fw pl-4">{{ request.employee_name || request.employee_email }}</td>
          <td class="mono">{{ new Date(request.start_date).toLocaleDateString('en-IN', { month: 'short', day: 'numeric', year: 'numeric' }) }}</td>
          <td class="mono">{{ new Date(request.end_date).toLocaleDateString('en-IN', { month: 'short', day: 'numeric', year: 'numeric' }) }}</td>
          <td>{{ request.reason }}</td>
          <td>
            <span :class="statusClass(request.status)">
              {{ request.status }}
            </span>
          </td>
          <td>
            <div v-if="canManageLeaves && request.status === 'Pending'" class="flex items-center gap-3">
              <button @click="approveLeave(request.id)" class="text-[var(--qx-green)] hover:underline font-medium text-[12px]">Approve</button>
              <button @click="rejectLeave(request.id)" class="text-[var(--qx-red)] hover:underline font-medium text-[12px]">Reject</button>
            </div>
            <div v-else class="text-[var(--qx-text3)] text-[12px] italic">
              {{ request.status !== 'Pending' ? 'Processed' : '—' }}
            </div>
          </td>
        </tr>
        <tr v-if="!leaveRequests.length">
          <td colspan="6" class="empty-cell text-center p-8">No leave requests found.</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import apiClient from '../api'; // Import the new API client
import { useAuthStore } from '../stores/auth';

const leaveRequests = ref([]);
const auth = useAuthStore();

const canManageLeaves = computed(() => {
  const role = auth.user?.role;
  return role === 'CEO' || role === 'HR' || role === 'Manager';
});

const fetchLeaveRequests = async () => {
  try {
    const response = await apiClient.get('/leave-requests/');
    leaveRequests.value = response.data;
  } catch (error) {
    console.error('Error fetching leave requests:', error);
    alert('Failed to load leave requests.');
  }
};

const approveLeave = async (id) => {
  try {
    await apiClient.patch(`/leave-requests/${id}/approve/`);
    await fetchLeaveRequests();
  } catch (error) {
    console.error('Error approving leave:', error);
    alert('Failed to approve leave request.');
  }
};

const rejectLeave = async (id) => {
  try {
    await apiClient.patch(`/leave-requests/${id}/reject/`);
    await fetchLeaveRequests();
  } catch (error) {
    console.error('Error rejecting leave:', error);
    alert('Failed to reject leave request.');
  }
};

const statusClass = (status) => {
  switch (status) {
    case 'Approved':
      return 'badge active';
    case 'Pending':
      return 'badge pending';
    case 'Rejected':
      return 'badge leave';
    default:
      return 'badge closed';
  }
};

onMounted(fetchLeaveRequests);

defineExpose({
  fetchLeaveRequests,
});
</script>