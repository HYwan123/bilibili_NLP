import axios from 'axios';
import { useAuthStore } from '@/stores/auth';
import { ElMessage } from 'element-plus';
import router from '@/router';

// Create a new Axios instance
const service = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL, // Use environment variables for base URL
  timeout: 600000, // Request timeout，60秒
});

// Request interceptor
service.interceptors.request.use(
  (config) => {
    // It's better to get the store inside the interceptor,
    // to avoid issues with Pinia initialization order.
    const authStore = useAuthStore();
    if (authStore.token) {
      config.headers['Authorization'] = `Bearer ${authStore.token}`;
    }
    return config;
  },
  (error) => {
    console.log(error); // for debug
    return Promise.reject(error);
  }
);

// Response interceptor
service.interceptors.response.use(
  (response) => {
    const res = response.data;
    // Check for custom backend code. `0` or `200` are typical success codes.
    if (res.code && res.code !== 200) {
       ElMessage({
        message: res.message || 'Error',
        type: 'error',
        duration: 5 * 1000,
      });

      // Handle specific error for token issues
      if (res.code === 401 || res.code === 403) {
         const authStore = useAuthStore();
         authStore.logout();
         router.push('/login');
      }
      return Promise.reject(new Error(res.message || 'Error'));
    } else {
      // Return the whole response if no custom code, or if code is success
      return response.data; // Directly return the `data` part for convenience
    }
  },
  (error) => {
    console.log('err' + error); // for debug
    ElMessage({
      message: error.message,
      type: 'error',
      duration: 5 * 1000,
    });
     if (error.response && error.response.status === 401) {
        const authStore = useAuthStore();
        authStore.logout();
        router.push('/login');
    }
    return Promise.reject(error);
  }
);

export default service; 