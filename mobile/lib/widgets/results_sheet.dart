import 'package:flutter/material.dart';
import 'package:open_filex/open_filex.dart';
import '../config/app_theme.dart';
import '../models/conversion_result.dart';
import '../services/storage_service.dart';
import '../utils/size_formatter.dart';

class ResultsSheet extends StatelessWidget {
  final List<ConversionResult> results;
  final VoidCallback onClear;

  const ResultsSheet({
    super.key,
    required this.results,
    required this.onClear,
  });

  Future<void> _downloadSingle(BuildContext context, ConversionResult res) async {
    final savedPath = await StorageService.downloadToPublicDirectory(
      sourceFilePath: res.localPath,
      filename: res.name,
    );

    if (savedPath != null && context.mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Downloaded: ${res.name}'),
          backgroundColor: AppTheme.emeraldSuccess,
          action: SnackBarAction(
            label: 'Open',
            textColor: Colors.white,
            onPressed: () => StorageService.openFile(savedPath),
          ),
          duration: const Duration(seconds: 4),
        ),
      );
    } else if (context.mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Failed to save file to Downloads'),
          backgroundColor: AppTheme.roseError,
        ),
      );
    }
  }

  Future<void> _downloadAll(BuildContext context) async {
    int count = 0;
    String? lastPath;

    for (final res in results) {
      final savedPath = await StorageService.downloadToPublicDirectory(
        sourceFilePath: res.localPath,
        filename: res.name,
      );
      if (savedPath != null) {
        count++;
        lastPath = savedPath;
      }
    }

    if (context.mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Downloaded $count file${count != 1 ? 's' : ''} to Downloads folder'),
          backgroundColor: AppTheme.emeraldSuccess,
          action: lastPath != null
              ? SnackBarAction(
                  label: 'Open Last',
                  textColor: Colors.white,
                  onPressed: () => StorageService.openFile(lastPath!),
                )
              : null,
          duration: const Duration(seconds: 5),
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    if (results.isEmpty) return const SizedBox.shrink();

    final isDark = Theme.of(context).brightness == Brightness.dark;

    final totalOriginal = results.fold<int>(0, (sum, r) => sum + r.originalSize);
    final totalNew = results.fold<int>(0, (sum, r) => sum + r.newSize);
    final totalSaved = totalOriginal > totalNew ? (totalOriginal - totalNew) : 0;
    final totalSavingsPercent = totalOriginal > 0 && totalSaved > 0
        ? ((totalSaved / totalOriginal) * 100).round()
        : 0;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Summary Header Banner
        Container(
          padding: const EdgeInsets.all(14),
          decoration: BoxDecoration(
            gradient: LinearGradient(
              colors: [
                AppTheme.emeraldSuccess.withValues(alpha: 0.15),
                AppTheme.primaryColor.withValues(alpha: 0.15),
              ],
            ),
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: AppTheme.emeraldSuccess.withValues(alpha: 0.3)),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Container(
                    padding: const EdgeInsets.all(8),
                    decoration: BoxDecoration(
                      color: AppTheme.emeraldSuccess.withValues(alpha: 0.2),
                      shape: BoxShape.circle,
                    ),
                    child: const Icon(Icons.check_circle_rounded, color: AppTheme.emeraldSuccess, size: 20),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Ready (${results.length} file${results.length > 1 ? 's' : ''})',
                          style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14),
                        ),
                        Text(
                          totalSaved > 0
                              ? 'Saved ${formatFileSize(totalSaved)} ($totalSavingsPercent% reduction)'
                              : 'Conversions completed successfully',
                          style: TextStyle(
                            fontSize: 11,
                            color: isDark ? Colors.grey[300] : Colors.grey[700],
                          ),
                        ),
                      ],
                    ),
                  ),
                  IconButton(
                    icon: const Icon(Icons.delete_outline_rounded, size: 20, color: Colors.grey),
                    tooltip: 'Clear results',
                    onPressed: onClear,
                  ),
                ],
              ),

              const SizedBox(height: 12),

              // Download All CTA Button
              SizedBox(
                width: double.infinity,
                child: FilledButton.icon(
                  onPressed: () => _downloadAll(context),
                  icon: const Icon(Icons.download_rounded, size: 18),
                  label: Text('Download All (${results.length}) to Downloads'),
                  style: FilledButton.styleFrom(
                    backgroundColor: AppTheme.emeraldSuccess,
                    foregroundColor: Colors.white,
                    padding: const EdgeInsets.symmetric(vertical: 10),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                  ),
                ),
              ),
            ],
          ),
        ),

        const SizedBox(height: 12),

        // Results List
        ListView.separated(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          itemCount: results.length,
          separatorBuilder: (_, _) => const SizedBox(height: 8),
          itemBuilder: (context, index) {
            final res = results[index];

            return Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: isDark ? const Color(0xFF131B2E) : Colors.white,
                borderRadius: BorderRadius.circular(16),
                border: Border.all(
                  color: isDark ? const Color(0xFF1E293B) : const Color(0xFFE2E8F0),
                ),
              ),
              child: Column(
                children: [
                  Row(
                    children: [
                      // Icon
                      Container(
                        padding: const EdgeInsets.all(10),
                        decoration: BoxDecoration(
                          color: AppTheme.emeraldSuccess.withValues(alpha: 0.12),
                          borderRadius: BorderRadius.circular(12),
                        ),
                        child: const Icon(Icons.file_download_done_rounded, color: AppTheme.emeraldSuccess, size: 20),
                      ),

                      const SizedBox(width: 12),

                      // Info
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              res.name,
                              style: const TextStyle(fontSize: 13, fontWeight: FontWeight.bold),
                              maxLines: 1,
                              overflow: TextOverflow.ellipsis,
                            ),
                            const SizedBox(height: 3),
                            Row(
                              children: [
                                Text(
                                  formatFileSize(res.originalSize),
                                  style: TextStyle(fontSize: 11, color: isDark ? Colors.grey[400] : Colors.grey[600]),
                                ),
                                const SizedBox(width: 4),
                                const Icon(Icons.arrow_forward_rounded, size: 10, color: Colors.grey),
                                const SizedBox(width: 4),
                                Text(
                                  formatFileSize(res.newSize),
                                  style: const TextStyle(fontSize: 11, fontWeight: FontWeight.bold),
                                ),
                                if (res.savingsPercent > 0) ...[
                                  const SizedBox(width: 6),
                                  Container(
                                    padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 1),
                                    decoration: BoxDecoration(
                                      color: AppTheme.emeraldSuccess.withValues(alpha: 0.15),
                                      borderRadius: BorderRadius.circular(6),
                                    ),
                                    child: Text(
                                      '-${res.savingsPercent}%',
                                      style: const TextStyle(
                                        fontSize: 9,
                                        fontWeight: FontWeight.bold,
                                        color: AppTheme.emeraldSuccess,
                                      ),
                                    ),
                                  ),
                                ],
                              ],
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),

                  const SizedBox(height: 10),

                  // Action Buttons: Download, Open, Share
                  Row(
                    children: [
                      // Primary Download Button
                      Expanded(
                        child: ElevatedButton.icon(
                          onPressed: () => _downloadSingle(context, res),
                          icon: const Icon(Icons.download_rounded, size: 16),
                          label: const Text(
                            'Download',
                            style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold),
                          ),
                          style: ElevatedButton.styleFrom(
                            backgroundColor: AppTheme.primaryColor,
                            foregroundColor: Colors.white,
                            padding: const EdgeInsets.symmetric(vertical: 8),
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(10),
                            ),
                            elevation: 0,
                          ),
                        ),
                      ),
                      const SizedBox(width: 8),

                      // Open Button
                      OutlinedButton.icon(
                        onPressed: () async {
                          final openResult = await StorageService.openFile(res.localPath);
                          if (openResult.type != ResultType.done && context.mounted) {
                            ScaffoldMessenger.of(context).showSnackBar(
                              SnackBar(content: Text('Cannot open: ${openResult.message}')),
                            );
                          }
                        },
                        icon: const Icon(Icons.open_in_new_rounded, size: 15),
                        label: const Text('Open', style: TextStyle(fontSize: 12)),
                        style: OutlinedButton.styleFrom(
                          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(10),
                          ),
                        ),
                      ),
                      const SizedBox(width: 8),

                      // Share Button
                      IconButton.outlined(
                        icon: const Icon(Icons.share_rounded, size: 16),
                        tooltip: 'Share',
                        style: IconButton.styleFrom(
                          padding: const EdgeInsets.all(8),
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(10),
                          ),
                        ),
                        onPressed: () async {
                          await StorageService.shareFile(
                            res.localPath,
                            text: 'Transformed with Convert App',
                          );
                        },
                      ),
                    ],
                  ),
                ],
              ),
            );
          },
        ),
      ],
    );
  }
}
