#!/usr/bin/env python3
"""Sound for the whole film (0 - 68 s): effects, room tone and the music bed in one stereo stem.

Every hit is placed one frame after the picture it belongs to (times come straight from the
compositions; film seconds). Recorded sources live in assets/sfx/src (see CREDITS.md); the
clock, pen, paper, marker, projector, crumple, drone, flaps and room tone are synthesised here
with a seeded generator, so the stem rebuilds bit-for-bit. The music (assets/bgm/warm.wav,
scripts/build-music.sh) enters at the turn and sits under the voice.

Usage: python3 scripts/build-sfx.py   ->  assets/sfx/film.wav
"""
import pathlib
import subprocess

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "assets" / "sfx" / "src"
OUT = ROOT / "assets" / "sfx" / "film.wav"
BGM = ROOT / "assets" / "bgm" / "warm.wav"

SR = 48000
DUR = 68.0
F = 1 / 30
rng = np.random.default_rng(1095)


# ------------------------------------------------------------------ plumbing
def decode(name):
    b = subprocess.run(
        ["ffmpeg", "-nostdin", "-v", "error", "-i", str(SRC / name), "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
        capture_output=True,
        check=True,
    ).stdout
    return np.frombuffer(b, np.float32).copy()


def filt(x, af):
    b = subprocess.run(
        ["ffmpeg", "-nostdin", "-v", "error", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-", "-af", af, "-f", "f32le", "-"],
        input=np.asarray(x, np.float32).tobytes(),
        capture_output=True,
        check=True,
    ).stdout
    return np.frombuffer(b, np.float32).copy()


def db(g):
    return 10 ** (g / 20)


def tt(sec):
    return np.arange(int(round(sec * SR))) / SR


def noise(sec):
    return rng.standard_normal(int(round(sec * SR))).astype(np.float32)


def norm(x):
    return x / (np.max(np.abs(x)) + 1e-9)


def pitch(x, semis):
    if abs(semis) < 1e-3:
        return x
    return filt(x, f"asetrate={int(SR * 2 ** (semis / 12))},aresample={SR}")


def trim_to_onset(x, thresh=0.02):
    i = int(np.argmax(np.abs(x) > thresh * np.max(np.abs(x))))
    return x[max(0, i - 48) :]


def shape(n, attack, release):
    """attack / release envelope (seconds) over n samples."""
    e = np.ones(n, np.float32)
    a, r = max(1, int(attack * SR)), max(1, int(release * SR))
    e[:a] *= np.linspace(0, 1, a)
    e[-r:] *= np.linspace(1, 0, r)
    return e


def bus():
    return np.zeros((int(round((DUR + 3) * SR)), 2), np.float32)


def place(buf, x, t, gain_db, pan=0.0, at_peak=False):
    """add mono x at time t (or with its loudest sample at t), constant-power pan."""
    if at_peak:
        t -= int(np.argmax(np.abs(x))) / SR
    i = int(round(t * SR))
    if i < 0:
        x, i = x[-i:], 0
    n = min(len(x), len(buf) - i)
    if n <= 0:
        return
    a = (pan + 1) * np.pi / 4
    g = db(gain_db) * np.sqrt(2)
    buf[i : i + n, 0] += x[:n] * g * np.cos(a)
    buf[i : i + n, 1] += x[:n] * g * np.sin(a)


def hit(buf, x, t_picture, gain_db, pan=0.0):
    place(buf, x, t_picture + F, gain_db, pan, at_peak=True)


# ------------------------------------------------------------------ synthesised sounds
def tick(tone=1.0, body=1.0):
    t = tt(0.06)
    x = (
        0.6 * np.sin(2 * np.pi * 3200 * tone * t) * np.exp(-t / 0.004)
        + 0.35 * np.sin(2 * np.pi * 5100 * tone * t) * np.exp(-t / 0.0025)
        + 0.5 * body * np.sin(2 * np.pi * 950 * tone * t) * np.exp(-t / 0.009)
    )
    x[:96] += noise(96 / SR) * np.linspace(1, 0, 96) * 0.8
    return norm(filt(x, "highpass=f=300"))


def thump(f0=75, tau=0.07, sec=0.3):
    t = tt(sec)
    f = f0 * (1 + 0.7 * np.exp(-t / 0.015))
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / tau)
    x[:120] += noise(120 / SR) * np.linspace(0.5, 0, 120)
    return norm(x)


def clunk():
    """the odometer's mechanical landing: a click on a dropping wooden body."""
    t = tt(0.4)
    f = 150 * (1 - 0.35 * (1 - np.exp(-t / 0.05)))
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.075)
    snap = filt(noise(0.4) * np.exp(-t / 0.012), "lowpass=f=1800")
    x = body + 0.8 * norm(snap)
    k = tick(0.7, 1.4)
    x[: len(k)] += 0.5 * k
    return norm(x)


def slap():
    t = tt(0.35)
    crack = filt(noise(0.35) * np.exp(-t / 0.018), "lowpass=f=3500,highpass=f=200")
    return norm(norm(crack) + 0.7 * thump(120, 0.045, 0.35))


def grain(sec, rate_hz=40):
    """slow random roughness, 0.35..1"""
    g = np.abs(filt(noise(sec), f"lowpass=f={rate_hz},lowpass=f={rate_hz}"))
    return 0.35 + 0.65 * norm(g)


def pen_stroke(sec, env="out", centre=3300):
    n = int(round(sec * SR))
    x = filt(noise(sec), f"bandpass=f={centre}:width_type=q:w=0.9,highpass=f=1400")
    p = np.linspace(0, 1, n)
    e = {"out": (1 - p) ** 0.7, "bell": np.sin(np.pi * p) ** 0.8, "in": p**0.6, "flat": np.ones(n)}[env]
    return norm(x * grain(sec) * e * shape(n, 0.008, 0.02))


def writing(sec):
    """handwriting: a run of short strokes and lifts."""
    out = np.zeros(int(round(sec * SR)) + SR, np.float32)
    t = 0.0
    while t < sec - 0.05:
        d = float(rng.uniform(0.05, 0.14))
        s = pen_stroke(d, env="bell", centre=float(rng.uniform(2600, 4300))) * float(rng.uniform(0.6, 1.0))
        i = int(t * SR)
        out[i : i + len(s)] += s
        t += d + float(rng.uniform(0.012, 0.045))
    return norm(out[: int(round(sec * SR))])


def marker(sec, env="bell"):
    """felt marker squeaking over glass."""
    n = int(round(sec * SR))
    t = tt(sec)
    sq = np.sin(2 * np.pi * np.cumsum(1950 + 90 * np.sin(2 * np.pi * 9 * t)) / SR)
    fric = filt(noise(sec), "bandpass=f=2300:width_type=q:w=4")
    p = np.linspace(0, 1, n)
    e = {"bell": np.sin(np.pi * p) ** 0.6, "in": p**0.5, "flat": np.ones(n)}[env]
    return norm((0.35 * sq + norm(fric)) * grain(sec, 25) * e * shape(n, 0.015, 0.03))


def paper_slide(sec):
    n = int(round(sec * SR))
    x = filt(noise(sec), "bandpass=f=2400:width_type=q:w=0.8,lowpass=f=6000")
    p = np.linspace(0, 1, n)
    return norm(x * grain(sec, 30) * (p**1.6) * shape(n, 0.01, 0.06))


def page_flip():
    out = np.zeros(int(0.3 * SR), np.float32)
    for k, (t0, g) in enumerate([(0, 1), (0.045, 0.8), (0.09, 0.9), (0.14, 0.6)]):
        b = filt(noise(0.06) * np.exp(-tt(0.06) / 0.012), "highpass=f=700,lowpass=f=7000") * g
        i = int(t0 * SR)
        out[i : i + len(b)] += b
    return norm(out)


def projector(sec):
    """the freeze-frame's film whirr: a 24 Hz shutter flutter over a soft motor."""
    n = int(round(sec * SR))
    t = tt(sec)
    flutter = 0.6 + 0.4 * np.clip(np.sin(2 * np.pi * 24 * t) * 3, -1, 1)
    hiss = filt(noise(sec), "bandpass=f=1100:width_type=q:w=1.5") * flutter
    motor = filt(noise(sec), "lowpass=f=160")
    return norm(norm(hiss) + 0.5 * norm(motor)) * shape(n, 0.15, 0.25)


def room(sec):
    n = int(round(sec * SR))
    lo = [filt(noise(sec), "highpass=f=40,lowpass=f=650,lowpass=f=650") for _ in range(2)]
    air = [filt(noise(sec), "highpass=f=2500,lowpass=f=7000") for _ in range(2)]
    st = np.stack([norm(lo[c]) + 0.08 * norm(air[c]) for c in range(2)], 1)
    rms = np.sqrt(np.mean(st**2))
    return st / rms * shape(n, 0.0, 0.3)[:, None]


def tape_stop(x, t0, length):
    """from t0, slow the tape to a halt over `length` s (speed and pitch fall together)."""
    out = x.copy()
    i0, m = int(t0 * SR), int(length * SR)
    u = np.arange(m) / m
    pos = i0 + np.cumsum((1 - u) ** 1.7)
    fade = np.minimum(1, (1 - u) / 0.3)
    for c in range(2):
        out[i0 : i0 + m, c] = np.interp(pos, np.arange(len(x)), x[:, c]) * fade
    out[i0 + m :] = 0
    return out


# ------------------------------------------------------------------ sources
s_notif = trim_to_onset(decode("notification.mp3"))
s_ping = trim_to_onset(decode("ping.mp3"))
s_pop = trim_to_onset(decode("pop.mp3"))
s_riser = decode("riser.mp3")
s_bass = decode("impact-bass-1.mp3")
s_click = trim_to_onset(decode("click.mp3"))
s_soft = trim_to_onset(decode("click-soft.mp3"))
s_whoosh = decode("whoosh.mp3")
s_wshort = decode("whoosh-short.mp3")
s_glass = decode("glass-breaking-gravity-sound.wav")

mix = bus()

# ------------------------------------------------------------------ HOOK: the avalanche (0 - 2.0), then a tape-stop on it
aval = bus()
place(aval, s_notif, 0.0, -5, 0.15)  # frame 0 already rings
lands = [0.18, 0.6, 0.86, 1.09, 1.29, 1.46, 1.61, 1.74]
ghosts = [1.86, 1.95, 2.03, 2.1, 2.16, 2.22, 2.28, 2.33]  # the pile keeps coming; the tape-stop eats these
pans = [0.2, -0.25, 0.3, -0.3, 0.25, -0.15, 0.35, -0.3]
for k, t in enumerate(lands + ghosts):
    hit(aval, pitch(s_ping, 0.8 * k), t, -10 + min(k, 10) * 0.5, pans[k % 8])
    if k < len(lands):
        hit(aval, thump(72 + 4 * k), t, -12, pans[k])
for k, t in enumerate([0.05, 0.45, 0.72, 0.95, 1.14, 1.3, 1.46, 1.62, 1.8]):
    hit(aval, pitch(s_pop, k * 1.0), t, -16, 0.45)
# the riser crests on the crack (its own crest is at 3.25 s into the file)
riser = s_riser * shape(len(s_riser), 0.0, 0.05)
place(aval, riser, 2.0 - 3.25, -9)
mix += tape_stop(aval, 2.0 + F, 0.42)

# ------------------------------------------------------------------ THE CRACK (2.0)
C = 2.0
hit(mix, s_glass, C, -3, 0.35)
snap = filt(noise(0.05) * np.exp(-tt(0.05) / 0.006), "highpass=f=2500")
hit(mix, norm(snap), C, -7, 0.35)
bass = s_bass.copy()
pk = int(np.argmax(np.abs(bass)))
bass[pk:] *= np.exp(-np.arange(len(bass) - pk) / SR / 0.4)
hit(mix, bass, C, -11)

# ------------------------------------------------------------------ THE FREEZE-FRAME (2.3 - 6.0)
hit(mix, s_click, 2.3, -9, 0.1)  # shutter: ka-
hit(mix, pitch(s_click, -5), 2.35, -12, 0.1)  # -chick
place(mix, projector(6.02 - 2.36), 2.36, -30)
place(mix, marker(0.45, "bell"), 2.42, -17, -0.35)  # circle
place(mix, marker(0.24, "in"), 2.88, -18, -0.2)  # arrow
place(mix, marker(0.1, "flat"), 3.12, -20, -0.25)  # head

# the clock: a tick every second from the freeze on (loud in the freeze, then under the voice)
clock = [2.6, 3.6, 4.6, 5.6, 6.6, 7.6, 8.6] + [11.6 + k for k in range(8)]
for k, t in enumerate(clock):
    hit(mix, tick(1.0 if k % 2 == 0 else 0.82), t, -18 if t < 6 else -25, -0.1)

# ------------------------------------------------------------------ RELEASE (6.02): colour returns, the pile falls away
R = 6.02
place(mix, s_whoosh, R - 0.02, -14)
hit(mix, pitch(s_pop, -4), R + 0.05, -21, 0.45)
for i in range(8):
    place(mix, paper_slide(0.5), R + 0.12 + i * 0.045, -23, pans[7 - i])

# ------------------------------------------------------------------ ACT 1: one note
hit(mix, filt(s_soft, "lowpass=f=2500"), 8.12, -14, -0.3)  # focus ring detent
hit(mix, filt(pitch(s_soft, -3), "lowpass=f=2500"), 8.155, -18, -0.3)

# Three years old: the counter, the time-lapse
hit(mix, pitch(s_pop, -2), 9.12, -20, -0.1)
V0, V1, T0, DUR_O = 1, 1095, 9.25, 1.65


def t_of(v):
    f = (v - V0) / (V1 - V0)
    p = np.sqrt(f / 2) if f < 0.5 else 1 - np.sqrt((1 - f) / 2)
    return T0 + p * DUR_O


for v in range(10, V1 + 1, 10):  # every tens wheel step: a fine mechanical tick
    heavy = v % 100 == 0
    hit(mix, tick(1.35 if not heavy else 0.9, 0.6 if not heavy else 1.3), t_of(v), -29 if not heavy else -21, 0.05 if v % 20 else -0.05)
# a soft whirr that rides the wheel's speed
n = int(DUR_O * SR)
p = np.linspace(0, 1, n)
speed = np.where(p < 0.5, 4 * p, 4 * (1 - p)) / 2
whirr = filt(noise(DUR_O), "bandpass=f=1700:width_type=q:w=1.2") * speed
place(mix, norm(whirr), T0, -31)
hit(mix, clunk(), T0 + DUR_O, -9)
hit(mix, tick(1.1, 0.8), T0 + DUR_O + 0.16, -26)  # overshoot settles
for k, t in enumerate([9.3 + 0.28 * j for j in range(6)] + [11.0]):  # the date flips through the years
    hit(mix, page_flip(), t, -21, -0.3 + 0.1 * k)

# It says: her words write themselves into the caption, then the double underline
for t, d in [(12.08, 0.3), (12.48, 0.08), (12.53, 0.4), (13.04, 0.32)]:
    place(mix, writing(d), t, -23, 0.0)
place(mix, pen_stroke(0.2, "out"), 13.38, -14, -0.15)
place(mix, pen_stroke(0.18, "out", 3000), 13.54, -15, -0.15)

# the same question: a second note slaps on, writes itself, "today" gets circled
place(mix, filt(s_wshort, "lowpass=f=3000"), 14.26, -22, -0.2)
hit(mix, slap(), 14.47, -10, -0.25)
place(mix, writing(0.7), 16.86, -19, -0.25)
place(mix, writing(0.62), 17.58, -19, -0.25)
place(mix, writing(0.3), 18.13, -20, 0.0)  # "today?" written into the caption
place(mix, pen_stroke(0.36, "bell", 2900), 18.42, -14, -0.1)  # circled
place(mix, filt(s_wshort, "lowpass=f=4000"), 18.36, -27, -0.1)

# ------------------------------------------------------------------ typography: every move of the type has a sound
for t in [2.78, 2.96, 3.21, 3.53, 4.76, 4.95, 5.27]:  # meme words slapped on like stickers
    hit(mix, slap(), t, -27, 0.0)
place(mix, pen_stroke(0.24, "bell", 2200), 8.38, -19, -0.1)  # highlighter swipe under "note."
hit(mix, thump(130, 0.03, 0.2), 8.3, -24, -0.1)  # "note." lands
for t in [15.98, 16.12, 16.26]:  # the dots type out
    hit(mix, tick(1.6, 0.3), t, -27, 0.1)
for t in [4.56, 8.98, 11.45, 14.06, 16.72]:  # each caption is pushed past the lens
    place(mix, filt(s_wshort, "lowpass=f=2500"), t - 0.06, -27, 0.0)

# ================================================================== ACTS 2 - 5
def decode_any(path):
    b = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-i", str(path), "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(b, np.float32).copy()


def crumple(sec=0.42):
    """paper balled up: a dense run of tiny crackles."""
    out = np.zeros(int(sec * SR) + SR // 10, np.float32)
    t = 0.0
    while t < sec - 0.02:
        d = float(rng.uniform(0.004, 0.018))
        b = filt(noise(d + 0.01) * np.exp(-tt(d + 0.01) / (d / 2)), f"bandpass=f={int(rng.uniform(1800, 6500))}:width_type=q:w=1.5")
        i = int(t * SR)
        out[i : i + len(b)] += norm(b) * float(rng.uniform(0.3, 1.0))
        t += float(rng.uniform(0.006, 0.03))
    out = out[: int(sec * SR)]
    return norm(out * shape(len(out), 0.02, 0.08))


def flick():
    """a card or a PDF flicked onto a pile."""
    x = filt(noise(0.09) * np.exp(-tt(0.09) / 0.018), "highpass=f=1800,lowpass=f=9000")
    return norm(x)


def note(f, sec=0.45):
    """a soft mallet note for the roadmap ladder."""
    t = tt(sec)
    x = np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t / 0.05) + 0.12 * np.sin(2 * np.pi * 4.01 * f * t) * np.exp(-t / 0.02)
    return norm(x * np.exp(-t / 0.16) * shape(len(t), 0.003, 0.05))


def blip(f0, f1, sec=0.12):
    t = tt(sec)
    f = np.linspace(f0, f1, len(t))
    return norm(np.sin(2 * np.pi * np.cumsum(f) / SR) * shape(len(t), 0.005, 0.04))


def sweep(f0, f1, sec, gain_shape="in"):
    t = tt(sec)
    f = np.geomspace(f0, f1, len(t))
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) + 0.3 * filt(noise(sec), f"bandpass=f={int((f0 + f1) / 2)}:width_type=q:w=0.7")
    p = np.linspace(0, 1, len(t))
    e = p**1.5 if gain_shape == "in" else np.sin(np.pi * p)
    return norm(x * e * shape(len(t), 0.01, 0.04))


def drone(sec):
    """the low hum that swells under 'nobody turned it into today'."""
    t = tt(sec)
    x = np.sin(2 * np.pi * 55 * t) + 0.6 * np.sin(2 * np.pi * 82.4 * t + 0.4) + 0.4 * np.sin(2 * np.pi * 110 * t + 1.1)
    x = x * (0.85 + 0.15 * np.sin(2 * np.pi * 0.7 * t)) + 0.25 * filt(noise(sec), "lowpass=f=220")
    return norm(x)


def flap_clack(heavy=False):
    x = filt(s_click, "highpass=f=600") * (1.0 if heavy else 0.7)
    if heavy:
        x = x.copy()
        k = thump(180, 0.02, 0.12)
        x[: len(k)] += 0.5 * k[: len(x)]
    return norm(x)


s_error = trim_to_onset(decode("error.mp3"))
s_chime = trim_to_onset(decode("chime.mp3"))
s_sparkle = trim_to_onset(decode("sparkle.mp3"))
s_typing = decode("typing.mp3")
s_whoosh_rev = s_whoosh[::-1].copy()
WH_PEAK = int(np.argmax(np.abs(s_whoosh))) / SR


def push_whoosh(cut, gain=-13):
    place(mix, s_whoosh, cut - WH_PEAK + F, gain)
    hit(mix, filt(thump(55, 0.12, 0.5), "lowpass=f=300"), cut, gain - 6)


def pull_whoosh(cut, gain=-14):
    hit(mix, s_whoosh_rev, cut, gain)


def typing_burst(t, sec, gain, pan=0.0):
    x = s_typing[: int(sec * SR)] * shape(int(sec * SR), 0.01, 0.06)
    place(mix, x, t, gain, pan)


# ------------------------------------------------------------------ the seams
push_whoosh(19.15)  # into her screen
pull_whoosh(33.2)  # back out to the desk
push_whoosh(37.3, -15)  # into the clean card
push_whoosh(45.0, -15)  # into today
pull_whoosh(57.45)  # back out to the desk

# ------------------------------------------------------------------ ACT 2: inside her screen
for k in range(12, 47):  # the tabs multiply: one soft click each, panned along the strip
    u = (k - 11) / 35
    t = 19.33 + 0.6 * (1 - (1 - u) ** 2)
    hit(mix, pitch(s_soft, 5 + (k % 3)), t, -25, -0.5 + k / 47)
hit(mix, pitch(s_pop, 2), 19.33, -19, 0.45)
for t in [20.86, 21.12, 21.42]:  # three roadmap PDFs flicked in
    hit(mix, flick(), t + 0.08, -15, 0.2)
    place(mix, paper_slide(0.16), t, -22, 0.2)
place(mix, filt(s_wshort, "lowpass=f=2500"), 22.36, -21, -0.1)  # the course card rises
place(mix, sweep(280, 560, 0.52), 22.62, -30, -0.1)  # the bar fills
hit(mix, thump(58, 0.09, 0.4), 23.32, -10, -0.1)  # and stalls: a dull thunk
for k in range(4):
    hit(mix, tick(0.6, 1.4), 23.46 + k * 0.07, -24, -0.1)  # the shudder
place(mix, s_whoosh, 24.45 - WH_PEAK + 0.15, -18)  # everything leaves left
hit(mix, flick(), 25.35, -20, -0.4)  # the new plan
for k in range(6):  # Sunday's plan deals itself out
    hit(mix, flick(), 25.45 + k * 0.065 + 0.12, -17, -0.3 + k * 0.12)
for t in [26.08, 27.38, 28.95]:  # caption reels roll on
    hit(mix, tick(0.9, 1.0), t, -24, 0.0)
for t in [25.35, 26.39, 27.89]:
    hit(mix, tick(1.2, 0.8), t, -22, 0.0)
hit(mix, s_error, 26.39, -19, 0.0)  # Wednesday: missed
hit(mix, slap(), 26.47, -17, 0.0)
for k in range(6):  # everything slides onto Friday
    place(mix, paper_slide(0.3), 27.48 + k * 0.035, -25, 0.25)
place(mix, crumple(0.42), 27.9, -11, 0.3)  # crumpled
place(mix, pitch(s_wshort, 3), 28.2, -16, 0.5)  # and tossed
hit(mix, thump(90, 0.06, 0.4), 30.23, -13)  # "big." lands
place(mix, filt(s_wshort, "lowpass=f=2500"), 30.8, -27)
place(mix, writing(0.32), 32.4, -20)  # "today." in her hand
dr = drone(4.4) * shape(int(4.4 * SR), 3.6, 0.15)  # the hum swells, then the turn cuts it
place(mix, dr, 28.85, -21)
for t in [29.0, 30.15, 31.45, 32.95]:  # the clock, slowing
    hit(mix, tick(0.95, 1.1), t, -23, -0.1)

# ------------------------------------------------------------------ ACT 3: the turn
place(mix, sweep(1400, 4200, 0.4, "bell") * 0.4 + crumple(0.4) * 0.6, 33.6, -15, -0.2)  # the note peels
place(mix, paper_slide(0.9), 33.98, -22, 0.0)  # and lifts toward camera
hit(mix, page_flip(), 34.5, -18, 0.0)  # "Monday?" flips down
place(mix, filt(s_wshort, "lowpass=f=2500"), 35.36, -27)
place(mix, s_sparkle, 35.6, -24, 0.0)  # paper turns into a clean card
hit(mix, s_chime, 36.0, -12, 0.0)  # the mark lands
hit(mix, tick(1.3, 0.6), 36.12, -24)
for t in [36.31, 36.48]:
    hit(mix, pitch(s_pop, -1), t, -22, 0.0)

# ------------------------------------------------------------------ ACT 4: the setup
hit(mix, slap(), 37.86, -22, -0.2)  # "from the note"
typing_burst(37.94, 0.75, -17)  # the goal, typed
hit(mix, s_click, 38.95, -13, -0.3)  # Beginner
hit(mix, s_click, 39.75, -13, -0.1)  # 1 hour
hit(mix, s_click, 40.43, -13, -0.1)  # 3 years
hit(mix, thump(110, 0.05, 0.3), 40.86, -13, 0.0)  # Create: thock
hit(mix, s_click, 40.86, -14, 0.0)
place(mix, filt(s_wshort, "lowpass=f=3000"), 41.24, -20)  # the form lifts away
sh = filt(noise(1.0), "highpass=f=3500,lowpass=f=9000") * np.sin(np.pi * np.linspace(0, 1, SR)) ** 2
place(mix, norm(sh), 41.7, -34)  # skeleton shimmer
for k, f in enumerate([523.25, 659.25, 783.99, 1046.5]):  # phases: a four-note ladder
    hit(mix, note(f), 42.75 + k * 0.07, -19, -0.2 + k * 0.13)
place(mix, filt(pitch(s_wshort, 4), "lowpass=f=4000"), 43.3, -24)  # the milestone opens
for k in range(4):  # tasks
    hit(mix, pitch(s_pop, 2 + k), 43.75 + k * 0.08, -24, 0.0)
hit(mix, pitch(s_pop, 5), 44.3, -18, 0.3)  # TODAY

# ------------------------------------------------------------------ ACT 4: today
place(mix, writing(0.32), 45.61, -20)
place(mix, filt(s_wshort, "lowpass=f=2500"), 46.1, -26)
hit(mix, thump(140, 0.03, 0.2), 46.3, -24)
hit(mix, slap(), 46.5, -24, 0.4)
for land in [46.34, 46.68, 47.59]:  # split-flap tiles riffle and land on the words
    for k in range(3):
        hit(mix, flap_clack(), land - (3 - k) * 0.055, -21, -0.2)
    hit(mix, flap_clack(True), land, -13, -0.2)
hit(mix, tick(1.3, 0.5), 48.81, -26)
hit(mix, pitch(s_pop, 1), 49.9, -24)
place(mix, s_whoosh, 50.36 - WH_PEAK + 0.15, -19)  # off to the week
hit(mix, blip(440, 330), 51.02, -21)  # Wednesday missed
for k in range(5):  # the plan moves: each block glides on a column
    place(mix, paper_slide(0.4), 51.47 + k * 0.05, -26, -0.1 + k * 0.1)
hit(mix, pitch(s_pop, 3), 51.8, -22)  # moved
hit(mix, pitch(s_pop, 4), 52.25, -16)  # toast: nothing piled up
hit(mix, blip(660, 880, 0.1), 52.3, -24)
place(mix, filt(s_wshort, "lowpass=f=2500"), 53.4, -24)
place(mix, pitch(s_wshort, 2), 53.58, -18)  # the assistant sheet slides up
hit(mix, pitch(s_pop, 2), 53.9, -20, 0.3)
typing_burst(53.94, 0.62, -20, 0.3)
for k in range(3):  # thinking dots
    hit(mix, blip(1200, 1250, 0.05), 54.74 + k * 0.07, -30, -0.3)
hit(mix, pitch(s_ping, -5), 55.02, -21, -0.3)  # the reply
for t in [55.14, 55.22, 55.34, 55.4]:
    hit(mix, tick(1.4, 0.4), t, -29, -0.3)
place(mix, filt(s_wshort, "lowpass=f=2500"), 55.02, -27)
place(mix, writing(0.32), 55.75, -20)  # "today." in her hand
hit(mix, s_click, 56.23, -11, -0.3)  # Apply
hit(mix, thump(120, 0.04, 0.25), 56.23, -18, -0.3)
place(mix, pitch(s_wshort, -2), 56.36, -19)  # the sheet slides away
hit(mix, pitch(s_pop, -2), 56.76, -21)  # today reflows
for k in range(2):
    hit(mix, flap_clack(), 56.76 - (2 - k) * 0.055, -21, -0.2)
hit(mix, flap_clack(True), 56.76, -14, -0.2)

# ------------------------------------------------------------------ ACT 5: her Monday
for t in [58.0, 59.0]:  # the room's clock again
    hit(mix, tick(1.0, 1.0), t, -26, -0.1)
hit(mix, thump(130, 0.03, 0.2), 57.85, -24, -0.1)  # "note"
place(mix, pen_stroke(0.24, "bell", 2200), 57.93, -19, -0.1)  # highlighter
place(mix, filt(s_wshort, "lowpass=f=2500"), 59.36, -27)
RW0, RWD = 59.66, 0.64  # the counter rewinds 1,095 -> 1


def rw_time(v):
    """when the rewind passes value v (inverse of the power3.inOut in s6-payoff.html)."""
    f = (1095 - v) / 1094
    p = np.cbrt(f / 4) if f < 0.5 else 1 - np.cbrt((1 - f) * 2) / 2
    return RW0 + p * RWD


for v in range(1090, 0, -10):
    heavy = v % 100 == 0
    hit(mix, tick(1.35 if not heavy else 0.9, 0.6 if not heavy else 1.3), rw_time(v), -29 if not heavy else -22, 0.05)
place(mix, sweep(2200, 380, RWD, "bell"), RW0, -29)  # the rewind whine
hit(mix, s_ping, RW0 + RWD, -12, 0.3)  # ding: Day 1
hit(mix, slap(), 60.32, -12, 0.2)  # her new note
hit(mix, tick(1.1, 0.9), 60.55, -18, 0.3)  # Day 2
hit(mix, tick(1.15, 0.9), 60.75, -17, 0.3)  # Day 3
place(mix, s_whoosh, 61.36 - WH_PEAK, -14)  # the camera tilts up the wall
bass2 = s_bass.copy()
pk2 = int(np.argmax(np.abs(bass2)))
bass2[pk2:] *= np.exp(-np.arange(len(bass2) - pk2) / SR / 0.6)
hit(mix, bass2, 61.5, -19)  # the mark: a soft impact
place(mix, s_sparkle, 61.56, -24, -0.2)
for t in [61.72, 61.97]:
    hit(mix, pitch(s_pop, -2), t, -21)
place(mix, filt(s_wshort, "lowpass=f=3000"), 64.1, -20)  # the card rises
hit(mix, pitch(s_pop, 3), 64.6, -24)
hit(mix, tick(1.3, 0.5), 64.71, -26)
hit(mix, slap(), 65.0, -16, 0.3)  # Day 1 ✓

# ------------------------------------------------------------------ the bed: room tone under everything
n_all = int(round(DUR * SR))
env = np.full(n_all, db(-41), np.float32)  # the desk


def seg(a, b, g, ramp=0.25):
    i0, i1, r = int(a * SR), int(b * SR), int(ramp * SR)
    env[i0:i1] = db(g)
    if r and i0 - r > 0:
        env[i0 - r : i0] = np.linspace(env[i0 - r - 1], db(g), r)


seg(19.15, 33.2, -45)  # inside the screen: quieter, closer
seg(33.2, 37.3, -42)
seg(37.3, 57.45, -48)  # the product: almost gone under the music
seg(57.45, DUR, -42)
mix[:n_all] += room(DUR) * env[:, None]
hum = filt(noise(14.05), "lowpass=f=180,lowpass=f=180")  # the screen's soft electrical hum
place(mix, norm(hum) * shape(len(hum), 0.3, 0.2), 19.15, -40)

# ------------------------------------------------------------------ the music bed: from the turn to the end
mb = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-i", str(BGM), "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True, check=True).stdout
music = np.frombuffer(mb, np.float32).reshape(-1, 2).copy()
M0 = 33.35
mt = M0 + np.arange(len(music)) / SR
g = np.interp(mt, [M0, 65.2, 65.9, 70.0], [db(-20), db(-20), db(-12), db(-12)])
i0 = int(M0 * SR)
n = min(len(music), len(mix) - i0)
mix[i0 : i0 + n] += music[:n] * g[:n, None]

# ------------------------------------------------------------------ out
i = n_all
out = mix[:i]
out *= shape(i, 0.0, 0.3)[:, None]
peak = float(np.max(np.abs(out)))
# a brick-wall limiter keeps the crack's transient under -1 dBFS without pulling the whole stem down
subprocess.run(
    ["ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-",
     "-af", "alimiter=limit=0.89:attack=1.5:release=60:level=disabled", "-c:a", "pcm_s16le", str(OUT)],
    input=out.astype(np.float32).tobytes(),
    check=True,
)
print(f"{OUT.relative_to(ROOT)}: {i / SR:.2f}s, pre-limiter peak {20 * np.log10(peak + 1e-9):.1f} dBFS")
