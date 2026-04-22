<template>
  <div class="panel">
    <div class="panel-hd flex-col items-start gap-4 md:flex-row md:items-center">
      <div class="panel-title">
        <span class="accent green"></span>
        Project Matrix
      </div>
      
      <button @click="downloadCSV" class="panel-btn">Export CSV</button>
    </div>

    <div class="panel-bd !p-0 overflow-x-auto">
      <table class="tbl w-full m-0">
        <thead>
          <tr>
            <th class="pl-4">Project Name</th>
            <th>Client</th>
            <th>Company</th>
            <th>Phone</th>
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
            <td>{{ project.company_name || '—' }}</td>
            <td>{{ project.phone_number || '—' }}</td>
            <td class="max-w-xs truncate" :title="project.description">{{ project.description || '—' }}</td>
            <td>
              <select 
                v-model="project.status" 
                @change="updateProjectStatus(project, $event.target.value)"
                class="bg-[var(--qx-bg1)] border border-[var(--qx-border)] text-[var(--qx-text1)] rounded px-1 py-0.5 text-[11px] outline-none"
                :class="getStatusClass(project.status)"
              >
                <option value="Not Started">Not Started</option>
                <option value="Active">Active</option>
                <option value="On Hold">On Hold</option>
                <option value="Completed">Completed</option>
                <option value="Deployed">Deployed</option>
              </select>
            </td>
            <td>
              <div class="flex items-center -space-x-2">
                <div v-if="!project.assigned_to?.length" class="text-[var(--qx-text3)] text-xs">—</div>
                <div v-for="user in project.assigned_to" :key="user.id" class="relative group/avatar" :title="user.email">
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
            <td colspan="8" class="empty-cell text-center p-8 text-slate-500 italic">No projects found in the matrix.</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="showEditModal" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm" @click.self="closeEditModal">
      <div class="bg-[var(--qx-bg1)] border border-[var(--qx-border)] w-full max-w-lg shadow-2xl rounded-2xl p-6">
        <h3 class="text-lg font-bold text-[var(--qx-text1)] mb-5 flex items-center gap-2">
          <span class="accent blue"></span> Update Project
        </h3>
        <form @submit.prevent="updateProject" class="space-y-4">
          <div>
            <label class="block text-[11px] font-medium text-slate-500 uppercase mb-1">Project Name</label>
            <input v-model="editingProject.name" type="text" class="w-full bg-[var(--qx-bg2)] border border-[var(--qx-border)] rounded-lg py-2 px-3 text-white text-[13px]">
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-[11px] font-medium text-slate-500 uppercase mb-1">Client</label>
              <input v-model="editingProject.client" type="text" class="w-full bg-[var(--qx-bg2)] border border-[var(--qx-border)] rounded-lg py-2 px-3 text-white text-[13px]">
            </div>
            <div>
              <label class="block text-[11px] font-medium text-slate-500 uppercase mb-1">Company</label>
              <input v-model="editingProject.company_name" type="text" class="w-full bg-[var(--qx-bg2)] border border-[var(--qx-border)] rounded-lg py-2 px-3 text-white text-[13px]">
            </div>
          </div>
          <div>
            <label class="block text-[11px] font-medium text-slate-500 uppercase mb-1">Phone Number</label>
            <input v-model="editingProject.phone_number" type="text" class="w-full bg-[var(--qx-bg2)] border border-[var(--qx-border)] rounded-lg py-2 px-3 text-white text-[13px]">
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-[11px] font-medium text-slate-500 uppercase mb-1">Status</label>
              <select v-model="editingProject.status" class="w-full bg-[var(--qx-bg2)] border border-[var(--qx-border)] rounded-lg py-2 px-3 text-white text-[13px]">
                <option value="Not Started">Not Started</option>
                <option value="Active">Active</option>
                <option value="On Hold">On Hold</option>
                <option value="Completed">Completed</option>
                <option value="Deployed">Deployed</option>
              </select>
            </div>
            <div>
              <label class="block text-[11px] font-medium text-slate-500 uppercase mb-1">Assign Team</label>
              <select multiple v-model="editingProject.assigned_to" class="w-full bg-[var(--qx-bg2)] border border-[var(--qx-border)] rounded-lg py-2 px-3 text-white h-24 text-[13px]">
                <option v-for="user in allUsers" :key="user.id" :value="user.id">{{ user.email }}</option>
              </select>
            </div>
          </div>
          <div class="mt-6 flex justify-end gap-3 pt-4 border-t border-white/5">
            <button type="button" @click="closeEditModal" class="px-4 py-2 text-slate-400 text-sm">Cancel</button>
            <button type="submit" class="px-6 py-2 bg-blue-600 text-white font-bold rounded-xl hover:bg-blue-500 transition-colors">Save Changes</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import apiClient from '../api';

const projects = ref([]);
const allUsers = ref([]);
const showEditModal = ref(false);
const editingProject = ref({});

const fetchProjects = async () => {
  try {
    const response = await apiClient.get('/projects/');
    projects.value = response.data.results || response.data;
  } catch (err) {
    console.error('Error fetching projects:', err);
  }
};

const fetchUsers = async () => {
  try {
    const response = await apiClient.get('/users/');
    allUsers.value = response.data.results || response.data;
  } catch (err) {
    console.error('Error fetching users:', err);
  }
};

onMounted(() => {
  fetchProjects();
  fetchUsers();
});

const openEditModal = (project) => {
  editingProject.value = { 
    ...project,
    // FIXED: Convert full user objects back to IDs for the <select multiple>
    assigned_to: project.assigned_to ? project.assigned_to.map(u => u.id) : []
  };
  showEditModal.value = true;
};

const closeEditModal = () => {
  showEditModal.value = false;
};

const updateProject = async () => {
  try {
    // Send updated project data with company_name and phone_number
    await apiClient.put(`/projects/${editingProject.value.id}/`, editingProject.value);
    await fetchProjects();
    closeEditModal();
  } catch (error) {
    console.error('Error updating project:', error.response?.data || error.message);
  }
};

const updateProjectStatus = async (project, newStatus) => {
  try {
    await apiClient.patch(`/projects/${project.id}/`, { status: newStatus });
  } catch (error) {
    console.error('Status update failed:', error);
    fetchProjects(); // Revert on UI if server fails
  }
};

const downloadCSV = async () => {
  const response = await apiClient.get('/projects/csv/', { responseType: 'blob' });
  const url = window.URL.createObjectURL(new Blob([response.data]));
  const link = document.createElement('a');
  link.href = url;
  link.setAttribute('download', 'qmexai_projects.csv');
  document.body.appendChild(link);
  link.click();
  link.remove();
};

const getAvatarColor = (id) => {
  const colors = ['#3b82f6', '#8b5cf6', '#f59e0b', '#10b981', '#ef4444'];
  return colors[id % colors.length];
};

const getInitials = (name) => {
  if (!name) return '??';
  const parts = name.split(/[.\s@]/);
  return parts.length > 1 ? (parts[0][0] + parts[1][0]).toUpperCase() : parts[0][0].toUpperCase();
};

const getStatusClass = (status) => {
  switch (status) {
    case 'Active': return 'text-blue-400';
    case 'Completed':
    case 'Deployed': return 'text-green-400';
    case 'On Hold': return 'text-amber-400';
    default: return 'text-slate-400';
  }
};
</script>