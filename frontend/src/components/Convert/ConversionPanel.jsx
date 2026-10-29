/**
 * ConversionPanel.jsx — Mode toggle (Convert / Compress) + action button.
 *
 * Renders the FormatSelector in Convert mode and the CompressPanel in
 * Compress mode, along with the "Start" CTA.
 */

import { useState } from "react";
import { ArrowRightLeft, Minimize2, Sparkles } from "lucide-react";
import FormatSelector from "./FormatSelector";
import CompressPanel from "../Compress/CompressPanel";
import { formatFileSize } from "../../utils/formatMap";

export default function ConversionPanel({
  files,
  mode,
  onModeChange,
  selectedFormat,
  onFormatSelect,
  quality,
  onQualityChange,
  onStartConvert,
  onStartCompress,
  isProcessing,
}) {
  // Estimate processing time (very rough: ~1s per MB)
  const totalBytes = files.reduce((sum, f) => sum + f.size, 0);
  const estSeconds = Math.max(1, Math.ceil(totalBytes / (1024 * 1024)));

  const canStart =
    mode === "convert"
      ? files.length > 0 && selectedFormat
      : files.length > 0;

  return (
    <div className="w-full space-y-6">
      {/* ---- Mode toggle ---- */}
      <div className="flex items-center justify-center">
        <div className="flex bg-slate-100 dark:bg-white/5 rounded-xl p-1 border border-slate-200 dark:border-white/10">
          <button
            onClick={() => onModeChange("convert")}
            className={`flex items-center gap-2 px-5 py-2.5 rounded-lg text-sm font-semibold transition-all duration-200 cursor-pointer
              ${
                mode === "convert"
                  ? "bg-white dark:bg-white/10 text-indigo-600 dark:text-indigo-400 shadow-sm"
                  : "text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-300"
              }`}
          >
            <ArrowRightLeft size={16} />
            Convert
          </button>

          <button
            onClick={() => onModeChange("compress")}
            className={`flex items-center gap-2 px-5 py-2.5 rounded-lg text-sm font-semibold transition-all duration-200 cursor-pointer
              ${
                mode === "compress"
                  ? "bg-white dark:bg-white/10 text-indigo-600 dark:text-indigo-400 shadow-sm"
                  : "text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-300"
              }`}
          >
            <Minimize2 size={16} />
            Compress
          </button>
        </div>
      </div>

      {/* ---- Mode-specific content ---- */}
      <div className="p-5 rounded-2xl bg-white/60 dark:bg-white/5 backdrop-blur-sm border border-slate-200/60 dark:border-white/10">
        {mode === "convert" ? (
          <FormatSelector
            files={files}
            selectedFormat={selectedFormat}
            onFormatSelect={onFormatSelect}
          />
        ) : (
          <CompressPanel quality={quality} onQualityChange={onQualityChange} />
        )}
      </div>

      {/* ---- Estimated time ---- */}
      <p className="text-xs text-center text-slate-500 dark:text-slate-500">
        {files.length} file{files.length !== 1 ? "s" : ""} · {formatFileSize(totalBytes)} total
        {" · "}
        ~{estSeconds}s estimated
      </p>

      {/* ---- Start button ---- */}
      <button
        disabled={!canStart || isProcessing}
        onClick={() => (mode === "convert" ? onStartConvert() : onStartCompress())}
        className={`
          w-full py-4 rounded-2xl text-base font-bold
          flex items-center justify-center gap-2
          transition-all duration-300
          ${
            canStart && !isProcessing
              ? "bg-gradient-to-r from-indigo-500 via-violet-500 to-indigo-600 text-white shadow-xl shadow-indigo-500/25 hover:shadow-indigo-500/40 hover:scale-[1.02] active:scale-[0.98] cursor-pointer"
              : "bg-slate-200 dark:bg-white/10 text-slate-400 dark:text-slate-600 cursor-not-allowed"
          }
        `}
      >
        {isProcessing ? (
          <>
            <Sparkles size={20} className="animate-spin" />
            Processing…
          </>
        ) : mode === "convert" ? (
          <>
            <ArrowRightLeft size={20} />
            Start Conversion
          </>
        ) : (
          <>
            <Minimize2 size={20} />
            Start Compression
          </>
        )}
      </button>
    </div>
  );
}
