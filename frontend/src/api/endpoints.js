export const AUTH = {
  login:   '/api/auth/token/',
  refresh: '/api/auth/token/refresh/',
  me:      '/api/user/me/',
  register: '/api/user/register/',
  verifyEmail: '/api/user/verify-email/',
  passwordResetRequest: '/api/user/password-reset/request/',
  passwordResetConfirm: '/api/user/password-reset/confirm/',
  deleteAccount: '/api/user/delete-account/',
};
export const PARCEL = {
  // lista działek zalogowanego użytkownika
  list: '/api/parcels/',

  // szczegóły pojedynczej działki
  detail: (id) => `/api/parcels/${id}/`,

  // akcja @action(detail=False, url_path='scrape') w ParcelViewSet
  scrape: '/api/parcels/scrape/',

  // przeliczenie łącznego podatku dla działki
  // @action(detail=True, methods=['post'], url_path='calculate-tax')
  calculateTax: (id) => `/api/parcels/${id}/calculate-tax/`,

  // kryteria podatkowe
  criteria: '/api/criteria/',
  criterionDetail: (id) => `/api/criteria/${id}/`,
};
