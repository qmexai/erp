<template>
  <div class="space-y-8 min-h-screen bg-[#09090b] text-white">
    <header class="flex flex-col md:flex-row md:items-end justify-between gap-6">
      <div>
        <h1 class="text-4xl font-bold tracking-tight text-white">Meetings & Syncs</h1>
        <p class="text-slate-400 mt-1">Coordinate with the Qmexai team and clients.</p>
      </div>

      <div class="flex items-center gap-4">
        <div class="hidden sm:block bg-blue-600/5 border border-blue-500/10 px-4 py-2 rounded-xl">
          <span class="text-[10px] text-blue-400 uppercase font-black tracking-widest block">Today's Schedule</span>
          <span class="text-lg font-bold text-white leading-none">4 Active</span>
        </div>

        <button 
          @click="showAddMeetingModal = true" 
          class="bg-white text-black font-bold px-6 py-3 rounded-xl hover:bg-slate-200 transition-all flex items-center gap-2 shadow-xl active:scale-95"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>
          Schedule Meeting
        </button>
      </div>
    </header>

    <div class="transition-all duration-500 ease-in-out">
      <MeetingsTable ref="meetingsTable" />
    </div>

    <AddMeetingModal 
      v-if="showAddMeetingModal" 
      @close="showAddMeetingModal = false"
      @meeting-created="handleMeetingCreated"
    />
  </div>
</template>

<script setup>
import { ref } from 'vue';
import MeetingsTable from '../components/MeetingsTable.vue';
import AddMeetingModal from '../components/AddMeetingModal.vue';

const showAddMeetingModal = ref(false);
const meetingsTable = ref(null);

/**
 * Handle meeting creation: Close modal and refresh table
 */
const handleMeetingCreated = () => {
  showAddMeetingModal.value = false;
  
  // Use the exposed fetchMeetings method from the child component
  if (meetingsTable.value) {
    meetingsTable.value.fetchMeetings();
  }
};
</script>

<style scoped>
/* Optional: Entrance animation for the page */
div {
  animation: fadeIn 0.4s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>