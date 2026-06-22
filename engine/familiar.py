#!/usr/bin/env python3
"""The familiar — your diegetic shell. It narrates the world, but every
word you whisper that it doesn't recognise is spoken to the world exactly
as typed: real commands, real tools, real consequences."""
import os
import subprocess
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.environ.get("AETHER_HOME", os.path.dirname(HERE))
os.environ["AETHER_HOME"] = ROOT
BIN = os.path.join(ROOT, "bin")
os.environ["PATH"] = BIN + os.pathsep + os.environ.get("PATH", "")
WORLD = os.path.join(ROOT, "world")
EVENTS = os.path.join(WORLD, ".events")

import progress as P  # noqa: E402  (needs AETHER_HOME set first)


def c(s, code):
    return f"\033[{code}m{s}\033[0m"


DIM = lambda s: c(s, "2")
CY = lambda s: c(s, "36")
MA = lambda s: c(s, "35")
GR = lambda s: c(s, "32")
RE = lambda s: c(s, "31")
YE = lambda s: c(s, "33")
BO = lambda s: c(s, "1")

state = {"cwd": os.path.join(WORLD, "glade"), "attuned": False, "ev_off": 0}

BANNER = MA(BO("""
        ┄┄┄  T H E   A E T H E R  ┄┄┄
   you are a compiler-witch. the world is a machine
   that does not know it is one. your familiar listens.
""")) + DIM("   type 'help' · 'character' shows your sheet · whisper real commands\n")

HELP = """
""" + BO("Your familiar understands:") + """
  look             survey where you stand
  character        your sheet — level, attributes, spellbook, deeds
  attune           toggle code-sight — see processes, streams, links beneath
  enter <passage>  step into a passage; leave / out to step back
  help · quit

""" + BO("Everything else") + """ you whisper is spoken to the world verbatim.
  ls, cat, tail, sed, ln, chmod, ps, kill, grimoire, ...  all real.
"""


# ── regalia (cosmetic packages) ───────────────────────────────────────────
def has_regalia(name):
    return os.path.isdir(os.path.join(P.REGALIA, name))


def theme():
    pal = {"accent": "35", "sigil": "◆"}
    f = os.path.join(P.REGALIA, "embertheme", "palette")
    if os.path.exists(f):
        for line in open(f):
            if "=" in line:
                k, v = line.strip().split("=", 1)
                pal[k] = v
    return pal


def hud_line():
    xp = P.xp_from(P.current_deeds())
    gold = P._read_int(P.GOLD_F, 0)
    mood = P._read(os.path.join(WORLD, "glade", "wraith", "mood")).strip() or "?"
    rel = os.path.relpath(state["cwd"], WORLD)
    sep = DIM(" │ ")
    return (DIM("  ┃") + YE(f" ⚔ {P.bar(xp)} ") + sep +
            GR(f"⟡ {gold}g") + sep + CY(f"◇ {rel}") + sep +
            MA(f"wraith: {mood}"))


# ── world narration ───────────────────────────────────────────────────────
def ev_init():
    try:
        state["ev_off"] = os.path.getsize(EVENTS)
    except OSError:
        state["ev_off"] = 0


def drain_events():
    try:
        size = os.path.getsize(EVENTS)
        if size < state["ev_off"]:
            state["ev_off"] = 0
        if size > state["ev_off"]:
            with open(EVENTS) as f:
                f.seek(state["ev_off"])
                new = f.read()
                state["ev_off"] = f.tell()
            for line in new.splitlines():
                if line.strip():
                    print("  " + MA("~ " + line))
    except OSError:
        pass


def look():
    cwd = state["cwd"]
    lk = os.path.join(cwd, ".look")
    if os.path.exists(lk):
        print()
        print(CY(open(lk).read().rstrip()))
    try:
        entries = sorted(os.listdir(cwd))
    except OSError as e:
        print(RE(str(e)))
        return
    visible = [e for e in entries if not e.startswith(".")]
    if visible:
        print()
        print(DIM("  Here you find:"))
        for e in visible:
            p = os.path.join(cwd, e)
            tag = "passage" if os.path.isdir(p) else "object"
            try:
                mode = oct(os.stat(p).st_mode)[-3:]
            except OSError:
                mode = "???"
            print("   - " + BO(e) + DIM(f"   ({tag}, perms {mode})"))
    if state["attuned"]:
        reveal_substrate()


def reveal_substrate():
    print()
    print(YE("  [code-sight] the machine beneath:"))
    pidf = os.path.join(WORLD, "glade", "wraith", "pid")
    moodf = os.path.join(WORLD, "glade", "wraith", "mood")
    if os.path.exists(pidf):
        pid = open(pidf).read().strip()
        mood = open(moodf).read().strip() if os.path.exists(moodf) else "?"
        print("   - the wraith is a living process " + BO("PID " + pid) +
              DIM(f"   (mood: {mood}) — you could kill it, or quiet it"))
    river = os.path.join(WORLD, "glade", "river")
    if os.path.exists(river):
        print("   - the river is a live stream you can tap: " + DIM(river))
    feed = os.path.join(WORLD, "glade", "wraith", "feed")
    if os.path.exists(feed) or os.path.islink(feed):
        print("   - the wraith drinks from: " + DIM(os.path.realpath(feed)))


# ── character sheet ───────────────────────────────────────────────────────
def character():
    deeds = P.current_deeds()
    xp = P.xp_from(deeds)
    gold = P._read_int(P.GOLD_F, 0)
    spells = P.owned_spells()
    arcana = [s for s in spells if s != "grimoire"]
    reg = P.owned_regalia()

    print()
    print(MA(BO("  ╔══════════════════════════════════════════════╗")))
    print(MA(BO("  ║   ◈  CHARACTER  ·  Compiler-Witch            ║")))
    print(MA(BO("  ╚══════════════════════════════════════════════╝")))
    print("   " + YE(BO(P.bar(xp))))
    print("   " + GR(f"⟡ {gold} gold"))

    print()
    print("   " + BO("Attributes") + DIM("  (your real powers over the machine)"))
    print(f"     Arcana    {len(arcana):>2}   " + DIM("spells you can cast"))
    print(f"     Standing  {len(reg):>2}   " + DIM("regalia worn"))
    print(f"     Deeds     {len(deeds):>2}   " + DIM("marks left on the world"))

    print()
    print("   " + BO("Spellbook") + DIM("  — your tools, and what they do"))
    if spells:
        for s in spells:
            print("     " + CY(f"{s:<11}") + DIM(P.spell_desc(s)))
    else:
        print(DIM("     (empty — loot or buy your first spell)"))

    print()
    print("   " + BO("Regalia"))
    print("     " + (GR("  ".join(reg)) if reg else DIM("(none — visit the grimoire)")))

    print()
    print("   " + BO("Deeds"))
    if deeds:
        for d in deeds:
            print("     " + GR("✦ ") + P.deed_title(d))
    else:
        print(DIM("     (the world is yet unmarked by you)"))
    print()


def character_view():
    """Full-screen living sheet on a real terminal; the inline sheet when
    piped or non-interactive (e.g. the smoke tests)."""
    import sys
    if sys.stdin.isatty() and sys.stdout.isatty():
        try:
            import sheet_tui
            sheet_tui.show()
            return
        except Exception as e:  # noqa: BLE001 — never let the sheet kill the game
            print(RE("(the full sheet faltered: %s — the plain one, then)" % e))
    character()


# ── movement / passthrough ────────────────────────────────────────────────
def prompt():
    pal = theme()
    acc = pal.get("accent", "35")
    sig = pal.get("sigil", "◆")
    rel = os.path.relpath(state["cwd"], WORLD)
    return c(sig + " ", acc) + CY(rel) + c(" ❯ ", acc)


def chdir(dest):
    dest = dest.strip().strip('"').strip("'")
    if not dest:
        dest = WORLD
    target = dest if os.path.isabs(dest) else os.path.normpath(
        os.path.join(state["cwd"], dest))
    if os.path.isdir(target):
        try:
            os.listdir(target)
        except PermissionError:
            print(RE("That way is barred. (permission denied)"))
            return
        state["cwd"] = target
        look()
        hollow = os.path.realpath(os.path.join(WORLD, "glade", "hollow"))
        if os.path.realpath(target) == hollow and P.grant("enter:hollow"):
            print("  " + GR("✦ deed: " + P.deed_title("enter:hollow")))
    else:
        print(RE("No such passage."))


def run(cmd):
    try:
        subprocess.run(["bash", "-c", cmd], cwd=state["cwd"])
    except Exception as e:
        print(RE(str(e)))
    time.sleep(0.15)


def tick(initial=False):
    """Reconcile reality into progression: announce new deeds, lapsed
    world-states, and level-ups."""
    new_acts, gained, lost = P.reconcile()
    if not initial:
        for d in new_acts + gained:
            print("  " + GR("✦ deed: " + P.deed_title(d)))
        for d in lost:
            print("  " + RE("✧ " + P.deed_lost_title(d)))
    delta, titles = P.claim_level_rewards()
    for lv in titles:
        print("  " + YE(BO(
            f"◈ You rise to Level {lv[0]} — {lv[1]}!  (+{20 * lv[0]} gold)")))
    drain_events()


def main():
    ev_init()
    print(BANNER)
    look()
    tick(initial=True)
    while True:
        print()
        if has_regalia("hud"):
            print(hud_line())
        try:
            raw = input(prompt())
        except (EOFError, KeyboardInterrupt):
            print()
            break
        cmd = raw.strip()
        if not cmd:
            tick()
            continue
        low = cmd.lower()
        if low in ("quit", "exit", ":q"):
            break
        elif low in ("help", "?"):
            print(HELP)
        elif low in ("character", "sheet", "stats"):
            character_view()
        elif low in ("char", "me"):
            character()
        elif low in ("look", "l"):
            look()
        elif low in ("attune", "sense"):
            state["attuned"] = not state["attuned"]
            print(YE("You attune to the substrate." if state["attuned"]
                     else "You let the code-sight fade."))
        elif low.startswith("enter ") or low.startswith("go "):
            chdir(cmd.split(None, 1)[1])
        elif low in ("leave", "out", "back"):
            chdir("..")
        elif low == "cd" or low.startswith("cd "):
            chdir(cmd[2:])
        else:
            run(cmd)
        tick()
    print(DIM("\nThe grimoire closes. The river keeps running without you.\n"))


if __name__ == "__main__":
    main()
