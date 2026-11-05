"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

interface Run {
  id: string;
  trace_id: string;
  status: string;
  duration_ms: number | null;
  created_at: string;
}

interface Metrics {
  total_runs: number;
  successful_runs: number;
  failed_runs: number;
  avg_latency_ms: number;
  recent_runs: Run[];
}

export default function DashboardPage() {
  const [data, setData] = useState<Metrics | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("http://localhost:8000/api/observability/metrics")
      .then((res) => res.json())
      .then((data) => {
        setData(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Failed to fetch metrics:", err);
        setLoading(false);
      });
  }, []);

  if (loading) return <div className="p-8 text-gray-400 bg-gray-950 min-h-screen">Loading dashboard metrics...</div>;

  return (
    <div className="min-h-screen bg-gray-950 text-white p-8">
      <div className="max-w-6xl mx-auto space-y-8">
        <h1 className="text-3xl font-bold">Observability Dashboard</h1>

        {/* Metric Cards Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
          <div className="bg-gray-900 border border-gray-800 p-6 rounded-xl">
            <p className="text-sm text-gray-400">Total Runs</p>
            <p className="text-3xl font-semibold mt-2">{data?.total_runs ?? 0}</p>
          </div>
          <div className="bg-gray-900 border border-gray-800 p-6 rounded-xl">
            <p className="text-sm text-gray-400">Successful Runs</p>
            <p className="text-3xl font-semibold mt-2 text-emerald-400">{data?.successful_runs ?? 0}</p>
          </div>
          <div className="bg-gray-900 border border-gray-800 p-6 rounded-xl">
            <p className="text-sm text-gray-400">Failed Runs</p>
            <p className="text-3xl font-semibold mt-2 text-rose-400">{data?.failed_runs ?? 0}</p>
          </div>
          <div className="bg-gray-900 border border-gray-800 p-6 rounded-xl">
            <p className="text-sm text-gray-400">Avg Latency</p>
            <p className="text-3xl font-semibold mt-2">{data?.avg_latency_ms ?? 0} ms</p>
          </div>
        </div>

        {/* Recent Runs Table */}
        <div className="bg-gray-900 border border-gray-800 rounded-xl overflow-hidden">
          <div className="p-6 border-b border-gray-800">
            <h2 className="text-xl font-semibold">Execution History</h2>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-gray-800 text-gray-400 text-sm">
                  <th className="p-4">Trace ID</th>
                  <th className="p-4">Status</th>
                  <th className="p-4">Duration</th>
                  <th className="p-4">Timestamp</th>
                  <th className="p-4 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-800 text-sm">
                {(data?.recent_runs || []).map((run) => (
                  <tr key={run.id} className="hover:bg-gray-850">
                    <td className="p-4 font-mono text-xs text-blue-400">{run.trace_id}</td>
                    <td className="p-4">
                      <span className={`px-2 py-1 rounded text-xs font-medium ${
                        run.status === "completed" ? "bg-emerald-500/10 text-emerald-400" : "bg-rose-500/10 text-rose-400"
                      }`}>
                        {run.status}
                      </span>
                    </td>
                    <td className="p-4">{run.duration_ms ? `${run.duration_ms} ms` : "N/A"}</td>
                    <td className="p-4 text-gray-400">{new Date(run.created_at).toLocaleString()}</td>
                    <td className="p-4 text-right">
                      <Link href={`/runs/${run.id}`} className="text-blue-400 hover:underline">
                        View Trace &rarr;
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}