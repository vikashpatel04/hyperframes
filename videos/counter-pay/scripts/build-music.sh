#!/usr/bin/env bash
# Loops the two MusicGen seeds to their act lengths with crossfades, loudness-normalised.
# tense: under acts 1–2 (0 → 30.55 s), dropping out on "Gone." (~27.7 s)
# bright: from the turn (30.55 s) to the end (74.5 s)
set -euo pipefail
cd "$(dirname "$0")/../assets/bgm"
loop() { # seed out length fadein fadeout_start fadeout_len
  ffmpeg -nostdin -loglevel error -y -i "$1" -i "$1" -i "$1" -filter_complex \
    "[0][1]acrossfade=d=1.0:c1=tri:c2=tri[a];[a][2]acrossfade=d=1.0:c1=tri:c2=tri,atrim=0:$3,afade=t=in:d=$4,afade=t=out:st=$5:d=$6,loudnorm=I=-14:TP=-1.5:LRA=7,aresample=44100,pan=stereo|c0=c0|c1=c0" "$2"
}
loop tense-seed.wav tense.wav 31.0 0.4 27.4 1.4
loop bright-seed.wav bright.wav 44.0 1.6 42.4 1.6
