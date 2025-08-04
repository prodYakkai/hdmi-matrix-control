a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('styles/dark_theme.qss', 'styles')],
    hiddenimports=[],
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
    [],
    exclude_binaries=True,
    name='HDMI_Matrix_Control',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    name='HDMI_Matrix_Control'
)

app = BUNDLE(
    coll,
    name='HDMI Matrix Control.app',
    bundle_identifier='com.prodyakkai.magicbox.hdmi_matrix_control',
    icon=None,
    info_plist={
        'CFBundleShortVersionString': '1.0.0',
        'CFBundleVersion': '1.0.0',
        'NSHighResolutionCapable': True,
        'NSPrincipalClass': 'NSApplication'
    }
)