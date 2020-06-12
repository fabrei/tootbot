#!/bin/sh

podman build \
	-t <image-name> \
	--build-arg username=<mastodon_username> \
	--build-arg instance=<mastodon_instance> \
	--build-arg source=<twitter_account> \
	.
