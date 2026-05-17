# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path

# Dieses Spec-File liegt im Ordner .\py2exe.
# Die eigentliche Anwendung liegt eine Ebene darueber.
PY2EXE_DIR = Path(SPECPATH).resolve()
PROJECT_DIR = PY2EXE_DIR.parent
ENTRY_FILE = PROJECT_DIR / "run.py"
ICON_FILE = PROJECT_DIR / "waltrone1-ASCII-ArtStudio.ico"
VERSION_FILE = PROJECT_DIR / "version_info.txt"
APP_NAME = "waltrone1-ASCII-ArtStudio"

hiddenimports = [
    "PIL",
    "PIL.Image",
    "PIL.ImageEnhance",
    "PIL.ImageOps",
    "PIL.ImageTk",
    "PIL.ImageDraw",
    "PIL.ImageFont",
]

datas = []

# Die App nutzt tkinter, daher tkinter NICHT ausschliessen.
# Grosse/unnötige Pakete bleiben ausgeschlossen, um die EXE schlank zu halten.
excludes = [
    "matplotlib",
    "numpy",
    "pandas",
    "scipy",
    "unittest",
    "pytest",
    "IPython",
    "jupyter",
]

if not ENTRY_FILE.exists():
    raise SystemExit(f"Startdatei nicht gefunden: {ENTRY_FILE}")
if not ICON_FILE.exists():
    raise SystemExit(f"Icon nicht gefunden: {ICON_FILE}")
if not VERSION_FILE.exists():
    raise SystemExit(f"version_info.txt nicht gefunden: {VERSION_FILE}")


a = Analysis(
    [str(ENTRY_FILE)],
    pathex=[str(PROJECT_DIR)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    noarchive=False,
    optimize=1,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name=APP_NAME,
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
    icon=str(ICON_FILE),
    version=str(VERSION_FILE),
)
