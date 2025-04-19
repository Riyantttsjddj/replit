[app]
title = YouTube Downloader
package.name = ytdownloader
package.domain = org.test
source.dir = .
source.include_exts = py,kv,png,jpg,json
version = 0.2
requirements = python3,kivy==2.2.1,yt-dlp,requests,pillow,urllib3
orientation = portrait
fullscreen = 0
icon = generated-icon.png

# Permissions
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,FOREGROUND_SERVICE

# (bool) Indicate if the application should be fullscreen or not
android.fullscreen = 0

# (list) The Android archs to build for, choices: armeabi-v7a, arm64-v8a, x86, x86_64
android.archs = arm64-v8a, armeabi-v7a

# (bool) Skip adb install and use system installation via intent URL
#android.skip_install = false

# (bool) Copy library instead of making a libpymodules.so
android.copy_libs = 1

# (str) Android logcat filters to use
android.logcat_filters = *:S python:D

# (int) Android API to use
android.api = 33

# (int) Minimum API required
android.minapi = 21

# (str) Android NDK version to use
android.ndk = 25b

# (bool) If True, then skip trying to update the Android sdk
# This can be useful to avoid excess Internet downloads or save time
# when an update is due and you just want to test/build your package
android.skip_update = True

# (bool) If True, then automatically accept SDK license
# agreements. This is intended for automation only. If set to False,
# the default, you will be shown the license when first running
# buildozer.
android.accept_sdk_license = True

# (str) Path to a custom bootstrap template
#android.bootstrap = %(source.dir)s/bootstrap

# (list) List of Java files to add to the android project (can be java or a directory containing the files)
#android.add_src =

# (list) Put these files or directories in the apk assets directory.
# Either form may be used, and assets need not be in 'source.dir'.
# 1) android.add_assets = source_dir/path/to/my_assets
# 2) android.add_assets = source_dir/path/to/my_assets/;destination_dir
#android.add_assets =

# (list) Put these files or directories in the apk res directory.
# The option may be used in three ways, the value may contain one or zero ';'.
#     1) android.add_resources = foo/bar
#     2) android.add_resources = foo/bar;moo/boo
#     3) android.add_resources = foo/bar;moo/boo/;moo/boo/baz
#android.add_resources =

[buildozer]
log_level = 2
warn_on_root = 1
