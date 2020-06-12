#!/bin/sh

podman generate systemd \
	-n <container-name> | sed  "/\[Service\]/a User=${USER}\nGroup=${USER}" > "${HOME}/tootbot/systemd/container-<container-name>.service"
