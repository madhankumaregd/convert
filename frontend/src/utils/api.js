/**
 * api.js — Axios-based HTTP client for the Convert backend.
 *
 * All network calls go through the shared `client` instance so the base URL
 * and any future interceptors are configured in one place.
 */

import axios from "axios";

/** Shared Axios instance pointing at the FastAPI backend. */
const client = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "https://convert-ten-rho.vercel.app/api",
});

/* ------------------------------------------------------------------ */
/*  Public API helpers                                                 */
/* ------------------------------------------------------------------ */

/**
 * Fetch the list of supported formats from the server.
 * GET /api/formats
 */
export async function fetchFormats() {
  const { data } = await client.get("/formats");
  return data;
}

/**
 * Convert a single file to `targetFormat`.
 * POST /api/convert  (multipart/form-data)
 *
 * @param {File}     file          – the source file
 * @param {string}   targetFormat  – desired output extension (e.g. "png")
 * @param {Function} onProgress    – optional progress callback (0-100)
 * @returns {Promise<{blob: Blob, filename: string}>}
 */
export async function convertFile(file, targetFormat, onProgress) {
  const form = new FormData();
  form.append("file", file);
  form.append("target_format", targetFormat);

  const response = await client.post("/convert", form, {
    responseType: "blob",
    onUploadProgress: (e) => {
      if (onProgress && e.total) {
        onProgress(Math.round((e.loaded / e.total) * 100));
      }
    },
  });

  // Try to pull the filename from the Content-Disposition header
  const disposition = response.headers["content-disposition"] || "";
  const filenameMatch = disposition.match(/filename="?([^";\n]+)"?/);
  const filename = filenameMatch
    ? filenameMatch[1]
    : `converted.${targetFormat}`;

  return { blob: response.data, filename };
}

/**
 * Compress a single file at the given quality level.
 * POST /api/compress  (multipart/form-data)
 *
 * The backend returns the compressed file as a blob and provides
 * size metadata via custom response headers.
 *
 * @param {File}     file       – the source file
 * @param {number}   quality    – compression quality 1-100
 * @param {Function} onProgress – optional progress callback (0-100)
 * @returns {Promise<{blob: Blob, filename: string, originalSize: number, compressedSize: number, savingsPercent: number}>}
 */
export async function compressFile(file, quality, onProgress) {
  const form = new FormData();
  form.append("file", file);
  form.append("quality", String(quality));

  const response = await client.post("/compress", form, {
    responseType: "blob",
    onUploadProgress: (e) => {
      if (onProgress && e.total) {
        onProgress(Math.round((e.loaded / e.total) * 100));
      }
    },
  });

  const originalSize = Number(response.headers["x-original-size"]) || file.size;
  const compressedSize =
    Number(response.headers["x-compressed-size"]) || response.data.size;
  const savingsPercent =
    Number(response.headers["x-savings-percent"]) ||
    Math.round((1 - compressedSize / originalSize) * 100);

  const disposition = response.headers["content-disposition"] || "";
  const filenameMatch = disposition.match(/filename="?([^";\n]+)"?/);
  const filename = filenameMatch ? filenameMatch[1] : file.name;

  return { blob: response.data, filename, originalSize, compressedSize, savingsPercent };
}

/**
 * Convert multiple files in a batch.
 * POST /api/convert/batch  (multipart/form-data)
 *
 * @param {File[]}   files        – array of source files
 * @param {string}   targetFormat – desired output extension
 * @param {Function} onProgress   – optional upload progress callback
 * @returns {Promise<{blob: Blob, filename: string}>}  (usually a zip)
 */
export async function convertBatch(files, targetFormat, onProgress) {
  const form = new FormData();
  files.forEach((f) => form.append("files", f));
  form.append("target_format", targetFormat);

  const response = await client.post("/convert/batch", form, {
    responseType: "blob",
    onUploadProgress: (e) => {
      if (onProgress && e.total) {
        onProgress(Math.round((e.loaded / e.total) * 100));
      }
    },
  });

  const disposition = response.headers["content-disposition"] || "";
  const filenameMatch = disposition.match(/filename="?([^";\n]+)"?/);
  const filename = filenameMatch ? filenameMatch[1] : `converted.zip`;

  return { blob: response.data, filename };
}

/**
 * Compress multiple files in a batch.
 * POST /api/compress/batch  (multipart/form-data)
 *
 * @param {File[]}   files      – array of source files
 * @param {number}   quality    – compression quality 1-100
 * @param {Function} onProgress – optional upload progress callback
 * @returns {Promise<{blob: Blob, filename: string}>}  (usually a zip)
 */
export async function compressBatch(files, quality, onProgress) {
  const form = new FormData();
  files.forEach((f) => form.append("files", f));
  form.append("quality", String(quality));

  const response = await client.post("/compress/batch", form, {
    responseType: "blob",
    onUploadProgress: (e) => {
      if (onProgress && e.total) {
        onProgress(Math.round((e.loaded / e.total) * 100));
      }
    },
  });

  const disposition = response.headers["content-disposition"] || "";
  const filenameMatch = disposition.match(/filename="?([^";\n]+)"?/);
  const filename = filenameMatch ? filenameMatch[1] : `compressed.zip`;

  return { blob: response.data, filename };
}

export default client;
