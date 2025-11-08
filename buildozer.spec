[app]
title = Bitacora de maquinas
package.name = bitacora_maquinas
package.domain = com.kapitojocha
source.dir = .
​Asegurar que los archivos CSV y JSON se incluyan, si se usan después.
​source.include_exts = py,kv,png,jpg,jpeg,gif,ttf,ttc,txt,json,csv
version = 0.1.0
orientation = portrait
fullscreen = 0
log_level = 2
​Requisitos mínimos: Python 3 y Kivy
​requirements = python3,kivy
icon.filename = assets/icon.png
​Android Permissions and Build Settings
​android.permissions = READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,INTERNET
​Usar API 33 para compatibilidad con Google Play Store (target SDK)
​android.api = 33
android.minapi = 21
​Compilar para ambas arquitecturas principales (32-bit y 64-bit)
​android.archs = arm64-v8a, armeabi-v7a
android.accept_sdk_license = True
android.enable_androidx = True
​[buildozer]
log_level = 2
warn_on_root = 0