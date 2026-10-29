import 'package:dio/dio.dart';
import '../config/api_constants.dart';
import '../models/conversion_result.dart';
import 'storage_service.dart';

class ApiService {
  final Dio _dio = Dio(BaseOptions(
    connectTimeout: const Duration(seconds: 30),
    receiveTimeout: const Duration(minutes: 5),
    sendTimeout: const Duration(minutes: 5),
  ));

  Future<Dio> _getClient() async {
    final rawBaseUrl = await ApiConstants.getBaseUrl();
    final normalized = ApiConstants.normalizeBaseUrl(rawBaseUrl);
    _dio.options.baseUrl = normalized;
    return _dio;
  }

  /// Check if the backend API is reachable
  Future<bool> checkHealth() async {
    try {
      final client = await _getClient();
      final res = await client.get('/api/formats');
      return res.statusCode == 200;
    } catch (_) {
      return false;
    }
  }

  /// Convert a single file to target format
  Future<ConversionResult> convertFile({
    required String filePath,
    required String fileName,
    required int originalSize,
    required String targetFormat,
    void Function(double progress)? onProgress,
  }) async {
    final client = await _getClient();

    final formData = FormData.fromMap({
      'file': await MultipartFile.fromFile(filePath, filename: fileName),
      'target_format': targetFormat,
    });

    final response = await client.post(
      '/api/convert',
      data: formData,
      options: Options(
        responseType: ResponseType.bytes,
      ),
      onSendProgress: (sent, total) {
        if (total > 0 && onProgress != null) {
          // Send progress is 0.0 to 0.7
          onProgress((sent / total) * 0.7);
        }
      },
      onReceiveProgress: (received, total) {
        if (total > 0 && onProgress != null) {
          // Receive progress is 0.7 to 1.0
          onProgress(0.7 + (received / total) * 0.3);
        }
      },
    );

    // Extract filename from disposition or craft from target
    String outFilename = 'converted_$fileName.$targetFormat';
    final disposition = response.headers.value('content-disposition');
    if (disposition != null) {
      final match = RegExp(r'filename="?([^";\n]+)"?').firstMatch(disposition);
      if (match != null) {
        outFilename = match.group(1)!;
      }
    }

    final bytes = response.data as List<int>;
    final savedPath = await StorageService.saveFileBytes(
      bytes: bytes,
      filename: outFilename,
    );

    final newSize = bytes.length;
    final savings = originalSize > 0 && newSize < originalSize
        ? (((originalSize - newSize) / originalSize) * 100).round()
        : 0;

    return ConversionResult(
      id: '${DateTime.now().millisecondsSinceEpoch}',
      name: outFilename,
      localPath: savedPath,
      originalSize: originalSize,
      newSize: newSize,
      savingsPercent: savings,
    );
  }

  /// Compress a single file
  Future<ConversionResult> compressFile({
    required String filePath,
    required String fileName,
    required int originalSize,
    required int quality,
    void Function(double progress)? onProgress,
  }) async {
    final client = await _getClient();

    final formData = FormData.fromMap({
      'file': await MultipartFile.fromFile(filePath, filename: fileName),
      'quality': quality.toString(),
    });

    final response = await client.post(
      '/api/compress',
      data: formData,
      options: Options(
        responseType: ResponseType.bytes,
      ),
      onSendProgress: (sent, total) {
        if (total > 0 && onProgress != null) {
          onProgress((sent / total) * 0.7);
        }
      },
      onReceiveProgress: (received, total) {
        if (total > 0 && onProgress != null) {
          onProgress(0.7 + (received / total) * 0.3);
        }
      },
    );

    String outFilename = 'compressed_$fileName';
    final disposition = response.headers.value('content-disposition');
    if (disposition != null) {
      final match = RegExp(r'filename="?([^";\n]+)"?').firstMatch(disposition);
      if (match != null) {
        outFilename = match.group(1)!;
      }
    }

    final bytes = response.data as List<int>;
    final savedPath = await StorageService.saveFileBytes(
      bytes: bytes,
      filename: outFilename,
    );

    final rawOrig = response.headers.value('x-original-size');
    final rawSavings = response.headers.value('x-savings-percent');

    final serverOrig = rawOrig != null ? int.tryParse(rawOrig) : null;
    final parsedSavings = rawSavings != null ? (double.tryParse(rawSavings)?.round() ?? 0) : 0;

    final origSize = serverOrig ?? originalSize;
    final newSize = bytes.length;
    final savings = parsedSavings > 0
        ? parsedSavings
        : (origSize > 0 && newSize < origSize
            ? (((origSize - newSize) / origSize) * 100).round()
            : 0);

    return ConversionResult(
      id: '${DateTime.now().millisecondsSinceEpoch}',
      name: outFilename,
      localPath: savedPath,
      originalSize: origSize,
      newSize: newSize,
      savingsPercent: savings,
    );
  }
}
