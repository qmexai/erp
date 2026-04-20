import axios from 'axios';
import { useAuthStore } from './stores/auth';

const apiClient = axios.create({
  baseURL: 'http://127.0.0.1:8000/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

apiClient.interceptors.request.use(
  async (config) => {
    const authStore = useAuthStore();
    // Use the new getFirebaseToken method to ensure a valid token
    const token = await authStore.getFirebaseToken(); 
    
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

export default apiClient;
