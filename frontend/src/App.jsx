/**
 * App.jsx — Main application orchestrator for Convert.
 *
 * Integrates drag-and-drop upload, dynamic format filtering, conversion/compression
 * execution, per-file progress tracking, and batch download management.
 */

import { useState } from "react";
import toast from "react-hot-toast";
import Header from "./components/Layout/Header";
import DropZone from "./components/Upload/DropZone";
import FileList from "./components/Upload/FileList";
import ConversionPanel from "./components/Convert/ConversionPanel";
import ProgressBar from "./components/Convert/ProgressBar";
import DownloadPanel from "./components/Results/DownloadPanel";
import AppToaster from "./components/ui/Toast";
import useFileUpload from "./hooks/useFileUpload";
import useConversion from "./hooks/useConversion";
import { Sparkles, ShieldCheck, Zap, RefreshCw } from "lucide-react";

export default function App() {
  const { files, addFiles, removeFile, clearFiles, updateFileStatus } =
    useFileUpload();

  const {
    isProcessing,
    results,
    convertFiles,
    compressFiles,
    downloadResult,
    downloadAll,
    clearResults,
  } = useConversion(files, updateFileStatus);

  const [mode, setMode] = useState("convert"); // "convert" | "compress"
  const [selectedFormat, setSelectedFormat] = useState("");
  const [quality, setQuality] = useState(85);

  /* Handle incoming files */
  const handleFilesAdded = (incomingFiles) => {
    addFiles(incomingFiles);
    // Reset selected format if previous was invalidated
    setSelectedFormat("");
    toast.success(
      `Added ${incomingFiles.length} file${incomingFiles.length > 1 ? "s" : ""}`
    );
  };

  /* Start conversion flow */
  const handleStartConvert = async () => {
    if (!selectedFormat) {
      toast.error("Please select a target format first.");
      return;
    }
    toast.loading("Converting files...", { id: "process-toast" });
    try {
      await convertFiles(selectedFormat);
      toast.success("Conversion completed!", { id: "process-toast" });
    } catch (err) {
      toast.error("Some files failed to convert.", { id: "process-toast" });
    }
  };

  /* Start compression flow */
  const handleStartCompress = async () => {
    toast.loading("Compressing files...", { id: "process-toast" });
    try {
      await compressFiles(quality);
      toast.success("Compression completed!", { id: "process-toast" });
    } catch (err) {
      toast.error("Some files failed to compress.", { id: "process-toast" });
    }
  };

  /* Active processing files list (files currently in-flight) */
  const processingFiles = files.filter(
    (f) => f.status === "uploading" || f.status === "processing"
  );

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-[#0b0f19] text-slate-900 dark:text-slate-100 relative overflow-x-hidden transition-colors duration-300">
      {/* Background Decorative Ambient Glows */}
      <div className="absolute top-0 left-1/4 w-96 h-96 bg-indigo-500/10 dark:bg-indigo-600/15 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute top-48 right-1/4 w-96 h-96 bg-violet-500/10 dark:bg-violet-600/15 rounded-full blur-3xl pointer-events-none" />

      {/* Navigation Header */}
      <Header />

      {/* Main Container */}
      <main className="max-w-4xl mx-auto px-4 sm:px-6 py-6 sm:py-10 space-y-8 relative z-10">
        {/* Hero Section */}
        <div className="text-center space-y-2">
          <h2 className="text-3xl sm:text-4xl font-extrabold tracking-tight bg-gradient-to-r from-slate-900 via-indigo-900 to-slate-800 dark:from-white dark:via-indigo-200 dark:to-slate-300 bg-clip-text text-transparent">
            Convert & Compress Anything Instantly
          </h2>
          <p className="text-sm sm:text-base text-slate-500 dark:text-slate-400 max-w-xl mx-auto">
            Universal file transformations across documents, images, audio, video,
            and archives. Fast, lossless, and secure right from your browser.
          </p>
        </div>

        {/* Upload Zone */}
        <section className="bg-white/80 dark:bg-white/5 backdrop-blur-xl border border-slate-200/80 dark:border-white/10 rounded-3xl p-4 sm:p-6 shadow-sm dark:shadow-2xl">
          <DropZone onFilesAdded={handleFilesAdded} disabled={isProcessing} />
        </section>

        {/* Uploaded File List */}
        {files.length > 0 && (
          <section className="bg-white/80 dark:bg-white/5 backdrop-blur-xl border border-slate-200/80 dark:border-white/10 rounded-3xl p-5 shadow-sm dark:shadow-2xl">
            <FileList
              files={files}
              onRemove={removeFile}
              onClear={clearFiles}
            />
          </section>
        )}

        {/* Conversion & Compression Controls */}
        {files.length > 0 && (
          <section className="bg-white/80 dark:bg-white/5 backdrop-blur-xl border border-slate-200/80 dark:border-white/10 rounded-3xl p-5 sm:p-6 shadow-sm dark:shadow-2xl">
            <ConversionPanel
              files={files}
              mode={mode}
              onModeChange={(newMode) => {
                setMode(newMode);
                setSelectedFormat("");
              }}
              selectedFormat={selectedFormat}
              onFormatSelect={setSelectedFormat}
              quality={quality}
              onQualityChange={setQuality}
              onStartConvert={handleStartConvert}
              onStartCompress={handleStartCompress}
              isProcessing={isProcessing}
            />
          </section>
        )}

        {/* Active Progress Bars */}
        {processingFiles.length > 0 && (
          <section className="bg-white/80 dark:bg-white/5 backdrop-blur-xl border border-slate-200/80 dark:border-white/10 rounded-3xl p-5 space-y-3 shadow-sm dark:shadow-2xl">
            <h4 className="text-xs font-bold uppercase tracking-wider text-indigo-500 dark:text-indigo-400 flex items-center gap-1.5">
              <RefreshCw size={14} className="animate-spin" />
              Processing Files
            </h4>
            {processingFiles.map((f) => (
              <ProgressBar
                key={f.id}
                progress={f.progress}
                status={f.status}
                filename={f.name}
              />
            ))}
          </section>
        )}

        {/* Download & Results Section */}
        {results.length > 0 && (
          <section className="bg-white/80 dark:bg-white/5 backdrop-blur-xl border border-slate-200/80 dark:border-white/10 rounded-3xl p-5 sm:p-6 shadow-sm dark:shadow-2xl">
            <DownloadPanel
              results={results}
              onDownload={downloadResult}
              onDownloadAll={downloadAll}
              onClear={clearResults}
            />
          </section>
        )}

        {/* Feature Highlights Grid (shown when idle) */}
        {files.length === 0 && results.length === 0 && (
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-4">
            <div className="p-4 rounded-2xl bg-white/50 dark:bg-white/5 border border-slate-200/60 dark:border-white/5 text-center space-y-2">
              <div className="w-10 h-10 mx-auto rounded-xl bg-indigo-500/10 text-indigo-500 flex items-center justify-center">
                <Zap size={20} />
              </div>
              <h4 className="text-sm font-semibold text-slate-800 dark:text-slate-200">
                Ultra-Fast Processing
              </h4>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                Optimized Python backend with non-blocking async executor streams.
              </p>
            </div>

            <div className="p-4 rounded-2xl bg-white/50 dark:bg-white/5 border border-slate-200/60 dark:border-white/5 text-center space-y-2">
              <div className="w-10 h-10 mx-auto rounded-xl bg-emerald-500/10 text-emerald-500 flex items-center justify-center">
                <Sparkles size={20} />
              </div>
              <h4 className="text-sm font-semibold text-slate-800 dark:text-slate-200">
                Dynamic Smart Filtering
              </h4>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                Only compatible output formats appear based on uploaded input files.
              </p>
            </div>

            <div className="p-4 rounded-2xl bg-white/50 dark:bg-white/5 border border-slate-200/60 dark:border-white/5 text-center space-y-2">
              <div className="w-10 h-10 mx-auto rounded-xl bg-violet-500/10 text-violet-500 flex items-center justify-center">
                <ShieldCheck size={20} />
              </div>
              <h4 className="text-sm font-semibold text-slate-800 dark:text-slate-200">
                Private & Secure
              </h4>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                Auto-cleaning temporary storage ensures your files are never retained.
              </p>
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="py-8 text-center text-xs text-slate-400 dark:text-slate-500 border-t border-slate-200/50 dark:border-white/5">
        <p>Convert — All-in-one Universal File Transformer & Compressor</p>
      </footer>

      {/* Toast Notification Container */}
      <AppToaster />
    </div>
  );
}
