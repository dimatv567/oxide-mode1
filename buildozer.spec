[app]

title = Oxide Mod Menu
package.name = oxidemod
package.domain = org.mod

source.dir = .
source.include_exts = py,png,jpg,kv,atlas
source.main_file = main.py

requirements = python3,kivy

version = 0.1
orientation = landscape

android.archs = arm64-v8a, armeabi-v7a
android.accept_sdk_license = True

android.api = 33
android.min_api = 21
android.ndk = 25b

# Принудительно указываем локальные папки для скачивания чистых компонентов
android.sdk_path = .buildozer/android/platform/android-sdk
android.ndk_path = .buildozer/android/platform/android-ndk-r25b
