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
0.30|Rush hour. The queue is out the door.
0.25|You say: one thousand and forty rupees.
0.30|The customer scans your standee QR, and pays one thousand.
0.40|Round off, na?
0.20|With ten people waiting, you can't argue over forty rupees.
0.70|So you give a forty-rupee discount you never offered.
0.30|Once, it's forty.
0.60|But twenty customers a day, rounding off thirty rupees each, is six hundred a day.
0.50|Eighteen thousand rupees, every month.
0.90|Gone. Not stolen. Just rounded off.
0.60|What if the customer couldn't change the amount?
0.40|Meet Counter Pay.
0.30|Press F nine. Type the amount. Press Enter.
0.35|Your billing software never loses focus.
0.20|The customer sees a QR for exactly one thousand and forty.
0.50|Amount fixed.
0.15|Built from your own standee QR, so the money lands in your account.
0.50|Every rupee.
0.70|In English, plus ten Indian languages.
0.30|And you don't need anything new.
0.30|An old phone. An extra monitor. Or a small custom screen.
0.40|Whatever's on your counter, Counter Pay works with it.
0.90|Want a custom device built for your shop? Get in touch.
0.50|Exact amount. Every time.
2.50|Counter Pay. Free and open source.
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
