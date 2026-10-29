import 'package:flutter/material.dart';
import '../config/app_theme.dart';

class CompressSlider extends StatelessWidget {
  final int quality;
  final ValueChanged<int> onQualityChanged;

  const CompressSlider({
    super.key,
    required this.quality,
    required this.onQualityChanged,
  });

  Color _getQualityColor(int q) {
    if (q <= 50) return AppTheme.roseError;
    if (q <= 70) return AppTheme.amberWarning;
    if (q <= 85) return AppTheme.emeraldSuccess;
    return AppTheme.cyanAccent;
  }

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final qualityColor = _getQualityColor(quality);

    final presets = [
      {'label': 'Low', 'value': 60, 'desc': 'Smallest size'},
      {'label': 'Medium', 'value': 75, 'desc': 'Balanced'},
      {'label': 'High', 'value': 85, 'desc': 'Recommended'},
      {'label': 'Max', 'value': 95, 'desc': 'Best quality'},
    ];

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Header & Quality Indicator
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              'Compression Quality',
              style: TextStyle(
                fontSize: 14,
                fontWeight: FontWeight.bold,
                color: isDark ? Colors.grey[200] : Colors.grey[800],
              ),
            ),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
              decoration: BoxDecoration(
                color: qualityColor.withValues(alpha: 0.15),
                borderRadius: BorderRadius.circular(10),
              ),
              child: Text(
                '$quality%',
                style: TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.w800,
                  color: qualityColor,
                ),
              ),
            ),
          ],
        ),

        const SizedBox(height: 14),

        // Slider
        SliderTheme(
          data: SliderTheme.of(context).copyWith(
            activeTrackColor: qualityColor,
            inactiveTrackColor: isDark ? const Color(0xFF1E293B) : const Color(0xFFE2E8F0),
            thumbColor: qualityColor,
            overlayColor: qualityColor.withValues(alpha: 0.15),
            trackHeight: 6,
            thumbShape: const RoundSliderThumbShape(enabledThumbRadius: 10),
          ),
          child: Slider(
            value: quality.toDouble(),
            min: 1,
            max: 100,
            onChanged: (val) => onQualityChanged(val.round()),
          ),
        ),

        const SizedBox(height: 10),

        // Presets Grid
        Row(
          children: presets.map((preset) {
            final val = preset['value'] as int;
            final isSelected = quality == val;

            return Expanded(
              child: Padding(
                padding: const EdgeInsets.symmetric(horizontal: 4.0),
                child: InkWell(
                  onTap: () => onQualityChanged(val),
                  borderRadius: BorderRadius.circular(12),
                  child: Container(
                    padding: const EdgeInsets.symmetric(vertical: 8),
                    decoration: BoxDecoration(
                      color: isSelected
                          ? AppTheme.primaryColor.withValues(alpha: 0.15)
                          : (isDark ? const Color(0xFF131B2E) : Colors.white),
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(
                        color: isSelected
                            ? AppTheme.primaryColor
                            : (isDark ? const Color(0xFF1E293B) : const Color(0xFFE2E8F0)),
                        width: isSelected ? 1.5 : 1,
                      ),
                    ),
                    child: Column(
                      children: [
                        Text(
                          preset['label'] as String,
                          style: TextStyle(
                            fontSize: 11,
                            fontWeight: FontWeight.bold,
                            color: isSelected
                                ? AppTheme.primaryColor
                                : (isDark ? Colors.grey[300] : Colors.grey[700]),
                          ),
                        ),
                        const SizedBox(height: 2),
                        Text(
                          '$val%',
                          style: TextStyle(
                            fontSize: 9,
                            color: isSelected
                                ? AppTheme.primaryColor
                                : (isDark ? Colors.grey[500] : Colors.grey[500]),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            );
          }).toList(),
        ),
      ],
    );
  }
}

