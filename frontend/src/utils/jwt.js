export function parseJwt(token) {
  try {
    return JSON.parse(atob(token.split('.')[1]));
  } catch { return null; }
}

export function isExpired(token, skewSeconds = 10) {
  const p = parseJwt(token);
  if (!p || !p.exp) return true;
  const now = Math.floor(Date.now() / 1000);
  return p.exp <= now + skewSeconds;
}
