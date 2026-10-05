# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files
from PyInstaller.utils.hooks import collect_submodules

datas = [('themes', 'themes'), ('plugins', 'plugins')]
hiddenimports = ['PyQt6.QtCore', 'PyQt6.QtGui', 'PyQt6.QtWidgets', 'qtawesome', 'pyqtgraph', 'numpy', 'markdown', 'psutil', 'pynput', 'pynput.keyboard._win32', 'pynput.mouse._win32', 'emoji', 'sympy', 'mpmath']
datas += collect_data_files('qtawesome')
datas += collect_data_files('pyqtgraph')
datas += collect_data_files('markdown')
hiddenimports += collect_submodules('qtawesome')
hiddenimports += collect_submodules('pynput')
hiddenimports += collect_submodules('sympy')


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['PyQt5', 'PySide6', 'PyQt5.QtCore', 'PySide6.QtCore', 'matplotlib', 'torch', 'torchvision', 'torchaudio', 'transformers', 'comfyui', 'IPython', 'notebook', 'tkinter', 'PyQt-Fluent-Widgets', 'PyQt5-Frameless-Window'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Nucleus',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['assets\\nucleus.ico'],
)
