[app]
title = Bitácora de Maquinarias
package.name = bitacora_maquinas
package.domain = com.bsgmarine
source.dir = .
source.include_exts = py,kv,png,jpg,ttf,txt,json,csv
# El entrypoint DEBE llamarse main.py
main = main.py

# Icono y splash (opcional si ya tienes assets/icon.png)
icon.filename = assets/icon.png
# presplash.filename = assets/presplash.png

# Requisitos de Python a incluir en el APK
# (manténlos cortos para compilar más rápido; agrega los que uses)
requirements = python3,kivy,plyer,openpyxl
# sqlite3 viene con Python estándar

# Si usas PIL para imágenes, añade: pillow
# Si NO usas openpyxl, puedes quitarlo para que pese menos.

# Arquitecturas
archs = arm64-v8a, armeabi-v7a

# Permisos Android (ajusta según tú)
android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
# Para Android 13+ usarás selectores SAF; esto sirve para compatibilidad.

# Orientación y tema
orientation = portrait
fullscreen = 0

# SDK/NDK/ API target (Buildozer elegirá por defecto valores compatibles)
# android.api = 33
# android.minapi = 21

# Si ves errores por compilación de openpyxl, puedes quitarlo de requirements.

[buildozer]
log_level = 2
warn_on_root = 1

[python]
# Módulos a incluir/excluir opcionalmente
# android.add_python_modules =
# android.exclude_python_modules =

[android]
# Para file chooser mediante SAF/Document Picker, plyer ayuda.
# si necesitas compartir archivos vía “share”, lo hace plyer tambi
