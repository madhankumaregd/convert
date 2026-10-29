import 'package:shared_preferences/shared_preferences.dart';

class ApiConstants {
  static const String _prefKeyBaseUrl = 'convert_backend_url';

  /// Production cloud backend deployed on Vercel (without trailing /api)
  static const String productionBaseUrl = 'https://convert-ten-rho.vercel.app';

  /// Normalizes any user-entered or default URL to strip trailing slashes or /api
  static String normalizeBaseUrl(String url) {
    var trimmed = url.trim();
    while (trimmed.endsWith('/')) {
      trimmed = trimmed.substring(0, trimmed.length - 1);
    }
    if (trimmed.endsWith('/api')) {
      trimmed = trimmed.substring(0, trimmed.length - 4);
    }
    return trimmed;
  }

  /// Default URL automatically configured to the production Vercel backend
  static String get defaultBaseUrl => productionBaseUrl;

  /// Get currently configured base URL (with auto-migration from local emulator IPs)
  static Future<String> getBaseUrl() async {
    final prefs = await SharedPreferences.getInstance();
    final saved = prefs.getString(_prefKeyBaseUrl);
    // If it was previously saved as local emulator or localhost, auto-upgrade to cloud URL
    if (saved == null || saved.contains('10.0.2.2') || saved.contains('localhost')) {
      await prefs.setString(_prefKeyBaseUrl, productionBaseUrl);
      return productionBaseUrl;
    }
    return normalizeBaseUrl(saved);
  }

  /// Save custom base URL
  static Future<void> setBaseUrl(String url) async {
    final prefs = await SharedPreferences.getInstance();
    final normalized = normalizeBaseUrl(url);
    await prefs.setString(_prefKeyBaseUrl, normalized);
  }

  /// Reset to platform default
  static Future<void> resetBaseUrl() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_prefKeyBaseUrl);
  }
}
