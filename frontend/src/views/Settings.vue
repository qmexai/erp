<template>
  <div class="settings-page">
    <header class="settings-header">
      <div>
        <p class="settings-eyebrow">Personal workspace</p>
        <h1>Settings</h1>
        <p>Manage your profile and everyday ERP preferences.</p>
      </div>
      <div class="settings-avatar">{{ initials }}</div>
    </header>

    <div v-if="message" class="settings-message settings-message--success">{{ message }}</div>
    <div v-if="error" class="settings-message settings-message--error">{{ error }}</div>

    <section class="settings-card">
      <div class="settings-card-heading">
        <div>
          <p class="settings-eyebrow">Profile</p>
          <h2>Personal information</h2>
        </div>
        <span class="settings-badge">Account</span>
      </div>
      <form class="settings-form" @submit.prevent="saveProfile">
        <label>First name
          <input v-model.trim="profile.first_name" required />
        </label>
        <label>Last name
          <input v-model.trim="profile.last_name" />
        </label>
        <label class="settings-wide">Work email
          <input :value="profile.email" disabled />
        </label>
        <label>Department
          <input v-model.trim="profile.department" placeholder="e.g. Engineering" />
        </label>
        <label>Designation
          <input :value="designation" disabled />
        </label>
        <div class="settings-wide settings-actions">
          <button class="settings-primary" type="submit" :disabled="saving">{{ saving ? 'Saving…' : 'Save profile' }}</button>
        </div>
      </form>
    </section>

    <section class="settings-card">
      <div class="settings-card-heading">
        <div>
          <p class="settings-eyebrow">Preferences</p>
          <h2>Personal workspace settings</h2>
        </div>
      </div>
      <div class="preference-list">
        <label class="preference-row">
          <span><strong>Activity notifications</strong><small>Keep operational updates visible in the workspace.</small></span>
          <input v-model="preferences.notifications" type="checkbox" @change="savePreferences" />
        </label>
        <label class="preference-row">
          <span><strong>Compact tables</strong><small>Use tighter rows when viewing projects and activity.</small></span>
          <input v-model="preferences.compactTables" type="checkbox" @change="savePreferences" />
        </label>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue';
import apiClient from '../api';
import { useAuthStore } from '../stores/auth';

const auth = useAuthStore();
const saving = ref(false);
const message = ref('');
const error = ref('');
const profile = ref({
  first_name: auth.user?.first_name || '',
  last_name: auth.user?.last_name || '',
  email: auth.user?.email || '',
  department: auth.user?.department || '',
});
const preferences = ref(JSON.parse(localStorage.getItem('qmexai-preferences') || '{"notifications":true,"compactTables":false}'));

const displayName = computed(() => [profile.value.first_name, profile.value.last_name].filter(Boolean).join(' ') || 'User');
const initials = computed(() => displayName.value.split(' ').map((part) => part[0]).join('').slice(0, 2).toUpperCase());
const designation = computed(() => ({
  CEO: 'Chief Executive Officer',
  HR: 'Human Resources',
  'Dept Head': 'Department Head',
  Employee: 'Employee',
}[auth.user?.role] || auth.user?.role || 'Team member'));

const saveProfile = async () => {
  saving.value = true;
  message.value = '';
  error.value = '';
  try {
    const response = await apiClient.patch('/profile/', {
      first_name: profile.value.first_name,
      last_name: profile.value.last_name,
      department: profile.value.department,
    });
    auth.user = response.data;
    localStorage.setItem('user', JSON.stringify(response.data));
    message.value = 'Profile updated successfully.';
  } catch (caughtError) {
    error.value = caughtError.response?.data?.detail || 'Unable to save your profile.';
  } finally {
    saving.value = false;
  }
};

const savePreferences = () => {
  localStorage.setItem('qmexai-preferences', JSON.stringify(preferences.value));
  message.value = 'Preferences saved.';
  error.value = '';
};
</script>

<style scoped>
.settings-page { max-width: 920px; margin: 0 auto; padding: 8px 0 40px; color: var(--qx-text1); }
.settings-header { display: flex; align-items: center; justify-content: space-between; gap: 18px; margin-bottom: 24px; }
.settings-header h1 { margin-top: 4px; font-size: 28px; font-weight: 700; letter-spacing: -.04em; }
.settings-header > div:first-child > p:last-child { margin-top: 6px; color: var(--qx-text3); font-size: 13px; }
.settings-eyebrow { color: var(--qx-blue); font-size: 10px; font-weight: 800; letter-spacing: .16em; text-transform: uppercase; }
.settings-avatar { display: grid; width: 48px; height: 48px; place-items: center; border-radius: 14px; background: linear-gradient(135deg, #4f8ef7, #a78bfa); color: white; font-weight: 800; }
.settings-message { margin-bottom: 16px; border-radius: 10px; padding: 11px 14px; font-size: 12px; }
.settings-message--success { border: 1px solid rgba(16,185,129,.25); background: var(--qx-green-d); color: #a7f3d0; }
.settings-message--error { border: 1px solid rgba(244,63,94,.25); background: var(--qx-red-d); color: #fda4af; }
.settings-card { margin-bottom: 16px; padding: 22px; border: 1px solid var(--qx-border); border-radius: 16px; background: var(--qx-bg1); box-shadow: 0 10px 28px rgba(2,6,23,.15); }
.settings-card-heading { display: flex; align-items: flex-start; justify-content: space-between; gap: 12px; margin-bottom: 20px; }
.settings-card h2 { margin-top: 4px; font-size: 16px; font-weight: 700; }
.settings-badge { border: 1px solid rgba(99,102,241,.25); border-radius: 999px; padding: 5px 9px; color: var(--qx-blue); background: var(--qx-blue-d); font-size: 10px; font-weight: 700; text-transform: uppercase; }
.settings-form { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 15px; }
.settings-form label { display: flex; flex-direction: column; gap: 7px; color: var(--qx-text3); font-size: 11px; font-weight: 700; letter-spacing: .04em; text-transform: uppercase; }
.settings-form input { width: 100%; min-height: 40px; text-transform: none; letter-spacing: normal; }
.settings-form input:disabled { cursor: not-allowed; opacity: .6; }
.settings-wide { grid-column: 1 / -1; }
.settings-actions { display: flex; justify-content: flex-end; }
.settings-primary { min-height: 40px; padding: 0 18px; }
.preference-list { display: grid; gap: 2px; }
.preference-row { display: flex; align-items: center; justify-content: space-between; gap: 20px; padding: 14px 0; border-bottom: 1px solid var(--qx-border); cursor: pointer; }
.preference-row:last-child { border-bottom: 0; }
.preference-row span { display: grid; gap: 4px; }
.preference-row strong { color: var(--qx-text1); font-size: 13px; }
.preference-row small { color: var(--qx-text3); font-size: 11px; }
.preference-row input { width: 17px; height: 17px; accent-color: var(--qx-blue); }
@media (max-width: 600px) { .settings-form { grid-template-columns: 1fr; } .settings-wide { grid-column: auto; } .settings-actions { justify-content: stretch; } .settings-primary { width: 100%; } }
</style>
