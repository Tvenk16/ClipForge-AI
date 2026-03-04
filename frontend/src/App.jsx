import { useState, useEffect, useCallback } from "react";
import { getJobs, createJob } from "./api";

const POLL_MS = 5000;

function formatSeconds(s) {
  const m = Math.floor(s / 60);
  const sec = Math.round(s % 60);
  return `${m}:${sec.toString().padStart(2, "0")}`;
}

function timeAgo(ts) {
  const secs = typeof ts === "string" ? new Date(ts).getTime() / 1000 : ts;
  const diff = Math.floor(Date.now() / 1000 - secs);
  if (diff < 60) return `${diff}s ago`;
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
  return `${Math.floor(diff / 3600)}h ago`;
}

const STATUS = {
  queued: { color: "#64748b", bg: "rgba(100,116,139,0.12)", border: "rgba(100,116,139,0.25)", glow: "none" },
  processing: { color: "#f59e0b", bg: "rgba(245,158,11,0.12)", border: "rgba(245,158,11,0.3)", glow: "0 0 12px rgba(245,158,11,0.3)" },
  completed: { color: "#10b981", bg: "rgba(16,185,129,0.12)", border: "rgba(16,185,129,0.3)", glow: "0 0 12px rgba(16,185,129,0.2)" },
  failed: { color: "#ef4444", bg: "rgba(239,68,68,0.12)", border: "rgba(239,68,68,0.3)", glow: "none" },
};

function StatusBadge({ status }) {
  const s = STATUS[status] || STATUS.queued;
  return (
    <span style={{
      display: "inline-flex", alignItems: "center", gap: 6,
      padding: "3px 10px", borderRadius: 999,
      fontSize: 11, fontWeight: 700, letterSpacing: "0.07em",
      textTransform: "uppercase",
      color: s.color, background: s.bg, border: `1px solid ${s.border}`,
      boxShadow: s.glow,
    }}>
      <span style={{
        width: 6, height: 6, borderRadius: "50%", background: s.color,
        animation: status === "processing" ? "throb 1.4s ease-in-out infinite" : "none",
      }} />
      {status}
    </span>
  );
}

function ScoreBar({ score }) {
  const pct = Math.round((score ?? 0.85) * 100);
  const color = pct >= 90 ? "#10b981" : pct >= 70 ? "#f59e0b" : "#64748b";
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
      <div style={{ flex: 1, height: 4, background: "rgba(255,255,255,0.06)", borderRadius: 2, overflow: "hidden" }}>
        <div style={{ width: `${pct}%`, height: "100%", background: color, borderRadius: 2,
          transition: "width 0.6s cubic-bezier(0.4,0,0.2,1)" }} />
      </div>
      <span style={{ fontSize: 11, color, fontWeight: 700, fontFamily: "monospace", minWidth: 28 }}>{pct}%</span>
    </div>
  );
}

function ClipCard({ clip, caption, index }) {
  const start = clip.start_seconds ?? clip.start ?? 0;
  const end = clip.end_seconds ?? clip.end ?? 0;
  const reason = clip.reason ?? "clip";
  const score = clip.score ?? 0.85;
  return (
    <div style={{
      background: "rgba(255,255,255,0.03)", border: "1px solid rgba(255,255,255,0.07)",
      borderRadius: 10, padding: "14px 16px", marginBottom: 8,
    }}>
      <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 10 }}>
        <span style={{
          background: "rgba(99,102,241,0.2)", border: "1px solid rgba(99,102,241,0.35)",
          color: "#818cf8", padding: "2px 8px", borderRadius: 5,
          fontSize: 11, fontFamily: "monospace", fontWeight: 600,
        }}>
          CLIP {index + 1}
        </span>
        <span style={{
          background: "rgba(255,255,255,0.05)", color: "#94a3b8",
          padding: "2px 8px", borderRadius: 5, fontSize: 11, fontFamily: "monospace",
        }}>
          {formatSeconds(start)} → {formatSeconds(end)}
        </span>
        <span style={{ fontSize: 11, color: "#475569", flex: 1 }}>{reason}</span>
      </div>
      <ScoreBar score={score} />
      {caption && (
        <div style={{ marginTop: 12, paddingTop: 12, borderTop: "1px solid rgba(255,255,255,0.05)" }}>
          <div style={{ fontSize: 13, fontWeight: 600, color: "#e2e8f0", marginBottom: 4, lineHeight: 1.4 }}>
            {caption.hook}
          </div>
          <div style={{ fontSize: 12, color: "#64748b", lineHeight: 1.6, marginBottom: 6 }}>
            {caption.caption}
          </div>
          {caption.hashtags?.length > 0 && (
            <div style={{ fontSize: 11, color: "#6366f1" }}>
              {caption.hashtags.join(" ")}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function JobRow({ job, isSelected, onClick }) {
  return (
    <div onClick={onClick} style={{
      padding: "14px 18px", cursor: "pointer",
      borderBottom: "1px solid rgba(255,255,255,0.05)",
      background: isSelected ? "rgba(99,102,241,0.07)" : "transparent",
      borderLeft: isSelected ? "2px solid #6366f1" : "2px solid transparent",
      transition: "all 0.15s",
    }}>
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 4 }}>
        <span style={{ fontSize: 11, color: "#475569", fontFamily: "monospace" }}>
          #{job.id.slice(0, 8)}
        </span>
        <StatusBadge status={job.status} />
      </div>
      <div style={{ fontSize: 12, color: "#94a3b8", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap", marginBottom: 4 }}>
        {job.youtube_url?.replace("https://www.youtube.com/watch?v=", "youtube.com/watch?v=") ?? job.youtube_url}
      </div>
      <div style={{ fontSize: 11, color: "#334155" }}>
        {timeAgo(job.created_at)}
        {job.clips?.length > 0 && ` · ${job.clips.length} clips`}
      </div>
    </div>
  );
}

function JobDetail({ job }) {
  if (!job) return (
    <div style={{ flex: 1, display: "flex", alignItems: "center", justifyContent: "center", color: "#1e293b" }}>
      <div style={{ textAlign: "center" }}>
        <div style={{ fontSize: 48, marginBottom: 12, opacity: 0.4 }}>⚡</div>
        <div style={{ fontSize: 14, color: "#334155" }}>Select a job to inspect</div>
      </div>
    </div>
  );

  const clips = job.clips ?? [];
  const captions = job.captions ?? [];

  return (
    <div style={{ flex: 1, overflowY: "auto", padding: "24px 28px" }}>
      <div style={{ marginBottom: 24 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 8 }}>
          <StatusBadge status={job.status} />
          <span style={{ fontSize: 11, color: "#475569", fontFamily: "monospace" }}>
            {job.id}
          </span>
        </div>
        <div style={{ fontSize: 13, color: "#60a5fa", marginBottom: 4, wordBreak: "break-all" }}>
          {job.youtube_url}
        </div>
        <div style={{ fontSize: 12, color: "#334155" }}>
          Created {timeAgo(job.created_at)} · Updated {timeAgo(job.updated_at)}
        </div>
      </div>

      {job.error && (
        <div style={{
          background: "rgba(239,68,68,0.08)", border: "1px solid rgba(239,68,68,0.2)",
          borderRadius: 8, padding: "12px 16px", marginBottom: 20,
          fontSize: 12, color: "#f87171", fontFamily: "monospace", lineHeight: 1.6,
        }}>
          ⚠ {job.error}
        </div>
      )}

      {job.status === "processing" && (
        <div style={{
          background: "rgba(245,158,11,0.07)", border: "1px solid rgba(245,158,11,0.2)",
          borderRadius: 8, padding: "14px 16px", marginBottom: 20,
          display: "flex", alignItems: "center", gap: 12,
        }}>
          <div style={{ width: 16, height: 16, borderRadius: "50%", border: "2px solid #f59e0b",
            borderTopColor: "transparent", animation: "spin 0.8s linear infinite", flexShrink: 0 }} />
          <div>
            <div style={{ fontSize: 13, color: "#fbbf24", fontWeight: 600, marginBottom: 2 }}>Pipeline running…</div>
            <div style={{ fontSize: 12, color: "#78350f" }}>ScoutAgent → ClipAgent → CaptionAgent → FFmpeg</div>
          </div>
        </div>
      )}

      {job.status === "queued" && (
        <div style={{
          background: "rgba(100,116,139,0.07)", border: "1px solid rgba(100,116,139,0.2)",
          borderRadius: 8, padding: "14px 16px", marginBottom: 20,
          fontSize: 13, color: "#64748b",
        }}>
          ⏳ Waiting for worker to pick up this job…
        </div>
      )}

      {job.transcript && (
        <details style={{ marginBottom: 20 }}>
          <summary style={{ cursor: "pointer", fontSize: 11, textTransform: "uppercase", letterSpacing: "0.1em", color: "#334155", fontWeight: 700, marginBottom: 8 }}>Transcript</summary>
          <pre style={{ fontSize: 11, color: "#64748b", lineHeight: 1.6, whiteSpace: "pre-wrap", maxHeight: 120, overflow: "auto", background: "rgba(255,255,255,0.02)", padding: 12, borderRadius: 8 }}>
            {job.transcript.slice(0, 500)}{job.transcript.length > 500 ? "…" : ""}
          </pre>
        </details>
      )}

      {clips.length > 0 && (
        <div>
          <div style={{ fontSize: 11, textTransform: "uppercase", letterSpacing: "0.1em",
            color: "#334155", fontWeight: 700, marginBottom: 12 }}>
            {clips.length} Clips Generated
          </div>
          {clips.map((clip, i) => (
            <ClipCard key={i} clip={clip} index={i} caption={captions[i]} />
          ))}
        </div>
      )}
    </div>
  );
}

export default function App() {
  const [jobs, setJobs] = useState([]);
  const [selected, setSelected] = useState(null);
  const [url, setUrl] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchJobs = useCallback(async () => {
    try {
      const data = await getJobs();
      setJobs(data);
      setError(null);
      if (!selected && data.length > 0) setSelected(data[0].id);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, [selected]);

  useEffect(() => {
    fetchJobs();
    const interval = setInterval(fetchJobs, POLL_MS);
    return () => clearInterval(interval);
  }, [fetchJobs]);

  function handleSubmit(e) {
    e.preventDefault();
    if (!url.trim()) return;
    setSubmitting(true);
    setError(null);
    const urlToUse = url.trim();
    createJob(urlToUse)
      .then(({ id }) => {
        setUrl("");
        setSelected(id);
        return fetchJobs();
      })
      .catch((e) => setError(e.message))
      .finally(() => setSubmitting(false));
  }

  useEffect(() => {
    if (jobs.length > 0 && !selected) setSelected(jobs[0].id);
  }, [jobs, selected]);

  const selectedJob = jobs.find((j) => j.id === selected) ?? (jobs[0] ?? null);

  const counts = jobs.reduce((a, j) => ({ ...a, [j.status]: (a[j.status] || 0) + 1 }), {});

  return (
    <div style={{ fontFamily: "'DM Mono', 'Fira Code', 'Consolas', monospace", minHeight: "100vh",
      background: "#050810", color: "#e2e8f0", display: "flex", flexDirection: "column" }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@300;400;500&family=Syne:wght@600;700;800&display=swap');
        * { box-sizing: border-box; margin: 0; padding: 0; }
        ::-webkit-scrollbar { width: 4px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.08); border-radius: 2px; }
        @keyframes throb { 0%,100% { opacity:1; transform:scale(1); } 50% { opacity:0.4; transform:scale(0.7); } }
        @keyframes spin { to { transform: rotate(360deg); } }
        @keyframes fadeSlideIn { from { opacity:0; transform:translateY(6px); } to { opacity:1; transform:translateY(0); } }
        .job-row:hover { background: rgba(255,255,255,0.03) !important; }
        .url-input:focus { border-color: rgba(99,102,241,0.6) !important; outline: none; box-shadow: 0 0 0 3px rgba(99,102,241,0.1); }
        .submit-btn:hover:not(:disabled) { background: rgba(99,102,241,0.9) !important; }
      `}</style>

      <header style={{
        padding: "0 28px", height: 56, display: "flex", alignItems: "center",
        justifyContent: "space-between", borderBottom: "1px solid rgba(255,255,255,0.06)",
        background: "rgba(5,8,16,0.8)", backdropFilter: "blur(12px)",
        position: "sticky", top: 0, zIndex: 100,
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <span style={{ fontSize: 18 }}>⚡</span>
          <span style={{ fontFamily: "'Syne', sans-serif", fontSize: 16, fontWeight: 800,
            letterSpacing: "-0.02em", color: "#e2e8f0" }}>
            ClipForge<span style={{ color: "#6366f1" }}>AI</span>
          </span>
          <span style={{ fontSize: 10, color: "#1e293b", background: "rgba(255,255,255,0.04)",
            border: "1px solid rgba(255,255,255,0.07)", padding: "2px 7px", borderRadius: 4,
            fontWeight: 500, letterSpacing: "0.05em" }}>LIVE</span>
        </div>
        <div style={{ display: "flex", gap: 16, alignItems: "center" }}>
          {[["queued","#64748b"],["processing","#f59e0b"],["completed","#10b981"],["failed","#ef4444"]].map(([s, c]) => (
            <span key={s} style={{ fontSize: 11, color: c, display: "flex", alignItems: "center", gap: 5 }}>
              <span style={{ fontSize: 14, fontWeight: 700 }}>{counts[s] || 0}</span>
              <span style={{ color: "#334155" }}>{s}</span>
            </span>
          ))}
          <span style={{ width: 1, height: 16, background: "rgba(255,255,255,0.07)" }} />
          <span style={{ display: "flex", alignItems: "center", gap: 5, fontSize: 11 }}>
            <span style={{ width: 6, height: 6, borderRadius: "50%", background: "#10b981",
              animation: "throb 2s ease-in-out infinite" }} />
            <span style={{ color: "#334155" }}>live</span>
          </span>
        </div>
      </header>

      <div style={{
        padding: "16px 28px", borderBottom: "1px solid rgba(255,255,255,0.05)",
        background: "rgba(255,255,255,0.015)",
      }}>
        <form onSubmit={handleSubmit} style={{ display: "flex", gap: 10, maxWidth: 800 }}>
          <input
            className="url-input"
            type="text"
            placeholder="https://www.youtube.com/watch?v=..."
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            disabled={submitting}
            style={{
              flex: 1, background: "rgba(255,255,255,0.03)",
              border: "1px solid rgba(255,255,255,0.08)", borderRadius: 8,
              padding: "9px 14px", color: "#e2e8f0", fontSize: 13,
              fontFamily: "inherit", transition: "all 0.2s",
            }}
          />
          <button
            className="submit-btn"
            type="submit"
            disabled={submitting || !url.trim()}
            style={{
              background: submitting ? "rgba(99,102,241,0.4)" : "rgba(99,102,241,0.75)",
              border: "1px solid rgba(99,102,241,0.4)", borderRadius: 8,
              color: "white", padding: "9px 20px", fontSize: 13, fontWeight: 600,
              cursor: submitting ? "not-allowed" : "pointer", fontFamily: "inherit",
              letterSpacing: "0.02em", transition: "all 0.15s", whiteSpace: "nowrap",
            }}
          >
            {submitting ? "Queuing…" : "▶ Process"}
          </button>
        </form>
        {error && (
          <div style={{ fontSize: 12, color: "#f87171", marginTop: 8 }}>{error}</div>
        )}
        <div style={{ fontSize: 11, color: "#1e293b", marginTop: 6 }}>
          Jobs poll every {POLL_MS / 1000}s · Worker runs ScoutAgent → ClipAgent → CaptionAgent
        </div>
      </div>

      <div style={{ display: "flex", flex: 1, overflow: "hidden", minHeight: 0, height: "calc(100vh - 130px)" }}>
        <div style={{
          width: 300, flexShrink: 0, borderRight: "1px solid rgba(255,255,255,0.06)",
          overflowY: "auto", background: "rgba(255,255,255,0.01)",
        }}>
          <div style={{ padding: "12px 18px 8px", fontSize: 10, textTransform: "uppercase",
            letterSpacing: "0.12em", color: "#1e293b", fontWeight: 700 }}>
            Jobs ({jobs.length})
          </div>
          {loading ? (
            <div style={{ padding: 24, fontSize: 12, color: "#64748b" }}>Loading jobs…</div>
          ) : (
            jobs.map((job) => (
              <div key={job.id} className="job-row" onClick={() => setSelected(job.id)}
                style={{ animation: "fadeSlideIn 0.2s ease" }}>
                <JobRow job={job} isSelected={selected === job.id} onClick={() => setSelected(job.id)} />
              </div>
            ))
          )}
        </div>
        <JobDetail job={selectedJob} />
      </div>
    </div>
  );
}
