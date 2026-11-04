"""Re-anchors Whisper word times to the exact line starts in lines.json.

Whisper drifts on joined takes; each line's start/end are known exactly (we built the file),
so its words are shifted to start on the line and scaled to end on it. Writes assets/voice/cues.json.
"""
import json, re

lines = json.load(open("assets/voice/lines.json"))
d = json.load(open("assets/voice/transcript.json"))
words = d if isinstance(d, list) else d["words"]
norm = lambda s: re.sub(r"[^a-z0-9]", "", s.lower())
# assign each Whisper word to a line by character position in the normalised script
bounds, pos = [], 0
for ln in lines:
    pos += len(norm(ln["text"]))
    bounds.append(pos)
out, cpos, per_line = [], 0, [[] for _ in lines]
for w in words:
    li = next((i for i, b in enumerate(bounds) if cpos < b), len(lines) - 1)
    per_line[li].append(w)
    cpos += len(norm(w["text"]))
for ln, ws in zip(lines, per_line):
    if not ws:
        continue
    a0, a1 = ws[0]["start"], max(ws[-1]["end"], ws[0]["start"] + 0.01)
    k = (ln["end"] - ln["start"]) / (a1 - a0)
    out.append({
        "line": ln["id"], "text": ln["text"], "start": ln["start"], "end": ln["end"],
        "words": [{"w": w["text"], "t": round(ln["start"] + (w["start"] - a0) * k, 2)} for w in ws],
    })
json.dump(out, open("assets/voice/cues.json", "w"), indent=1, ensure_ascii=False)
for c in out:
    print(f"{c['line']:2} " + " ".join(f"{w['w']}@{w['t']}" for w in c["words"]))
