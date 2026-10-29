/**
 * ProgressBar.jsx — Animated progress indicator for a single file.
 *
 * Shows a gradient progress bar, percentage, filename, and status text
 * with a subtle pulse while processing.
 */

import { CheckCircle2, AlertCircle, Loader2 } from "lucide-react";

const STATUS_CONFIG = {
  idle: { label: "Waiting…", color: "text-slate-400" },
  uploading: { label: "Uploading…", color: "text-indigo-400" },
  processing: { label: "Processing…", color: "text-violet-400" },
  done: { label: "Done!", color: "text-emerald-400" },
  error: { label: "Error", color: "text-rose-400" },
};

export default function ProgressBar({ progress = 0, status = "idle", filename = "" }) {
  const cfg = STATUS_CONFIG[status] || STATUS_CONFIG.idle;
  const isActive = status === "uploading" || status === "processing";

  return (
    <div className="w-full space-y-1.5">
      {/* Top row: filename + percentage */}
      <div className="flex items-center justify-between text-xs">
        <span className="text-slate-600 dark:text-slate-300 truncate max-w-[70%] font-medium">
          {filename}
        </span>
        <span className={`font-semibold ${cfg.color}`}>
          {status === "done" && <CheckCircle2 size={14} className="inline mr-1" />}
          {status === "error" && <AlertCircle size={14} className="inline mr-1" />}
          {isActive && <Loader2 size={14} className="inline mr-1 animate-spin" />}
          {status === "done" ? "100%" : status === "error" ? "Failed" : `${progress}%`}
        </span>
      </div>

      {/* Bar track */}
      <div className="w-full h-2 rounded-full bg-slate-200 dark:bg-white/10 overflow-hidden">
        <div
          className={`h-full rounded-full transition-all duration-500 ease-out
            ${status === "error"
              ? "bg-gradient-to-r from-rose-500 to-rose-600"
              : status === "done"
              ? "bg-gradient-to-r from-emerald-500 to-emerald-400"
              : "bg-gradient-to-r from-indigo-500 via-violet-500 to-cyan-500"}
            ${isActive ? "animate-pulse" : ""}
          `}
          style={{ width: `${Math.max(progress, status === "error" ? 100 : 0)}%` }}
        />
      </div>

      {/* Status label */}
      <p className={`text-[11px] ${cfg.color}`}>{cfg.label}</p>
    </div>
  );
}
