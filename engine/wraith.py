#!/usr/bin/env python3
"""The moss-wraith: a real process. It drinks from its feed and its mood
follows what it tastes — but only if the flow is *living*. A stale puddle
(no fresh bytes in 3s) leaves it thirsting and hostile; murk enrages it;
a sustained clear current calms it.

When calm for a few beats it steps aside and the Hollow opens (chmod 755).
Let the flow lapse and it closes the way again. Nothing about this is a
'win condition' — it is just a creature reacting to its environment."""
import os
import signal
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.environ.get("AETHER_HOME", os.path.dirname(HERE))
GLADE = os.path.join(ROOT, "world", "glade")
FEED = os.path.join(GLADE, "wraith", "feed")
MOOD = os.path.join(GLADE, "wraith", "mood")
PIDF = os.path.join(GLADE, "wraith", "pid")
HOLLOW = os.path.join(GLADE, "hollow")
EVENTS = os.path.join(ROOT, "world", ".events")

STALE_AFTER = 3.0  # seconds without fresh bytes -> the flow is dead

_running = True


def _stop(*_):
    global _running
    _running = False


signal.signal(signal.SIGTERM, _stop)
signal.signal(signal.SIGINT, _stop)


def log(msg):
    try:
        with open(EVENTS, "a") as f:
            f.write(msg + "\n")
    except Exception:
        pass


def sense_mood():
    try:
        mtime = os.path.getmtime(FEED)  # follows symlinks to the real source
    except OSError:
        return "thirsting"
    if (time.time() - mtime) > STALE_AFTER:
        return "thirsting"
    try:
        with open(FEED) as f:
            lines = [l for l in f.read().splitlines() if l.strip()]
    except OSError:
        return "thirsting"
    if not lines:
        return "thirsting"
    last = lines[-1].lower()
    if "murk" in last or "rage" in last or "poison" in last:
        return "enraged"
    if "water" in last or "clear" in last or "calm" in last:
        return "calm"
    return "restless"


def main():
    try:
        with open(PIDF, "w") as f:
            f.write(str(os.getpid()) + "\n")
    except Exception:
        pass

    prev = None
    calm_streak = 0
    hollow_open = False

    while _running:
        mood = sense_mood()
        try:
            with open(MOOD, "w") as f:
                f.write(mood + "\n")
        except Exception:
            pass

        if mood != prev:
            flavor = {
                "enraged": "The moss-wraith bares its teeth — it tastes only murk.",
                "thirsting": "The moss-wraith rasps, parched. Its puddle has gone still.",
                "restless": "The moss-wraith shifts, uneasy, unsure of what it drinks.",
                "calm": "The moss-wraith's shoulders ease as clear water reaches it.",
            }.get(mood, "")
            if flavor:
                log(flavor)
            prev = mood

        calm_streak = calm_streak + 1 if mood == "calm" else 0

        if calm_streak >= 3 and not hollow_open:
            try:
                os.chmod(HOLLOW, 0o755)
                hollow_open = True
                log("The wraith rises and steps aside. The Hollow lies open.")
            except Exception:
                pass
        elif mood in ("enraged", "thirsting") and hollow_open:
            try:
                os.chmod(HOLLOW, 0o000)
                hollow_open = False
                log("The wraith hunches back over the path. The Hollow is barred.")
            except Exception:
                pass

        time.sleep(1)


if __name__ == "__main__":
    main()
