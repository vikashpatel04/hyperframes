# SPEC: Counter Pay, problem → solution

```text
GOAL:    A shop owner feels the ₹18,000/month they lose to "round off", then sees one
         shortcut make the amount uncatchable, and remembers "Exact amount. Every time."
OUTPUT:  HyperFrames, 1920 x 1080, 30 fps
TIME:    74.5 s x 30 = 2235 frames. Narrated: the voice is the clock (assets/voice/lines.json).
LOOK:    Two grounds, one arc. Act 1–2 PAPER #f3f5f2 (the shop by day) with INK #0f1513,
         LOSS RED #d93025 only on lost money (the 40, the ₹18,000). "Gone." floods to
         NIGHT #0c110f, which holds for the product (the real customer display's own
         ground). ACCENT GREEN #14b37d only on what Counter Pay does (the flood, the fixed
         amount, the mark), one focus per frame.
         Display face Inter 900, 150–220 px, tracking -0.035em; quiet lines Inter 700
         44–56 px; product UI in its own sizes x2.4 (customer display) / x2 (popup pill).
         Medium: the product's real flat UI (cards with its own shadows, 16 px radii x scale),
         thermal paper receipt, acrylic standee. No grain, no glow, no gradients.
OBJECTS: thermal receipt (scalloped bottom edge, dotted rule, TOTAL line); acrylic QR
         standee (clear slab with a bright top edge, foot, "Scan & Pay" header); customer
         phone (rounded 44 px body, notch, a UPI amount screen with a keypad); queue of
         people (head + shoulders silhouettes); billing PC window (title bar, item table);
         Counter Pay popup pill (360x88, r20, rgb(12 15 14/.92), ₹ glyph, green flood);
         customer display monitor (bezel, stand) showing the real Pay screen; an old phone,
         an ESP32 board with a black/white e-paper panel.
MOTION:  enter expo.out / power4.out; in-scene moves power2.inOut or the nudge curve
         (power3.in 20% → linear 18% → power4.out 62%); exits power3.in, ~0.75x entry.
         Words: waterfall entry (binary tl.set, y 40–80 px, 0.13–0.2 s, gaps shrink x0.84)
         or per-word grey→ink 0.08 s apart. Keycaps press 0.06 s down / 0.18 s up.
         No idle loops, no breathing. Seams: stamped from ledger.json.
SHOTS:   (master seconds)
  s1 rush   0.00–17.95  paper. RUSH HOUR waterfall; queue cascades in; camera nudges to the
                        counter; receipt TOTAL ₹1,040 lands on "one thousand and forty";
                        standee + phone, 1-0-0-0 typed on "pays one thousand"; bubble
                        "Round off, na?"; "can't argue." with the queue ticking to 10;
                        the 40 splits off the total, turns red, and FALLS → seam DOWN.
  s2 stack 17.95–30.55  the ₹40 lands on one chip; 20 × ₹30 chips cascade into a grid,
                        camera pulls back; "= ₹600 / day"; 30-day calendar fills; 0.5 s
                        stillness; ₹18,000 slams on "eighteen thousand"; "Gone." floods the
                        frame to night; "Not stolen. Just rounded off." → seam UP.
  s3 meet  30.55–40.75  night. The question rises word by word, "couldn't change" in green;
                        rack-focus to the mark + "Counter Pay" per letter; billing window;
                        F9 keycap press → the real pill rises; 1040 typed in sync; Enter →
                        green flood "Sent"; focus returns to billing → zoom-through (Z push).
  s4 display 40.75–54.35 the real landscape Pay screen on a monitor at x2.4; QR draws;
                        ₹1,040 lands on the word; lock + "Amount fixed."; standee slides in,
                        its payee chip flies into the screen's PAYING row; "Every rupee.";
                        "Scan to pay" flips through हिन्दी, বাংলা, தமிழ், తెలుగు, ಕನ್ನಡ
                        → inverse zoom (Z pull, arrival).
  s5 devices 54.35–67.15 "Nothing new to buy."; old phone (portrait Pay), extra monitor,
                        ESP32 e-ink cascade in on their words; "Works with what you have.";
                        contact card with vikashpatel.d0414@gmail.com holds 3 s → seam UP.
  s6 close 67.15–74.50  "Exact amount." / "Every time." land hard; the mark fills with
                        green, wordmark wipes in; "Free & open source · Windows 10/11" and the
                        GitHub link hold to the end (≥ 2 s).
SOUND:   voice 1.0; music: MusicGen "tense" bed under acts 1–2 at 0.12, "bright" bed from
         the turn (30.55) at 0.14, 1.5 s fade-out under the end card. SFX (bundled, ~0.35):
         pop on the receipt total, key-press on the 1-0-0-0 and the 1040, impact-bass on
         ₹18,000, whoosh-short on seams 1/2/5, whoosh on the Z seams, click on F9 and Enter,
         chime on "Sent", pop on each device.
BANNED:  dark void with small floating things; glow, neon, particles; purple/blue gradients,
         glass cards; everything centred; everything fading and sliding up; titles that
         drift after landing; corner labels/HUD; three cards in a row as a feature list;
         logo in a corner; crossfades between scenes; idle wobble.
QA:      1.0 RUSH HOUR legible; 3.6 receipt TOTAL ₹1,040; 8.6 phone shows ₹1,000;
         9.7 bubble; 16.5 red 40 detached; 17.9 / 18.0 seam; 26.2 ₹18,000 red & large;
         29.0 night flood; 31.8 question; 34.2 lockup; 36.6 pill with 1,040; 37.7 flood
         "Sent"; 40.7 / 40.8 Z seam; 44.2 Pay ₹1,040 with QR; 45.5 lock; 48.5 payee match;
         53.0 a language line; 54.3 / 54.4 Z seam; 60.0 three devices; 65.0 email card;
         70.0 lockup; 74.4 final frame complete.
```
