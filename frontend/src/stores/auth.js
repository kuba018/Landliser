import { defineStore } from 'pinia';
import api from '../api/http';
import { isExpired } from '../utils/jwt';
import { AUTH } from '../api/endpoints';

export const useAuthStore = defineStore('auth', {
  state: () => ({ access: null, refresh: null, user: null, isLoading: false }),
  getters: {
    isAuthenticated: (s) => !!s.access && !isExpired(s.access),
  },
  actions: {
    initFromStorage() {
      const raw = localStorage.getItem('landliser_auth');
      if (!raw) return;
      const { access, refresh, user } = JSON.parse(raw);
      this.access = access; this.refresh = refresh; this.user = user;
    },
    persist() {
      localStorage.setItem('landliser_auth', JSON.stringify({
        access: this.access, refresh: this.refresh, user: this.user
      }));
    },
    async login(credentials) {
      this.isLoading = true;
      try {
        const { data } = await api.post(AUTH.login, credentials);
        this.access = data.access; this.refresh = data.refresh ?? null;
        this.persist();
        await this.fetchMe().catch(() => {});
        return true;
      } finally { this.isLoading = false; }
    },
    async fetchMe() {
      const { data } = await api.get(AUTH.me);
      this.user = data; this.persist();
    },
    async tryRefresh() {
      if (!this.refresh) return false;
      try {
        const { data } = await api.post(AUTH.refresh, { refresh: this.refresh });
        this.access = data.access; this.persist(); return true;
      } catch { this.logout(); return false; }
    },
    logout() {
      this.access = null; this.refresh = null; this.user = null;
      localStorage.removeItem('landliser_auth');
    },
  },
});
