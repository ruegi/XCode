# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['xcode2.py'],
             pathex=['D:\\\\DEV\\\\Py\\\\xcode\\\\xcode2', 'D:\\DEV\\Py\\XCode'],
             binaries=[('./MediaInfo.dll', '.')],
             datas=[],
             hiddenimports=['transcodeWin', 'videoFile', 'sqlalchemy', 'pymediainfo'],
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
          name='XCode',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False , icon='XC.ico')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='XCode')
