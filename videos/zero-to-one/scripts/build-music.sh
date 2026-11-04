#!/usr/bin/env bash
# Shapes the MusicGen seed (scripts/gen-music.py) into the bed that runs from the turn
# ("What if your goal came with a Monday?", 33.35 s) to the end of the film (68.0 s):
# two copies crossfaded, gentle fade in, a long resolve out, loudness-normalised.
set -euo pipefail
cd "$(dirname "$0")/../assets/bgm"
LEN=34.65
ffmpeg -nostdin -loglevel error -y -i warm-seed.wav -i warm-seed.wav -filter_complex \
  "[0][1]acrossfade=d=1.5:c1=tri:c2=tri,atrim=0:$LEN,afade=t=in:d=1.6,afade=t=out:st=32.0:d=2.65,loudnorm=I=-14:TP=-1.5:LRA=7,aresample=48000,pan=stereo|c0=c0|c1=c0" \
  warm.wav
ffprobe -v error -show_entries format=duration -of csv=p=0 warm.wav
