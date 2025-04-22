# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['f:\\workspace\\project\\ScreenMailer\\src\\gui\\screenmailer_gui.py'],
    pathex=[],
    binaries=[],
    datas=[('f:\\workspace\\project\\ScreenMailer\\src', 'src')],
    hiddenimports=['PIL', 'PIL._imagingtk', 'PIL._tkinter_finder', 'PIL.ImageGrab', 'PIL.Image', 'Pillow', 'smtplib', 'email', 'email.mime.multipart', 'email.mime.text', 'email.mime.image', 'logging', 'logging.handlers', 'datetime', 'yaml', 'platform', 'schedule', 'threading'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    name='ScreenMailer',
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
    icon=['f:\\workspace\\project\\ScreenMailer\\tools\\assets\\icon.ico'],
)
