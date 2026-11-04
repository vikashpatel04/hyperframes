# SPEC: 0 to 1, "Zero, to one" (coming soon)

```text
GOAL:    Someone with a big goal feels the gap ("1,095 hours, and nobody tells you what to do
         with the first one"), sees one connected system close it, and joins the waitlist.
OUTPUT:  HyperFrames, 1920 x 1080, 30 fps
TIME:    64.0 s x 30 = 1920 frames. Narrated: the voice is the clock (assets/voice/lines.json,
         word cues re-anchored in assets/voice/cues.json).
LOOK:    No brand yet: the NAME is the mark. The "0" is an empty progress ring; it fills as the
         plan comes together and completes on the end card.
         Two worlds. NIGHT (#09090b ground, #18181b cards, #27272a borders, #fafafa ink,
         #a1a1aa muted) for the struggle; it floods to DAY (#fafafa ground, #ffffff cards,
         #e4e4e7 borders, #09090b ink, #71717a muted) when the product arrives.
         ONE accent: shadcn orange (#f97316; #ea580c for type on white), only on what moves you
         forward: the ring's progress, primary buttons, "today", the payoff. Missed = #ef4444,
         only on the missed day.
         Type: Inter 900 for kinetic lines at 120-200 px, tracking -0.04em; second lines in
         muted grey (the site hero's "Clear next steps." treatment). UI in Inter 400/700 at
         1.75x shadcn sizes (body 26-30 px), 12 px x 1.75 radii, 1 px x 2 borders, shadcn
         shadows (0 1px 2px rgb(0 0 0 / 5%), 0 10px 30px rgb(0 0 0 / 8%)).
OBJECTS: the ring (stroke 14 px, track #27272a / #e4e4e7, progress orange, round caps); a
         year-grid of 1,095 day cells (3 x 53 x 7, like a contribution graph); a week strip
         Mon-Sun of shadcn cards with task chips; shadcn Input, toggle groups, Button, Badge,
         Card, Progress, Checkbox, Sheet (assistant), Toast; an oversized macOS cursor.
MOTION:  arrivals expo.out / power4.out; in-scene moves the nudge curve or power2.inOut;
         exits power3.in. Words: waterfall entry (binary set, y 40-90 px, gaps x0.84) or
         per-word grey-to-ink. Typing at 22 ms a character. The cursor clicks and the next
         thing happens on the same frame. No idle loops.
SHOTS:   (master seconds; scene hosts tile with no gaps)
  s1 zero    0.00-14.40  night. Ring + "Every big goal / starts at zero." -> push into the ring:
                         GOAL input retypes 3 goals on their words -> "3 years" "1 hour per day"
                         chips -> 0 -> 1,095 hours count-up -> the number becomes 1,095 day cells
                         -> all fade but the first: "the first one." -> zoom-through into it.
  s2 week   14.40-24.70  night. Week strip: Sunday plan fills the week -> Wednesday missed (red)
                         -> its tasks shove into Thu/Fri, the stacks overflow and topple out of
                         frame on "gone." -> "Knowing what you want" / "isn't knowing how to
                         get there." -> inverse zoom (arrival).
  s3 goal   24.70-30.75  night -> day. The ring + "to 1" lockup lands; the first orange arc
                         draws; day floods out of the ring. Create-goal card: goal types,
                         Beginner / 1 hour / 3 years select on their words; cursor clicks the
                         orange "Create my roadmap" -> cut-the-curve LEFT.
  s4 plan   30.75-41.60  day. Roadmap: 4 phases on "Phases", the milestone on "Milestones",
                         4 tasks on "Tasks"; Draft -> Approved on "approve" (cursor click);
                         dive into phase 01 -> Today: 9:00 / 9:25 / 9:45 blocks, Next-up card,
                         first task checks off -> cut-the-curve LEFT.
  s5 adapt  41.60-51.95  day. The week strip again, calm: Wednesday's missed block glides to
                         Thursday, toast "Rescheduled · nothing piled up"; assistant sheet slides
                         in, "I only have 30 minutes today", a suggestion with Keep / Apply,
                         cursor applies, today reorganizes; "every decision stays yours."
                         -> cut-the-curve UP.
  s6 one    51.95-64.00  day. Progress dashboard; the ring fills to 100% (the payoff, once);
                         the full ring becomes the 0 of "0 to 1"; "Big goals." / "Clear next
                         steps."; the waitlist card: Coming soon, email, orange "Join the
                         waitlist", 0-to-1-waitlist.vercel.app; holds 3 s.
SOUND:   voice 1.0; MusicGen "tense" bed to 25 s (out under the reveal), "bright" bed from the
         reveal at 0.12; bundled SFX: key ticks on typing, click on every cursor click, pop on
         chips/badges, whoosh on seams, one impact on the full ring.
BANNED:  dark void with small floating UI (the night world fills the frame); glow, neon,
         particles; purple/blue gradients; glass cards; everything centred; fade-and-slide-up
         on everything; titles drifting after landing; docked logo; three cards in a row;
         crossfades between scenes; idle wobble.
QA:      0.0 ring + first words on screen; 3.0 goal typing; 10.6 1,095 hours; 13.6 one cell;
         15.6 week plan; 17.3 Wednesday red; 19.8 topple; 22.5 knowing line; 25.9 lockup;
         26.6 day flood; 29.5 goal card filled; 33.5 phases + milestone; 36.4 Approved;
         39.5 Today; 42.5 missed block; 44.0 glide + toast; 48.5 assistant suggestion;
         50.8 "stays yours"; 55.4 ring full; 57.8 tagline; 61.5 waitlist card; 63.9 final.
```
