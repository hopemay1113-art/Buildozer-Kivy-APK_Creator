[app]
# (str) Title of your application
title = DemoApp

# (str) Package name
package.name = demoapp

# (str) Package domain
package.domain = org.example

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include
source.include_exts = py,kv,txt

# (str) Application versioning
version = 0.0.1

# (list) Application requirements
requirements = python3,kivy

# (list) Supported orientations
orientation = portrait

# (int) Android API to use
android.api = 31

# (int) Minimum API your APK will support
android.minapi = 21

# (str) Android NDK version to use
android.ndk = 23b

# (list) The Android archs to build for
android.archs = arm64-v8a, armeabi-v7a

# (str) Debug artifact format
android.debug_artifact = apk
