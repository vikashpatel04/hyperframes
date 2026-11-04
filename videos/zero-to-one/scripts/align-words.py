"""Word cues per line: each line's take is cut out of narration.wav at its exact start/end
(lines.json) and transcribed on its own, so word times can never leak across lines.
Writes assets/voice/cues.json. Run from the project root; needs the hyperframes CLI."""
import json
import os
import subprocess
import sys
import tempfile

CLI = os.environ.get("HYPERFRAMES_CLI", "npx hyperframes").split()
V = "assets/voice/raw" if "--raw" in sys.argv else "assets/voice"
lines = json.load(open(f"{V}/lines.json"))
out = []
with tempfile.TemporaryDirectory() as tmp:
    for ln in lines:
        clip = os.path.join(tmp, f"l{ln['id']:02d}.wav")
        subprocess.run(["ffmpeg", "-nostdin", "-loglevel", "error", "-y", "-ss", str(max(0, ln["start"] - 0.05)),
                        "-to", str(ln["end"] + 0.1), "-i", f"{V}/narration.wav", clip], check=True)
        subprocess.run(CLI + ["transcribe", clip, "--model", "small.en", "--json"], cwd=tmp,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        data = json.load(open(os.path.join(tmp, "transcript.json")))
        words = data if isinstance(data, list) else data["words"]
        base = max(0, ln["start"] - 0.05)
        out.append({"line": ln["id"], "text": ln["text"], "start": ln["start"], "end": ln["end"],
                    "words": [{"w": w["text"], "t": round(base + w["start"], 2)} for w in words]})
        print(f"{ln['id']:2} " + " ".join(f"{w['text']}@{round(base + w['start'], 2)}" for w in words), flush=True)
json.dump(out, open(f"{V}/cues.json", "w"), indent=1, ensure_ascii=False)
