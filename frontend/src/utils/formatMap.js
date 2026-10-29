/**
 * formatMap.js — Central format registry for the Convert app.
 *
 * Every supported file type, its category, valid conversion targets, and
 * helper utilities live here so every other module stays in sync.
 */

export const FORMAT_CATEGORIES = {
  image: {
    label: "Images",
    icon: "Image",
    color: "emerald",
    extensions: ["jpg", "jpeg", "png", "webp", "bmp", "tiff", "tif", "gif", "ico", "svg"],
    targets: {
      jpg:  ["png", "webp", "bmp", "tiff", "gif", "ico", "pdf"],
      jpeg: ["png", "webp", "bmp", "tiff", "gif", "ico", "pdf"],
      png:  ["jpg", "webp", "bmp", "tiff", "gif", "ico", "pdf"],
      webp: ["jpg", "png", "bmp", "tiff", "gif", "ico", "pdf"],
      bmp:  ["jpg", "png", "webp", "tiff", "gif", "ico", "pdf"],
      tiff: ["jpg", "png", "webp", "bmp", "gif", "ico", "pdf"],
      tif:  ["jpg", "png", "webp", "bmp", "gif", "ico", "pdf"],
      gif:  ["jpg", "png", "webp", "bmp", "tiff", "ico"],
      ico:  ["jpg", "png", "webp", "bmp"],
      svg:  ["png", "jpg", "webp", "pdf"],
    },
  },

  document: {
    label: "Documents",
    icon: "FileText",
    color: "blue",
    extensions: ["pdf", "docx", "txt", "xlsx", "csv"],
    targets: {
      pdf:  ["docx", "txt"],
      docx: ["pdf", "txt"],
      txt:  ["pdf", "docx"],
      xlsx: ["csv", "pdf"],
      csv:  ["xlsx", "pdf"],
    },
  },

  audio: {
    label: "Audio",
    icon: "Music",
    color: "violet",
    extensions: ["mp3", "wav", "ogg", "flac", "aac", "wma", "m4a"],
    targets: {
      mp3:  ["wav", "ogg", "flac", "aac", "m4a"],
      wav:  ["mp3", "ogg", "flac", "aac", "m4a"],
      ogg:  ["mp3", "wav", "flac", "aac", "m4a"],
      flac: ["mp3", "wav", "ogg", "aac", "m4a"],
      aac:  ["mp3", "wav", "ogg", "flac", "m4a"],
      wma:  ["mp3", "wav", "ogg", "flac", "aac"],
      m4a:  ["mp3", "wav", "ogg", "flac", "aac"],
    },
  },

  video: {
    label: "Video",
    icon: "Video",
    color: "rose",
    extensions: ["mp4", "mkv", "avi", "webm", "mov", "flv", "wmv"],
    targets: {
      mp4:  ["mkv", "avi", "webm", "mov", "mp3", "wav", "gif"],
      mkv:  ["mp4", "avi", "webm", "mov", "mp3", "wav"],
      avi:  ["mp4", "mkv", "webm", "mov", "mp3", "wav"],
      webm: ["mp4", "mkv", "avi", "mov", "mp3", "wav"],
      mov:  ["mp4", "mkv", "avi", "webm", "mp3", "wav"],
      flv:  ["mp4", "mkv", "avi", "webm", "mov"],
      wmv:  ["mp4", "mkv", "avi", "webm", "mov"],
    },
  },

  archive: {
    label: "Archives",
    icon: "Archive",
    color: "amber",
    extensions: ["zip", "tar", "gz", "bz2", "7z", "rar"],
    targets: {
      zip:  ["tar", "gz", "bz2"],
      tar:  ["zip", "gz", "bz2"],
      gz:   ["zip", "tar"],
      bz2:  ["zip", "tar"],
      "7z": ["zip", "tar"],
      rar:  ["zip", "tar"],
    },
  },
};

/* ------------------------------------------------------------------ */
/*  Helper utilities                                                   */
/* ------------------------------------------------------------------ */

/**
 * Extract the lowercase extension from a filename (without the leading dot).
 * e.g. "photo.JPG" → "jpg"
 */
export function getFileExtension(filename) {
  if (!filename || typeof filename !== "string") return "";
  const parts = filename.split(".");
  return parts.length > 1 ? parts.pop().toLowerCase() : "";
}

/**
 * Return the category key ("image", "audio", …) for a given extension,
 * or null when the extension is not supported.
 */
export function getCategory(extension) {
  const ext = (extension || "").toLowerCase();
  for (const [key, cat] of Object.entries(FORMAT_CATEGORIES)) {
    if (cat.extensions.includes(ext)) return key;
  }
  return null;
}

/**
 * Return the full category info object ({ label, icon, color, … })
 * for a given extension, or null.
 */
export function getCategoryInfo(extension) {
  const key = getCategory(extension);
  return key ? { key, ...FORMAT_CATEGORIES[key] } : null;
}

/**
 * Return the array of valid target formats an extension can be converted to,
 * or an empty array if the extension is not supported.
 */
export function getValidTargets(extension) {
  const ext = (extension || "").toLowerCase();
  for (const cat of Object.values(FORMAT_CATEGORIES)) {
    if (cat.targets[ext]) return [...cat.targets[ext]];
  }
  return [];
}

/**
 * Return a flat array of every supported extension string.
 */
export function getAllSupportedExtensions() {
  const all = [];
  for (const cat of Object.values(FORMAT_CATEGORIES)) {
    all.push(...cat.extensions);
  }
  return all;
}

/**
 * Format a byte count into a human-readable string.
 * e.g. 10485760 → "10.00 MB"
 */
export function formatFileSize(bytes) {
  if (bytes === 0) return "0 B";
  const units = ["B", "KB", "MB", "GB", "TB"];
  const i = Math.floor(Math.log(bytes) / Math.log(1024));
  const size = (bytes / Math.pow(1024, i)).toFixed(2);
  return `${size} ${units[i]}`;
}
