[app]
title = Bitacora de maquinas
package.name = bitacora_maquinas
package.domain = com.kapitojocha
source.dir = .
​Asegurar que los archivos .py, .kv, y los de datos se incluyan
​source.include_exts = py,kv,png,jpg,jpeg,gif,ttf,ttc,txt,json,csv
version = 0.1.0
orientation = portrait
fullscreen = 0
log_level = 2
​Requerimientos: Python 3 es obligatorio
​requirements = python3,kivy
icon.filename = assets/icon.png
​Android Permissions and Build Settings
​android.permissions = READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,INTERNET
​Usar API 33 para cumplir con los requisitos de Google Play Store (target SDK)
​android.api = 33
android.minapi = 21
​Compilar para arquitecturas de 32 y 64 bits para máxima compatibilidad
​android.archs = arm64-v8a, armeabi-v7a
android.accept_sdk_license = True
android.enable_androidx = True
​[buildozer]
log_level = 2
warn_on_root = 0