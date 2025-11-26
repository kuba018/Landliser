import axios from 'axios';
import { useAuthStore } from '../stores/auth';
import { isExpired } from '../utils/jwt';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
});

// ŚCIEŻKA, pod którą masz formularz logowania
const LOGIN_PATH = '/';

api.interceptors.request.use(async (config) => {
  const auth = useAuthStore();
  if (auth.access) {
    if (isExpired(auth.access) && auth.refresh) {
      await auth.tryRefresh();
    }
    if (auth.access && !isExpired(auth.access)) {
      config.headers.Authorization = `Bearer ${auth.access}`;
    }
  }
  return config;
});

let refreshing = false;
let queue = [];

function flushQueue(err, token) {
  queue.forEach((p) => (err ? p.reject(err) : p.resolve(token)));
  queue = [];
}

api.interceptors.response.use(
  (r) => r,
  async (error) => {
    const { response, config } = error;
    const auth = useAuthStore();

    // jeśli brak odpowiedzi, inny status niż 401 albo już retryowane → nie ruszamy
    if (!response || response.status !== 401 || config.__isRetry) {
      throw error;
    }

    // BRAK refresh tokena → wyloguj i ewentualnie przerzuć na stronę logowania
    if (!auth.refresh) {
      auth.logout();

      // przerzucamy tylko wtedy, jeśli NIE jesteśmy już na stronie logowania
      if (location.pathname !== LOGIN_PATH) {
        location.assign(LOGIN_PATH);
      }

      throw error;
    }

    // jeśli refresh już w toku – dokładamy request do kolejki
    if (refreshing) {
      return new Promise((resolve, reject) => {
        queue.push({
          resolve: (token) => {
            config.__isRetry = true;
            config.headers.Authorization = `Bearer ${token}`;
            resolve(api(config));
          },
          reject,
        });
      });
    }

    refreshing = true;

    try {
      const ok = await auth.tryRefresh();
      flushQueue(null, auth.access);

      if (!ok) {
        throw error;
      }

      config.__isRetry = true;
      config.headers.Authorization = `Bearer ${auth.access}`;
      return api(config);
    } catch (e) {
      flushQueue(e, null);
      auth.logout();

      // znów: tylko jeśli nie jesteśmy już na stronie logowania
      if (location.pathname !== LOGIN_PATH) {
        location.assign(LOGIN_PATH);
      }

      throw e;
    } finally {
      refreshing = false;
    }
  },
);

export default api;
