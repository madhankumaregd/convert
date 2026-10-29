import '../utils/format_registry.dart';

enum FileStatus {
  idle,
  uploading,
  processing,
  done,
  error,
}

class FileItem {
  final String id;
  final String name;
  final String path;
  final int size;
  final String extension;
  final CategoryMeta? category;
  FileStatus status;
  double progress; // 0.0 to 1.0
  String? error;

  FileItem({
    required this.id,
    required this.name,
    required this.path,
    required this.size,
    required this.extension,
    this.category,
    this.status = FileStatus.idle,
    this.progress = 0.0,
    this.error,
  });

  factory FileItem.fromPath(String path, {String? customName, int? customSize}) {
    final normalizedPath = path.replaceAll('\\', '/');
    final filename = customName ?? normalizedPath.split('/').last;
    final ext = FormatRegistry.getFileExtension(filename);
    final cat = FormatRegistry.getCategory(ext);

    return FileItem(
      id: '${DateTime.now().millisecondsSinceEpoch}_${filename.hashCode}',
      name: filename,
      path: path,
      size: customSize ?? 0,
      extension: ext,
      category: cat,
    );
  }
}

