# REVIEW: Counter Pay, problem → solution (v1)

74.5 s · 1920×1080 · 30 fps · `renders/counter-pay.mp4`

## Creative calls

- **One thread through the film: the ₹40.** It breaks off the ₹1,040 bill, falls through the first cut, multiplies into 20 × ₹30 chips and ₹18,000, rises back green at the turn, becomes the Counter Pay mark, and returns as the fixed ₹1,040 on every screen.
- **Two grounds, one arc.** Paper (the shop by day) for the problem; "Gone." floods to night, which is the real customer display's own ground, for the product. Red only on lost money; green only on what Counter Pay does.
- **Real UI, rebuilt from the source.** The popup pill (360×88, r20, ₹ glyph, green flood, "Enter to show · Esc to cancel") and the landscape and portrait Pay screens use the repo's own CSS, sizes and locale strings (`apps/agent/src/renderer/popup`, `apps/display/src/scenes`, `locales/*.json`), shown at 1.8–2×. The mark is drawn from the same geometry as `apps/agent/scripts/make-icons.py`. The billing window, receipt, standee and phone are generic stand-ins and are labelled as such ("Your billing software").
- **The QR codes are real and scannable but go nowhere.** They encode `upi://pay?pa=yourshop@example&…&am=1040.00`. `example` is not a UPI handle, so scanning the film never pays anyone.
- **Seams:** five, stamped from `ledger.json`. Cut-the-curve DOWN (the 40 falls), UP (the turn rises), a zoom-through into the customer screen, an inverse zoom (arrival of "nothing new to buy"), and UP into the close. No crossfades.
- **Voice is the clock.** Each line was generated separately with Kokoro `af_heart` and joined with authored pauses (`scripts/build-voice.sh` → `assets/voice/lines.json`). Every reveal is timed to those line starts and to Whisper word times.

## Measured

- `hyperframes check`: passed, 0 errors. Contrast 49/49 AA.
- Seam gate (`seam-gate.mjs verify`): 5/5 passed (direction, speed match, zero overlap, Z sign).
- `snapshot --review`: beats, seams and the phone sheet were looked at. Fixed afterwards: a dark dip at seam 1 (added a paper stage ground until the night flood), an empty QR card at seam 3 (the QR now starts drawing at +0.2 s), and an empty arrival at seam 5 ("Exact" is in flight at the cut).
- Sound: levels and placement were **measured, not heard**. Beds are loudness-normalised (−1.5 dBTP ceiling) at 0.12 under the voice. Each SFX peak is placed one frame after its picture using `hyperframes audio` peak times.

## Warnings kept on purpose

- `line_unread` on the typed digits 1 / 10 / 104: this is typing, and the field settles on 1,040.
- `line_unread` on the language roll (0.5 s each): it is a slot-machine roll meant to show "many scripts", not to be read. Hindi holds 7 s before it.
- `line_unread` on the "Counter Pay" lockup in s3 (1.2 s): it is said aloud and returns as the end card for 4.4 s.
- `text_below_floor` on small product labels ("Paying", "Your billing software", device labels while scaled behind the contact card): these are the product's own sizes and are texture, not reading text.
- `duplicate_media_discovery_risk`: the same QR SVG appears on three devices on purpose.

## Weakest shot / next

- **s4 standee → payee chip (48–49.5 s):** the chip flight is small and quick. With more time, punch the camera into the PAYING row as the chip lands.
- **The music** is local MusicGen (free). It is serviceable but generic. A real track, or a HeyGen library bed, would lift the film most.
- **Not built:** a 9:16 vertical cut. The scenes are 16:9-specific, so a vertical cut needs re-layout.
