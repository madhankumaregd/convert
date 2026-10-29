/**
 * ResultCard.jsx — Card displaying a converted or compressed file result.
 *
 * Shows file details, size reduction comparison, and individual download CTA.
 */

import { Download, ArrowRight, CheckCircle2, FileCheck } from "lucide-react";
import { formatFileSize } from "../../utils/formatMap";

export default function ResultCard({ result, onDownload }) {
  const { id, name, originalSize, newSize, savings } = result;

  // Calculate savings percentage if not already present
  const calculatedSavings =
    savings !== undefined
      ? savings
      : originalSize > 0 && newSize < originalSize
      ? Math.round(((originalSize - newSize) / originalSize) * 100)
      : 0;

  return (
    <div
      className="p-4 rounded-2xl bg-white/70 dark:bg-white/5 backdrop-blur-md
                 border border-slate-200/80 dark:border-white/10
                 hover:border-indigo-400/50 dark:hover:border-indigo-500/30
                 transition-all duration-300 shadow-sm hover:shadow-md
                 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4"
    >
      {/* File Info */}
      <div className="flex items-center gap-3 min-w-0">
        <div className="p-3 rounded-xl bg-emerald-500/10 text-emerald-500 dark:bg-emerald-500/20 dark:text-emerald-400 shrink-0">
          <FileCheck size={22} />
        </div>
        <div className="min-w-0">
          <h4 className="text-sm font-semibold text-slate-800 dark:text-slate-200 truncate max-w-xs sm:max-w-md">
            {name}
          </h4>
          <div className="flex items-center gap-2 mt-1 text-xs text-slate-500 dark:text-slate-400">
            <span>{formatFileSize(originalSize)}</span>
            <ArrowRight size={12} className="text-slate-400" />
            <span className="font-medium text-slate-700 dark:text-slate-300">
              {formatFileSize(newSize)}
            </span>
            {calculatedSavings > 0 && (
              <span className="ml-1.5 px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-500/15 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20">
                -{calculatedSavings}%
              </span>
            )}
          </div>
        </div>
      </div>

      {/* Action Button */}
      <button
        onClick={() => onDownload(id)}
        className="w-full sm:w-auto px-4 py-2 rounded-xl text-xs font-semibold
                   bg-indigo-600 hover:bg-indigo-500 text-white
                   shadow-sm hover:shadow-indigo-500/20
                   transition-all duration-200 flex items-center justify-center gap-2
                   cursor-pointer shrink-0"
      >
        <Download size={14} />
        Download
      </button>
    </div>
  );
}

