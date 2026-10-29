class ConversionResult {
  final String id;
  final String name;
  final String localPath;
  final int originalSize;
  final int newSize;
  final int savingsPercent;

  ConversionResult({
    required this.id,
    required this.name,
    required this.localPath,
    required this.originalSize,
    required this.newSize,
    required this.savingsPercent,
  });
}

