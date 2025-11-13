export async function getHealth(apiBase = import.meta.env.VITE_API_URL || 'http://localhost:8080/api') {
  const res = await fetch(`${apiBase}/health`);
  return res.json();
}