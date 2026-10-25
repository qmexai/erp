<script setup>
import { ref } from 'vue';
import apiClient from '../api';

const initialForm = () => ({ email: '', name: '', role: 'Employee', department: '' });
const form = ref(initialForm());
const result = ref(null);
const error = ref('');
const submitting = ref(false);

const generatePassword = () => Math.random().toString(36).slice(-8);

const submitForm = async () => {
  error.value = '';
  result.value = null;
  submitting.value = true;

  try {
    const payload = { ...form.value, password: generatePassword() };
    const response = await apiClient.post('/create-employee/', payload);
    result.value = response.data;
    form.value = initialForm();
  } catch (err) {
    console.error('Error creating employee:', err.response?.data || err.message);
    error.value = err.response?.data?.error
      || 'Unable to create the employee. Please check the details and try again.';
  } finally {
    submitting.value = false;
  }
};
</script>

<template>
  <div class="add-employee-card">
    <div class="add-employee-heading">
      <div>
        <p class="eyebrow">Team access</p>
        <h2>Register new personnel</h2>
        <p class="form-hint">Create a secure Firebase and ERP account in one step.</p>
      </div>
      <span class="form-badge">Admin</span>
    </div>

    <div v-if="error" class="form-error" role="alert">{{ error }}</div>

    <form @submit.prevent="submitForm" class="employee-form">
      <label>
        Full name
        <input v-model.trim="form.name" placeholder="e.g. John Doe" required autocomplete="name" />
      </label>
      <label>
        Work email
        <input v-model.trim="form.email" type="email" placeholder="name@company.com" required autocomplete="email" />
      </label>
      <label>
        Designation
        <select v-model="form.role" required>
          <option value="Employee">Employee</option>
          <option value="Dept Head">Dept Head</option>
          <option value="HR">HR Manager</option>
          <option value="CEO">CEO</option>
        </select>
      </label>
      <label>
        Department <span class="optional">Optional</span>
        <input v-model.trim="form.department" placeholder="e.g. Engineering" />
      </label>
      <button type="submit" :disabled="submitting" class="employee-submit">
        {{ submitting ? 'Creating account…' : 'Create QM account' }}
      </button>
    </form>

    <div v-if="result" class="form-success">
      <p class="success-title">Account created successfully</p>
      <p v-if="result.email"><strong>Email:</strong> {{ result.email }}</p>
      <p v-if="result.password"><strong>Temporary password:</strong> {{ result.password }}</p>
      <p>{{ result.message }}</p>
    </div>
  </div>
</template>

<style scoped>
.add-employee-card {
  padding: 22px;
  border: 1px solid var(--qx-border);
  border-radius: 16px;
  background: linear-gradient(145deg, rgba(99, 102, 241, .08), var(--qx-bg1) 42%);
  box-shadow: 0 12px 30px rgba(2, 6, 23, .18), inset 0 1px 0 rgba(255, 255, 255, .02);
}
.add-employee-heading { display: flex; justify-content: space-between; gap: 16px; margin-bottom: 20px; }
.add-employee-heading h2 { color: var(--qx-text1); font-size: 18px; font-weight: 700; }
.eyebrow { color: var(--qx-blue); font-size: 10px; font-weight: 700; letter-spacing: .12em; text-transform: uppercase; margin-bottom: 5px; }
.form-hint { color: var(--qx-text3); font-size: 12px; margin-top: 5px; }
.form-badge, .optional { color: var(--qx-blue); font-size: 10px; font-weight: 700; letter-spacing: .06em; text-transform: uppercase; }
.form-badge { align-self: flex-start; padding: 5px 8px; border: 1px solid rgba(99, 102, 241, .25); border-radius: 6px; background: var(--qx-blue-d); }
.employee-form { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 14px; }
.employee-form label {
  display: flex;
  flex-direction: column;
  gap: 7px;
  font-size: 11px;
  letter-spacing: .03em;
  text-transform: uppercase;
  color: var(--qx-text3);
}
.employee-form input, .employee-form select {
  width: 100%;
  min-height: 40px;
  text-transform: none;
  letter-spacing: normal;
}
.employee-submit { grid-column: 1 / -1; min-height: 40px; margin-top: 4px; }
.employee-submit:disabled { cursor: wait !important; opacity: .65; transform: none !important; }
.form-error, .form-success { margin-bottom: 16px; padding: 11px 13px; border-radius: 9px; font-size: 12px; line-height: 1.5; }
.form-error { color: #fda4af; background: var(--qx-red-d); border: 1px solid rgba(244, 63, 94, .25); }
.form-success { color: #a7f3d0; background: var(--qx-green-d); border: 1px solid rgba(16, 185, 129, .25); }
.success-title { color: #fff; font-weight: 700; margin-bottom: 4px; }
@media (max-width: 768px) {
  .add-employee-card { padding: 18px; }
  .add-employee-heading { flex-direction: column; gap: 10px; }
  .form-badge { align-self: flex-start; }
}
@media (max-width: 600px) { .employee-form { grid-template-columns: 1fr; } .employee-submit { grid-column: auto; } }
</style>
