[app]

title = BiliPink

package.name = bilipink
package.domain = org.bilipink

source.dir = .

source.include_exts = py,png,jpg,jpeg,kv,atlas,ttf,json,xml
source.include_patterns = assets/*

version = 1.0


# Android稳定组合
requirements = python3,kivy==2.1.0,kivymd==1.1.1,pillow


orientation = portrait


# 权限
android.permissions = INTERNET,ACCESS_NETWORK_STATE


# Android SDK
android.api = 33
android.minapi = 24


# 稳定NDK
android.ndk = 25c


android.accept_sdk_license = True


# bdl二进制文件
android.add_assets = assets/bdl-android-aarch64


# 只编译你的手机架构
android.archs = arm64-v8a


android.debuggable = True


android.version_code = 1
android.version_name = 1.0



[buildozer]

log_level = 2

warn_on_root = 1
