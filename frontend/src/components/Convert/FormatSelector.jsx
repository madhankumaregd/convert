/**
 * FormatSelector.jsx — Dynamic format picker grid.
 *
 * Computes the valid output formats based on the intersection of all
 * uploaded files' capabilities, groups them by category, and renders
 * color-coded "pills" the user can click.
 */

import { useMemo } from "react";
import { getValidTargets, getCategoryInfo } from "../../utils/formatMap";

/** Static color classes for each category color token. */
const PILL_COLORS = {
  emerald: {
    base: "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/20 hover:bg-emerald-500/20",
    active: "!bg-emerald-500 !text-white !border-emerald-400 ring-2 ring-emerald-400/50 shadow-lg shadow-emerald-500/25",
  },
  blue: {
    base: "bg-blue-500/10 text-blue-600 dark:text-blue-400 border-blue-500/20 hover:bg-blue-500/20",
    active: "!bg-blue-500 !text-white !border-blue-400 ring-2 ring-blue-400/50 shadow-lg shadow-blue-500/25",
  },
  violet: {
    base: "bg-violet-500/10 text-violet-600 dark:text-violet-400 border-violet-500/20 hover:bg-violet-500/20",
    active: "!bg-violet-500 !text-white !border-violet-400 ring-2 ring-violet-400/50 shadow-lg shadow-violet-500/25",
  },
  rose: {
    base: "bg-rose-500/10 text-rose-600 dark:text-rose-400 border-rose-500/20 hover:bg-rose-500/20",
    active: "!bg-rose-500 !text-white !border-rose-400 ring-2 ring-rose-400/50 shadow-lg shadow-rose-500/25",
  },
  amber: {
    base: "bg-amber-500/10 text-amber-600 dark:text-amber-400 border-amber-500/20 hover:bg-amber-500/20",
    active: "!bg-amber-500 !text-white !border-amber-400 ring-2 ring-amber-400/50 shadow-lg shadow-amber-500/25",
  },
};

const DEFAULT_PILL = {
  base: "bg-slate-500/10 text-slate-600 dark:text-slate-400 border-slate-500/20 hover:bg-slate-500/20",
  active: "!bg-indigo-500 !text-white !border-indigo-400 ring-2 ring-indigo-400/50 shadow-lg shadow-indigo-500/25",
};

export default function FormatSelector({ files, selectedFormat, onFormatSelect }) {
  /**
   * Compute the intersection of all files' valid targets.
   * If files share a category, we intersect their target lists.
   * Mixed categories → intersection (may be empty).
   */
  const { grouped, hasTargets } = useMemo(() => {
    if (!files.length) return { grouped: {}, hasTargets: false };

    // Get each file's target set
    const targetSets = files.map((f) => new Set(getValidTargets(f.extension)));

    // Intersect them: a format is valid only if every file can convert to it
    const intersection = [...targetSets[0]].filter((fmt) =>
      targetSets.every((s) => s.has(fmt))
    );

    if (!intersection.length) return { grouped: {}, hasTargets: false };

    // Group by category
    const groups = {};
    for (const fmt of intersection) {
      const info = getCategoryInfo(fmt);
      const catLabel = info ? info.label : "Other";
      const color = info ? info.color : "slate";
      if (!groups[catLabel]) groups[catLabel] = { color, formats: [] };
      groups[catLabel].formats.push(fmt);
    }

    return { grouped: groups, hasTargets: true };
  }, [files]);

  if (!files.length) return null;

  if (!hasTargets) {
    return (
      <div className="text-center py-6">
        <p className="text-sm text-slate-500 dark:text-slate-400">
          No common output format available for the selected files.
          <br />
          <span className="text-xs">
            Try uploading files of the same type.
          </span>
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4 transition-all duration-300">
      <p className="text-sm font-medium text-slate-600 dark:text-slate-400">
        Convert to:
      </p>

      {Object.entries(grouped).map(([catLabel, { color, formats }]) => (
        <div key={catLabel}>
          {/* Category sub-header */}
          <p className="text-xs font-semibold text-slate-500 dark:text-slate-500 uppercase tracking-wider mb-2">
            {catLabel}
          </p>

          {/* Format pills grid */}
          <div className="flex flex-wrap gap-2">
            {formats.map((fmt) => {
              const isSelected = selectedFormat === fmt;
              const pillColor = PILL_COLORS[color] || DEFAULT_PILL;

              return (
                <button
                  key={fmt}
                  onClick={() => onFormatSelect(fmt)}
                  className={`
                    px-4 py-2 text-sm font-semibold rounded-xl border
                    transition-all duration-200 cursor-pointer
                    ${pillColor.base}
                    ${isSelected ? pillColor.active : ""}
                  `}
                >
                  {fmt.toUpperCase()}
                </button>
              );
            })}
          </div>
        </div>
      ))}
    </div>
  );
}
