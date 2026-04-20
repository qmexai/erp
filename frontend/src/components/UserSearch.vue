<template>
  <div class="relative">
    <input
      type="text"
      v-model="searchQuery"
      @input="searchUsers"
      placeholder="Search for a user..."
      class="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
    />
    <ul v-if="users.length" class="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-md shadow-lg">
      <li
        v-for="user in users"
        :key="user.id"
        @click="selectUser(user)"
        class="px-4 py-2 cursor-pointer hover:bg-gray-100"
      >
        {{ user.name }} ({{ user.email }})
      </li>
    </ul>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import apiClient from '../api'; // Import the new API client

const searchQuery = ref('');
const users = ref([]);
const emit = defineEmits(['user-selected']);

let debounceTimer;

const searchUsers = () => {
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(async () => {
    if (searchQuery.value.length < 2) {
      users.value = [];
      return;
    }
    try {
      const response = await apiClient.get('/users/', {
        params: { search: searchQuery.value }
      });
      users.value = response.data;
    } catch (error) {
      console.error('Error searching users:', error);
      users.value = []; // Clear users on error
    }
  }, 300);
};

const selectUser = (user) => {
  searchQuery.value = '';
  users.value = [];
  emit('user-selected', user);
};
</script>