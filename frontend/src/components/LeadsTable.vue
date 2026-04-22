<template>
  <div class="panel">
    <div class="panel-hd">
      <div class="panel-title">
        <span class="accent amber"></span>
        Leads
      </div>
      <div class="flex items-center gap-3">
        <button class="panel-btn" @click="downloadCSV">Export CSV</button>
        <button class="panel-btn" @click="showAdd = !showAdd">+ Add Lead</button>
      </div>
    </div>

    <div v-if="showAdd" class="p-4 bg-[var(--qx-bg2)] border-b border-[var(--qx-border)]">
      <form @submit.prevent="addLead">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-3 mb-3">
          <input v-model="form.client_name" placeholder="Client Name" class="w-full px-2 py-1 rounded bg-[var(--qx-bg1)] border border-[var(--qx-border)] text-[var(--qx-text1)] focus:outline-none text-[13px]" />
          <input v-model="form.company_name" placeholder="Company Name" class="w-full px-2 py-1 rounded bg-[var(--qx-bg1)] border border-[var(--qx-border)] text-[var(--qx-text1)] focus:outline-none text-[13px]" />
          <input v-model="form.field" placeholder="Field (e.g. Dental Clinic)" class="w-full px-2 py-1 rounded bg-[var(--qx-bg1)] border border-[var(--qx-border)] text-[var(--qx-text1)] focus:outline-none text-[13px]" />
          <input v-model="form.phone_number" placeholder="Phone Number" class="w-full px-2 py-1 rounded bg-[var(--qx-bg1)] border border-[var(--qx-border)] text-[var(--qx-text1)] focus:outline-none text-[13px]" />
          <input v-model="form.address" placeholder="Address" class="w-full px-2 py-1 rounded bg-[var(--qx-bg1)] border border-[var(--qx-border)] text-[var(--qx-text1)] focus:outline-none text-[13px]" />
          <select v-model="form.status" class="w-full px-2 py-1 rounded bg-[var(--qx-bg1)] border border-[var(--qx-border)] text-[var(--qx-text1)] focus:outline-none text-[13px]">
            <option value="Not Started">Not Started</option>
            <option value="Open">Open</option>
            <option value="Not Interested">Not Interested</option>
            <option value="Closed">Closed</option>
          </select>
        </div>
        <textarea v-model="form.notes" placeholder="Notes" class="w-full px-2 py-1 rounded bg-[var(--qx-bg1)] border border-[var(--qx-border)] text-[var(--qx-text1)] focus:outline-none text-[13px] mb-3"></textarea>
        <button type="submit" class="px-4 py-1.5 bg-[var(--qx-green-d)] text-[var(--qx-green)] text-[12px] font-medium rounded hover:bg-[var(--qx-green)] hover:text-white transition-colors">Submit</button>
      </form>
    </div>

    <div class="panel-bd">
      <table class="tbl">
        <thead>
          <tr>
            <th>Client</th>
            <th>Company</th>
            <th>Field</th>
            <th>Phone</th>
            <th>Status</th>
            <th>Services</th>
            <th>Notes</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="lead in leads" :key="lead.id">
            <td class="fw">{{ lead.client_name }}</td>
            <td>{{ lead.company_name }}</td>
            <td>{{ lead.field }}</td>
            <td class="mono">{{ lead.phone_number }}</td>
            <td>
              <span
                :class="[
                  'badge',
                  lead.status === 'Closed' ? 'closed' :
                  lead.status === 'Open' ? 'active' :
                  lead.status === 'Not Interested' ? 'leave' : 'pending'
                ]"
              >
                {{ lead.status }}
              </span>
              <select v-model="lead.status" @change="handleStatusChange(lead)" class="ml-2 bg-[var(--qx-bg1)] border border-[var(--qx-border)] text-[var(--qx-text1)] rounded px-1 text-[11px] outline-none">
                <option value="Not Started">Not Started</option>
                <option value="Open">Open</option>
                <option value="Not Interested">Not Interested</option>
                <option value="Closed">Closed</option>
              </select>
            </td>
            <td>{{ (lead.services_needed || []).join(', ') || '—' }}</td>
            <td class="max-w-[150px] truncate" :title="lead.notes">{{ lead.notes || '—' }}</td>
            <td>
              <button class="text-[var(--qx-blue)] font-medium text-[12px] hover:underline" @click="editLead(lead)">Edit</button>
            </td>
          </tr>
          <tr v-if="!leads.length">
            <td colspan="8" class="empty-cell text-center p-8 text-slate-500 italic">No leads found.</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Edit Modal -->
    <div v-if="showEditModal" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm" @click.self="closeEditModal">
      <div class="bg-[var(--qx-bg1)] border border-[var(--qx-border)] w-full max-w-lg shadow-2xl rounded-2xl p-6">
        <h3 class="text-lg font-bold text-[var(--qx-text1)] mb-5 flex items-center gap-2">
          <span class="accent amber"></span>
          Update Lead
        </h3>
        <form @submit.prevent="updateLead" class="space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-[11px] font-medium text-[var(--qx-text3)] uppercase tracking-wider mb-1.5">Client Name</label>
              <input v-model="editingLead.client_name" type="text" class="w-full bg-[var(--qx-bg2)] border border-[var(--qx-border)] rounded-lg py-2 px-3 text-[var(--qx-text1)] focus:outline-none focus:border-[var(--qx-amber)] text-[13px]">
            </div>
            <div>
              <label class="block text-[11px] font-medium text-[var(--qx-text3)] uppercase tracking-wider mb-1.5">Company Name</label>
              <input v-model="editingLead.company_name" type="text" class="w-full bg-[var(--qx-bg2)] border border-[var(--qx-border)] rounded-lg py-2 px-3 text-[var(--qx-text1)] focus:outline-none focus:border-[var(--qx-amber)] text-[13px]">
            </div>
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-[11px] font-medium text-[var(--qx-text3)] uppercase tracking-wider mb-1.5">Field</label>
              <input v-model="editingLead.field" type="text" class="w-full bg-[var(--qx-bg2)] border border-[var(--qx-border)] rounded-lg py-2 px-3 text-[var(--qx-text1)] focus:outline-none focus:border-[var(--qx-amber)] text-[13px]" placeholder="e.g. Dental Clinic">
            </div>
            <div>
              <label class="block text-[11px] font-medium text-[var(--qx-text3)] uppercase tracking-wider mb-1.5">Phone Number</label>
              <input v-model="editingLead.phone_number" type="text" class="w-full bg-[var(--qx-bg2)] border border-[var(--qx-border)] rounded-lg py-2 px-3 text-[var(--qx-text1)] focus:outline-none focus:border-[var(--qx-amber)] text-[13px]">
            </div>
          </div>
          <div>
            <label class="block text-[11px] font-medium text-[var(--qx-text3)] uppercase tracking-wider mb-1.5">Address</label>
            <input v-model="editingLead.address" type="text" class="w-full bg-[var(--qx-bg2)] border border-[var(--qx-border)] rounded-lg py-2 px-3 text-[var(--qx-text1)] focus:outline-none focus:border-[var(--qx-amber)] text-[13px]">
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-[11px] font-medium text-[var(--qx-text3)] uppercase tracking-wider mb-1.5">Status</label>
              <select v-model="editingLead.status" class="w-full bg-[var(--qx-bg2)] border border-[var(--qx-border)] rounded-lg py-2 px-3 text-[var(--qx-text1)] focus:outline-none text-[13px]">
                <option value="Not Started">Not Started</option>
                <option value="Open">Open</option>
                <option value="Not Interested">Not Interested</option>
                <option value="Closed">Closed</option>
              </select>
            </div>
            <div>
              <label class="block text-[11px] font-medium text-[var(--qx-text3)] uppercase tracking-wider mb-1.5">Services Needed (comma-separated)</label>
              <input v-model="editingLead.services_needed_string" type="text" class="w-full bg-[var(--qx-bg2)] border border-[var(--qx-border)] rounded-lg py-2 px-3 text-[var(--qx-text1)] focus:outline-none focus:border-[var(--qx-amber)] text-[13px]" placeholder="e.g. Web Dev, SEO">
            </div>
          </div>
          <div>
            <label class="block text-[11px] font-medium text-[var(--qx-text3)] uppercase tracking-wider mb-1.5">Notes</label>
            <textarea v-model="editingLead.notes" class="w-full bg-[var(--qx-bg2)] border border-[var(--qx-border)] rounded-lg py-2 px-3 text-[var(--qx-text1)] focus:outline-none focus:border-[var(--qx-amber)] text-[13px]" rows="3"></textarea>
          </div>
          <div class="mt-6 flex justify-end gap-3 pt-4 border-t border-[var(--qx-border)]">
            <button type="button" @click="closeEditModal" class="px-4 py-1.5 bg-[var(--qx-bg2)] text-[var(--qx-text2)] rounded hover:bg-[var(--qx-bg3)] transition-colors text-[13px] font-medium">Cancel</button>
            <button type="submit" class="px-4 py-1.5 bg-[var(--qx-amber-d)] text-[var(--qx-amber)] font-medium rounded hover:bg-[var(--qx-amber)] hover:text-black transition-colors text-[13px]">Save Changes</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import apiClient from '../api'; // Import the new API client

const leads = ref([]);
const users = ref([]); // To store the list of users
const showAdd = ref(false);

const form = ref({
  client_name: '',
  company_name: '',
  field: '',
  phone_number: '',
  address: '',
  status: 'Not Started',
  // services_needed: '',
  notes: ''
});

const handleStatusChange = async (lead) => {
  if (lead.status === 'Closed') {
    try {
      await apiClient.post(`/leads/${lead.id}/convert_to_project/`);
      await fetchLeads();
      // Optionally, you can show a success message or redirect to the projects page
    } catch (error) {
      console.error('Error converting lead to project:', error);
    }
  } else {
    try {
      await apiClient.patch(`/leads/${lead.id}/`, { status: lead.status });
      await fetchLeads(); // Refresh the list
    } catch (error) {
      console.error('Error updating lead status:', error);
      // Revert status on failure?
    }
  }
};

const fetchLeads = async () => {
  try {
    const response = await apiClient.get('/leads/');
    leads.value = response.data;
  } catch (err) {
    console.error('LeadsTable fetchLeads exception:', err);
    alert('Error loading leads: ' + (err.response?.data?.detail || err.message));
    leads.value = [];
  }
};

const fetchUsers = async () => {
  try {
    const response = await apiClient.get('/users/');
    users.value = response.data;
  } catch (err) {
    console.error('Error fetching users:', err);
  }
};

const addLead = async () => {
  try {
    await apiClient.post('/leads/', form.value);
    showAdd.value = false;
    // Reset form
    Object.assign(form.value, { client_name: '', company_name: '', field: '', phone_number: '', address: '', status: 'Not Started', notes: '' });
    fetchLeads(); // Refresh list
  } catch (err) {
    console.error('LeadsTable addLead exception:', err);
    alert('Error adding lead: ' + (err.response?.data?.detail || err.message));
  }
};

const downloadCSV = async () => {
  try {
    const response = await apiClient.get('/leads/download/', { responseType: 'blob' });
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', 'leads.csv');
    document.body.appendChild(link);
    link.click();
    link.remove();
  } catch (error) {
    console.error('Error downloading CSV:', error);
    alert('Failed to download CSV.');
  }
};

const showEditModal = ref(false);
const editingLead = ref({});

const editLead = (lead) => {
  editingLead.value = { ...lead };
  editingLead.value.services_needed_string = (lead.services_needed || []).join(', ');
  showEditModal.value = true;
};

const closeEditModal = () => {
  showEditModal.value = false;
};

const updateLead = async () => {
  try {
    const payload = { ...editingLead.value };
    if (payload.services_needed_string !== undefined) {
      payload.services_needed = payload.services_needed_string.split(',').map(s => s.trim()).filter(s => s);
      delete payload.services_needed_string;
    }
    
    await apiClient.put(`/leads/${payload.id}/`, payload);
    await fetchLeads();
    closeEditModal();
  } catch (error) {
    console.error('Error updating lead:', error);
    alert('Error updating lead: ' + (error.response?.data?.detail || error.message));
  }
};

onMounted(() => {
  fetchLeads();
  fetchUsers(); // Fetch users when the component mounts
});
</script>


<style scoped>
.minimal-table {
  font-family: 'Inter', sans-serif;
}
/* ... existing styles ... */
</style>

