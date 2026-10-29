import 'package:shared_preferences/shared_preferences.dart';

class ApiConstants {
  static const String _prefKeyBaseUrl = 'convert_backend_url';

  /// Production cloud backend deployed on Vercel
  static const String productionBaseUrl = 'https://convert-ten-rho.vercel.app/api';

  /// Default URL automatically configured to the production Vercel backend
  static String get defaultBaseUrl => productionBaseUrl;

  /// Get currently configured base URL (or fallback to default)
  static Future<String> getBaseUrl() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_prefKeyBaseUrl) ?? defaultBaseUrl;
  }

  /// Save custom base URL
  static Future<void> setBaseUrl(String url) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_prefKeyBaseUrl, url.trim());
  }

  /// Reset to platform default
  static Future<void> resetBaseUrl() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_prefKeyBaseUrl);
  }
}
