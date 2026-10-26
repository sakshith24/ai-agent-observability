"use client"

import { useState } from "react";

export default function ChatPage() {
  const [message, setMessage] = useState("");
  const [chatLog, setChatLog] = useState<{ role: string; content: string }[]>([]);
  const [loading, setLoading] = useState(false);

  const sendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!message.trim()) return;

    const userMsg = message;
    setMessage("");
    setChatLog((prev) => [...prev, { role: "user", content: userMsg }]);
    setLoading(true);

    try {
      const res = await fetch("http://localhost:8000/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: "00000000-0000-0000-0000-000000000000", message: userMsg }),
      });
      const data = await res.json();
      setChatLog((prev) => [...prev, { role: "assistant", content: data.response }]);
    } catch (err) {
      console.error(err);
      setChatLog((prev) => [...prev, { role: "assistant", content: "Error communicating with backend." }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="flex flex-col h-screen max-w-2xl mx-auto p-4 justify-between">
      <div className="flex flex-col gap-4 overflow-y-auto flex-1">
        <h1 className="text-xl font-bold">AI Developer Assistant</h1>
        {chatLog.map((log, index) => (
          <div key={index} className={`p-3 rounded-lg ${log.role === "user" ? "bg-blue-100 self-end" : "bg-gray-100 self-start"}`}>
            <strong>{log.role}: </strong> {log.content}
          </div>
        ))}
        {loading && <div className="text-gray-500 italic">Agent is processing and invoking MCP tools...</div>}
      </div>
      <form onSubmit={sendMessage} className="flex gap-2 mt-4">
        <input
          type="text"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Ask something about your codebase..."
          className="border flex-1 p-2 rounded"
        />
        <button type="submit" className="bg-blue-600 text-white px-4 py-2 rounded">Send</button>
      </form>
    </main>
  );
}