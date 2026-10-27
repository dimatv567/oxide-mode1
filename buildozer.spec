[app]

# Название приложения
title = Oxide Mod Menu

# Имя пакета
package.name = oxidemod
package.domain = org.mod

# Путь к исходным файлам (точка означает текущую корневую папку)
source.dir = .

# Расширения файлов проекта
source.include_exts = py,png,jpg,kv,atlas

# Главный файл
source.main_file = main.py

# Зависимости
requirements = python3,kivy

# Версия и ориентация
version = 0.1
orientation = landscape

# Архитектура процессора
android.archs = arm64-v8a, armeabi-v7a
# Автоматическое принятие лицензий Android SDK
android.accept_sdk_license = True

# Укажем стабильные версии API и Android-инструментов, чтобы Buildozer не пытался ставить экспериментальные
android.api = 31
android.min_api = 21
android.sdk = 31
android.ndk = 23b
