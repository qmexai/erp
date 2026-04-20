<template>
  <div class="panel">
    <div class="panel-hd">
      <div class="panel-title">
        <span class="accent violet"></span>
        System Activity Log
      </div>
      <button class="panel-btn" @click="fetchActivityLogs">Refresh</button>
    </div>
    <div class="panel-bd">
      <table class="tbl">
        <thead>
          <tr>
            <th>Actor</th>
            <th>Action</th>
            <th>Details</th>
            <th>Timestamp</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="log in activityLogs" :key="log.id">
            <td class="fw">{{ log.actor_name || 'System' }}</td>
            <td>
              <span class="badge pending">{{ log.action }}</span>
            </td>
            <td>{{ log.details }}</td>
            <td class="mono">{{ new Date(log.timestamp).toLocaleString('en-IN', { dateStyle: 'short', timeStyle: 'short' }) }}</td>
          </tr>
          <tr v-if="!activityLogs.length">
            <td colspan="4" class="empty-cell">No recent activity.</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import apiClient from '../api';

const activityLogs = ref([]);

const fetchActivityLogs = async () => {
  try {
    const response = await apiClient.get('/activity-logs/');
    activityLogs.value = response.data;
  } catch (error) {
    console.error('Error fetching activity logs:', error);
  }
};

onMounted(fetchActivityLogs);
</script>

<style scoped>
/* Inherits global panel and table styles */
</style>
