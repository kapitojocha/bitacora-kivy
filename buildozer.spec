[app]
title = Bitacora de Maquinas
package.name = bitacora_maquinas
package.domain = com.kapitojocha
source.dir = .
source.include_exts = py,png,jpg,kv,txt,ttf,json,db,sqlite3
version = 1.0.0
requirements = python3,kivy==2.2.1
orientation = portrait
fullscreen = 0
android.api = 33
android.minapi = 21
android.sdk = 33
android.build_tools = 33.0.2
android.ndk = 25b
android.arch = arm64-v8a,armeabi-v7a
android.allow_backup = True
android.debug = 1
#android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# Si no tienes icono aún, déjalo comentado para evitar error:
#icon.filename = assets/icon.png

# Mantener nombre del archivo principal:
main.py = 1

[buildozer]
log_level = 2
warn_on_root = 0

[app.android]
# Si exportas/compartes archivos luego, descomenta permisos:
# android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

[python]
# Si luego agregas libs (openpyxl, etc.) añádelas en requirements
