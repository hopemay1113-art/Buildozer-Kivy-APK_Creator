[app]
# (str) Title of your application
title = Cyn Enhancements

# (str) Package name
package.name = cynenhancments

# (str) Package domain
package.domain = org.cyn

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include
source.include_exts = py,kv,txt,json

# (str) Application versioning
version = 0.1.0

# (list) Application requirements
requirements = python3,kivy,pyjnius,android

# (list) Supported orientations
orientation = portrait

# (int) Android API to use
android.api = 31

# (int) Minimum API your APK will support
android.minapi = 21

# (str) Android NDK version to use
android.ndk = 23b

# (list) Permissions
android.permissions = QUERY_ALL_PACKAGES,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE

# (list) The Android archs to build for
android.archs = arm64-v8a, armeabi-v7a

# (str) Debug artifact format
android.debug_artifact = apk
