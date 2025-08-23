import axios from 'axios';
import { getToken, clearToken } from '@/lib/auth';

const api = axios.create({
  baseURL: 'http://localhost:8000/api/v1/',
  headers: { 'Content-Type': 'application/json' },
});

api.interceptors.request.use(config => {
  const token = getToken();
  if (token) config.headers.Authorization = `Token ${token}`;
  return config;
});

api.interceptors.response.use(
  res => res,
  err => {
    if (err.response?.status === 401) {
      clearToken();
      // No redirect here! Protected pages handle their own redirects.
    }
    return Promise.reject(err);
  }
);

export default api;
