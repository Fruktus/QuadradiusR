GD := godot
BUILD_DIR := build
APP_NAME := QuadradiusR

RELEASE := false

GD_OPTS := --no-window -v

PRESET_LINUX_X11 := "Linux/X11"
PRESET_WINDOWS := "Windows Desktop"
PRESET_HTML5 := "HTML5"
PRESET_MACOS := "Mac OSX"
PRESET_ANDROID := "Android"

ifeq ($(RELEASE),true)
	EXPORT_SUFFIX :=
else
	EXPORT_SUFFIX := -debug
endif

_default: linux windows html5 macos android

linux:
	mkdir -p $(BUILD_DIR)/$@
	$(GD) $(GD_OPTS) --export$(EXPORT_SUFFIX) $(PRESET_LINUX_X11) $(BUILD_DIR)/$@/$(APP_NAME)

windows:
	mkdir -p $(BUILD_DIR)/$@
	$(GD) $(GD_OPTS) --export$(EXPORT_SUFFIX) $(PRESET_WINDOWS) $(BUILD_DIR)/$@/$(APP_NAME).exe

html5:
	mkdir -p $(BUILD_DIR)/$@
	$(GD) $(GD_OPTS) --export$(EXPORT_SUFFIX) $(PRESET_HTML5) $(BUILD_DIR)/$@/index.html

macos:
	mkdir -p $(BUILD_DIR)/$@
	$(GD) $(GD_OPTS) --export$(EXPORT_SUFFIX) $(PRESET_MACOS) $(BUILD_DIR)/$@/$(APP_NAME)

android:
	mkdir -p $(BUILD_DIR)/$@
	$(GD) $(GD_OPTS) --export$(EXPORT_SUFFIX) $(PRESET_ANDROID) $(BUILD_DIR)/$@/$(APP_NAME).apk

clean:
	rm -rf $(BUILD_DIR)

.PHONY: _default linux windows html5 macos android
