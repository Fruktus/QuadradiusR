GD := godot
BUILD_DIR := build
APP_NAME := QuadradiusR

GD_OPTS := --no-window -v

PRESET_LINUX_X11 := "Linux/X11"
PRESET_WINDOWS := "Windows Desktop"

_default: linux

linux:
	mkdir -p $(BUILD_DIR)
	$(GD) $(GD_OPTS) --export $(PRESET_LINUX_X11) $(BUILD_DIR)/$(APP_NAME)

windows:
	mkdir -p $(BUILD_DIR)
	$(GD) $(GD_OPTS) --export $(PRESET_WINDOWS) $(BUILD_DIR)/$(APP_NAME).exe

clean:
	rm -rf $(BUILD_DIR)

.PHONY: _default build
