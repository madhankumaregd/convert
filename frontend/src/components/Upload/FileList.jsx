/**
 * FileList.jsx — Displays uploaded files as styled horizontal cards.
 *
 * Each card shows the file icon (color-coded by category), name, size,
 * a category badge, and a remove button.
 */

import {
  Image,
  FileText,
  Music,
  Video,
  Archive,
  File,
  X,
  Trash2,
} from "lucide-react";
import { formatFileSize } from "../../utils/formatMap";

/** Map category icon name → Lucide component */
const ICON_MAP = {
  Image,
  FileText,
  Music,
  Video,
  Archive,
};

/** Map category color name → Tailwind class sets */
const COLOR_MAP = {
  emerald: {
    bg: "bg-emerald-500/10 dark:bg-emerald-500/15",
    text: "text-emerald-600 dark:text-emerald-400",
    badge: "bg-emerald-500/15 text-emerald-600 dark:text-emerald-400 border-emerald-500/25",
  },
  blue: {
    bg: "bg-blue-500/10 dark:bg-blue-500/15",
    text: "text-blue-600 dark:text-blue-400",
    badge: "bg-blue-500/15 text-blue-600 dark:text-blue-400 border-blue-500/25",
  },
  violet: {
    bg: "bg-violet-500/10 dark:bg-violet-500/15",
    text: "text-violet-600 dark:text-violet-400",
    badge: "bg-violet-500/15 text-violet-600 dark:text-violet-400 border-violet-500/25",
  },
  rose: {
    bg: "bg-rose-500/10 dark:bg-rose-500/15",
    text: "text-rose-600 dark:text-rose-400",
    badge: "bg-rose-500/15 text-rose-600 dark:text-rose-400 border-rose-500/25",
  },
  amber: {
    bg: "bg-amber-500/10 dark:bg-amber-500/15",
    text: "text-amber-600 dark:text-amber-400",
    badge: "bg-amber-500/15 text-amber-600 dark:text-amber-400 border-amber-500/25",
  },
};

const DEFAULT_COLOR = {
  bg: "bg-slate-500/10",
  text: "text-slate-500",
  badge: "bg-slate-500/15 text-slate-500 border-slate-500/25",
};

export default function FileList({ files, onRemove, onClear }) {
  if (!files.length) return null;

  return (
    <div className="w-full space-y-3">
      {/* Header row */}
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-slate-700 dark:text-slate-300">
          Uploaded Files ({files.length})
        </h3>

        {files.length > 1 && (
          <button
            onClick={onClear}
            className="flex items-center gap-1.5 text-xs font-medium text-rose-500 hover:text-rose-400
                       transition-colors duration-200 cursor-pointer"
          >
            <Trash2 size={14} />
            Clear All
          </button>
        )}
      </div>

      {/* File cards */}
      <div className="grid gap-2">
        {files.map((f, idx) => {
          const colors = f.categoryInfo
            ? COLOR_MAP[f.categoryInfo.color] || DEFAULT_COLOR
            : DEFAULT_COLOR;
          const IconComponent = f.categoryInfo
            ? ICON_MAP[f.categoryInfo.icon] || File
            : File;

          return (
            <div
              key={f.id}
              style={{ animationDelay: `${idx * 50}ms` }}
              className="flex items-center gap-3 p-3 rounded-xl
                         bg-white/60 dark:bg-white/5 backdrop-blur-sm
                         border border-slate-200/60 dark:border-white/10
                         transition-all duration-300 hover:border-slate-300 dark:hover:border-white/20
                         animate-fade-in-up"
            >
              {/* Category icon */}
              <div className={`p-2 rounded-lg ${colors.bg}`}>
                <IconComponent size={18} className={colors.text} />
              </div>

              {/* File name & size */}
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-slate-700 dark:text-slate-200 truncate">
                  {f.name}
                </p>
                <p className="text-xs text-slate-500 dark:text-slate-400">
                  {formatFileSize(f.size)}
                </p>
              </div>

              {/* Category badge */}
              {f.categoryInfo && (
                <span
                  className={`hidden sm:inline-flex text-[11px] font-medium px-2 py-0.5 rounded-full border ${colors.badge}`}
                >
                  {f.extension?.toUpperCase()}
                </span>
              )}

              {/* Remove button */}
              <button
                onClick={() => onRemove(f.id)}
                aria-label={`Remove ${f.name}`}
                className="p-1.5 rounded-lg text-slate-400 hover:text-rose-500
                           hover:bg-rose-500/10 transition-all duration-200 cursor-pointer"
              >
                <X size={16} />
              </button>
            </div>
          );
        })}
      </div>
    </div>
  );
}
