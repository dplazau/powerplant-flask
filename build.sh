#!/usr/bin/env sh

DEV_IMG=docker:0.0
LOCAL_APP_PATH=${PWD}
CONTAINER_PATH=/home/

docker build . -t ${DEV_IMG} && \
docker run -p 127.0.0.1:8888:8888 -itv ${LOCAL_APP_PATH}:${CONTAINER_PATH} ${DEV_IMG}