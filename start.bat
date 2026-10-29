@echo off
echo ==============================================================
echo       Convert — Universal File Converter & Compressor
echo ==============================================================
echo [1] Launch Backend API (FastAPI) + React Web Frontend
echo [2] Launch Backend API + Flutter Android App
echo [3] Launch All (Backend + Web + Flutter)
echo ==============================================================
set /p choice="Select an option (1-3) [default: 1]: "

if "%choice%"=="" set choice=1

if "%choice%"=="1" goto option1
if "%choice%"=="2" goto option2
if "%choice%"=="3" goto option3

:option1
start "Convert - Backend API" cmd /k "cd backend && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
timeout /t 2 /nobreak >nul
start "Convert - Web Frontend" cmd /k "cd frontend && npm run dev"
echo Backend:  http://localhost:8000/docs
echo Frontend: http://localhost:5173
goto end

:option2
start "Convert - Backend API" cmd /k "cd backend && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
timeout /t 2 /nobreak >nul
start "Convert - Flutter App" cmd /k "cd mobile && flutter run"
echo Backend: http://localhost:8000/docs
echo Flutter Android launching...
goto end

:option3
start "Convert - Backend API" cmd /k "cd backend && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
timeout /t 2 /nobreak >nul
start "Convert - Web Frontend" cmd /k "cd frontend && npm run dev"
start "Convert - Flutter App" cmd /k "cd mobile && flutter run"
echo All services launching!
goto end

:end
echo ==============================================================
