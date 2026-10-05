@echo off
chcp 65001 >nul
setlocal

echo === Nucleus build ===

REM 1. ставим только нужное
pip install -r requirements.txt

REM 2. чистим старые сборки
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist Nucleus.spec del /q Nucleus.spec

REM 3. собираем одним файлом, без консоли, с иконкой
pyinstaller ^
  --noconfirm ^
  --clean ^
  --onefile ^
  --windowed ^
  --name Nucleus ^
  --icon=assets\nucleus.ico ^
  --add-data "themes;themes" ^
  --add-data "plugins;plugins" ^
  --hidden-import=PyQt6.QtCore ^
  --hidden-import=PyQt6.QtGui ^
  --hidden-import=PyQt6.QtWidgets ^
  --hidden-import=qtawesome ^
  --hidden-import=pyqtgraph ^
  --hidden-import=numpy ^
  --hidden-import=markdown ^
  --hidden-import=psutil ^
  --hidden-import=pynput ^
  --hidden-import=pynput.keyboard._win32 ^
  --hidden-import=pynput.mouse._win32 ^
  --hidden-import=emoji ^
  --hidden-import=sympy ^
  --hidden-import=mpmath ^
  --collect-data qtawesome ^
  --collect-data pyqtgraph ^
  --collect-data markdown ^
  --collect-submodules qtawesome ^
  --collect-submodules pynput ^
  --collect-submodules sympy ^
  --exclude-module PyQt5 ^
  --exclude-module PySide6 ^
  --exclude-module PyQt5.QtCore ^
  --exclude-module PySide6.QtCore ^
  --exclude-module matplotlib ^
  --exclude-module torch ^
  --exclude-module torchvision ^
  --exclude-module torchaudio ^
  --exclude-module transformers ^
  --exclude-module comfyui ^
  --exclude-module IPython ^
  --exclude-module notebook ^
  --exclude-module tkinter ^
  --exclude-module PyQt-Fluent-Widgets ^
  --exclude-module PyQt5-Frameless-Window ^
  main.py

echo.
echo === Готово: dist\Nucleus.exe ===
pause