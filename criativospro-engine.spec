# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['backend\\core\\main.py'],
    pathex=['backend'],
    binaries=[],
    datas=[('backend/core/providers', 'core/providers')],
    hiddenimports=['engineio.async_drivers.aiohttp', 'core.providers.base_provider', 'core.providers.deepseek.provider', 'core.providers.deepseek.brain', 'core.providers.groq.provider', 'core.providers.groq.brain', 'core.providers.openrouter.provider', 'core.providers.openrouter.brain', 'core.providers.ollama.provider', 'core.providers.ollama.brain', 'core.providers.lmstudio.provider', 'core.providers.lmstudio.brain', 'core.providers.huggingface.provider', 'core.providers.huggingface.brain'],
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
    name='criativospro-engine',
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
)
