[app]
title = Bitácora de Máquinas
package.name = bitacora_maquinas
package.domain = org.basygmarine
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,db,sqlite,ini,json,ttf
version = 1.0.0
requirements = python3,kivy,pillow,openpyxl,sqlite3
orientation = portrait
fullscreen = 0
android.archs = arm64-v8a, armeabi-v7a
android.api = 33
android.minapi = 21
android.sdk = 33
android.ndk = 25b
android.ndk_api = 21
android.entrypoint = main.py
icon.filename = assets/icon.png
presplash.filename = assets/presplash.png
# Si no tienes estos archivos, comenta las líneas con "#"
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

[buildozer]
log_level = 2
warn_on_root = 1
strict = false
requirements.source = false
