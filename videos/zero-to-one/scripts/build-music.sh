#!/usr/bin/env bash
# Loops the two MusicGen seeds to their act lengths with crossfades, loudness-normalised.
# tense: under the struggle (0 → ~26 s), fading out under the reveal
# bright: from the reveal (24.9 s) to the end (64 s)
set -euo pipefail
cd "$(dirname "$0")/../assets/bgm"
loop() { # seed out length fadein fadeout_start fadeout_len
  ffmpeg -nostdin -loglevel error -y -i "$1" -i "$1" -i "$1" -filter_complex \
    "[0][1]acrossfade=d=1.0:c1=tri:c2=tri[a];[a][2]acrossfade=d=1.0:c1=tri:c2=tri,atrim=0:$3,afade=t=in:d=$4,afade=t=out:st=$5:d=$6,loudnorm=I=-14:TP=-1.5:LRA=7,aresample=44100,pan=stereo|c0=c0|c1=c0" "$2"
}
loop tense-seed.wav tense.wav 26.6 0.3 24.8 1.8
loop bright-seed.wav bright.wav 39.1 1.4 37.4 1.7
