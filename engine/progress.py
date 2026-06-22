#!/usr/bin/env python3
"""Progression, derived from reality.

There is no hidden XP counter you can poke. Your standing is *reconciled*
from the actual state of the machine: spells you can really cast (executable
files on your PATH), marks you've really left on the world (a readable chest,
a calmed process, an opened directory). To gain a level you must genuinely
change the world — and if you did it by "cheating" with chmod, well, you
learned chmod. The deed is real either way.
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.environ.get("AETHER_HOME", os.path.dirname(HERE))
STATE = os.path.join(ROOT, "state")
BIN = os.path.join(ROOT, "bin")
WORLD = os.path.join(ROOT, "world")
GLADE = os.path.join(WORLD, "glade")
REGALIA = os.path.join(STATE, "regalia")
DEEDS_F = os.path.join(STATE, "deeds")
GOLD_F = os.path.join(STATE, "gold")
CLAIM_F = os.path.join(STATE, "level_claimed")

# (level, title, xp threshold)
LEVELS = [
    (1, "Apprentice", 0),
    (2, "Cantor", 40),
    (3, "Adept", 90),
    (4, "Conjurer", 160),
    (5, "Streamwarden", 250),
    (6, "Compiler-Witch", 360),
]

DEED_TITLES = {
    "loot:chest": "Unbound the barred chest",
    "calm:wraith": "Quieted the moss-wraith",
    "open:hollow": "Opened the Hollow",
    "enter:hollow": "Walked into the Hollow",
}


def _read(p, default=""):
    try:
        with open(p) as f:
            return f.read()
    except OSError:
        return default


def _read_int(p, default=0):
    try:
        return int((_read(p, "").strip() or default))
    except (ValueError, TypeError):
        return default


def load_deeds():
    return [d for d in _read(DEEDS_F).splitlines() if d.strip()]


def save_deeds(deeds):
    os.makedirs(STATE, exist_ok=True)
    with open(DEEDS_F, "w") as f:
        f.write(("\n".join(deeds) + "\n") if deeds else "")


def deed_value(d):
    if d == "loot:chest":
        return 15
    if d in ("calm:wraith", "open:hollow"):
        return 25
    if d == "enter:hollow":
        return 20
    if d.startswith("learn:"):
        return 10
    if d.startswith("regalia:"):
        return 5
    return 5


def deed_title(d):
    if d in DEED_TITLES:
        return DEED_TITLES[d]
    if d.startswith("learn:"):
        return "Learned the spell '%s'" % d.split(":", 1)[1]
    if d.startswith("regalia:"):
        return "Donned the %s" % d.split(":", 1)[1]
    return d


def xp_from(deeds):
    return sum(deed_value(d) for d in deeds)


def owned_spells():
    out = []
    if os.path.isdir(BIN):
        for n in sorted(os.listdir(BIN)):
            p = os.path.join(BIN, n)
            if os.path.isfile(p) and os.access(p, os.X_OK):
                out.append(n)
    return out


def spell_desc(name):
    """A spell describes itself: the first real comment line in its source."""
    p = os.path.join(BIN, name)
    try:
        with open(p) as f:
            for line in f:
                s = line.strip()
                if s.startswith("#!") or s == "":
                    continue
                if s.startswith("#"):
                    s = s.lstrip("#").strip().strip("= ").strip()
                    if s:
                        return s
                else:
                    break
    except OSError:
        pass
    return "an unknown working"


def owned_regalia():
    out = []
    if os.path.isdir(REGALIA):
        for n in sorted(os.listdir(REGALIA)):
            if os.path.isdir(os.path.join(REGALIA, n)):
                out.append(n)
    return out


def detect_deeds():
    """What the current state of the machine proves you have done."""
    found = set()
    chest = os.path.join(GLADE, "chest")
    try:
        if os.path.exists(chest) and (os.stat(chest).st_mode & 0o400):
            found.add("loot:chest")
    except OSError:
        pass
    if _read(os.path.join(GLADE, "wraith", "mood")).strip() == "calm":
        found.add("calm:wraith")
    hollow = os.path.join(GLADE, "hollow")
    try:
        if os.path.isdir(hollow) and (os.stat(hollow).st_mode & 0o100):
            found.add("open:hollow")
    except OSError:
        pass
    for s in owned_spells():
        if s == "grimoire":
            continue
        found.add("learn:" + s)
    for r in owned_regalia():
        found.add("regalia:" + r)
    return found


def grant(deed):
    """Record a deed the filesystem can't prove on its own (e.g. entering a
    room). Returns True if it was newly granted."""
    have = load_deeds()
    if deed in have:
        return False
    have.append(deed)
    save_deeds(have)
    return True


def reconcile():
    """Grant any newly-earned deeds. Returns the list of new deed keys."""
    have = load_deeds()
    haveset = set(have)
    newly = sorted(d for d in detect_deeds() if d not in haveset)
    if newly:
        have.extend(newly)
        save_deeds(have)
    return newly


def level_for(xp):
    cur = LEVELS[0]
    for lv in LEVELS:
        if xp >= lv[2]:
            cur = lv
        else:
            break
    return cur


def next_level(xp):
    for lv in LEVELS:
        if xp < lv[2]:
            return lv
    return None


def bar(xp, width=12):
    cur = level_for(xp)
    nxt = next_level(xp)
    if not nxt:
        return "Lv%d %s  (mastery)" % (cur[0], cur[1])
    span = nxt[2] - cur[2]
    into = xp - cur[2]
    filled = int(round(width * into / span)) if span else width
    filled = max(0, min(width, filled))
    return "Lv%d %s  [%s%s] %d/%d xp" % (
        cur[0], cur[1], "█" * filled, "░" * (width - filled),
        into, span)


def claim_level_rewards():
    """Award gold for each new level since last claim.
    Returns (gold_delta, [new level tuples])."""
    xp = xp_from(load_deeds())
    cur = level_for(xp)
    claimed = _read_int(CLAIM_F, 1)
    if cur[0] <= claimed:
        return 0, []
    delta = 0
    titles = []
    for lv in LEVELS:
        if claimed < lv[0] <= cur[0]:
            delta += 20 * lv[0]
            titles.append(lv)
    gold = _read_int(GOLD_F, 0) + delta
    os.makedirs(STATE, exist_ok=True)
    with open(GOLD_F, "w") as f:
        f.write(str(gold) + "\n")
    with open(CLAIM_F, "w") as f:
        f.write(str(cur[0]) + "\n")
    return delta, titles
