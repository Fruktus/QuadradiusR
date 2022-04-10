
REVISION := $(shell git rev-parse HEAD)
IMAGE_FULL_NAME := quadradiusr:$(REVISION)

RUN_OPTS ?= --set server.database.create_metadata=true

_default: build

build:
	docker build -f Dockerfile.bundle . -t $(IMAGE_FULL_NAME)

run: build
	docker run -it -p 8888:80 $(IMAGE_FULL_NAME) $(RUN_OPTS)

.PHONY: _default build run
