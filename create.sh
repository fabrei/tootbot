#!/bin/sh

podman create \
	-d \
	-v $HOME/tootbot/data:/usr/src/app/data \
	--name <container-name>
	<image-name>
