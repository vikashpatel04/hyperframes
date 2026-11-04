#!/usr/bin/env python3
"""Copy the approved glass-crack drawing from the portrait style frame into s1-desk.html.

The style frame (styleframes-portrait/desk.html, state p2a) is the source of truth for the
crack: fracture rays, shard facets and the impact point at the 99+ badge (975, 690).
This script lifts its <g> group and writes it between the <crack:auto> markers of the
composition, so the animated crack is exactly the one that was approved.

Usage: python3 scripts/gen-crack.py
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "styleframes-portrait" / "desk.html"
DST = ROOT / "compositions" / "s1-desk.html"

src = SRC.read_text()
m = re.search(r'<svg id="crack"[^>]*>(<g .*?</g>)</svg>', src, re.S)
if not m:
    sys.exit("crack group not found in style frame")
group = m.group(1)

dst = DST.read_text()
start, end = "<!-- <crack:auto> -->", "<!-- </crack:auto> -->"
a, b = dst.index(start) + len(start), dst.index(end)
dst = dst[:a] + "\n" + group + "\n        " + dst[b:]
DST.write_text(dst)
print(f"crack: {group.count('<path')} paths, {group.count('<polygon')} shards -> {DST.name}")
