[app]
title = BiliPink
package.name = bilipink
package.domain = org.bilipink
source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,ttf,json,xml
source.include_patterns = assets/*
version = 1.0

# 【修复核心：版本更换 + 语法修正！逗号放行末尾】
requirements = python3,kivy==2.3.0,kivymd==1.1.1,pillow,pyjnius

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
log_level = 2
warn_on_root = 1
