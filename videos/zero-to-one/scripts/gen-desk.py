#!/usr/bin/env python3
"""Copies the desk (room, sun, monitor, lock screen, Day counter, the note, the plant) from
compositions/s1-desk.html into the other desk scenes, so the room is the same room.

Each target holds two marker pairs that this script fills:
  /* <desk-css:auto> */ ... /* </desk-css:auto> */     (styles)
  <!-- <desk:auto> --> ... <!-- </desk:auto> -->         (markup)
Ids and classes are re-prefixed (d- -> the target's prefix) so scenes never collide.

Usage: python3 scripts/gen-desk.py
"""
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = (ROOT / "compositions" / "s1-desk.html").read_text()
TARGETS = {"s3-turn.html": "e", "s6-payoff.html": "g"}


def cut(text, start, end, inclusive_end=False):
    a = text.index(start)
    b = text.index(end, a) + (len(end) if inclusive_end else 0)
    return text[a:b]


style = cut(SRC, "<style>\n", "  </style>")[len("<style>\n") :]
# keep the room and the caption system; drop the hook's notifications, crack, marks and memes
css = style[: style.index("    .d-ntf {")] + style[style.index("    /* ---- act 1 captions") :]

filters = cut(SRC, '    <svg width="0" height="0"', "    </svg>\n", inclusive_end=True)
room = cut(SRC, '    <div id="d-cam"', "        <!-- the avalanche -->")
note2 = cut(room, '        <div id="d-note2"', '        <svg id="d-plant"')
room = room.replace(note2, "")
grain = cut(SRC, '    <svg id="d-grain"', '<div id="d-vig" class="d-abs"></div>', inclusive_end=True)
markup = filters + room + "      </div>\n    </div>\n" + grain + "\n"

PREFIX = re.compile(r"(?<![A-Za-z0-9_])d-(?=[a-z0-9])")

for name, p in TARGETS.items():
    path = ROOT / "compositions" / name
    text = path.read_text()
    for (a, b), body in [
        (("/* <desk-css:auto> */", "/* </desk-css:auto> */"), PREFIX.sub(f"{p}-", css)),
        (("<!-- <desk:auto> -->", "<!-- </desk:auto> -->"), PREFIX.sub(f"{p}-", markup)),
    ]:
        i, j = text.index(a) + len(a), text.index(b)
        text = text[:i] + "\n" + body + "    " + text[j:]
    path.write_text(text)
    print(f"{name}: desk copied with prefix {p}-")
