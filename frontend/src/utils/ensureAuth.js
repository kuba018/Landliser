import { useAuthStore } from '../stores/auth';
import { isExpired } from './jwt';

export async function ensureAuth({ redirectTo = '/' } = {}) {
  const auth = useAuthStore();
  if (auth.access && !isExpired(auth.access)) return true;
  if (auth.refresh) {
    const ok = await auth.tryRefresh();
    if (ok) return true;
  }
  if (location.pathname !== redirectTo) location.assign(redirectTo);
  return false;
}
