[app]
title = Bitacora de Maquinas
package.name = bitacora
package.domain = com.kapitojocha
source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,txt,json,db,sqlite3
version = 1.0.0

requirements = python3,kivy==2.2.1,pillow,openpyxl,plyer
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
android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

[buildozer]
log_level = 2
warn_on_root = 0
