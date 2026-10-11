[app]
title = BiliPink
package.name = bilipink
package.domain = org.bilipink
source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,ttf,json,xml
source.include_patterns = assets/*
version = 1.0

# 【关键】去掉pyjnius，buildozer会自动内置，避免版本冲突
requirements = python3,kivy==2.3.0,kivymd==1.1.1,pillow

orientation = portrait

android.permissions = INTERNET,READ_MEDIA_VIDEO,READ_MEDIA_IMAGES,ACCESS_NETWORK_STATE

android.api = 33
android.minapi = 24
android.ndk = 25b

android.accept_sdk_license = True
android.add_assets = assets/bdl-android-aarch64

android.debuggable = False
android.release_artifact = apk
android.archs = arm64-v8a

android.version_code = 1
android.version_name = 1.0

[buildozer]
log_level = 3
warn_on_root = 1
