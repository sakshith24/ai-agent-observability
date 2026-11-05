"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";

interface ExecutionEvent {
  id: string;
  event_type: string;
  status: string;
  duration_ms: number | null;
  payload: Record<string, any>;
  created_at: string;
}

interface RunDetails {
  id: string;
  session_id: string;
  trace_id: string;
  status: string;
  duration_ms: number | null;
  created_at: string;
  events: ExecutionEvent[];
}

export default function RunDetailsPage() {
  const params = useParams();
  const runId = params.id;
  const [run, setRun] = useState<RunDetails | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!runId) return;
    fetch(`http://localhost:8000/api/observability/runs/${runId}`)
      .then((res) => res.json())
      .then((data) => {
        setRun(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Failed to load run details:", err);
        setLoading(false);
      });
  }, [runId]);

  if (loading) return <div className="p-8 text-gray-400 bg-gray-950 min-h-screen">Loading run trace details...</div>;
  if (!run) return <div className="p-8 text-rose-400 bg-gray-950 min-h-screen">Run not found.</div>;

  return (
    <div className="min-h-screen bg-gray-950 text-white p-8">
      <div className="max-w-4xl mx-auto space-y-6">
        <Link href="/dashboard" className="text-sm text-blue-400 hover:underline">
          &larr; Back to Dashboard
        </Link>

        {/* Run Header Summary */}
        <div className="bg-gray-900 border border-gray-800 p-6 rounded-xl space-y-4">
          <div className="flex justify-between items-start">
            <div>
              <h1 className="text-2xl font-bold">Execution Trace Details</h1>
              <p className="text-xs font-mono text-gray-400 mt-1">Trace ID: {run.trace_id}</p>
            </div>
            <span className={`px-3 py-1 rounded-full text-xs font-medium ${
              run.status === "completed" ? "bg-emerald-500/10 text-emerald-400" : "bg-rose-500/10 text-rose-400"
            }`}>
              {run.status}
            </span>
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 text-sm pt-2 border-t border-gray-800">
            <div>
              <span className="text-gray-400">Total Duration:</span> <p className="font-semibold">{run.duration_ms ?? 0} ms</p>
            </div>
            <div>
              <span className="text-gray-400">Started At:</span> <p className="font-semibold">{new Date(run.created_at).toLocaleString()}</p>
            </div>
          </div>
        </div>

        {/* Chronological Event Timeline */}
        <div className="space-y-4">
          <h2 className="text-xl font-semibold">Timeline & Execution Events</h2>
          <div className="space-y-3">
            {run.events.map((event, index) => (
              <div key={event.id} className="bg-gray-900 border border-gray-800 p-5 rounded-xl space-y-3">
                <div className="flex justify-between items-center">
                  <div className="flex items-center space-x-3">
                    <span className="bg-gray-800 text-gray-300 px-2.5 py-1 rounded text-xs font-mono">
                      #{index + 1}
                    </span>
                    <span className="font-semibold text-blue-400 uppercase text-xs tracking-wider">
                      {event.event_type}
                    </span>
                  </div>
                  <div className="flex items-center space-x-3">
                    {event.duration_ms !== null && (
                      <span className="text-xs text-gray-400">{event.duration_ms} ms</span>
                    )}
                    <span className={`px-2 py-0.5 rounded text-xs font-medium ${
                      event.status === "completed" ? "bg-emerald-500/10 text-emerald-400" : "bg-rose-500/10 text-rose-400"
                    }`}>
                      {event.status}
                    </span>
                  </div>
                </div>

                {/* Structured Payload Viewer */}
                <div className="bg-gray-950 p-3 rounded-lg border border-gray-850 overflow-x-auto">
                  <pre className="text-xs font-mono text-gray-300">
                    {JSON.stringify(event.payload, null, 2)}
                  </pre>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}