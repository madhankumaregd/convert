/**
 * useConversion.js — Custom hook for running conversions & compressions.
 *
 * Orchestrates backend calls, tracks per-file progress, collects results,
 * and offers helpers to download individual or all output files.
 */

import { useState, useCallback } from "react";
import { convertFile, compressFile } from "../utils/api";

/**
 * @param {import('./useFileUpload').UploadedFile[]} files
 * @param {Function} updateFileStatus
 */
export default function useConversion(files, updateFileStatus) {
  const [isProcessing, setIsProcessing] = useState(false);
  const [results, setResults] = useState([]);

  /* ---------------------------------------------------------------- */
  /*  Convert all files to a target format                             */
  /* ---------------------------------------------------------------- */
  const convertFiles = useCallback(
    async (targetFormat) => {
      setIsProcessing(true);
      const newResults = [];

      for (const entry of files) {
        try {
          // Mark uploading
          updateFileStatus(entry.id, { status: "uploading", progress: 0 });

          const { blob, filename } = await convertFile(
            entry.file,
            targetFormat,
            (progress) => {
              // First half of the bar = upload, second half = server processing
              updateFileStatus(entry.id, {
                status: progress < 100 ? "uploading" : "processing",
                progress: Math.min(progress, 95),
              });
            }
          );

          const url = URL.createObjectURL(blob);
          const result = {
            id: entry.id,
            name: filename,
            blob,
            url,
            originalSize: entry.size,
            newSize: blob.size,
          };

          newResults.push(result);
          updateFileStatus(entry.id, {
            status: "done",
            progress: 100,
            result,
          });
        } catch (err) {
          const message =
            err.response?.data?.message ||
            err.message ||
            "Conversion failed";
          updateFileStatus(entry.id, {
            status: "error",
            progress: 0,
            error: message,
          });
        }
      }

      setResults((prev) => [...prev, ...newResults]);
      setIsProcessing(false);
    },
    [files, updateFileStatus]
  );

  /* ---------------------------------------------------------------- */
  /*  Compress all files                                               */
  /* ---------------------------------------------------------------- */
  const compressFiles = useCallback(
    async (quality) => {
      setIsProcessing(true);
      const newResults = [];

      for (const entry of files) {
        try {
          updateFileStatus(entry.id, { status: "uploading", progress: 0 });

          const { blob, filename, originalSize, compressedSize, savingsPercent } =
            await compressFile(entry.file, quality, (progress) => {
              updateFileStatus(entry.id, {
                status: progress < 100 ? "uploading" : "processing",
                progress: Math.min(progress, 95),
              });
            });

          const url = URL.createObjectURL(blob);
          const result = {
            id: entry.id,
            name: filename,
            blob,
            url,
            originalSize,
            newSize: compressedSize,
            savings: savingsPercent,
          };

          newResults.push(result);
          updateFileStatus(entry.id, {
            status: "done",
            progress: 100,
            result,
          });
        } catch (err) {
          const message =
            err.response?.data?.message ||
            err.message ||
            "Compression failed";
          updateFileStatus(entry.id, {
            status: "error",
            progress: 0,
            error: message,
          });
        }
      }

      setResults((prev) => [...prev, ...newResults]);
      setIsProcessing(false);
    },
    [files, updateFileStatus]
  );

  /* ---------------------------------------------------------------- */
  /*  Download helpers                                                 */
  /* ---------------------------------------------------------------- */

  /** Trigger a browser download for a single result by id. */
  const downloadResult = useCallback(
    (id) => {
      const r = results.find((res) => res.id === id);
      if (!r) return;
      const a = document.createElement("a");
      a.href = r.url;
      a.download = r.name;
      document.body.appendChild(a);
      a.click();
      a.remove();
    },
    [results]
  );

  /** Download every result file one by one. */
  const downloadAll = useCallback(() => {
    results.forEach((r) => {
      const a = document.createElement("a");
      a.href = r.url;
      a.download = r.name;
      document.body.appendChild(a);
      a.click();
      a.remove();
    });
  }, [results]);

  /** Clear results and revoke object URLs to free memory. */
  const clearResults = useCallback(() => {
    results.forEach((r) => URL.revokeObjectURL(r.url));
    setResults([]);
  }, [results]);

  return {
    isProcessing,
    results,
    convertFiles,
    compressFiles,
    downloadResult,
    downloadAll,
    clearResults,
  };
}
