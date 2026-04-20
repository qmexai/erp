<template>
  <div class="min-h-screen bg-[#09090b] flex items-center justify-center p-4">
    <div class="w-full max-w-md bg-[#121214] border border-white/10 p-8 rounded-2xl shadow-2xl">
      <h1 class="text-2xl font-bold text-white mb-2 text-center">QMEXAI ERP</h1>
      <p class="text-gray-400 text-sm text-center mb-8">Enter your QM credentials to access Qmexai</p>

      <form @submit.prevent="handleLogin" class="space-y-6">
        <div>
          <label class="block text-xs font-medium text-gray-400 uppercase tracking-wider mb-2">Email Address</label>
          <input v-model="email" type="email" required 
            class="w-full bg-black/50 border border-white/10 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-white/40 transition-all"
            placeholder="name@qmexai.com" />
        </div>

        <div>
          <label class="block text-xs font-medium text-gray-400 uppercase tracking-wider mb-2">Password</label>
          <input v-model="password" type="password" required 
            class="w-full bg-black/50 border border-white/10 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-white/40 transition-all"
            placeholder="••••••••" />
        </div>

        <button type="submit" :disabled="loading"
          class="w-full bg-white text-black font-semibold py-3 rounded-lg hover:bg-gray-200 transition-all disabled:opacity-50">
          {{ loading ? 'Authenticating...' : 'Sign In' }}
        </button>
        
        <p v-if="error" class="text-red-500 text-sm text-center mt-4">{{ error }}</p>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useAuthStore } from '../stores/auth';
import { useRouter } from 'vue-router';

const email = ref('');
const password = ref('');
const error = ref('');
const loading = ref(false);
const authStore = useAuthStore();
const router = useRouter();

const handleLogin = async () => {
  loading.value = true;
  error.value = '';
  try {
    await authStore.login(email.value, password.value);
    router.push('/dashboard');
  } catch (err) {
    console.error("Login failed:", err); // Detailed error logging
    error.value = "Invalid credentials or account blocked. Check console for details.";
    if (err.response && err.response.data) {
      console.error("Backend error details:", err.response.data);
      const backendError = err.response.data.detail || err.response.data.error;
      if (backendError) {
        error.value = backendError;
      }
    }
  } finally {
    loading.value = false;
  }
};
</script>