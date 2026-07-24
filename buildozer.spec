[app]

# (str) Title of your application
title = Game Controller

# (str) Package name
package.name = gamecontroller

# (str) Package domain (needed for android/ios packaging)
package.domain = org.myapp

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (leave empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas

# (str) Application versioning (method 1)
version = 1.0.0

# (list) Application requirements
requirements = python3,kivy

# (list) Supported orientations
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

#
# Android specific
#

# (list) Permissions
android.permissions = INTERNET

# (int) Target Android API
android.api = 33

# (int) Minimum API
android.minapi = 24

# (list) The Android archs to build for
android.archs = arm64-v8a, armeabi-v7a

# (bool) enables Android auto backup feature
android.allow_backup = True

# ============================================================
# ========== НАСТРОЙКИ ДЛЯ ФИЗИЧЕСКОЙ КЛАВИАТУРЫ ==========
# ============================================================

# РАЗРЕШАЕМ физическую клавиатуру (Bluetooth/USB)
android.manifest.uses_feature = android.hardware.keyboard,true

# НО ЗАПРЕЩАЕМ появление экранной клавиатуры
android.manifest.soft_input_mode = stateHidden

# Запрещаем изменение состояния клавиатуры
android.manifest.window_soft_input_mode = stateHidden|adjustPan

# Говорим системе, что у нас сенсорный экран
android.manifest.uses_feature = android.hardware.touchscreen,true

# Дополнительная защита от экранной клавиатуры
android.manifest.uses_feature = android.hardware.keyboard_hide,false

# ============================================================

#
# Python for android (p4a) specific
#

# (str) python-for-android branch to use
p4a.branch = master

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug)
log_level = 2

# (int) Display warning if buildozer is run as root
warn_on_root = 1
