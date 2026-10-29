import 'package:flutter/material.dart';

class CategoryMeta {
  final String key;
  final String label;
  final IconData icon;
  final Color color;
  final List<String> extensions;
  final Map<String, List<String>> targets;

  const CategoryMeta({
    required this.key,
    required this.label,
    required this.icon,
    required this.color,
    required this.extensions,
    required this.targets,
  });
}

class FormatRegistry {
  static const Map<String, CategoryMeta> categories = {
    'image': CategoryMeta(
      key: 'image',
      label: 'Images',
      icon: Icons.image_rounded,
      color: Color(0xFF10B981), // Emerald
      extensions: [
        'jpg', 'jpeg', 'png', 'webp', 'bmp', 'tiff', 'tif', 'gif', 'ico', 'svg'
      ],
      targets: {
        'jpg': ['png', 'webp', 'bmp', 'tiff', 'gif', 'ico', 'pdf'],
        'jpeg': ['png', 'webp', 'bmp', 'tiff', 'gif', 'ico', 'pdf'],
        'png': ['jpg', 'webp', 'bmp', 'tiff', 'gif', 'ico', 'pdf'],
        'webp': ['jpg', 'png', 'bmp', 'tiff', 'gif', 'ico', 'pdf'],
        'bmp': ['jpg', 'png', 'webp', 'tiff', 'gif', 'ico', 'pdf'],
        'tiff': ['jpg', 'png', 'webp', 'bmp', 'gif', 'ico', 'pdf'],
        'tif': ['jpg', 'png', 'webp', 'bmp', 'gif', 'ico', 'pdf'],
        'gif': ['jpg', 'png', 'webp', 'bmp', 'tiff', 'ico'],
        'ico': ['jpg', 'png', 'webp', 'bmp'],
        'svg': ['png', 'jpg', 'webp', 'pdf'],
      },
    ),
    'document': CategoryMeta(
      key: 'document',
      label: 'Documents',
      icon: Icons.description_rounded,
      color: Color(0xFF3B82F6), // Blue
      extensions: ['pdf', 'docx', 'txt', 'xlsx', 'csv'],
      targets: {
        'pdf': ['docx', 'txt'],
        'docx': ['pdf', 'txt'],
        'txt': ['pdf', 'docx'],
        'xlsx': ['csv', 'pdf'],
        'csv': ['xlsx', 'pdf'],
      },
    ),
    'audio': CategoryMeta(
      key: 'audio',
      label: 'Audio',
      icon: Icons.music_note_rounded,
      color: Color(0xFF8B5CF6), // Violet
      extensions: ['mp3', 'wav', 'ogg', 'flac', 'aac', 'wma', 'm4a'],
      targets: {
        'mp3': ['wav', 'ogg', 'flac', 'aac', 'm4a'],
        'wav': ['mp3', 'ogg', 'flac', 'aac', 'm4a'],
        'ogg': ['mp3', 'wav', 'flac', 'aac', 'm4a'],
        'flac': ['mp3', 'wav', 'ogg', 'aac', 'm4a'],
        'aac': ['mp3', 'wav', 'ogg', 'flac', 'm4a'],
        'wma': ['mp3', 'wav', 'ogg', 'flac', 'aac'],
        'm4a': ['mp3', 'wav', 'ogg', 'flac', 'aac'],
      },
    ),
    'video': CategoryMeta(
      key: 'video',
      label: 'Video',
      icon: Icons.videocam_rounded,
      color: Color(0xFFF43F5E), // Rose
      extensions: ['mp4', 'mkv', 'avi', 'webm', 'mov', 'flv', 'wmv'],
      targets: {
        'mp4': ['mkv', 'avi', 'webm', 'mov', 'mp3', 'wav', 'gif'],
        'mkv': ['mp4', 'avi', 'webm', 'mov', 'mp3', 'wav'],
        'avi': ['mp4', 'mkv', 'webm', 'mov', 'mp3', 'wav'],
        'webm': ['mp4', 'mkv', 'avi', 'mov', 'mp3', 'wav'],
        'mov': ['mp4', 'mkv', 'avi', 'webm', 'mp3', 'wav'],
        'flv': ['mp4', 'mkv', 'avi', 'webm', 'mov'],
        'wmv': ['mp4', 'mkv', 'avi', 'webm', 'mov'],
      },
    ),
    'archive': CategoryMeta(
      key: 'archive',
      label: 'Archives',
      icon: Icons.folder_zip_rounded,
      color: Color(0xFFF59E0B), // Amber
      extensions: ['zip', 'tar', 'gz', 'bz2', '7z', 'rar'],
      targets: {
        'zip': ['tar', 'gz', 'bz2'],
        'tar': ['zip', 'gz', 'bz2'],
        'gz': ['zip', 'tar'],
        'bz2': ['zip', 'tar'],
        '7z': ['zip', 'tar'],
        'rar': ['zip', 'tar'],
      },
    ),
  };

  /// Extract lowercase extension without leading dot
  static String getFileExtension(String filename) {
    final dot = filename.lastIndexOf('.');
    if (dot == -1 || dot == filename.length - 1) return '';
    return filename.substring(dot + 1).toLowerCase();
  }

  /// Get category metadata for an extension
  static CategoryMeta? getCategory(String extension) {
    final ext = extension.toLowerCase();
    for (final cat in categories.values) {
      if (cat.extensions.contains(ext)) return cat;
    }
    return null;
  }

  /// Get valid conversion targets for a specific input extension
  static List<String> getValidTargets(String extension) {
    final ext = extension.toLowerCase();
    final cat = getCategory(ext);
    if (cat == null) return [];
    return cat.targets[ext] ?? [];
  }

  /// Compute the intersection of valid target formats across multiple file extensions.
  /// If all files can convert to a given target, it is included.
  static List<String> getCommonTargets(List<String> extensions) {
    if (extensions.isEmpty) return [];

    Set<String>? common;
    for (final ext in extensions) {
      final targets = getValidTargets(ext).toSet();
      if (common == null) {
        common = targets;
      } else {
        common = common.intersection(targets);
      }
    }
    return common?.toList() ?? [];
  }

  /// Group a list of target formats by their destination category
  static Map<CategoryMeta, List<String>> groupTargetsByCategory(List<String> targets) {
    final Map<CategoryMeta, List<String>> map = {};
    for (final fmt in targets) {
      final cat = getCategory(fmt) ??
          const CategoryMeta(
            key: 'other',
            label: 'Other',
            icon: Icons.insert_drive_file_rounded,
            color: Colors.grey,
            extensions: [],
            targets: {},
          );
      map.putIfAbsent(cat, () => []).add(fmt);
    }
    return map;
  }
}

