#!/usr/bin/env python3
"""Final narration timing, cut from the raw Kokoro takes (assets/voice/raw/).

Lines 1-7 (hook + Act 1, already approved) keep their exact timing. From Act 2 on, each
take is sped up a touch (atempo, pitch kept) and the pauses are tightened, so the film
lands nearer a minute. Word cues move with their line, scaled by the same speed.

Usage: python3 scripts/retime-voice.py  ->  assets/voice/{narration.wav,lines.json,cues.json}
"""
import json
import pathlib
import subprocess

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parent.parent
RAW = ROOT / "assets" / "voice" / "raw"
OUT = ROOT / "assets" / "voice"
SR = 44100
SPEED = 1.05  # from line 8 on
KEEP = 7  # lines 1..KEEP are untouched
# pause after each line (seconds); the last value is the tail under the end card
PAUSE = [0.55, 1.05, 0.35, 1.45, 0.60, 0.45, 0.75,
         0.25, 0.25, 0.45, 0.25, 0.25, 0.55, 0.30, 0.80,
         0.50, 0.50, 0.30, 0.25, 0.20, 0.40, 0.35, 0.65,
         0.40, 0.70, 2.80]


def pcm(path, af=None):
    cmd = ["ffmpeg", "-nostdin", "-v", "error", "-i", str(path)] + (["-af", af] if af else []) + ["-ac", "1", "-ar", str(SR), "-f", "f32le", "-"]
    return np.frombuffer(subprocess.run(cmd, capture_output=True, check=True).stdout, np.float32)


lines = json.loads((RAW / "lines.json").read_text())
cues = json.loads((RAW / "cues.json").read_text())
raw = pcm(RAW / "narration.wav")
assert len(lines) == len(PAUSE) == len(cues)

out = [raw[: int(round(lines[0]["start"] * SR))]]
t = lines[0]["start"]
new_lines, new_cues = [], []
for i, (ln, cu) in enumerate(zip(lines, cues)):
    seg = raw[int(round(ln["start"] * SR)) : int(round(ln["end"] * SR))]
    speed = 1.0 if i < KEEP else SPEED
    if speed != 1.0:
        seg = np.frombuffer(
            subprocess.run(
                ["ffmpeg", "-nostdin", "-v", "error", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-", "-af", f"atempo={speed}", "-f", "f32le", "-"],
                input=seg.tobytes(), capture_output=True, check=True,
            ).stdout,
            np.float32,
        )
    start, end = t, t + len(seg) / SR
    new_lines.append({"id": ln["id"], "start": round(start, 3), "end": round(end, 3), "text": ln["text"]})
    new_cues.append({**cu, "start": round(start, 3), "end": round(end, 3),
                     "words": [{**w, "t": round(start + (w["t"] - ln["start"]) / speed, 3)} for w in cu["words"]]})
    out += [seg, np.zeros(int(round(PAUSE[i] * SR)), np.float32)]
    t = end + PAUSE[i]

audio = np.concatenate(out)
subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-", "-c:a", "pcm_s16le", str(OUT / "narration.wav")],
               input=audio.tobytes(), check=True)
(OUT / "lines.json").write_text(json.dumps(new_lines, indent=1) + "\n")
(OUT / "cues.json").write_text(json.dumps(new_cues, indent=1) + "\n")
print(f"narration {len(audio) / SR:.2f}s")
for l in new_lines:
    print(f"{l['id']:2d} {l['start']:6.2f}-{l['end']:6.2f} {l['text']}")
