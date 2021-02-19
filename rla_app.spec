# -*- mode: python ; coding: utf-8 -*-
block_cipher = None
added_files = [
    ("rla_app_files/info_text.json",
    "rla_app_files"),
    ("rla_app_files/rla-logo.ico",
    "rla_app_files"),
    ("rla_app_files/rla-logo.png",
    "rla_app_files"),
    ("rla_app_files/search-folder-icon.png",
    "rla_app_files"),
    # Include these files to prevent inital import not working
    ("rla_app_files/lawn-polygon.poly",
    "rla_app_files"),
    ("rla_app_files/polygon-path.txt",
    "rla_app_files")
]
a = Analysis(['rla_app.py'],
             pathex=['C:\\Users\\Bi\\Documents\\GitHub_Repo\\GDP_RLA'],
             binaries=[],
             datas=added_files,
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='rla_app',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False, # --noconsole/--windowed/-w
          icon="rla_app_files\\rla-logo.ico")  # --icon/-i
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='rla_app')