# REVIEW: 0 to 1, "Zero, to one" (v1)

64 s · 1920×1080 · 30 fps · `renders/zero-to-one.mp4`

## Creative calls

- **No brand yet, so the name is the mark.** The "0" is an empty progress ring. It opens the film empty, takes its first orange step at the reveal, fills to 100% on the dashboard, and becomes the 0 of "0 to 1" on the end card. The ring's journey is the product's promise.
- **Dark to day.** The struggle plays on night (`#09090b`). Day floods out of the ring at the reveal, so the product world is bright shadcn.
- **One accent:** shadcn's orange theme, only on forward motion: the ring, progress, today and primary actions. Buttons use orange-600 (`#ea580c`) so white text passes contrast. Red appears only on the missed day.
- **The pain is a real arithmetic, not a stat:** 3 years × 365 days × 1 hour = 1,095 hours, drawn as 1,095 day cells. "The first one" is the only cell that lights. It's derived from the demo's own settings (3 years, 1 hour a day).
- **The missed day appears twice on purpose:** first the plan topples (Act 1), then the same miss glides forward calmly (Act 3).
- **UI is recreated, not screenshotted:** shadcn components at 1.75×, using the site demo's labels (the Software Engineer roadmap, its four phases and the Today blocks). The **assistant is a concept screen**, since the site has none yet.
- **Seams:** five, stamped from `ledger.json`: a zoom-through into the first hour, an inverse zoom as the mark arrives, cut-the-curve LEFT twice and UP into the close. No crossfades.

## Measured

- `hyperframes check`: passed, 0 errors. Contrast 100/100 AA.
- Seam gate: 5/5 passed (direction, speed match, zero overlap, Z sign).
- `snapshot --review`: beats, all five seams and the phone sheet were looked at. Fixed after review: hook words appearing before they're spoken, the counter label crowding, and "the first one." leaving early.
- Sound was **measured, not heard**. Each SFX peak is placed one frame after its picture. The beds are local MusicGen, loudness-normalised.

## Warnings kept on purpose

- `line_unread` on the typed goals: characters are split for typing, so the check counts each letter as a word. Each goal is spoken while it types.
- `line_unread` on the 0 → 1,095 count steps and the falling week chips: they're meant to roll and fall, not to be read.
- `text_below_floor` on chip labels in the week strips and the scaled-down week beside the assistant: they're texture; the story is the stack, not each label.

## Weakest shot / next

- **The assistant (s5):** the left half shows a tiny week while the sheet works. With more time: a larger "today" card that visibly reflows when Apply is clicked.
- **Music:** local MusicGen is serviceable. A real track would lift the reveal most.
- **A 9:16 cut** for Reels and Shorts needs its own layout.
