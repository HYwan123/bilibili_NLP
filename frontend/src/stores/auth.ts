import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { jwtDecode } from 'jwt-decode';

interface JwtPayload {
  sub: string;
  exp: number;
}

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || '');
  const isAuthenticated = ref(!!token.value);

  const username = computed(() => {
    if (token.value) {
      try {
        const decoded = jwtDecode<JwtPayload>(token.value);
        return decoded.sub;
      } catch (error) {
        console.error("Failed to decode token:", error);
        return '';
      }
    }
    return '';
  });

  function setToken(newToken: string) {
    localStorage.setItem('token', newToken);
    token.value = newToken;
    isAuthenticated.value = true;
  }

  function clearToken() {
    localStorage.removeItem('token');
    token.value = '';
    isAuthenticated.value = false;
  }

  return { token, isAuthenticated, username, setToken, clearToken };
}); 