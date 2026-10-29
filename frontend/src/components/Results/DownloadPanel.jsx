/**
 * DownloadPanel.jsx — Renders completed conversion/compression results.
 *
 * Displays individual ResultCards, summary statistics, and batch download actions.
 */

import { DownloadCloud, Trash2, CheckCircle2, Sparkles } from "lucide-react";
import ResultCard from "./ResultCard";
import { formatFileSize } from "../../utils/formatMap";

export default function DownloadPanel({
  results,
  onDownload,
  onDownloadAll,
  onClear,
}) {
  if (!results.length) return null;

  // Aggregate stats
  const totalOriginal = results.reduce((sum, r) => sum + (r.originalSize || 0), 0);
  const totalNew = results.reduce((sum, r) => sum + (r.newSize || 0), 0);
  const totalSavings =
    totalOriginal > 0 && totalNew < totalOriginal
      ? Math.round(((totalOriginal - totalNew) / totalOriginal) * 100)
      : 0;

  return (
    <div className="w-full space-y-4 animate-in fade-in slide-in-from-bottom-4 duration-500">
      {/* Header bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-4 rounded-2xl bg-gradient-to-r from-emerald-500/10 via-indigo-500/10 to-violet-500/10 border border-emerald-500/20">
        <div className="flex items-center gap-2.5">
          <div className="p-2 rounded-xl bg-emerald-500/20 text-emerald-500 dark:text-emerald-400">
            <CheckCircle2 size={20} />
          </div>
          <div>
            <h3 className="text-base font-bold text-slate-800 dark:text-slate-100 flex items-center gap-2">
              Ready for Download ({results.length})
            </h3>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              {totalSavings > 0 ? (
                <span>
                  Saved {formatFileSize(totalOriginal - totalNew)} ({totalSavings}% reduction overall)
                </span>
              ) : (
                <span>Processed successfully</span>
              )}
            </p>
          </div>
        </div>

        {/* Global actions */}
        <div className="flex items-center gap-2">
          {results.length > 1 && (
            <button
              onClick={onDownloadAll}
              className="px-4 py-2 rounded-xl text-xs font-semibold
                         bg-gradient-to-r from-indigo-500 to-violet-600 hover:from-indigo-400 hover:to-violet-500
                         text-white shadow-md shadow-indigo-500/20
                         transition-all duration-200 flex items-center gap-1.5 cursor-pointer"
            >
              <DownloadCloud size={15} />
              Download All
            </button>
          )}

          <button
            onClick={onClear}
            className="p-2 rounded-xl text-slate-400 hover:text-rose-500 hover:bg-rose-500/10
                       transition-colors duration-200 cursor-pointer"
            title="Clear finished downloads"
          >
            <Trash2 size={16} />
          </button>
        </div>
      </div>

      {/* List of cards */}
      <div className="space-y-2.5">
        {results.map((result) => (
          <ResultCard
            key={result.id}
            result={result}
            onDownload={onDownload}
          />
        ))}
      </div>
    </div>
  );
}

