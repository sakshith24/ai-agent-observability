"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { fetchSessions, createSession } from "@/lib/api";

interface SessionItem {
  session_id: string;
  title: string;
  created_at: string;
}

interface ChatLogItem {
  role: string;
  content: string;
  run_id?: string;
  duration_ms?: number;
}

export default function ChatPage() {
  const [sessions, setSessions] = useState<SessionItem[]>([]);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [message, setMessage] = useState("");
  const [chatLog, setChatLog] = useState<ChatLogItem[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadSessions();
  }, []);

  async function loadSessions() {
    try {
      const list = await fetchSessions();
      setSessions(list);
      if (list.length > 0 && !sessionId) {
        setSessionId(list[0].session_id);
      } else if (list.length === 0) {
        handleNewSession();
      }
    } catch (err) {
      console.error("Error loading sessions:", err);
    }
  }

  async function handleNewSession() {
    try {
      const data = await createSession();
      setSessionId(data.session_id);
      setChatLog([]);
      await loadSessions();
    } catch (err) {
      console.error("Failed to create session:", err);
    }
  }

  const sendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!message.trim() || !sessionId) return;

    const userMsg = message;
    setMessage("");
    setChatLog((prev) => [...prev, { role: "user", content: userMsg }]);
    setLoading(true);

    try {
      const res = await fetch("http://localhost:8000/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: sessionId, message: userMsg }),
      });
      const data = await res.json();
      
      // Capture run_id and duration_ms from your observability backend!
      setChatLog((prev) => [
        ...prev, 
        { 
          role: "assistant", 
          content: data.response, 
          run_id: data.run_id,
          duration_ms: data.duration_ms 
        }
      ]);
    } catch (err) {
      console.error(err);
      setChatLog((prev) => [...prev, { role: "assistant", content: "Error communicating with backend." }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="flex flex-col h-screen max-w-3xl mx-auto p-4 justify-between bg-gray-950 text-white">
      {/* Top Header with Dashboard Link */}
      <div className="flex justify-between items-center pb-4 border-b border-gray-800">
        <h1 className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-indigo-500">
          AI Developer Assistant & Observability
        </h1>
        <Link
          href="/dashboard"
          className="bg-gray-900 hover:bg-gray-800 border border-gray-700 text-xs px-3 py-1.5 rounded-lg font-medium transition-colors"
        >
          Open Observability Dashboard &rarr;
        </Link>
      </div>

      {/* Chat Log Window */}
      <div className="flex flex-col gap-4 overflow-y-auto flex-1 py-4">
        {chatLog.map((log, index) => (
          <div
            key={index}
            className={`p-4 rounded-xl max-w-[85%] space-y-2 ${
              log.role === "user"
                ? "bg-blue-600 text-white self-end ml-auto"
                : "bg-gray-900 border border-gray-800 text-gray-200 self-start mr-auto"
            }`}
          >
            <div className="flex justify-between items-center text-xs opacity-70">
              <span className="font-semibold uppercase">{log.role}</span>
              {log.duration_ms && <span>{log.duration_ms} ms</span>}
            </div>
            
            <p className="whitespace-pre-wrap text-sm">{log.content}</p>

            {/* Direct Link to the Observability Trace for this specific run */}
            {log.run_id && (
              <div className="pt-2 border-t border-gray-800 text-right">
                <Link
                  href={`/runs/${log.run_id}`}
                  className="text-xs text-blue-400 hover:underline font-mono"
                >
                  🔍 Inspect Execution Trace &rarr;
                </Link>
              </div>
            )}
          </div>
        ))}
        {loading && (
          <div className="text-gray-500 italic text-sm animate-pulse">
            Agent is thinking, invoking tools, and recording telemetry...
          </div>
        )}
      </div>

      {/* Message Input Form */}
      <form onSubmit={sendMessage} className="flex gap-2 pt-4 border-t border-gray-800">
        <input
          type="text"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Ask something about your codebase..."
          className="bg-gray-900 border border-gray-800 text-white flex-1 p-3 rounded-xl focus:outline-none focus:border-blue-500 text-sm"
        />
        <button
          type="submit"
          className="bg-blue-600 hover:bg-blue-500 text-white px-5 py-3 rounded-xl font-medium text-sm transition-colors"
        >
          Send
        </button>
      </form>
    </main>
  );
}