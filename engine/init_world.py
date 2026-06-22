#!/usr/bin/env python3
"""Build (idempotently) the world that the OS will animate.

Rooms are directories. Objects are files. Attributes are permissions.
Nothing here scripts a "puzzle" — it only places matter. The daemons
(river.py, wraith.py) and the real shell do the rest.
"""
import os
import stat

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.environ.get("AETHER_HOME", os.path.dirname(HERE))

WORLD = os.path.join(ROOT, "world")
GLADE = os.path.join(WORLD, "glade")
WRAITH = os.path.join(GLADE, "wraith")
HOLLOW = os.path.join(GLADE, "hollow")
STATE = os.path.join(ROOT, "state")
BIN = os.path.join(ROOT, "bin")


def ensure_dir(p, mode=0o755):
    if not os.path.isdir(p):
        os.makedirs(p, exist_ok=True)
        os.chmod(p, mode)


def write_if_missing(path, content, mode=0o644):
    if not os.path.exists(path):
        with open(path, "w") as f:
            f.write(content)
        os.chmod(path, mode)


def main():
    ensure_dir(WORLD)
    ensure_dir(GLADE)
    ensure_dir(WRAITH)
    ensure_dir(STATE)
    ensure_dir(BIN)

    # The event log the familiar tails for ambient world-life.
    write_if_missing(os.path.join(WORLD, ".events"), "")

    # Room descriptions.
    write_if_missing(os.path.join(GLADE, ".look"),
        "The Whispering Glade.\n"
        "A clear river threads the moss, murmuring without pause. Something\n"
        "hunched and grey crouches at the water's edge, and beyond it the dark\n"
        "mouth of a hollow waits — shut, for now.\n")

    # The Hollow: created, described, then BARRED (000). The wraith opens it
    # at runtime. Force it writable first so re-init works even if a prior
    # run left it barred.
    os.makedirs(HOLLOW, exist_ok=True)
    os.chmod(HOLLOW, 0o755)
    write_if_missing(os.path.join(HOLLOW, ".look"),
        "The Hollow.\n"
        "Cooler air. Roots overhead like rafters. The path runs deeper than\n"
        "your sight reaches.\n")
    os.chmod(HOLLOW, 0o000)

    # The wraith's mouth. Seeded with murk, so it begins hostile.
    # (mtime is fresh now, so the wraith reads 'murk' -> enraged.)
    write_if_missing(os.path.join(WRAITH, "feed"),
        "murk wells up from the seep\n")
    write_if_missing(os.path.join(WRAITH, "mood"), "enraged\n")

    # The river file is owned by the river daemon; seed it so it exists.
    write_if_missing(os.path.join(GLADE, "river"), "clear water :: 0\n")

    # A locked chest. chmod +r it, read it, and you'll find a spell-scroll
    # you can install onto your own PATH.
    chest_scroll = (
        "#!/usr/bin/env bash\n"
        "# Ripple — peek the latest current of any stream.\n"
        "# (A scroll looted from the barred chest.)\n"
        "#\n"
        "# To learn it, copy this scroll into your grimoire and make it yours:\n"
        "#   cp chest \"$AETHER_HOME/bin/ripple\" && chmod +x \"$AETHER_HOME/bin/ripple\"\n"
        "#\n"
        "tail -n \"${2:-3}\" \"${1:-river}\"\n"
    )
    chest = os.path.join(GLADE, "chest")
    if not os.path.exists(chest):
        with open(chest, "w") as f:
            f.write(chest_scroll)
    os.chmod(chest, 0o000)  # barred until you chmod +r it

    # Starting gold.
    write_if_missing(os.path.join(STATE, "gold"), "25\n")

    # Make engine + shop executable.
    for f in ("init_world.py", "river.py", "wraith.py", "familiar.py"):
        p = os.path.join(HERE, f)
        if os.path.exists(p):
            os.chmod(p, 0o755)
    grim = os.path.join(BIN, "grimoire")
    if os.path.exists(grim):
        os.chmod(grim, 0o755)
    play = os.path.join(ROOT, "play")
    if os.path.exists(play):
        os.chmod(play, 0o755)


if __name__ == "__main__":
    main()
