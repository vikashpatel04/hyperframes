#!/usr/bin/env bash
# Builds assets/voice/narration.wav from per-line Kokoro takes joined with
# authored pauses, then writes word timings to assets/voice/transcript.json.
# Each line: <pause-after-seconds>|<text>
set -euo pipefail
cd "$(dirname "$0")/.."
CLI="${HYPERFRAMES_CLI:-npx hyperframes}"
VOICE="${VOICE:-af_heart}"
OUT=assets/voice
TMP=$(mktemp -d)
LEAD="${LEAD:-2.7}"

LINES=$(cat <<'TXT'
0.55|That's Riya's Monday morning.
1.05|Every Monday morning.
0.35|Underneath all of it, one note.
1.45|Three years old.
0.60|It says: become a software engineer.
0.45|And every morning, the same question.
0.95|What do I actually do today?
0.25|Forty-seven tabs.
0.25|Three complete roadmaps.
0.60|One course, twelve percent done.
0.25|New plan on Sunday.
0.25|Missed Wednesday.
0.70|Start over Friday.
0.30|The goal was never too big.
0.90|Nobody turned it into today.
0.60|What if your goal came with a Monday?
0.60|This is Zero to One.
0.30|She tells it the goal, where she's starting, and the hour a day she really has.
0.30|It turns three years into phases, milestones, and tasks.
0.20|Then into today.
0.50|Monday, nine A.M. Twenty-five minutes. JavaScript basics.
0.40|Miss a day? The plan moves. Nothing piles up.
0.80|Only thirty minutes? Ask. It reshapes today. She decides.
0.50|Riya's note never changed.
0.80|Her Monday did.
2.40|Zero to One. Big goals. Clear next steps. Join the waitlist.
TXT
)

ffmpeg -loglevel error -f lavfi -i anullsrc=r=24000:cl=mono -t "$LEAD" -c:a pcm_s16le "$TMP/lead.wav"
echo "file '$TMP/lead.wav'" > "$TMP/list.txt"
T=$LEAD
echo "[" > "$TMP/lines.json"
i=0
while IFS='|' read -r pause text; do
  i=$((i+1)); n=$(printf %02d "$i")
  $CLI tts "$text" --voice "$VOICE" -o "$TMP/l$n.wav" </dev/null >/dev/null 2>&1
  ffmpeg -nostdin -loglevel error -i "$TMP/l$n.wav" -ar 24000 -ac 1 -c:a pcm_s16le "$TMP/n$n.wav"
  ffmpeg -nostdin -loglevel error -f lavfi -i anullsrc=r=24000:cl=mono -t "$pause" -c:a pcm_s16le "$TMP/p$n.wav"
  printf "file '%s'\nfile '%s'\n" "$TMP/n$n.wav" "$TMP/p$n.wav" >> "$TMP/list.txt"
  D=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$TMP/n$n.wav")
  E=$(python3 -c "print(round($T+$D,3))")
  [ "$i" -gt 1 ] && echo "," >> "$TMP/lines.json"
  python3 -c "import json,sys;print(json.dumps({'id':$i,'start':round($T,3),'end':$E,'text':sys.argv[1]}),end='')" "$text" >> "$TMP/lines.json"
  T=$(python3 -c "print($E+$pause)")
done <<< "$LINES"

ffmpeg -loglevel error -y -f concat -safe 0 -i "$TMP/list.txt" -ar 44100 "$OUT/narration.wav"
echo "]" >> "$TMP/lines.json"
cp "$TMP/lines.json" "$OUT/lines.json"
$CLI transcribe "$OUT/narration.wav" --model small.en --json >/dev/null 2>&1
rm -rf "$TMP"
ffprobe -v error -show_entries format=duration -of csv=p=0 "$OUT/narration.wav"
