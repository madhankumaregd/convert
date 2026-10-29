import 'package:flutter/material.dart';
import '../config/app_theme.dart';
import 'server_settings_dialog.dart';

class HeaderWidget extends StatelessWidget {
  final bool isDarkMode;
  final VoidCallback onToggleTheme;
  final bool isServerOnline;
  final VoidCallback? onRefreshServer;

  const HeaderWidget({
    super.key,
    required this.isDarkMode,
    required this.onToggleTheme,
    required this.isServerOnline,
    this.onRefreshServer,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 12.0),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          // Logo & Title
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(10),
                decoration: BoxDecoration(
                  gradient: const LinearGradient(
                    colors: [AppTheme.primaryColor, AppTheme.secondaryColor],
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                  ),
                  borderRadius: BorderRadius.circular(14),
                  boxShadow: [
                    BoxShadow(
                      color: AppTheme.primaryColor.withValues(alpha: 0.35),
                      blurRadius: 12,
                      offset: const Offset(0, 4),
                    ),
                  ],
                ),
                child: const Icon(Icons.sync_alt_rounded, color: Colors.white, size: 24),
              ),
              const SizedBox(width: 12),
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  ShaderMask(
                    shaderCallback: (bounds) => const LinearGradient(
                      colors: [Color(0xFF818CF8), Color(0xFFA78BFA), Color(0xFF22D3EE)],
                    ).createShader(bounds),
                    child: const Text(
                      'Convert',
                      style: TextStyle(
                        fontSize: 24,
                        fontWeight: FontWeight.w900,
                        color: Colors.white,
                        letterSpacing: -0.5,
                      ),
                    ),
                  ),
                  InkWell(
                    onTap: onRefreshServer,
                    borderRadius: BorderRadius.circular(6),
                    child: Padding(
                      padding: const EdgeInsets.symmetric(vertical: 2.0),
                      child: Row(
                        children: [
                          // Animated status indicator
                          AnimatedContainer(
                            duration: const Duration(milliseconds: 400),
                            width: 8,
                            height: 8,
                            decoration: BoxDecoration(
                              shape: BoxShape.circle,
                              color: isServerOnline ? AppTheme.emeraldSuccess : AppTheme.roseError,
                              boxShadow: isServerOnline
                                  ? [
                                      BoxShadow(
                                        color: AppTheme.emeraldSuccess.withValues(alpha: 0.5),
                                        blurRadius: 6,
                                        spreadRadius: 1,
                                      ),
                                    ]
                                  : null,
                            ),
                          ),
                          const SizedBox(width: 6),
                          AnimatedSwitcher(
                            duration: const Duration(milliseconds: 300),
                            child: Text(
                              isServerOnline ? 'Cloud Backend Online' : 'Connecting...',
                              key: ValueKey(isServerOnline),
                              style: TextStyle(
                                fontSize: 11,
                                fontWeight: FontWeight.w600,
                                color: isServerOnline
                                    ? AppTheme.emeraldSuccess
                                    : AppTheme.roseError,
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                ],
              ),
            ],
          ),

          // Actions: Server Settings + Theme Toggle
          Row(
            children: [
              IconButton(
                icon: const Icon(Icons.dns_outlined, size: 22),
                tooltip: 'Server Settings',
                onPressed: () async {
                  final changed = await showDialog<bool>(
                    context: context,
                    builder: (ctx) => const ServerSettingsDialog(),
                  );
                  if (changed == true && onRefreshServer != null) {
                    onRefreshServer!();
                  }
                },
              ),
              IconButton(
                icon: Icon(
                  isDarkMode ? Icons.light_mode_rounded : Icons.dark_mode_rounded,
                  size: 22,
                ),
                tooltip: isDarkMode ? 'Switch to Light' : 'Switch to Dark',
                onPressed: onToggleTheme,
              ),
            ],
          ),
        ],
      ),
    );
  }
}
