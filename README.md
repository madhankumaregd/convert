# 🔄 Convert — Universal File Converter & Lossless Compressor

Convert is a modern, high-performance file transformation platform available for **Web (React + Vite)** and **Android (Flutter)**, powered by a unified **Python FastAPI** backend.

It allows users to convert almost any file type into another compatible format and perform lossless/near-lossless compression across images, documents, audio, video, and archives.

---

## 🌟 Key Features

### 1. 🎯 Smart Dynamic Output Filtering
- **Context-Aware Target Picker**: Tap, select, or drag-and-drop any file, and the application instantly detects its format and category.
- **Strict Compatibility**: The format picker dynamically filters to display **only valid conversion targets** for the selected file type (e.g., uploading a `PNG` displays image targets + `PDF`, uploading `PDF` displays document formats).
- **Multi-File Intersection**: When uploading multiple files, the selector displays only the common compatible target formats.

### 2. 🔀 Universal Conversion Engine
- **Images**: PNG, JPG/JPEG, WEBP, BMP, TIFF, GIF, ICO, SVG $\leftrightarrow$ PDF / other image types
- **Documents**: PDF, DOCX, TXT, XLSX, CSV (bi-directional transformations)
- **Audio**: MP3, WAV, OGG, FLAC, AAC, WMA, M4A
- **Video**: MP4, MKV, AVI, WEBM, MOV, FLV, WMV (including video-to-audio extraction)
- **Archives**: ZIP, TAR, GZ, BZ2, 7Z, RAR repackaging

### 3. 🗜️ Lossless & Smart Compression
- Dedicated **Compress Mode** alongside conversion.
- Configurable quality slider with quick presets (*Low*, *Medium*, *High / Recommended (85%)*, *Maximum*).
- Stream & metadata optimization for PDFs and smart re-encoding for images/media.
- Header-based size comparison displaying exact bytes saved and percentage reduction.

### 4. 📱 Full Android App (Flutter)
- Built with **Flutter 3 + Dart** with Material 3 design and Google Fonts.
- **Native Android File System**: Native document picker with multi-selection support.
- **Open & Share Integration**: Converted files can be opened immediately via Android intents or shared directly to WhatsApp, Google Drive, Gmail, etc.
- **In-App Server Switcher**: Seamlessly connects to `10.0.2.2:8000` (Android emulator default) or custom Wi-Fi network IPs for physical Android devices.

---

## 🏗️ Project Architecture

```
Convert/
├── backend/                       # Python FastAPI Backend
│   ├── app/
│   │   ├── main.py                # FastAPI entrypoint & CORS config
│   │   ├── config.py              # Directory paths & size limits
│   │   ├── routers/
│   │   │   ├── convert.py         # /api/convert & /api/convert/batch
│   │   │   └── compress.py        # /api/compress & /api/compress/batch
│   │   ├── services/
│   │   │   ├── image_service.py   # Pillow image conversion & compression
│   │   │   ├── document_service.py# PDF/DOCX/TXT/XLSX/CSV processing
│   │   │   ├── media_service.py   # Pydub audio & FFmpeg video processing
│   │   │   ├── archive_service.py # ZIP/TAR/GZ/BZ2 packaging
│   │   │   └── compression_service.py # Central compression router
│   │   └── utils/
│   │       ├── format_registry.py # Comprehensive format maps & validator
│   │       └── file_utils.py      # Safe upload, stream, & cleanup utils
│   └── requirements.txt
│
├── mobile/                        # Android App (Flutter)
│   ├── lib/
│   │   ├── config/                # AppTheme (Dark/Light) & ApiConstants
│   │   ├── models/                # FileItem, ConversionResult
│   │   ├── services/              # ApiService (Dio) & StorageService (Open/Share)
│   │   ├── utils/                 # FormatRegistry & SizeFormatter
│   │   ├── widgets/               # Header, UploadBox, FileList, FormatSelector,
│   │   │                          # CompressSlider, ProgressCard, ResultsSheet,
│   │   │                          # ServerSettingsDialog
│   │   ├── screens/               # HomeScreen
│   │   └── main.dart
│   ├── build/app/outputs/flutter-apk/app-debug.apk # Compiled Android APK
│   └── pubspec.yaml
│
└── frontend/                      # Web Client (React 19 + Vite + Tailwind v4)
    ├── src/
    │   ├── components/
    │   ├── hooks/
    │   ├── utils/
    │   ├── App.jsx
    │   └── index.css
    ├── vite.config.js
    └── package.json
```

---

## 🚀 Running the Apps

### 1. Start the Backend API (FastAPI)
```bash
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
*(Interactive Swagger documentation available at `http://localhost:8000/docs`)*

### 2. Run the Android App (Flutter)
```bash
cd mobile

# Run on connected Android device or emulator
flutter run

# Or install the pre-built debug APK directly
adb install build/app/outputs/flutter-apk/app-debug.apk
```

> **Note for Android Testing**:
> - **Android Emulator**: Automatically defaults to `http://10.0.2.2:8000/api` (points to host PC localhost).
> - **Physical Android Device**: Tap the **Server Settings** (DNS icon) in the app header and enter your PC's local Wi-Fi IP (e.g. `http://192.168.1.100:8000/api`).

### 3. Run the Web App (React)
```bash
cd frontend
npm run dev
```
Open `http://localhost:5173` in your browser.
