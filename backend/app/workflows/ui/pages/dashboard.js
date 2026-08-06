import { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';

export default function ExecutiveDashboard() {
  const [briefingData, setBriefingData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchBriefing() {
      try {
        const response = await fetch('http://localhost:8000/api/v1/agent/daily-briefing', {
          method: 'POST',
        });
        const data = await response.json();
        if (data.status === 'success') {
          setBriefingData(data);
        }
      } catch (error) {
        console.error("Error connecting to Agentic Job Search API:", error);
      } finally {
        setLoading(false);
      }
    }
    fetchBriefing();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-900 flex flex-col justify-center items-center text-slate-200">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-indigo-500 mb-4"></div>
        <p className="text-sm font-medium tracking-wide">Assembling morning executive intelligence channels...</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 font-sans">
      {/* Top Navigation */}
      <header className="border-b border-slate-800 bg-slate-900/50 backdrop-blur sticky top-0 z-50 px-8 py-4 flex justify-between items-center">
        <div>
          <h1 className="text-xl font-bold bg-gradient-to-r from-indigo-400 to-cyan-400 bg-clip-text text-transparent">
            Agentic Job Search System
          </h1>
          <p className="text-xs text-slate-400">Enterprise Engineering Leadership Command Center</p>
        </div>
        <div className="flex items-center gap-3">
          <span className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse"></span>
          <span className="text-xs font-mono text-slate-400 bg-slate-800 px-3 py-1 rounded-md border border-slate-700">
            Pipeline Live
          </span>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-8">
        {/* High-Level Metric Cards Row */}
        <section className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-slate-900 p-6 rounded-xl border border-slate-800 shadow-xl">
            <p className="text-xs font-medium uppercase tracking-wider text-slate-400">Target Role Profile</p>
            <h3 className="text-lg font-bold text-slate-100 mt-2">Sr. Director / VP</h3>
            <p className="text-xs text-indigo-400 mt-1">Platform & AI Infrastructure</p>
          </div>
          <div className="bg-slate-900 p-6 rounded-xl border border-slate-800 shadow-xl">
            <p className="text-xs font-medium uppercase tracking-wider text-slate-400">Compensation Floor</p>
            <h3 className="text-2xl font-black text-emerald-400 mt-1">$250,000+</h3>
            <p className="text-xs text-slate-500 mt-1">Total Comp Target Ingested</p>
          </div>
          <div className="bg-slate-900 p-6 rounded-xl border border-slate-800 shadow-xl">
            <p className="text-xs font-medium uppercase tracking-wider text-slate-400">Agent Processing Status</p>
            <h3 className="text-lg font-bold text-cyan-400 mt-2">Optimizations Ready</h3>
            <p className="text-xs text-slate-500 mt-1">Resume modifications generated</p>
          </div>
        </section>

        {/* Live Dynamic Markdown Stream Section */}
        <section className="bg-slate-900 rounded-xl border border-slate-800 shadow-2xl overflow-hidden">
          <div className="border-b border-slate-800 bg-slate-850 px-6 py-4 flex justify-between items-center">
            <h2 className="text-sm font-semibold text-slate-300 tracking-wide uppercase">
              Morning Intelligence Stream
            </h2>
            <span className="text-xs text-slate-400 font-mono">
              Generated: {briefingData?.briefing_date}
            </span>
          </div>
          
          <div className="p-8 prose prose-invert prose-indigo max-w-none text-slate-300 space-y-4 leading-relaxed">
            {briefingData?.content_markdown ? (
              <ReactMarkdown>{briefingData.content_markdown}</ReactMarkdown>
            ) : (
              <p className="text-slate-500 italic">No briefing streams compiled for today.</p>
            )}
          </div>
        </section>
      </main>
    </div>
  );
}