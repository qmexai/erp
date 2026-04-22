<template>
  <div class="panel">
    <div class="panel-hd flex-col items-start gap-4 md:flex-row md:items-center">
      <div class="panel-title">
        <span class="accent green"></span>
        Project Matrix
      </div>
      
      <button 
        @click="downloadCSV" 
        class="panel-btn"
      >
        Export CSV
      </button>
    </div>

    <div class="panel-bd !p-0 overflow-x-auto">
      <table class="tbl w-full m-0">
        <thead>
          <tr>
            <th class="pl-4">Project Name</th>
            <th>Client</th>
            <th v-if="!hideCompanyPhone">Company</th>
            <th v-if="!hideCompanyPhone">Phone</th>
            <th>Description</th>
            <th>Status</th>
            <th>Assigned Team</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="project in projects" :key="project.id">
            <td class="fw pl-4">{{ project.name }}</td>
            <td>{{ project.client }}</td>
            <td v-if="!hideCompanyPhone">{{ project.company || '—' }}</td>
            <td v-if="!hideCompanyPhone">{{ project.phone || '—' }}</td>
            <td class="max-w-xs truncate" :title="project.description">{{ project.description || '—' }}</td>
            <td>
              <select 
                v-model="project.status" 
                @change="updateProjectStatus(project, $event.target.value)"
                class="bg-[var(--qx-bg1)] border border-[var(--qx-border)] text-[var(--qx-text1)] rounded px-1 py-0.5 text-[11px] outline-none"
                :class="getStatusClass(project.status)"
              >
                <option value="Not Started" class="text-[var(--qx-text1)]">Not Started</option>
                <option value="Active" class="text-[var(--qx-blue)]">Active</option>
                <option value="On Hold" class="text-[var(--qx-amber)]">On Hold</option>
                <option value="Completed" class="text-[var(--qx-green)]">Completed</option>
                <option value="Deployed" class="text-[var(--qx-green)]">Deployed</option>
              </select>
            </td>
            <td>
              <div class="flex items-center -space-x-2">
                <div v-if="!project.assigned_to?.length" class="text-[var(--qx-text3)] text-xs">—</div>
                <div v-for="user in project.assigned_to" :key="user.id" class="relative group/avatar" :title="user.name || user.email">
                  <div 
                    :style="{ backgroundColor: getAvatarColor(user.id) }"
                    class="w-6 h-6 rounded-full flex items-center justify-center text-white text-[9px] font-bold border-2 border-[var(--qx-bg1)] shadow-sm"
                  >
                    {{ getInitials(user.name || user.email) }}
                  </div>
                </div>
              </div>
            </td>
            <td>
              <button @click="openEditModal(project)" class="text-[var(--qx-blue)] hover:underline font-medium text-[12px]">Edit</button>
            </td>
          </tr>
          <tr v-if="!projects.length">
            <td colspan="6" class="empty-cell text-center p-8">No active projects.</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Edit Modal -->
    <div v-if="showEditModal" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm" @click.self="closeEditModal">
      <div class="bg-[var(--qx-bg1)] border border-[var(--qx-border)] w-full max-w-lg shadow-2xl rounded-2xl p-6">
        <h3 class="text-lg font-bold text-[var(--qx-text1)] mb-5 flex items-center gap-2">
          <span class="accent blue"></span>
          Update Project
        </h3>
        <form @submit.prevent="updateProject" class="space-y-4">
          <div>
            <label class="block text-[11px] font-medium text-[var(--qx-text3)] uppercase tracking-wider mb-1.5">Project Name</label>
            <input v-model="editingProject.name" type="text" class="w-full bg-[var(--qx-bg2)] border border-[var(--qx-border)] rounded-lg py-2 px-3 text-[var(--qx-text1)] focus:outline-none focus:border-[var(--qx-blue)] text-[13px]">
          </div>
          <div>
            <label class="block text-[11px] font-medium text-[var(--qx-text3)] uppercase tracking-wider mb-1.5">Client</label>
            <input v-model="editingProject.client" type="text" class="w-full bg-[var(--qx-bg2)] border border-[var(--qx-border)] rounded-lg py-2 px-3 text-[var(--qx-text1)] focus:outline-none focus:border-[var(--qx-blue)] text-[13px]">
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-[11px] font-medium text-[var(--qx-text3)] uppercase tracking-wider mb-1.5">Company</label>
              <input v-model="editingProject.company" type="text" class="w-full bg-[var(--qx-bg2)] border border-[var(--qx-border)] rounded-lg py-2 px-3 text-[var(--qx-text1)] focus:outline-none focus:border-[var(--qx-blue)] text-[13px]">
            </div>
            <div>
              <label class="block text-[11px] font-medium text-[var(--qx-text3)] uppercase tracking-wider mb-1.5">Phone</label>
              <input v-model="editingProject.phone" type="text" class="w-full bg-[var(--qx-bg2)] border border-[var(--qx-border)] rounded-lg py-2 px-3 text-[var(--qx-text1)] focus:outline-none focus:border-[var(--qx-blue)] text-[13px]">
            </div>
          </div>
          <div>
            <label class="block text-[11px] font-medium text-[var(--qx-text3)] uppercase tracking-wider mb-1.5">Description</label>
            <textarea v-model="editingProject.description" class="w-full bg-[var(--qx-bg2)] border border-[var(--qx-border)] rounded-lg py-2 px-3 text-[var(--qx-text1)] focus:outline-none focus:border-[var(--qx-blue)] text-[13px]" rows="3"></textarea>
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-[11px] font-medium text-[var(--qx-text3)] uppercase tracking-wider mb-1.5">Status</label>
              <select v-model="editingProject.status" class="w-full bg-[var(--qx-bg2)] border border-[var(--qx-border)] rounded-lg py-2 px-3 text-[var(--qx-text1)] focus:outline-none text-[13px]">
                <option value="Not Started">Not Started</option>
                <option value="Active">Active</option>
                <option value="On Hold">On Hold</option>
                <option value="Completed">Completed</option>
                <option value="Deployed">Deployed</option>
              </select>
            </div>
            <div>
              <label class="block text-[11px] font-medium text-[var(--qx-text3)] uppercase tracking-wider mb-1.5">Team Assignment</label>
              <select multiple v-model="editingProject.assigned_to_ids" class="w-full bg-[var(--qx-bg2)] border border-[var(--qx-border)] rounded-lg py-2 px-3 text-[var(--qx-text1)] focus:outline-none h-24 text-[13px]">
                <option v-for="user in allUsers" :key="user.id" :value="user.id" class="p-1 hover:bg-[var(--qx-bg3)]">{{ user.name || user.email }}</option>
              </select>
            </div>
          </div>
          <div class="mt-6 flex justify-end gap-3 pt-4 border-t border-[var(--qx-border)]">
            <button type="button" @click="closeEditModal" class="px-4 py-1.5 bg-[var(--qx-bg2)] text-[var(--qx-text2)] rounded hover:bg-[var(--qx-bg3)] transition-colors text-[13px] font-medium">Cancel</button>
            <button type="submit" class="px-4 py-1.5 bg-[var(--qx-blue-d)] text-[var(--qx-blue)] font-medium rounded hover:bg-[var(--qx-blue)] hover:text-white transition-colors text-[13px]">Save Changes</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import apiClient from '../api';

const props = defineProps({
  hideCompanyPhone: {
    type: Boolean,
    default: false
  }
});

const projects = ref([]);
const allUsers = ref([]);
const showEditModal = ref(false);
const editingProject = ref({});

onMounted(async () => {
  await fetchProjects();
  await fetchUsers();
});

const fetchProjects = async () => {
  const response = await apiClient.get('/projects/');
  projects.value = response.data;
};

const fetchUsers = async () => {
  const response = await apiClient.get('/users/');
  allUsers.value = response.data;
};

const openEditModal = (project) => {
  editingProject.value = { 
    ...project,
    assigned_to_ids: project.assigned_to ? project.assigned_to.map(u => u.id) : []
  };
  showEditModal.value = true;
};

const closeEditModal = () => {
  showEditModal.value = false;
};

const updateProject = async () => {
  try {
    await apiClient.put(`/projects/${editingProject.value.id}/`, editingProject.value);
    await fetchProjects();
    closeEditModal();
  } catch (error) {
    console.error('Error updating project:', error);
  }
};

const downloadCSV = async () => {
  const response = await apiClient.get('/projects/csv/', { responseType: 'blob' });
  const url = window.URL.createObjectURL(new Blob([response.data]));
  const link = document.createElement('a');
  link.href = url;
  link.setAttribute('download', 'projects.csv');
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};

const getAvatarColor = (id) => {
  const colors = ['#4A90E2', '#50E3C2', '#F5A623', '#D0021B', '#9013FE'];
  return colors[id % colors.length];
};

const getInitials = (name) => {
  if (!name) return '';
  const names = name.split(' ');
  return names.length > 1 ? names[0][0] + names[1][0] : names[0][0];
};

const updateProjectStatus = async (project, newStatus) => {
  try {
    await apiClient.patch(`/projects/${project.id}/`, { status: newStatus });
    // Optionally show a success notification
  } catch (error) {
    console.error('Failed to update project status:', error);
    // Revert the status in the UI on failure
    project.status = projects.value.find(p => p.id === project.id)?.status;
    // Optionally show an error notification
  }
};

const getStatusClass = (status) => {
  switch (status) {
    case 'Active':
      return 'text-blue-400';
    case 'Completed':
    case 'Deployed':
      return 'text-green-400';
    case 'On Hold':
      return 'text-yellow-400';
    case 'Not Started':
    default:
      return 'text-slate-400';
  }
};
// ... rest of the script setup ...
</script>