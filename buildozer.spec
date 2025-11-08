[app]
title = Bitácora de Máquinas
package.name = bitacora_maquinas
package.domain = com.kapitojocha
source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,txt,ttf,json,csv,db,sqlite3
version = 1.0.1

# Requisitos de Python (coinciden con los que instala el workflow)
requirements = python3,kivy==2.2.1,plyer,pillow,openpyxl

orientation = portrait
fullscreen = 0

# Android targets
android.api = 33
android.minapi = 21
android.sdk = 33
android.ndk = 25b
android.build_tools = 33.0.2
android.arch = arm64-v8a,armeabi-v7a
android.allow_backup = True
android.debug = 1

# Permisos (ajusta según necesites compartir/leer archivos)
android.permissions = READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,READ_MEDIA_IMAGES,READ_MEDIA_VIDEO,READ_MEDIA_AUDIO

# Icono opcional (coloca assets/icon.png si quieres icono personalizado)
# icon.filename = assets/icon.png

# Nombre del archivo principal
main.py = 1

[buildozer]
log_level = 2
warn_on_root = 0

[app.android]
# Si más adelante compartes archivos externos, podrías ajustar aquí
# opciones adicionales del manifest si lo necesitas.