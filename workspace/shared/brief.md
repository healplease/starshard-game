# Project Brief

## Theme (from the human)
> A top-down auto-scrolling 2D space shooter. A little spaceship flies through the cosmos,
> avoiding debris and asteroids while fighting enemy ships.

## One-line pitch (Orchestrator's framing)
"**Starshard**" — pilot a lone scout ship through an endless scrolling starfield; dodge drifting
asteroids/debris and blast enemy fighters to rack up a score before your ship is destroyed.

## Genre & shape
- **Genre:** top-down vertical auto-scroller / arcade shoot-'em-up (shmup).
- **Camera:** fixed single screen; the world scrolls past the player (starfield + hazards move
  downward, ship moves left/right/up/down within the screen).
- **Win/lose:** arcade-style — survive and score as high as possible; lose when health/lives run out.

## Hard constraints (from CLAUDE.md — every role respect these)
- One single screen, keyboard-only, 2D.
- Placeholder art ONLY: colored shapes + on-screen text, no external image/sound files.
- **Code is modular (v2): the ~500-line single-file cap is RETIRED.** Split `workspace/game/` into
  focused MVC-ish modules; `main.py` stays the entry point and still supports `--smoke-test`
  (120 frames, simulated input, exits 0). Keep the smoke gate green across the refactor.
- Python 3.14 + `pygame-ce` from the `.venv`.

---

> **Closed-increment framings archived.** The orchestrator's kickoff framings for **v2** (bonuses +
> modular refactor) and **v5** (three enemy types) — both shipped & passed QA — moved to
> `../archive/brief-increments-v2-v5.md` to keep this file to the theme + the latest increment. The
> **v6** framing (bombs / Z-X remap, shipped & passed QA) is fully captured in its shipped specs +
> `handoffs.md`/`history.md`; it has been superseded here by the **latest** increment (v7) below.

## v7 increment (added 2026-06-05) — Bosses (periodic mothership boss fights)

> v1/v2/v5/v6 shipped & passed QA; v3 reorganized the KB; v4 added standing QA docs. The human now
> wants **bosses**: large-health-pool enemies with **learnable attack patterns** that interrupt the
> normal run on a **periodic breakpoint**. This is a big increment — it touches every role. Full build
> run (BA → Designer → Artist → Writer → Level-designer → Programmer → QA).

### Feature: bosses (human's words, lightly framed)
**The boss-fight loop:**
1. **Breakpoint trigger.** Every now and then a boss arrives. The trigger is **time- or point-based** —
   human's examples: *every 5 minutes* or *every 5000 points*. Designer/Level-designer pick **which
   metric and the exact value(s)**, and whether it repeats on a fixed interval or scales.
2. **Field clears + spawns freeze.** When the breakpoint fires, the **field clears fully** — reuse the
   **v6 bomb flush + flash visual** (the screen-covering flash) so it reads the same, but **this is a
   system-initiated clear: it does NOT consume a player bomb charge** and is not a player action. While
   the boss is active, **all regular enemy and asteroid spawns are disabled**.
3. **Boss entrance + movement.** A **slow-moving boss enemy appears**, travels in, and **settles at the
   vertical center of the screen**, then **moves slowly left and right** (oscillates) to make dodging
   harder. Bosses have a **large health pool** and a **moveset** (see Mothership below).
4. **Defeat + resume.** When the boss is defeated, the player is awarded a **big amount of points**, and
   the **normal loop resumes** — asteroids and regular enemies start spawning again — **until the next
   breakpoint** brings the next boss.

**First boss — the Mothership.** Large, slow, central-oscillating. Its moveset (a repeating attack
cycle — Designer locks order, timing, and whether it loops 1→2→3→4→1):
1. **Spawn 5 regular enemies** (the v5 REGULAR type).
2. **Spawn 2 heavy enemies** (the v5 HEAVY type).
3. **Spawn 7 scout enemies** (the v5 SCOUT type).
4. **Fire a fan of yellow bullets** that **midway split into 12 red bullets** flying outward **in all
   directions** (≈30° apart for an even 360° burst — Designer confirms counts/angles/split point).

### Design questions for the BA & Designer to nail down (delegate values — DO NOT assume)
- **Breakpoint:** time **vs** points **vs** both? Exact value(s)? Fixed interval or scaling per boss?
  First-boss timing. **Reconcile with AC13** (runs are typically 1–3 min): a 5-min/5000-pt gate may
  mean most runs never see a boss — Designer/Level-designer decide whether to lower it for this game's
  pace or accept bosses as a late-run event. **This is the #1 thing to resolve.**
- **Boss stats:** health pool (how many player hits), size/shape (Mothership = large geometry),
  entrance path + speed, the central oscillation amplitude + speed, vertical resting position.
- **Field-clear semantics on boss arrival:** reuse the v6 flush — confirm exactly what it clears
  (enemies / asteroids / enemy bullets) and what it spares (player bullets? pickups? cosmetics?), and
  that it awards **no score** and **costs no charge** (it's the system, not the player).
- **Spawn suppression:** while the boss is alive, freeze the v1 asteroid spawner + the v5 enemy spawner
  (and bonus-pickup drip? boss-minion drops?). Boss-spawned minions are the exception. How/when normal
  spawning re-enables after the kill.
- **Moveset cadence:** intervals between the 4 attacks, the order, looping, and whether the boss can
  attack during its entrance. Minion caps (does step 1 re-spawn 5 even if the last 5 are alive?).
- **Attack-4 detail:** yellow-fan count + spread; the **split trigger** ("midway" = screen midpoint?
  after N frames/distance?); the 12 red children's directions (even 360°?) + their speed/damage.
- **Boss damage model:** does the boss collide-damage the player (ram)? boss-bullet damage. Is the
  **boss immune to the player's bomb flush**, or does the flush chip it / clear only its minions+bullets?
  (Edge case: player bombs mid-boss-fight.) Can the player's shots always hit the boss?
- **Reward:** the "big amount of points" on defeat (flat value); do boss-spawned minions award normal
  score / drop pickups?
- **Boss HUD:** a boss health bar + label (Artist/Writer) — distinct from the player HP bar.
- **Smoke-test plan:** the headless `--smoke-test` (120 f) must stay green AND **exercise a boss** —
  seed/force a boss spawn early in the headless run so the field-clear + entrance + at least one attack
  step fire within 120 frames (QA/Programmer design the seed, like the v6 bomb seed). Keep AC1–AC38
  regression-clean.
- Keep everything renderable as **shapes + text**, single-screen, keyboard-only, no external assets.

### Notes (orientation only — Programmer owns the real touch-list)
- Likely touches: `config.py` (breakpoint value, boss HP/size/speed, oscillation, fan/split counts,
  reward), `entities/` (a Boss model + boss-state, reuse v5 enemy + green-split-style bullet logic for
  the yellow→red split), `systems/` (a boss/encounter manager that watches the breakpoint, runs the
  field-clear, gates the v1 asteroid + v5 enemy spawners, drives the moveset, awards points), `view/`
  (boss shape + boss health bar + yellow/red boss bullets; the flush flash already exists from v6),
  `input.py` unchanged. The **yellow→red split** strongly resembles the **v5 green→red splitting
  pellet** — reuse that machinery. The **field-clear flash** reuses the **v6 bomb flush/flash** —
  factor it so the boss manager can trigger it without a charge.

## Next
No active increment until v7 closes — **v6 shipped**. The next increment opens when the human gives a
new feature or theme: the Orchestrator records its framing here (superseding the previous) and kicks off
the Business Analyst (`workspace/requirements/requirements/`).
