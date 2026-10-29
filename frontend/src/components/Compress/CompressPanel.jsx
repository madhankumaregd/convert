/**
 * CompressPanel.jsx — Quality slider with presets for compression mode.
 *
 * Provides a range slider, preset buttons (Low / Medium / High / Maximum),
 * and a description explaining how quality affects output.
 */

import { Gauge } from "lucide-react";

const PRESETS = [
  { label: "Low", value: 60, desc: "Smallest file" },
  { label: "Medium", value: 75, desc: "Balanced" },
  { label: "High", value: 85, desc: "Recommended" },
  { label: "Maximum", value: 95, desc: "Best quality" },
];

/**
 * Returns a Tailwind color class based on the current quality value.
 */
function qualityColor(q) {
  if (q <= 50) return "text-rose-500";
  if (q <= 70) return "text-amber-500";
  if (q <= 85) return "text-emerald-500";
  return "text-cyan-500";
}

function trackGradient(q) {
  // Percentage position for the filled portion
  return `linear-gradient(to right, #6366f1 0%, #8b5cf6 ${q}%, #334155 ${q}%)`;
}

export default function CompressPanel({ quality, onQualityChange }) {
  return (
    <div className="space-y-5">
      {/* Header */}
      <div className="flex items-center gap-2">
        <Gauge size={18} className="text-indigo-400" />
        <p className="text-sm font-medium text-slate-600 dark:text-slate-400">
          Compression Quality
        </p>
      </div>

      {/* Current value display */}
      <div className="text-center">
        <span className={`text-4xl font-bold ${qualityColor(quality)} transition-colors duration-300`}>
          {quality}
        </span>
        <span className="text-lg text-slate-500 dark:text-slate-400 ml-1">%</span>
      </div>

      {/* Slider */}
      <div className="px-1">
        <input
          type="range"
          min={1}
          max={100}
          value={quality}
          onChange={(e) => onQualityChange(Number(e.target.value))}
          aria-label="Compression quality"
          className="w-full h-2 rounded-full appearance-none cursor-pointer
                     bg-slate-200 dark:bg-white/10
                     accent-indigo-500
                     [&::-webkit-slider-thumb]:appearance-none
                     [&::-webkit-slider-thumb]:w-5
                     [&::-webkit-slider-thumb]:h-5
                     [&::-webkit-slider-thumb]:rounded-full
                     [&::-webkit-slider-thumb]:bg-indigo-500
                     [&::-webkit-slider-thumb]:shadow-lg
                     [&::-webkit-slider-thumb]:shadow-indigo-500/30
                     [&::-webkit-slider-thumb]:border-2
                     [&::-webkit-slider-thumb]:border-white
                     [&::-webkit-slider-thumb]:dark:border-slate-800
                     [&::-webkit-slider-thumb]:transition-transform
                     [&::-webkit-slider-thumb]:duration-150
                     [&::-webkit-slider-thumb]:hover:scale-125"
          style={{ background: trackGradient(quality) }}
        />
        <div className="flex justify-between text-[10px] text-slate-500 dark:text-slate-500 mt-1">
          <span>1 — Smallest</span>
          <span>100 — Best quality</span>
        </div>
      </div>

      {/* Preset buttons */}
      <div className="grid grid-cols-4 gap-2">
        {PRESETS.map((p) => (
          <button
            key={p.label}
            onClick={() => onQualityChange(p.value)}
            className={`
              py-2 px-2 rounded-xl text-center border transition-all duration-200 cursor-pointer
              ${
                quality === p.value
                  ? "bg-indigo-500/15 border-indigo-500/40 text-indigo-500 dark:text-indigo-400"
                  : "bg-white/50 dark:bg-white/5 border-slate-200 dark:border-white/10 text-slate-600 dark:text-slate-400 hover:border-indigo-500/30"
              }
            `}
          >
            <span className="block text-sm font-semibold">{p.label}</span>
            <span className="block text-[10px] opacity-70 mt-0.5">{p.desc}</span>
          </button>
        ))}
      </div>

      {/* Description */}
      <p className="text-xs text-slate-500 dark:text-slate-500 text-center">
        Lower quality = smaller file size. Higher quality = better fidelity.
      </p>
    </div>
  );
}
