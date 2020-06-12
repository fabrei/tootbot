#!/bin/sh

[ ! -z $(podman ps -a --format "{{.Names}}" | grep <container-name>) ] && podman rm <container-name>

podman create \
	-d \
	-v $HOME/tootbot/data:/usr/src/app/data \
	--name <container-name> \
	<image-name>
