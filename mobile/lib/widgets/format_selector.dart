import 'package:flutter/material.dart';
import '../config/app_theme.dart';
import '../models/file_item.dart';
import '../utils/format_registry.dart';

class FormatSelector extends StatelessWidget {
  final List<FileItem> files;
  final String? selectedFormat;
  final ValueChanged<String> onFormatSelected;

  const FormatSelector({
    super.key,
    required this.files,
    required this.selectedFormat,
    required this.onFormatSelected,
  });

  @override
  Widget build(BuildContext context) {
    if (files.isEmpty) return const SizedBox.shrink();

    final isDark = Theme.of(context).brightness == Brightness.dark;
    final extensions = files.map((f) => f.extension).toList();
    final commonTargets = FormatRegistry.getCommonTargets(extensions);

    if (commonTargets.isEmpty) {
      return Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: AppTheme.amberWarning.withValues(alpha: 0.1),
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: AppTheme.amberWarning.withValues(alpha: 0.3)),
        ),
        child: Row(
          children: [
            const Icon(Icons.info_outline_rounded, color: AppTheme.amberWarning),
            const SizedBox(width: 12),
            Expanded(
              child: Text(
                'No compatible output format found for this combination of files. Please select files of the same category.',
                style: TextStyle(
                  fontSize: 12,
                  color: isDark ? Colors.grey[300] : Colors.grey[800],
                ),
              ),
            ),
          ],
        ),
      );
    }

    final grouped = FormatRegistry.groupTargetsByCategory(commonTargets);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              'Select Target Format',
              style: TextStyle(
                fontSize: 14,
                fontWeight: FontWeight.bold,
                color: isDark ? Colors.grey[200] : Colors.grey[800],
              ),
            ),
            if (selectedFormat != null)
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                decoration: BoxDecoration(
                  color: AppTheme.primaryColor.withValues(alpha: 0.15),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Text(
                  'Converting to .${selectedFormat!.toUpperCase()}',
                  style: const TextStyle(
                    fontSize: 11,
                    fontWeight: FontWeight.w700,
                    color: AppTheme.primaryColor,
                  ),
                ),
              ),
          ],
        ),
        const SizedBox(height: 12),

        // Grouped Target Chips
        ListView.separated(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          itemCount: grouped.entries.length,
          separatorBuilder: (_, _) => const SizedBox(height: 12),
          itemBuilder: (context, index) {
            final entry = grouped.entries.elementAt(index);
            final category = entry.key;
            final formats = entry.value;

            return Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Category Label
                Row(
                  children: [
                    Icon(category.icon, size: 14, color: category.color),
                    const SizedBox(width: 6),
                    Text(
                      category.label.toUpperCase(),
                      style: TextStyle(
                        fontSize: 10,
                        fontWeight: FontWeight.w800,
                        letterSpacing: 0.8,
                        color: category.color,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 8),

                // Formats Pills
                Wrap(
                  spacing: 8,
                  runSpacing: 8,
                  children: formats.map((fmt) {
                    final isSelected = selectedFormat == fmt;

                    return InkWell(
                      onTap: () => onFormatSelected(fmt),
                      borderRadius: BorderRadius.circular(12),
                      child: AnimatedContainer(
                        duration: const Duration(milliseconds: 180),
                        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
                        decoration: BoxDecoration(
                          color: isSelected
                              ? category.color
                              : (category.color.withValues(alpha: 0.08)),
                          borderRadius: BorderRadius.circular(12),
                          border: Border.all(
                            color: isSelected
                                ? category.color
                                : category.color.withValues(alpha: 0.25),
                            width: isSelected ? 2 : 1,
                          ),
                          boxShadow: isSelected
                              ? [
                                  BoxShadow(
                                    color: category.color.withValues(alpha: 0.4),
                                    blurRadius: 8,
                                    offset: const Offset(0, 2),
                                  ),
                                ]
                              : null,
                        ),
                        child: Text(
                          fmt.toUpperCase(),
                          style: TextStyle(
                            fontSize: 12,
                            fontWeight: FontWeight.w700,
                            color: isSelected ? Colors.white : category.color,
                          ),
                        ),
                      ),
                    );
                  }).toList(),
                ),
              ],
            );
          },
        ),
      ],
    );
  }
}

