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
  downward, ship moves within the screen).
- **Win/lose:** arcade-style — survive and score as high as possible; lose when health runs out.

## Hard constraints (from CLAUDE.md — every role respect these)
- One single screen, keyboard-only, 2D.
- Placeholder art ONLY: colored shapes + on-screen text, no external image/sound files.
- Code is modular; `main.py` stays the entry point and supports `--smoke-test` (120 frames, simulated
  input, exits 0). Keep the smoke gate green.
- Python 3.14 + `pygame-ce` from the `.venv`.

## Current state & where the detail lives
v1–v20 shipped & passed QA — see `backlog.md` for the capability summary and the canonical specs in
each role folder. Closed-increment framings (v2, v5, v7–v19) are archived in
`../archive/brief-increments-*.md`; the v20 framing below is current.

## Current increment — v20: laser enemy (charged sweeping beam) + projectile ownership + death attribution

**Human's words:** add a **new enemy that shoots deadly lasers**. The attack: the **laser is a line from
the enemy to (slightly past) the edge of the screen** so it looks endless. There is a **~0.5 s windup**
during which the laser **charges — it shows only a thin line that can be passed through without harm**.
After charging, the laser enters its **damaging phase (~1 s)**, **widening over time up to ~5–7 px** and
**moving toward the player at very low speed (~0.1× the player's speed)**. **Touching the laser during the
damaging phase damages the player; the laser does NOT disappear on touch — only on timeout.** The
**attacking ship cannot move while the laser is firing**, and **takes breaks between attacks to
reposition**. To support this, **projectiles get a `source` field** identifying which ship fired them, and
**each ship gets a unique ID**; the laser's owner reads this to **not move while its own laser is active**.
Finally: **when the player dies from colliding with an enemy or a projectile, the GAME_OVER screen shows
"Killed by &lt;enemy name&gt;".**

This is a **new mechanic + content + infrastructure** change (new enemy type, a novel timed two-phase
beam weapon, a projectile-ownership / ship-ID system, and a death-attribution → copy change) →
**full pipeline**: BA → Designer → Artist → Writer → Level-designer → Programmer → QA.

**Baseline being changed (current code, for reference — roles confirm against the code):**
- **Enemies** live in `game/entities/hazards.py` (`class Enemy`, `kind` ∈ REGULAR/HEAVY/SCOUT; stats in
  `config.ENEMY_KINDS`); enemies descend then strafe and fire via `entities/projectiles.py`. Bosses are
  separate (`entities/boss.py`, the v7/v16 `BOSS_POOL`).
- **Projectiles:** `entities/projectiles.py` — `PlayerBullet` and `EnemyBullet` (fields x/y/vx/vy,
  `family`, `dmg`, split/ring timers). **Neither bullets nor ships currently carry an identity / owner.**
- **Combat / death:** `systems/combat.py` resolves hits; player HP→0 transitions to GAME_OVER. There is
  **no "what killed me" tracking** today.
- **The laser is a new projectile kind** — not a moving point bullet but a **persistent, timed, growing
  swept line segment** with two phases. Whether it's an `EnemyBullet` family or its own entity/struct is
  the Programmer's call; the *behavior contract* is what the specs lock.

**Decisions locked at kickoff (2026-06-07):**
- **New enemy = a laser shooter** (its own `kind` in the enemy roster). Identity/name/appearance are
  downstream (Designer/Artist/Writer).
- **Laser attack = three states:** (1) **WINDUP ~0.5 s** — a **thin, harmless telegraph line** from the
  enemy to just past the screen edge; the player can pass through it safely. (2) **DAMAGING ~1 s** — the
  beam is lethal on contact, **widens over its lifetime to ~5–7 px**, and **sweeps toward the player at
  ~0.1× player move speed**; it **persists for its full duration** (does **not** vanish on touch). (3) the
  enemy is **immobile for the whole attack (windup + damaging)** and **repositions only during a cooldown
  gap between attacks**.
- **Laser geometry:** a line originating at the firing ship, extending to **slightly beyond** a screen
  edge (endless look). Exact origin/extent/anchor and whether it aims at the player's position-at-fire are
  design/level calls.
- **Contact damages, beam survives:** touching the live beam damages the player; the beam is removed only
  on **timeout** (end of the damaging phase), never on contact. Per-frame vs per-contact damage cadence is
  a Designer/Level-designer call.
- **Projectile ownership infrastructure (cross-cutting):** **every ship gets a unique ID**; **every
  projectile carries a `source`** = the firing ship's ID (player shots too, for consistency). The laser
  owner uses `source` to **freeze its own movement while its laser is live**. This is a general field, not
  laser-only — exact representation (counter ID, enum+id, etc.) is the Programmer's; the *contract* (every
  ship identifiable, every projectile attributable to a ship) is what BA locks.
- **Death attribution → copy:** the game **tracks what dealt the killing blow** (enemy body collision →
  that enemy's name; projectile collision → the owning ship's enemy name via `source`); GAME_OVER shows
  **"Killed by &lt;enemy name&gt;"**. Every lethal source needs a **display name** — including existing
  ones (asteroid/debris, the three enemy kinds, both bosses, and the new laser enemy). The exact string
  format + every source's name are the Writer's; the attribution *contract* (which sources, fallback when
  unknown) is the BA's.

**Open questions left to downstream roles (not pre-decided here):** the new enemy's name/identity/shape/
color and the laser's color + the windup-vs-damaging visual distinction (Designer/Artist); exact windup
(~0.5 s), damaging (~1 s), final width (5–7 px), sweep speed (~0.1×), per-hit damage, laser-enemy HP,
fire cadence, reposition/cooldown duration, spawn weight & earliest spawn time (Designer/Level-designer);
damage cadence while touching (per-frame tick vs once); whether the beam aims at the player at fire-time
or fires straight; the "Killed by …" exact wording + names for every lethal source incl. legacy ones
(Writer); the ship-ID / `source` representation + laser entity shape in code (Programmer).

**Out of scope / unchanged:** existing enemy/boss movesets & stats; the bonus economy; HP/score; screen
flow (only GAME_OVER gains the "Killed by" line); player controls; all existing copy except the new death
line + any laser-enemy naming.

**Scoped roles:** full pipeline — **BA → Designer → Artist → Writer → Level-designer → Programmer → QA.**
