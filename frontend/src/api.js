// Auto-updated API file for direct backend requests
// Set VITE_API_URL in .env (e.g. http://127.0.0.1:8000/api) if localhost fails

const BASE_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000/api";

export const getJobs = async () => {
  const response = await fetch(`${BASE_URL}/jobs`);
  if (!response.ok) throw new Error(await response.text());
  return response.json();
};

export const createJob = async (youtubeUrl) => {
  const response = await fetch(`${BASE_URL}/jobs`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ youtube_url: youtubeUrl }),
  });
  if (!response.ok) throw new Error(await response.text());
  return response.json();
};
