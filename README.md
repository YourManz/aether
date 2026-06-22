# The Aether — vertical slice

A text world where the physics *is* the operating system. You play a
compiler-witch who can see the machine beneath reality. Magic is system calls.
You don't learn the tools — you wield them because they're the only verbs that
move matter. The skill transfers because it was never fake.

## Run it

```bash
cd ~/aether
./play
```

You'll be dropped into the **familiar** — your diegetic shell. It narrates the
world, but any real command you whisper is run for real, in the room you're
standing in.

```
look            survey where you stand
character       your sheet — level, attributes, spellbook, deeds  (also: char, me)
attune          toggle code-sight — see processes, streams, links beneath the skin
enter <passage> step through a passage   (leave / out to go back)
help · quit
```

Everything else (`ls`, `cat`, `tail`, `sed`, `ln`, `chmod`, `ps`, `kill`,
`grimoire`, …) is spoken to the world verbatim.

## What's alive in here

- **The river** is a real background process appending fresh bytes to
  `world/glade/river` every second. A *living* stream.
- **The moss-wraith** is a real process. It drinks from `world/glade/wraith/feed`
  and its mood follows what it tastes — but only if the flow is *fresh*. A
  one-shot pour goes stale in 3 seconds and it thirsts again. To quiet it you
  must route it a *sustained* current. When calm, it steps aside and the Hollow
  opens (you'll literally watch the directory's permissions change).
- **A barred chest** (`chmod 000`) holds a spell-scroll. Loot it, then install
  it onto your own PATH — that's how you "learn" a spell.
- **The grimoire** (`grimoire list` / `grimoire buy <name>`) is the shop, in
  the shape of a package manager. It sells **spells** (real scripts onto your
  PATH) and **regalia** (cosmetic packages that re-skin the familiar —
  `hud` draws a status band, `embertheme` recolours your sight). Gold lives in
  `state/gold`.

## Progression (derived from reality, not a hidden counter)

Your standing is *reconciled* from the actual state of the machine — see
`engine/progress.py`. You don't grind XP; you earn **deeds** by genuinely
changing the world, and each deed is worth XP:

- `loot:chest` — the chest is readable (you `chmod`'d it)
- `learn:<spell>` — an executable spell sits on your PATH
- `calm:wraith` / `open:hollow` — the wraith process is calm / the dir is open
- `enter:hollow` — you walked in
- `regalia:<name>` — a package is installed

XP rolls up into **levels** (Apprentice → … → Compiler-Witch); each level-up
pays out gold, which you spend on more spells/regalia — closing the loop. Open
your sheet with `character`. Because deeds are read from real permissions and
real processes, you literally cannot level without doing the thing (and if you
"cheat" with `chmod`, congratulations — you learned `chmod`).

## Design notes (for future me)

- **Real OS as engine.** No simulated computer. Rooms = dirs, objects = files,
  attributes = permissions, creatures = processes, streams = pipes/files,
  portals = symlinks. Emergence comes free from how these already compose.
- **No scripted puzzles / no levels.** The wraith just *reacts*; opening the
  Hollow is a consequence, not a quest flag. Many solutions are valid (symlink
  the feed to the river, `tail -f | …`, even `kill` the wraith — with
  trade-offs). That openness is the point.
- **Next matter to place:** a continuous murk-seep (arms race against the
  river → forces `sed`/`grep` filtering); hardlinked "entangled twin" objects;
  a remote realm reachable over a real socket (`nc`); C-forged keys for
  deep magic; VM snapshots as the save/permadeath system.
```
