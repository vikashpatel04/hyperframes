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
LEAD=0.4

LINES=$(cat <<'TXT'
0.35|Every big goal starts at zero.
0.25|Become a software engineer.
0.20|Launch your own product.
0.50|Run a half marathon.
0.20|Three years. One hour a day.
0.25|That's over a thousand hours,
0.80|and no one tells you what to do with the first one.
0.25|So you plan on Sunday.
0.25|Miss a day on Wednesday.
0.60|And by Friday, the plan is gone.
0.80|Because knowing what you want isn't the same as knowing how to get there.
0.60|This is Zero to One.
0.30|Tell it your goal, where you're starting, and how much time you really have.
0.20|It builds a realistic roadmap. Phases. Milestones. Tasks.
0.40|You review it, and you approve it.
0.40|Then it turns the roadmap into today: exactly what to do next, and when.
0.20|Miss a day?
0.40|Your plan adapts, instead of piling up.
0.60|And an AI assistant explains, suggests and reorganizes, while every decision stays yours.
0.30|Progress you can see.
0.70|One clear step at a time.
0.50|Zero to One. Big goals. Clear next steps.
2.60|Coming soon. Join the waitlist.
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
