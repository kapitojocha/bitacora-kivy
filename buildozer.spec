[app]
title = Bitacora de maquinas
package.name = bitacora_maquinas
package.domain = com.kapitojocha
source.dir = .
source.include_exts = py,kv,png,jpg,jpeg,gif,ttf,ttc,txt,json,csv
version = 0.1.0
orientation = portrait
fullscreen = 0
log_level = 2
requirements = python3,kivy
icon.filename = assets/icon.png
Android Permissions and Build Settings
android.permissions = READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,INTERNET
Target SDK: 33 es el requisito mínimo actual para nuevas apps en Google Play
android.api = 33
android.minapi = 21
Compilar para arquitecturas ARM de 64 y 32 bits
android.archs = arm64-v8a, armeabi-v7a
android.accept_sdk_license = True
android.enable_androidx = True
[buildozer]
log_level = 2
warn_on_root = 0