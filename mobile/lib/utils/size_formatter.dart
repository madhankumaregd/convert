import 'dart:math';

/// Format bytes into human-readable string (e.g. 1.2 MB, 450 KB).
String formatFileSize(int bytes) {
  if (bytes <= 0) return '0 B';
  const suffixes = ['B', 'KB', 'MB', 'GB', 'TB'];
  final i = (log(bytes) / log(1024)).floor();
  final clampedIndex = i.clamp(0, suffixes.length - 1);
  final value = bytes / pow(1024, clampedIndex);
  return '${value.toStringAsFixed(value < 10 && clampedIndex > 0 ? 1 : 0)} ${suffixes[clampedIndex]}';
}

