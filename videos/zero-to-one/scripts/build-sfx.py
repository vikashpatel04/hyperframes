#!/usr/bin/env python3
"""Sound for the hook + Act 1 review cut (0 - 19.6 s): one stereo effects stem.

Every hit is placed one frame after the picture it belongs to (times come straight from
compositions/s1-desk.html). Recorded sources live in assets/sfx/src (see CREDITS.md);
the clock, pen, paper, marker, projector and room tone are synthesised here with a
seeded generator, so the stem rebuilds bit-for-bit.

Usage: python3 scripts/build-sfx.py   ->  assets/sfx/hook-act1.wav
"""
import pathlib
import subprocess

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "assets" / "sfx" / "src"
OUT = ROOT / "assets" / "sfx" / "hook-act1.wav"

SR = 48000
DUR = 19.6
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

# It says: become a software engineer (double underline)
place(mix, pen_stroke(0.2, "out"), 13.04, -14, -0.3)
place(mix, pen_stroke(0.18, "out", 3000), 13.2, -15, -0.3)

# the same question: a second note slaps on, writes itself, "today" gets circled
place(mix, filt(s_wshort, "lowpass=f=3000"), 14.26, -22, -0.2)
hit(mix, slap(), 14.47, -10, -0.25)
place(mix, writing(0.7), 16.86, -19, -0.25)
place(mix, writing(0.62), 17.58, -19, -0.25)
place(mix, pen_stroke(0.34, "bell", 2900), 18.22, -14, -0.25)
place(mix, filt(s_wshort, "lowpass=f=4000"), 18.16, -27, -0.25)

# ------------------------------------------------------------------ the bed: room tone under everything
place_room = room(DUR)
i = int(round(DUR * SR))
mix[:i] += place_room * db(-41)

# ------------------------------------------------------------------ out
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
