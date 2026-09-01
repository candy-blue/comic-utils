# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_data_files, collect_submodules

datas = [
    ('src/assets', 'src/assets'),
]
datas += collect_data_files('qfluentwidgets')

hiddenimports = [
    'qfluentwidgets',
    'app',
    'src',
]
hiddenimports += collect_submodules('qfluentwidgets')
hiddenimports += collect_submodules('app')
hiddenimports += collect_submodules('src')

excludes = [
    'pikepdf',
    'torch',
    'torchvision',
    'scipy',
    'matplotlib',
    'transformers',
    'onnxruntime',
    'cv2',
    'pandas',
    'sklearn',
    'IPython',
    'jupyter',
    'notebook',
    'tkinter',
    'tensorboard',
    'tensorboardX',
    'kornia',
    'kornia_rs',
    'safetensors',
]

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='ComicUtils',
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
    icon='src/assets/icon.ico'
)
