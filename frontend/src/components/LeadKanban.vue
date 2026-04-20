<template>
  <div class="kanban-board grid grid-cols-1 md:grid-cols-3 gap-6">
    <div v-for="col in columns" :key="col.status" class="kanban-col bg-[#18181b] rounded-2xl p-4 border border-white/10">
      <h4 class="text-lg font-bold mb-4 font-sans flex items-center gap-2">
        <span :class="['status-badge', col.badgeClass]">{{ col.label }}</span>
      </h4>
      <div class="flex flex-col gap-4">
        <div v-for="lead in filteredLeads(col.status)" :key="lead.id" class="kanban-card bg-[#23232b] rounded-xl p-4 shadow-bento transition-all hover:scale-[1.02]">
          <div class="font-semibold text-white text-base font-sans mb-1">{{ lead.client_name }}</div>
          <div class="text-xs text-gray-400 font-sans mb-2">{{ lead.company_name }}</div>
          <div class="flex flex-wrap gap-2 mb-2">
            <span class="status-badge" :class="col.badgeClass">{{ lead.status }}</span>
          </div>
          <div class="text-xs text-gray-500 font-sans">{{ lead.notes }}</div>
        </div>
        <div v-if="filteredLeads(col.status).length === 0" class="text-gray-500 text-xs italic text-center py-4">No leads</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
const props = defineProps({
  leads: { type: Array, required: true }
});

const columns = [
  { status: 'Not Started', label: 'Not Started', badgeClass: 'not-started' },
  { status: 'Open', label: 'Open', badgeClass: 'open' },
  { status: 'Closed (Won)', label: 'Closed', badgeClass: 'closed' },
  // You can add 'Not Interested' as a column if desired
];

const filteredLeads = (status) => props.leads.filter(l => l.status === status);
</script>

<style scoped>
.kanban-board {
  min-height: 220px;
}
.kanban-card {
  border: 1px solid rgba(255,255,255,0.04);
}
</style>
