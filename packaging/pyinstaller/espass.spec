# Build from repository root: pyinstaller --noconfirm packaging/pyinstaller/espass.spec
from PyInstaller.utils.hooks import collect_submodules

hiddenimports = collect_submodules('argon2')
hiddenimports += collect_submodules('PySide6')
hiddenimports += collect_submodules('keyring')
a = Analysis(
    ['src/pyvault/__main__.py'], pathex=['src'], binaries=[], datas=[('assets/icons/espass.ico', 'assets/icons')], hiddenimports=hiddenimports,
    hookspath=[], hooksconfig={}, runtime_hooks=[], excludes=['tkinter'], noarchive=False, optimize=1,
)
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, a.binaries, a.datas, [], name='espass', debug=False,
          bootloader_ignore_signals=False, strip=False, upx=True, console=False, icon='assets/icons/espass.ico',
          disable_windowed_traceback=True)
