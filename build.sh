#!/bin/bash

ARCH=$(uname -m)
case ${ARCH} in
  x86_64)
    export DOCKERFILE_PATH=Dockerfile.amd64
    ;;
  aarch64)
    echo "building for aarch64 (Raspberry Pi))"
    export DOCKERFILE_PATH=Dockerfile.aarch64
    ;;
  arm64)
    echo "building for arm64 (MacOs)"
    export DOCKERFILE_PATH=Dockerfile.arm64
    ;;
  *)
    echo "Unsupported architecture: ${ARCH}"
    exit 1
    ;;
esac

docker compose build --no-cache