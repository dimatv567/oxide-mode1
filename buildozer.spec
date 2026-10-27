[app]

# Название вашего приложения
title = Oxide Mod Menu 

# Имя пакета (должно быть уникальным)
package.name = oxidemod

# Домен пакета
package.domain = org.mod

# Все файлы вашего проекта, которые нужно включить (через запятую)
source.include_exts = py,png,jpg,kv,atlas

# Главный файл приложения
source.main_file = main.py

# Список используемых библиотек (например, python3, kivy и т.д.)
requirements = python3,kivy

# Версия приложения
version = 0.1

# Ориентация экрана (landscape — альбомная, так как это игра)
orientation = landscape

# Поддерживаемые архитектуры процессоров
android.archs = arm64-v8a, armeabi-v7a

# Разрешения (если модулю нужны права, например интернет)
# android.permissions = INTERNET
