[app]
​Nombre de la aplicación
​title = Bitacora de Maquinas
​Nombre del paquete (usado por Android)
​package.name = bitacora_maquinas
package.domain = com.kapitojocha
​Directorio donde se encuentra el código fuente
​source.dir = .
​Extensiones de archivos que deben incluirse en el APK
​source.include_exts = py,kv,png,jpg,jpeg,gif,ttf,ttc,txt,json,csv
​Versión de la aplicación
​version = 0.1.0
​Orientación de la pantalla (portrait o landscape)
​orientation = portrait
​Si la app debe ser fullscreen (0=No)
​fullscreen = 0
​Nivel de log (2 es Debug, 0 es Mute)
​log_level = 2
​Dependencias de Python necesarias: kivy, y las usadas en main.py
​requirements = python3,kivy,csv,json,uuid,datetime
​Ruta al ícono
​icon.filename = assets/icon.png
​Ajustes de Android
​Permisos requeridos
​android.permissions = INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE
​API target (33 es Android 13, mínimo para Google Play)
​android.api = 33
​API mínima (21 es Android 5.0)
​android.minapi = 21
​Arquitecturas para compilar (arm64-v8a es 64-bit, preferido)
​android.archs = arm64-v8a, armeabi-v7a
android.accept_sdk_license = True
android.enable_androidx = True
​[buildozer]
log_level = 2
warn_on_root = 0
