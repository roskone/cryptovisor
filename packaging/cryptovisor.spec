# -*- mode: python ; coding: utf-8 -*-
"""Спека PyInstaller. Запуск из корня проекта:
    pyinstaller packaging/cryptovisor.spec --noconfirm
Результат: dist/CryptoVisor/ (Windows, Linux) или dist/CryptoVisor.app (macOS).
"""
import sys
from pathlib import Path

ROOT = Path(SPECPATH).parent
sys.path.insert(0, str(ROOT))
from app.version import APP_ID, VERSION  # noqa: E402

icon = ROOT / "assets" / ("icon.icns" if sys.platform == "darwin" else "icon.ico")

a = Analysis(
    [str(ROOT / "main.py")],
    pathex=[str(ROOT)],
    datas=[(str(ROOT / "assets" / "fonts"), "assets/fonts")],
    hiddenimports=[],
    excludes=[
        # неиспользуемые модули Qt — заметно уменьшают размер
        "PySide6.QtNetwork", "PySide6.QtQml", "PySide6.QtQuick", "PySide6.QtWebEngineCore",
        "PySide6.QtMultimedia", "PySide6.QtPdf", "PySide6.QtSql", "PySide6.QtTest",
        "PySide6.QtOpenGL", "PySide6.QtSvg", "PySide6.QtPrintSupport", "PySide6.QtXml",
        "PySide6.Qt3DCore", "PySide6.QtCharts", "PySide6.QtDataVisualization",
    ],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    exclude_binaries=True,
    name=APP_ID,
    console=False,
    icon=str(icon) if icon.exists() else None,
    version=str(ROOT / "packaging" / "windows" / "version_info.txt") if sys.platform == "win32" else None,
)
coll = COLLECT(exe, a.binaries, a.datas, name=APP_ID)

if sys.platform == "darwin":
    app = BUNDLE(
        coll,
        name=f"{APP_ID}.app",
        icon=str(icon) if icon.exists() else None,
        bundle_identifier="dev.cryptovisor.app",
        info_plist={"CFBundleDisplayName": "Криптовизор", "CFBundleShortVersionString": VERSION,
                    "NSHighResolutionCapable": True},
    )
