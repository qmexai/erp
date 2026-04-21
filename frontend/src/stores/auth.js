// frontend/src/stores/auth.js
import { defineStore } from 'pinia';
import { auth } from '../firebaseConfig';
import { signInWithEmailAndPassword, signOut } from 'firebase/auth';
import axios from 'axios';

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: JSON.parse(localStorage.getItem('user')) || null,
    token: localStorage.getItem('token') || null,
  }),
  actions: {
    async login(email, password) {
      console.log('[AUTH] Attempting login for', email);
      const userCredential = await signInWithEmailAndPassword(auth, email, password);
      const token = await userCredential.user.getIdToken();
      console.log('[AUTH] Firebase token:', token);
      // Verify with Django
      // Use the Render backend URL instead of localhost
      const backendUrl = import.meta.env.VITE_API_URL || 'https://erp-e1ax.onrender.com';
      const response = await axios.post(`${backendUrl}/api/login/`, { token });
      console.log('[AUTH] Django login response:', response.data);
      this.user = response.data; // The whole user object is the response
      this.token = token;
      localStorage.setItem('user', JSON.stringify(this.user));
      localStorage.setItem('token', token);
      console.log('[AUTH] Login complete. User:', this.user);
    },
    logout() {
      console.log('[AUTH] Logging out');
      signOut(auth);
      this.user = null;
      this.token = null;
      localStorage.removeItem('user');
      localStorage.removeItem('token');
      console.log('[AUTH] Logout complete');
    },
    async getFirebaseToken() {
      if (!auth.currentUser) {
        console.log('[AUTH] No current user for token refresh.');
        this.logout(); // Clean up state if user is gone
        return null;
      }
      try {
        // The `true` forces a token refresh if the current one is expired.
        const token = await auth.currentUser.getIdToken(true);
        this.token = token;
        localStorage.setItem('token', token);
        console.log('[AUTH] Token refreshed successfully.');
        return token;
      } catch (error) {
        console.error('[AUTH] Error refreshing token:', error);
        this.logout(); // Logout on token refresh failure
        return null;
      }
    }
  }
});