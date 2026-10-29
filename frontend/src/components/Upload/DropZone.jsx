/**
 * DropZone.jsx — Hero drag-and-drop file upload area.
 *
 * Supports click-to-browse and drag-and-drop with animated visual feedback.
 * Multiple files are accepted at once.
 */

import { useRef, useState, useCallback } from "react";
import { UploadCloud } from "lucide-react";
import { FORMAT_CATEGORIES } from "../../utils/formatMap";

export default function DropZone({ onFilesAdded, disabled = false }) {
  const inputRef = useRef(null);
  const [dragActive, setDragActive] = useState(false);

  /* ---- drag event handlers ---- */
  const handleDrag = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
  }, []);

  const handleDragIn = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.dataTransfer?.items?.length > 0) setDragActive(true);
  }, []);

  const handleDragOut = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
  }, []);

  const handleDrop = useCallback(
    (e) => {
      e.preventDefault();
      e.stopPropagation();
      setDragActive(false);
      if (disabled) return;
      if (e.dataTransfer?.files?.length) {
        onFilesAdded(e.dataTransfer.files);
      }
    },
    [disabled, onFilesAdded]
  );

  const handleClick = () => {
    if (!disabled) inputRef.current?.click();
  };

  const handleChange = (e) => {
    if (e.target.files?.length) {
      onFilesAdded(e.target.files);
      e.target.value = ""; // allow re-selecting same file
    }
  };

  /* ---- Build format badges ---- */
  const badges = Object.values(FORMAT_CATEGORIES).map((cat) => ({
    label: cat.label,
    color: cat.color,
    count: cat.extensions.length,
  }));

  return (
    <div className="w-full">
      {/* Drop area */}
      <div
        onClick={handleClick}
        onDragEnter={handleDragIn}
        onDragOver={handleDrag}
        onDragLeave={handleDragOut}
        onDrop={handleDrop}
        role="button"
        tabIndex={0}
        onKeyDown={(e) => e.key === "Enter" && handleClick()}
        aria-label="Upload files by clicking or dragging"
        className={`
          relative group cursor-pointer
          w-full min-h-[220px] sm:min-h-[260px]
          flex flex-col items-center justify-center gap-4 p-8
          rounded-2xl border-2 border-dashed
          transition-all duration-300 ease-out
          ${disabled ? "opacity-50 cursor-not-allowed" : ""}
          ${
            dragActive
              ? "border-indigo-400 bg-indigo-500/10 scale-[1.02] shadow-xl shadow-indigo-500/10"
              : "border-slate-300 dark:border-slate-600 hover:border-indigo-400 dark:hover:border-indigo-500 bg-white/50 dark:bg-white/5 hover:bg-indigo-50/50 dark:hover:bg-indigo-500/5"
          }
          backdrop-blur-sm
        `}
      >
        {/* Pulsing ring on drag */}
        {dragActive && (
          <div className="absolute inset-0 rounded-2xl border-2 border-indigo-400 animate-pulse pointer-events-none" />
        )}

        {/* Icon */}
        <div
          className={`p-4 rounded-2xl transition-all duration-300
            ${
              dragActive
                ? "bg-indigo-500/20 text-indigo-400 scale-110"
                : "bg-slate-100 dark:bg-white/10 text-slate-400 dark:text-slate-500 group-hover:text-indigo-400 group-hover:bg-indigo-100 dark:group-hover:bg-indigo-500/10"
            }`}
        >
          <UploadCloud size={40} strokeWidth={1.5} />
        </div>

        {/* Text */}
        <div className="text-center">
          <p className="text-base sm:text-lg font-semibold text-slate-700 dark:text-slate-200">
            {dragActive ? "Drop your files here" : "Drag & drop files here"}
          </p>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
            or{" "}
            <span className="text-indigo-500 dark:text-indigo-400 font-medium underline underline-offset-2">
              click to browse
            </span>
          </p>
        </div>

        {/* Hidden file input */}
        <input
          ref={inputRef}
          type="file"
          multiple
          onChange={handleChange}
          className="hidden"
          aria-hidden="true"
        />
      </div>

      {/* Supported format badges */}
      <div className="flex flex-wrap justify-center gap-2 mt-4">
        {badges.map((b) => (
          <span
            key={b.label}
            className={`
              text-xs font-medium px-3 py-1 rounded-full
              bg-${b.color}-500/10 text-${b.color}-500
              dark:bg-${b.color}-500/15 dark:text-${b.color}-400
              border border-${b.color}-500/20
            `}
          >
            {b.label} ({b.count})
          </span>
        ))}
      </div>
    </div>
  );
}
