#!/usr/bin/env python3
"""The river: a live stream. Every tick it adds fresh clear water and
trims to the last 20 currents. Because it is rewritten each second its
mtime stays fresh — anything drinking from it (directly, or via a symlink,
or a `tail -f` pipe) receives a *living* flow."""
import os
import signal
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.environ.get("AETHER_HOME", os.path.dirname(HERE))
RIVER = os.path.join(ROOT, "world", "glade", "river")

_running = True


def _stop(*_):
    global _running
    _running = False


signal.signal(signal.SIGTERM, _stop)
signal.signal(signal.SIGINT, _stop)

n = 0
while _running:
    n += 1
    try:
        lines = []
        if os.path.exists(RIVER):
            with open(RIVER) as f:
                lines = f.read().splitlines()
        lines.append(f"clear water :: {n}")
        lines = lines[-20:]
        tmp = RIVER + ".tmp"
        with open(tmp, "w") as f:
            f.write("\n".join(lines) + "\n")
        os.replace(tmp, RIVER)
    except Exception:
        pass
    time.sleep(1)
