import 'dart:io';
import 'package:file_picker/file_picker.dart';
import 'package:flutter/foundation.dart';
import 'package:open_filex/open_filex.dart';
import 'package:path_provider/path_provider.dart';
import 'package:share_plus/share_plus.dart';

class StorageService {
  /// Save bytes to a local app cache / document directory
  static Future<String> saveFileBytes({
    required List<int> bytes,
    required String filename,
  }) async {
    Directory dir;
    if (kIsWeb) {
      return filename;
    }

    try {
      dir = await getApplicationDocumentsDirectory();
    } catch (_) {
      dir = await getTemporaryDirectory();
    }

    final convertDir = Directory('${dir.path}/Convert');
    if (!await convertDir.exists()) {
      await convertDir.create(recursive: true);
    }

    final filePath = '${convertDir.path}/$filename';
    final file = File(filePath);
    await file.writeAsBytes(bytes);
    return filePath;
  }

  /// Download and copy file to the user-accessible public Downloads folder
  /// (e.g. /storage/emulated/0/Download on Android)
  static Future<String?> downloadToPublicDirectory({
    required String sourceFilePath,
    required String filename,
  }) async {
    final sourceFile = File(sourceFilePath);
    if (!await sourceFile.exists()) return null;

    final bytes = await sourceFile.readAsBytes();

    if (kIsWeb) {
      await FilePicker.saveFile(
        fileName: filename,
        bytes: bytes,
      );
      return filename;
    }

    String? targetDir;

    if (Platform.isAndroid) {
      // Standard Android public Downloads folder
      final androidDownload = Directory('/storage/emulated/0/Download');
      if (await androidDownload.exists()) {
        targetDir = androidDownload.path;
      }
    }

    if (targetDir == null) {
      try {
        final downloadDir = await getDownloadsDirectory();
        if (downloadDir != null) {
          targetDir = downloadDir.path;
        }
      } catch (_) {}
    }

    if (targetDir == null) {
      final docDir = await getApplicationDocumentsDirectory();
      targetDir = docDir.path;
    }

    String destinationPath = '$targetDir/$filename';
    var targetFile = File(destinationPath);

    // If file with same name exists, append counter (e.g. file (1).png)
    if (await targetFile.exists()) {
      final dot = filename.lastIndexOf('.');
      final base = dot != -1 ? filename.substring(0, dot) : filename;
      final ext = dot != -1 ? filename.substring(dot) : '';
      int counter = 1;
      while (await targetFile.exists()) {
        destinationPath = '$targetDir/$base ($counter)$ext';
        targetFile = File(destinationPath);
        counter++;
      }
    }

    await targetFile.writeAsBytes(bytes);
    return targetFile.path;
  }

  /// Save file using native file saver dialog (allows user to select destination)
  static Future<bool> saveWithFilePicker({
    required String sourceFilePath,
    required String filename,
  }) async {
    final sourceFile = File(sourceFilePath);
    if (!await sourceFile.exists()) return false;

    final bytes = await sourceFile.readAsBytes();
    final uri = await FilePicker.saveFile(
      fileName: filename,
      bytes: bytes,
    );
    return uri != null;
  }

  /// Open file using default Android intent / system handler
  static Future<OpenResult> openFile(String filePath) async {
    return await OpenFilex.open(filePath);
  }

  /// Share file to other Android apps (WhatsApp, Drive, Gmail, etc.)
  static Future<void> shareFile(String filePath, {String? text}) async {
    final xFile = XFile(filePath);
    await SharePlus.instance.share(
      ShareParams(
        files: [xFile],
        text: text,
      ),
    );
  }
}
