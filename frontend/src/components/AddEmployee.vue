<script setup>
import { ref } from 'vue';
import apiClient from '../api';

const form = ref({ email: '', name: '', role: 'Employee', department: '', password: '' });
const result = ref(null);

const generatePassword = () => {
  // Simple password generator for the example
  return Math.random().toString(36).slice(-8);
}

const submitForm = async () => {
  try {
    const payload = { ...form.value, password: generatePassword() };
    const res = await apiClient.post('/create-employee/', payload);
    result.value = res.data;
  } catch (err) {
    console.error("Error creating employee:", err.response?.data || err.message);
    alert("Error creating employee: " + (err.response?.data?.error || 'An unknown error occurred.'));
  }
};
</script>

<template>
  <div class="bg-[#121214] p-6 rounded-xl border border-white/10">
    <h2 class="text-xl font-bold text-white mb-4">Register New Personnel</h2>
    <form @submit.prevent="submitForm" class="grid grid-cols-2 gap-4">
      <input v-model="form.name" placeholder="Full Name" required class="bg-black border border-white/10 p-2 text-white rounded" />
      <input v-model="form.email" type="email" placeholder="Email" required class="bg-black border border-white/10 p-2 text-white rounded" />
      <select v-model="form.role" required class="bg-black border border-white/10 p-2 text-white rounded">
        <option value="Employee">Employee</option>
        <option value="Dept Head">Dept Head</option>
        <option value="HR">HR Manager</option>
        <option value="CEO">CEO</option>
      </select>
      <input v-model="form.department" placeholder="Department" class="bg-black border border-white/10 p-2 text-white rounded" />
      <div class="col-span-2">
        <button type="submit" class="mt-4 bg-blue-600 px-4 py-2 rounded text-white w-full">Generate QM Account</button>
      </div>
    </form>

    <div v-if="result" class="mt-4 p-4 bg-green-900/20 border border-green-500/50 rounded text-green-200">
      <p>Account Created!</p>
      <p v-if="result.email"><strong>Email:</strong> {{ result.email }}</p>
      <p v-if="result.password"><strong>Temp Password:</strong> {{ result.password }}</p>
      <p>{{ result.message }}</p>
    </div>
  </div>
</template>