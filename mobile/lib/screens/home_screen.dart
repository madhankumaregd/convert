import 'dart:async';
import 'package:flutter/material.dart';
import '../config/app_theme.dart';
import '../models/conversion_result.dart';
import '../models/file_item.dart';
import '../services/api_service.dart';
import '../utils/size_formatter.dart';
import '../widgets/compress_slider.dart';
import '../widgets/file_list_widget.dart';
import '../widgets/format_selector.dart';
import '../widgets/header_widget.dart';
import '../widgets/mode_toggle.dart';
import '../widgets/progress_card.dart';
import '../widgets/results_sheet.dart';
import '../widgets/upload_box.dart';

class HomeScreen extends StatefulWidget {
  final bool isDarkMode;
  final VoidCallback onToggleTheme;

  const HomeScreen({
    super.key,
    required this.isDarkMode,
    required this.onToggleTheme,
  });

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final ApiService _apiService = ApiService();
  final ScrollController _scrollController = ScrollController();
  final List<FileItem> _files = [];
  final List<ConversionResult> _results = [];

  AppMode _mode = AppMode.convert;
  String? _selectedFormat;
  int _quality = 85;
  bool _isProcessing = false;
  bool _isServerOnline = false;
  Timer? _healthTimer;

  @override
  void initState() {
    super.initState();
    _checkServerStatus();
    _healthTimer = Timer.periodic(const Duration(seconds: 15), (_) => _checkServerStatus());
  }

  @override
  void dispose() {
    _healthTimer?.cancel();
    _scrollController.dispose();
    super.dispose();
  }

  Future<void> _checkServerStatus() async {
    final online = await _apiService.checkHealth();
    if (mounted) {
      setState(() => _isServerOnline = online);
    }
  }

  void _onFilesSelected(List<FileItem> incoming) {
    setState(() {
      _files.addAll(incoming);
      _selectedFormat = null; // Reset format to force re-evaluation of compatibility
    });

    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text('Added ${incoming.length} file${incoming.length > 1 ? 's' : ''}'),
        duration: const Duration(seconds: 2),
      ),
    );
  }

  void _removeFile(String id) {
    setState(() {
      _files.removeWhere((f) => f.id == id);
      _selectedFormat = null;
    });
  }

  void _clearFiles() {
    setState(() {
      _files.clear();
      _selectedFormat = null;
    });
  }

  Future<void> _startProcessing() async {
    if (_files.isEmpty || _isProcessing) return;

    if (_mode == AppMode.convert && _selectedFormat == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please select a target format first.')),
      );
      return;
    }

    setState(() => _isProcessing = true);

    int successCount = 0;
    int failedCount = 0;
    String lastErrorMessage = '';

    for (final file in _files) {
      setState(() {
        file.status = FileStatus.uploading;
        file.progress = 0.0;
        file.error = null;
      });

      try {
        ConversionResult result;

        if (_mode == AppMode.convert) {
          result = await _apiService.convertFile(
            filePath: file.path,
            fileName: file.name,
            originalSize: file.size,
            targetFormat: _selectedFormat!,
            onProgress: (p) {
              setState(() {
                file.progress = p;
                if (p >= 0.7) {
                  file.status = FileStatus.processing;
                }
              });
            },
          );
        } else {
          result = await _apiService.compressFile(
            filePath: file.path,
            fileName: file.name,
            originalSize: file.size,
            quality: _quality,
            onProgress: (p) {
              setState(() {
                file.progress = p;
                if (p >= 0.7) {
                  file.status = FileStatus.processing;
                }
              });
            },
          );
        }

        setState(() {
          file.status = FileStatus.done;
          file.progress = 1.0;
          _results.insert(0, result);
        });
        successCount++;
      } catch (e) {
        final errStr = e.toString();
        lastErrorMessage = errStr.contains('Failed host lookup') || errStr.contains('Connection refused')
            ? 'Cannot reach cloud server. Tap the server settings icon in the header.'
            : 'Processing error: ${errStr.split('\n').first}';

        setState(() {
          file.status = FileStatus.error;
          file.error = lastErrorMessage;
        });
        failedCount++;
      }
    }

    setState(() => _isProcessing = false);

    if (mounted) {
      if (successCount > 0) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              _mode == AppMode.convert
                  ? 'Conversion finished! Scroll down to download.'
                  : 'Compression finished! Scroll down to download.',
            ),
            backgroundColor: AppTheme.emeraldSuccess,
            duration: const Duration(seconds: 4),
          ),
        );

        // Smoothly auto-scroll to the bottom so the results and download buttons are in view!
        Future.delayed(const Duration(milliseconds: 300), () {
          if (_scrollController.hasClients) {
            _scrollController.animateTo(
              _scrollController.position.maxScrollExtent,
              duration: const Duration(milliseconds: 600),
              curve: Curves.easeOutCubic,
            );
          }
        });
      } else if (failedCount > 0) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(lastErrorMessage.isNotEmpty ? lastErrorMessage : 'Failed to process file.'),
            backgroundColor: AppTheme.roseError,
            duration: const Duration(seconds: 5),
          ),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final totalBytes = _files.fold<int>(0, (sum, f) => sum + f.size);
    final canStart = _files.isNotEmpty &&
        !_isProcessing &&
        (_mode == AppMode.compress || _selectedFormat != null);

    return Scaffold(
      body: SafeArea(
        child: RefreshIndicator(
          onRefresh: _checkServerStatus,
          child: SingleChildScrollView(
            controller: _scrollController,
            physics: const AlwaysScrollableScrollPhysics(),
            padding: const EdgeInsets.only(bottom: 32),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                // Header
                HeaderWidget(
                  isDarkMode: widget.isDarkMode,
                  onToggleTheme: widget.onToggleTheme,
                  isServerOnline: _isServerOnline,
                  onRefreshServer: _checkServerStatus,
                ),

                const SizedBox(height: 8),

                // Main Content
                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 16.0),
                  child: Column(
                    children: [
                      // Upload Box
                      UploadBox(
                        onFilesSelected: _onFilesSelected,
                        disabled: _isProcessing,
                      ),

                      // Uploaded Files
                      if (_files.isNotEmpty) ...[
                        const SizedBox(height: 20),
                        FileListWidget(
                          files: _files,
                          onRemove: _removeFile,
                          onClear: _clearFiles,
                        ),
                      ],

                      // Controls Card (Mode + Format / Slider)
                      if (_files.isNotEmpty) ...[
                        const SizedBox(height: 20),
                        Container(
                          padding: const EdgeInsets.all(16),
                          decoration: BoxDecoration(
                            color: isDark ? const Color(0xFF131B2E) : Colors.white,
                            borderRadius: BorderRadius.circular(20),
                            border: Border.all(
                              color: isDark ? const Color(0xFF1E293B) : const Color(0xFFE2E8F0),
                            ),
                          ),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              // Mode Toggle
                              ModeToggle(
                                mode: _mode,
                                onModeChanged: (m) {
                                  setState(() {
                                    _mode = m;
                                    _selectedFormat = null;
                                  });
                                },
                              ),

                              const SizedBox(height: 18),

                              // Dynamic Format Selector or Compression Slider
                              if (_mode == AppMode.convert)
                                FormatSelector(
                                  files: _files,
                                  selectedFormat: _selectedFormat,
                                  onFormatSelected: (fmt) {
                                    setState(() => _selectedFormat = fmt);
                                  },
                                )
                              else
                                CompressSlider(
                                  quality: _quality,
                                  onQualityChanged: (q) {
                                    setState(() => _quality = q);
                                  },
                                ),
                            ],
                          ),
                        ),

                        const SizedBox(height: 16),

                        // File Count & Estimated Time
                        Text(
                          '${_files.length} file${_files.length != 1 ? 's' : ''} • ${formatFileSize(totalBytes)}',
                          style: TextStyle(
                            fontSize: 12,
                            color: isDark ? Colors.grey[400] : Colors.grey[600],
                          ),
                          textAlign: TextAlign.center,
                        ),

                        const SizedBox(height: 12),

                        // Action Button
                        SizedBox(
                          width: double.infinity,
                          height: 52,
                          child: DecoratedBox(
                            decoration: BoxDecoration(
                              gradient: canStart
                                  ? const LinearGradient(
                                      colors: [AppTheme.primaryColor, AppTheme.secondaryColor],
                                    )
                                  : null,
                              color: canStart ? null : (isDark ? Colors.grey[800] : Colors.grey[300]),
                              borderRadius: BorderRadius.circular(16),
                              boxShadow: canStart
                                  ? [
                                      BoxShadow(
                                        color: AppTheme.primaryColor.withValues(alpha: 0.35),
                                        blurRadius: 12,
                                        offset: const Offset(0, 4),
                                      ),
                                    ]
                                  : null,
                            ),
                            child: ElevatedButton(
                              onPressed: canStart ? _startProcessing : null,
                              style: ElevatedButton.styleFrom(
                                backgroundColor: Colors.transparent,
                                shadowColor: Colors.transparent,
                                shape: RoundedRectangleBorder(
                                  borderRadius: BorderRadius.circular(16),
                                ),
                              ),
                              child: _isProcessing
                                  ? const SizedBox(
                                      width: 24,
                                      height: 24,
                                      child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2.5),
                                    )
                                  : Row(
                                      mainAxisAlignment: MainAxisAlignment.center,
                                      children: [
                                        Icon(
                                          _mode == AppMode.convert
                                              ? Icons.sync_alt_rounded
                                              : Icons.compress_rounded,
                                          color: Colors.white,
                                        ),
                                        const SizedBox(width: 8),
                                        Text(
                                          _mode == AppMode.convert
                                              ? 'Start Conversion'
                                              : 'Start Compression',
                                          style: const TextStyle(
                                            color: Colors.white,
                                            fontWeight: FontWeight.bold,
                                            fontSize: 15,
                                          ),
                                        ),
                                      ],
                                    ),
                            ),
                          ),
                        ),
                      ],

                      // In-Flight or Errored Progress Bars
                      if (_files.any((f) =>
                          f.status == FileStatus.uploading ||
                          f.status == FileStatus.processing ||
                          f.status == FileStatus.error)) ...[
                        const SizedBox(height: 20),
                        Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const Text(
                              'Status',
                              style: TextStyle(fontSize: 13, fontWeight: FontWeight.bold),
                            ),
                            const SizedBox(height: 8),
                            ..._files
                                .where((f) =>
                                    f.status == FileStatus.uploading ||
                                    f.status == FileStatus.processing ||
                                    f.status == FileStatus.error)
                                .map((f) => Padding(
                                      padding: const EdgeInsets.only(bottom: 8.0),
                                      child: ProgressCard(file: f),
                                    )),
                          ],
                        ),
                      ],

                      // Results Sheet with Download & Open Actions
                      if (_results.isNotEmpty) ...[
                        const SizedBox(height: 24),
                        ResultsSheet(
                          results: _results,
                          onClear: () {
                            setState(() => _results.clear());
                          },
                        ),
                      ],
                    ],
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
