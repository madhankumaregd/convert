import 'package:flutter/material.dart';
import '../config/app_theme.dart';
import '../models/file_item.dart';

class ProgressCard extends StatelessWidget {
  final FileItem file;

  const ProgressCard({super.key, required this.file});

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;

    Color statusColor;
    String statusText;
    IconData statusIcon;

    switch (file.status) {
      case FileStatus.uploading:
        statusColor = AppTheme.primaryColor;
        statusText = 'Uploading ${(file.progress * 100).toInt()}%';
        statusIcon = Icons.cloud_upload_outlined;
        break;
      case FileStatus.processing:
        statusColor = AppTheme.secondaryColor;
        statusText = 'Converting / Compressing...';
        statusIcon = Icons.autorenew_rounded;
        break;
      case FileStatus.done:
        statusColor = AppTheme.emeraldSuccess;
        statusText = 'Completed';
        statusIcon = Icons.check_circle_outline_rounded;
        break;
      case FileStatus.error:
        statusColor = AppTheme.roseError;
        statusText = file.error ?? 'Failed';
        statusIcon = Icons.error_outline_rounded;
        break;
      case FileStatus.idle:
        statusColor = Colors.grey;
        statusText = 'Waiting...';
        statusIcon = Icons.hourglass_empty_rounded;
        break;
    }

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
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Expanded(
                child: Text(
                  file.name,
                  style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
              ),
              const SizedBox(width: 8),
              Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(statusIcon, size: 14, color: statusColor),
                  const SizedBox(width: 4),
                  Text(
                    statusText,
                    style: TextStyle(
                      fontSize: 11,
                      fontWeight: FontWeight.bold,
                      color: statusColor,
                    ),
                  ),
                ],
              ),
            ],
          ),
          const SizedBox(height: 8),
          ClipRRect(
            borderRadius: BorderRadius.circular(4),
            child: LinearProgressIndicator(
              value: file.status == FileStatus.done
                  ? 1.0
                  : (file.status == FileStatus.error
                      ? 1.0
                      : (file.progress > 0 ? file.progress : null)),
              minHeight: 6,
              backgroundColor: isDark ? const Color(0xFF1E293B) : const Color(0xFFE2E8F0),
              valueColor: AlwaysStoppedAnimation<Color>(statusColor),
            ),
          ),
        ],
      ),
    );
  }
}

