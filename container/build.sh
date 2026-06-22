#!/usr/bin/env bash
# Build the golden Aether rootfs. Run rarely — only when a platform-level
# thing changes (a package, the autologin, the banner). Produces ./base/, an
# immutable systemd-nspawn root with the RPG terminal baked in.
#
# The GAME is NOT copied here for dev: `make dev` bind-mounts it live from the
# host so edits need no rebuild. `make image` is what bakes it in for release.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BASE="$ROOT/base"
PKGS="$(grep -vE '^[[:space:]]*#|^[[:space:]]*$' "$ROOT/container/packages.txt" | tr '\n' ' ')"

if ! command -v pacstrap >/dev/null 2>&1; then
  echo "pacstrap missing. Install it:  sudo pacman -S --needed arch-install-scripts" >&2
  exit 1
fi

echo ">> pacstrap $BASE"
echo "   packages: $PKGS"
sudo pacstrap -c -K "$BASE" $PKGS

echo ">> player account (uid 1000 — matches the host owner of the bind mount)"
# uid parity keeps the chmod-based gameplay honest across the live mount.
sudo systemd-nspawn -q -D "$BASE" useradd -m -u 1000 -s /bin/bash player 2>/dev/null || \
  echo "   (player already exists — ok)"

echo ">> overlay configs (autologin, banner, .bash_profile)"
sudo cp -a "$ROOT/container/overlay/." "$BASE/"
sudo chown -R 1000:1000 "$BASE/home/player"
sudo chmod +x "$BASE/etc/aether-banner.sh"

echo ">> base rootfs ready."
echo "   iterate:  make dev      (boots it, ~/aether bind-mounted live)"
echo "   release:  make image    (bakes the game in -> dist/aether.tar.zst)"
