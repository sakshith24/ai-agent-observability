const API_BASE_URL = "http://localhost:8000/api";

export async function fetchSessions() {
  const res = await fetch(`${API_BASE_URL}/sessions`);
  if (!res.ok) throw new Error("Failed to fetch sessions");
  return res.json();
}

export async function createSession() {
  const res = await fetch(`${API_BASE_URL}/sessions`, {
    method: "POST",
  });
  if (!res.ok) throw new Error("Failed to create session");
  return res.json();
}

export async function sendChatMessage(sessionId: string, message: string) {
  const res = await fetch(`${API_BASE_URL}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session_id: sessionId, message }),
  });
  
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Chat request failed");
  return data;
}