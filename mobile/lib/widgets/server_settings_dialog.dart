import 'package:flutter/material.dart';
import '../config/api_constants.dart';

class ServerSettingsDialog extends StatefulWidget {
  const ServerSettingsDialog({super.key});

  @override
  State<ServerSettingsDialog> createState() => _ServerSettingsDialogState();
}

class _ServerSettingsDialogState extends State<ServerSettingsDialog> {
  late final TextEditingController _controller;
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _controller = TextEditingController();
    _loadCurrentUrl();
  }

  Future<void> _loadCurrentUrl() async {
    final current = await ApiConstants.getBaseUrl();
    setState(() {
      _controller.text = current;
      _isLoading = false;
    });
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: Row(
        children: [
          Icon(Icons.settings_ethernet_rounded, color: Theme.of(context).colorScheme.primary),
          const SizedBox(width: 10),
          const Text('Backend Server URL', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
        ],
      ),
      content: _isLoading
          ? const SizedBox(height: 100, child: Center(child: CircularProgressIndicator()))
          : SingleChildScrollView(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'Set the backend API endpoint for conversion & compression processing.',
                    style: TextStyle(fontSize: 13, color: Colors.grey),
                  ),
                  const SizedBox(height: 16),
                  TextField(
                    controller: _controller,
                    decoration: InputDecoration(
                      labelText: 'API Base URL',
                      hintText: 'e.g. https://convert-ten-rho.vercel.app',
                      border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                      prefixIcon: const Icon(Icons.link_rounded),
                    ),
                  ),
                  const SizedBox(height: 12),
                  const Text(
                    'Quick Presets:',
                    style: TextStyle(fontSize: 12, fontWeight: FontWeight.w600),
                  ),
                  const SizedBox(height: 8),
                  Wrap(
                    spacing: 8,
                    runSpacing: 8,
                    children: [
                      ActionChip(
                        avatar: const Icon(Icons.cloud_done_rounded, size: 14),
                        label: const Text('Vercel (Cloud)'),
                        onPressed: () {
                          _controller.text = ApiConstants.vercelBaseUrl;
                        },
                      ),
                      ActionChip(
                        avatar: const Icon(Icons.dns_rounded, size: 14),
                        label: const Text('Render (Docker)'),
                        tooltip: 'High-quality: LibreOffice + FFmpeg',
                        onPressed: () {
                          _controller.text = ApiConstants.renderBaseUrl;
                        },
                      ),
                      ActionChip(
                        label: const Text('Emulator'),
                        onPressed: () {
                          _controller.text = 'http://10.0.2.2:8000';
                        },
                      ),
                      ActionChip(
                        label: const Text('Localhost'),
                        onPressed: () {
                          _controller.text = 'http://localhost:8000';
                        },
                      ),
                    ],
                  ),
                ],
              ),
            ),
      actions: [
        TextButton(
          onPressed: () => Navigator.pop(context),
          child: const Text('Cancel'),
        ),
        FilledButton(
          onPressed: () async {
            if (_controller.text.trim().isNotEmpty) {
              await ApiConstants.setBaseUrl(_controller.text.trim());
              if (context.mounted) {
                Navigator.pop(context, true);
              }
            }
          },
          child: const Text('Save'),
        ),
      ],
    );
  }
}
