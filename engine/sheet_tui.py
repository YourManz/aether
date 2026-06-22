#!/usr/bin/env python3
"""The character sheet, as a full-screen living portrait.

A curses view reconciled from the same real machine state as everything
else: it reads progress.py and redraws once a second, so the wraith
calming or the Hollow opening shows here while you watch. Press q to step
back into the familiar. Pure presentation — no game state lives here.
"""
import curses
import locale
import os

import progress as P

ART = os.path.join(os.path.dirname(os.path.abspath(__file__)), "art")


def portrait(level):
    """The ASCII portrait for a level. One is shipped; the lookup is wired
    so later levels just drop a <name>.txt beside apprentice.txt."""
    name = {1: "apprentice"}.get(level, "apprentice") + ".txt"
    try:
        with open(os.path.join(ART, name)) as f:
            return f.read().rstrip("\n").splitlines()
    except OSError:
        return ["", "   ( the mirror is dark )", ""]


def _wraith_mood():
    return P._read(os.path.join(P.WORLD, "glade", "wraith", "mood")).strip() or "?"


def run(scr):
    curses.curs_set(0)
    scr.timeout(1000)  # wake to redraw / re-read the world every second
    MA = YE = GR = CY = RE = 0
    if curses.has_colors():
        curses.start_color()
        try:
            curses.use_default_colors()
            bg = -1
        except curses.error:
            bg = curses.COLOR_BLACK
        curses.init_pair(1, curses.COLOR_MAGENTA, bg)
        curses.init_pair(2, curses.COLOR_YELLOW, bg)
        curses.init_pair(3, curses.COLOR_GREEN, bg)
        curses.init_pair(4, curses.COLOR_CYAN, bg)
        curses.init_pair(5, curses.COLOR_RED, bg)
        MA, YE, GR, CY, RE = (curses.color_pair(i) for i in range(1, 6))

    while True:
        deeds = P.current_deeds()
        xp = P.xp_from(deeds)
        lvl = P.level_for(xp)
        spells = [s for s in P.owned_spells() if s != "grimoire"]
        reg = P.owned_regalia()
        gold = P._read_int(P.GOLD_F, 0)
        mood = _wraith_mood()

        scr.erase()
        h, w = scr.getmaxyx()

        def put(y, x, s, attr=0):
            if 0 <= y < h and 0 <= x < w - 1:
                try:
                    scr.addnstr(y, x, s, w - x - 1, attr)
                except curses.error:
                    pass

        # Header.
        put(0, 2, "◈ CHARACTER", curses.A_BOLD | MA)
        put(0, 16, "· the Compiler-Witch's path", curses.A_DIM)
        put(1, 2, "─" * (w - 4), curses.A_DIM)

        # Portrait — left column.
        art = portrait(lvl[0])
        top = 3
        for i, line in enumerate(art):
            put(top + i, 3, line, MA)
        col = max(28, 3 + max((len(l) for l in art), default=18) + 4)

        # Stats — right column.
        y = top
        put(y, col, P.bar(xp), curses.A_BOLD | YE); y += 1
        put(y, col, "⟡ %d gold" % gold, GR); y += 2

        put(y, col, "ATTRIBUTES", curses.A_BOLD); y += 1
        put(y, col, "  Arcana    %2d  spells you can cast" % len(spells)); y += 1
        put(y, col, "  Standing  %2d  regalia worn" % len(reg)); y += 1
        put(y, col, "  Deeds     %2d  marks on the world" % len(deeds)); y += 2

        put(y, col, "SPELLBOOK", curses.A_BOLD); y += 1
        if spells:
            for s in spells:
                put(y, col, "  %-11s" % s, CY)
                put(y, col + 13, P.spell_desc(s), curses.A_DIM); y += 1
        else:
            put(y, col, "  (empty — loot or buy a spell)", curses.A_DIM); y += 1
        y += 1

        put(y, col, "REGALIA", curses.A_BOLD); y += 1
        put(y, col, "  " + ("  ".join(reg) if reg else "(none)"),
            GR if reg else curses.A_DIM); y += 2

        put(y, col, "DEEDS", curses.A_BOLD); y += 1
        if deeds:
            for d in deeds:
                put(y, col, "  ✦ " + P.deed_title(d), GR); y += 1
        else:
            put(y, col, "  (the world is yet unmarked)", curses.A_DIM); y += 1

        # Footer — the live world-state and the way out.
        put(h - 2, 2, "─" * (w - 4), curses.A_DIM)
        put(h - 1, 2, "wraith: ", curses.A_DIM)
        put(h - 1, 10, mood, GR if mood == "calm" else RE)
        put(h - 1, max(20, w - 22), "q  return to world", curses.A_DIM)

        scr.refresh()
        if scr.getch() in (ord("q"), ord("Q"), 27):
            return


def show():
    """Run the full-screen sheet, restoring the terminal afterwards."""
    locale.setlocale(locale.LC_ALL, "")
    curses.wrapper(run)


if __name__ == "__main__":
    show()
