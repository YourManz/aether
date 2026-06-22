# Running the Aether in a container

The Aether ships as a `systemd-nspawn` container: a real OS so the game's
"the physics is the operating system" premise holds (real PID 1, real
processes, real permissions), but one that boots in under a second and never
needs an image rebuild to test a change.

The trick is two decoupled artifacts:

- **The golden base rootfs** (`base/`) — OS + the RPG terminal (autologin,
  banner, theme). Changes rarely. Built once with `make base`.
- **The game** (`engine/`, `bin/`, `play`) — changes constantly. In dev it is
  **bind-mounted live** from the host, so editing a file and re-running `./play`
  shows the change instantly. It is baked into the image only for release.

## Prerequisites (Arch host)

```bash
sudo pacman -S --needed arch-install-scripts   # provides pacstrap
# systemd-nspawn + machinectl already ship with systemd.
# Optional garnish: lolcat (AUR) or toilet for a rainbow banner — the login
# degrades gracefully to plain figlet without them.
```

## Build the golden rootfs (once)

```bash
make base
```

This `pacstrap`s a minimal rootfs into `base/` (no kernel — correct for a
container), creates the `player` account at **uid 1000** (so it matches the
host owner of the bind mount and the `chmod`-based gameplay behaves identically
on both sides), and lays the autologin / banner / `.bash_profile` over it.

## The dev loop (no rebuild, ever)

```bash
make dev
```

Boots the container with `~/aether` bind-mounted at `/opt/aether`. You autologin
straight into the Glade. To test a change:

1. Edit any file under `~/aether` on the **host** with your normal tools.
2. In the container, re-run `./play` (or run `watchexec -r ./play` to
   auto-relaunch on save).

There is no build step — the world is plain Python read fresh each run. The
image is rebuilt only when you change a *package* or the terminal config.

> During dev the game's own writes (`world/`, `state/`) land on the **host**
> repo through the mount — persistent and inspectable, which is what you want
> while building. Throwaway/permadeath behaviour belongs to the release image
> below, not the dev loop.

## The character sheet

Inside the world, `character` (also `sheet`, `stats`) opens the full-screen
curses sheet: an ASCII portrait beside live stats — the XP bar, attributes,
self-documented spellbook, regalia, deeds, and the wraith's current mood, all
refreshing once a second. Press `q` to step back. `char` / `me` print the quick
inline sheet without clearing the screen.

## Release: the one unit

```bash
make image
```

Bakes the current game into a copy of the rootfs and tars it to
`dist/aether.tar.zst` — a single self-contained file. Boot it anywhere:

```bash
machinectl import-tar dist/aether.tar.zst aether
machinectl start aether && machinectl login aether
```

## Saves and permadeath

```bash
make play-image
```

Boots the released image under a **persistent overlay** (`dist/play-root`), so
progress survives reboots — the gentle default.

- **Save slot:** `sudo cp -a dist/play-root dist/save-<name>`
- **Permadeath:** append `--volatile=overlay` to the `play-image` nspawn line.
  Every write is discarded on shutdown — death = reboot, the world resets
  pristine. `rm -rf dist/play-root` to die for real.

The writable overlay *is* the game state — the same reason the artifact is a
rootfs tarball, not an ISO, and the same reason dev never needs a rebuild.
