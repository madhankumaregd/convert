/**
 * useFileUpload.js — Custom hook for managing the uploaded-file list.
 *
 * Provides state and helpers to add, remove, update, and clear files
 * while auto-detecting category metadata on import.
 */

import { useState, useCallback } from "react";
import {
  getFileExtension,
  getCategory,
  getCategoryInfo,
} from "../utils/formatMap";

/**
 * @typedef {Object} UploadedFile
 * @property {string}  id           – unique identifier
 * @property {File}    file         – raw File object
 * @property {string}  name         – display name
 * @property {number}  size         – byte size
 * @property {string}  extension    – lowercase extension
 * @property {string|null}  category     – category key ("image", "audio", …)
 * @property {Object|null}  categoryInfo – { key, label, icon, color, … }
 * @property {'idle'|'uploading'|'processing'|'done'|'error'} status
 * @property {number}  progress     – 0-100
 * @property {any}     result       – conversion / compression result
 * @property {string|null}  error   – error message if failed
 */

export default function useFileUpload() {
  const [files, setFiles] = useState([]);

  /**
   * Add one or more files from a FileList or File[].
   * Each file is wrapped with metadata derived from formatMap.
   */
  const addFiles = useCallback((fileList) => {
    const incoming = Array.from(fileList).map((file) => {
      const extension = getFileExtension(file.name);
      return {
        id: crypto.randomUUID?.() ?? `${Date.now()}-${Math.random()}`,
        file,
        name: file.name,
        size: file.size,
        extension,
        category: getCategory(extension),
        categoryInfo: getCategoryInfo(extension),
        status: "idle",
        progress: 0,
        result: null,
        error: null,
      };
    });

    setFiles((prev) => [...prev, ...incoming]);
  }, []);

  /** Remove a single file by its id. */
  const removeFile = useCallback((id) => {
    setFiles((prev) => prev.filter((f) => f.id !== id));
  }, []);

  /** Remove every file from the list. */
  const clearFiles = useCallback(() => {
    setFiles([]);
  }, []);

  /**
   * Merge partial updates into the file entry matching `id`.
   * e.g. updateFileStatus(id, { status: "processing", progress: 42 })
   */
  const updateFileStatus = useCallback((id, updates) => {
    setFiles((prev) =>
      prev.map((f) => (f.id === id ? { ...f, ...updates } : f))
    );
  }, []);

  return { files, addFiles, removeFile, clearFiles, updateFileStatus };
}
