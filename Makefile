# Aether — container build + dev loop. Full runbook in CONTAINER.md.
#
#   make base        build the golden rootfs (once / on package change)
#   make dev         boot it with ~/aether bind-mounted live — iterate here
#   make image       bake the game in -> dist/aether.tar.zst (the one unit)
#   make play-image  boot the released image, persistent overlay (save survives)
#
# base/, dev, image, and play-image use sudo (pacstrap + nspawn need root).

ROOT := $(shell pwd)
BASE := $(ROOT)/base
DIST := $(ROOT)/dist

.PHONY: help base dev image play-image clean

help:
	@sed -n '3,7p' Makefile

base:
	bash container/build.sh

dev:
	@test -d $(BASE) || { echo "run 'make base' first"; exit 1; }
	sudo systemd-nspawn -b -D $(BASE) \
	  --bind=$(ROOT):/opt/aether \
	  --hostname=aether
# Inside the container you autologin into the Glade. To test a change: edit
# ~/aether on the host, then re-run ./play inside. No rebuild — the game is
# read fresh each run. (Or: watchexec -r ./play to auto-relaunch on save.)

image:
	@test -d $(BASE) || { echo "run 'make base' first"; exit 1; }
	sudo rm -rf $(DIST)/rootfs
	mkdir -p $(DIST)
	sudo cp -a $(BASE) $(DIST)/rootfs
	sudo mkdir -p $(DIST)/rootfs/opt/aether
	sudo cp -a engine bin play README.md $(DIST)/rootfs/opt/aether/
	sudo chown -R 1000:1000 $(DIST)/rootfs/opt/aether
	cd $(DIST)/rootfs && sudo tar --numeric-owner -caf $(DIST)/aether.tar.zst .
	@echo ">> dist/aether.tar.zst ready"
	@echo "   import elsewhere:  machinectl import-tar dist/aether.tar.zst aether"

play-image:
	@test -f $(DIST)/aether.tar.zst || { echo "run 'make image' first"; exit 1; }
	@test -e $(DIST)/play-root/usr || { sudo mkdir -p $(DIST)/play-root && \
	  sudo tar -C $(DIST)/play-root --numeric-owner -xaf $(DIST)/aether.tar.zst; }
	@echo "Persistent overlay: writes land in dist/play-root and survive reboots."
	@echo "Save slot:  sudo cp -a dist/play-root dist/save-<name>"
	@echo "Permadeath: append --volatile=overlay below to discard writes on exit."
	sudo systemd-nspawn -b -D $(DIST)/play-root --hostname=aether

clean:
	sudo rm -rf $(DIST)
	@echo "removed dist/ (base/ kept — 'sudo rm -rf base' to drop the rootfs too)"
