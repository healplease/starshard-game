r"""config — the single source of truth for all tuning numbers, the palette, and
UI strings (Starshard v1 + v2).

This module is **data only**: plain constants, a few pure ramp formulas (just
math), and string/registry tables. It imports nothing game-side (no entities,
systems, or pygame), so every other module can depend on it freely.

Traceability:
  - v1 numbers ............ GDD.md §7.3 (master table) + level_spec.md §3/§6/§7
  - v2 buffs/pickups ...... GDD.md §V2.2/§V2.4 + level_spec.md §V2.1
  - palette ............... art_spec.md §1 (v1) + §V2.1 (v2)
  - strings ............... story.md §5 (v1) + §V2.3 (v2)
Bonus registries are keyed by the **BonusKind name** (the str "REPAIR"/"FAN"/…)
so this module never needs to import the enum (which lives in world.py).
"""

import math

# ── Window / timing (GDD §5, §7.3) ───────────────────────────────────────────
W, H, FPS = 600, 800, 60

# ── Palette — v1 (art_spec §1) ───────────────────────────────────────────────
BG = (10, 12, 22)
STAR_FAR = (90, 100, 130)
STAR_MID = (160, 170, 200)
STAR_NEAR = (235, 240, 255)
PLAYER = (80, 220, 255)
PLAYER_EDGE = (220, 250, 255)
BULLET_P = (120, 255, 245)
ASTEROID_S = (150, 150, 160)
ASTEROID_L = (110, 110, 122)
FLASH = (255, 255, 255)
ENEMY = (255, 70, 200)
ENEMY_EDGE = (255, 180, 235)
BULLET_E = (255, 90, 40)
HP_GREEN = (60, 210, 90)
HP_AMBER = (240, 190, 50)
HP_RED = (230, 60, 60)
HP_BACK = (40, 44, 58)
HP_BORDER = (210, 215, 235)
TEXT = (235, 240, 255)
TEXT_DIM = (140, 148, 170)
OVERLAY = (10, 12, 22)

# ── Palette — v2 bonuses (art_spec §V2.1; 4 new + reuses) ────────────────────
BONUS_REPAIR = HP_GREEN  # reuse — ties repair to the health color
BONUS_FAN = (255, 140, 40)  # #FF8C28 new orange
BONUS_RAPID = PLAYER  # reuse — "your gun" cyan
BONUS_SHIELD = (180, 220, 255)  # #B4DCFF new pale blue
BONUS_SCORE = (255, 210, 70)  # #FFD246 new gold
BONUS_INK = BG  # dark glyph on bright fills
PILL_TRACK = HP_BACK  # empty timer-bar track

# ── Palette — v6 bomb (art_spec §V6.1; 1 new + the flash tint) ───────────────
BONUS_BOMB = (180, 100, 245)  # #B464F5 vivid electric violet — the 6th pickup kind
FLASH_TINT = (240, 248, 255)  # #F0F8FF near-white (cool) — activation flash, ≠ pure-white FLASH

# ── Palette — v7 bosses (art_spec §V7.1; 2 new + reuses) ─────────────────────
# The Mothership is the magenta fleet's capital ship: a dark steel hull trimmed in
# the enemy magenta with a yellow weapon core. Only 2 genuinely new colors.
BOSS_HULL = (52, 44, 74)  # #342C4A dark indigo-violet steel — the massive hull
BOSS_PLATE = (84, 72, 116)  # #544874 mid plate — panel lines (lighter hull step)
BOSS_TRIM = ENEMY  # reuse magenta — hull edge + window-lights (faction read)
BOSS_CORE = (255, 234, 0)  # #FFEA00 reactor/weapon core (== EB_COLOR_YELLOW)
EB_COLOR_YELLOW = (255, 234, 0)  # #FFEA00 NEW — the 3-bullet yellow fan (telegraph)
BOSS_BAR_FILL = ENEMY  # boss health (enemy-faction magenta)
BOSS_BAR_BACK = HP_BACK  # empty track (reuse dark HP track)
BOSS_BAR_EDGE = ENEMY_EDGE  # pink enemy-edge frame

# ── Palette — v16 second boss: NOVA, an electric-blue pulsar core (art_spec §V16.1) ──
# Deliberately the Mothership's opposite: that boss is a DARK indigo carrier trimmed
# magenta with a YELLOW core; NOVA is a RADIANT electric-BLUE star with a white-hot heart.
# 3 genuinely new colors; the white-hot core reuses STAR_NEAR + a FLASH rim.
NOVA_BODY = (60, 90, 255)  # #3C5AFF deep electric blue — the solid star disc (the mass)
NOVA_RAY = (90, 150, 255)  # #5A96FF lighter blue — radiant spikes + inner ring + bar frame
NOVA_BULLET = (74, 124, 255)  # #4A7CFF bright plasma azure — NOVA's bullets + its bar fill/label
NOVA_BAR_FILL = NOVA_BULLET  # draining HP, blue (= NOVA's shot color) — NOT the Mothership magenta
NOVA_BAR_BACK = HP_BACK  # reuse the dark empty track (same as both HP bars)
NOVA_BAR_EDGE = NOVA_RAY  # light-blue frame — second NOVA signal (vs pink ENEMY_EDGE)
NOVA_BULLET_DRAW_R = 6  # plasma body (collision still EB_R = 5) — render-only (art_spec §V16.3)
# NOVA silhouette draw radii (art_spec §V16.2.1) — painted body ⊇ the r=60 collision circle.
NOVA_DISC_R = 62  # solid disc (>= NOVA_R collision)
NOVA_SPIKE_R = 90  # radiant spike tip radius (overall ~180 px)
NOVA_RING_R = 40  # inner energy ring
NOVA_HOT_R = 16  # white-hot core
NOVA_SPIKES = 12
NOVA_SPIKE_HALF_DEG = 7  # spike half-width at the disc edge

# ── Player (GDD §6.1) ────────────────────────────────────────────────────────
P_SPEED, P_R = 5, 13
P_START = (300, 720)
P_MAX_HP = 100
IFRAMES = 60  # i-frames after a hit (R18)

# ── Invulnerability pulse (v11 — supersedes the §V2.5 hard 6-f blink) ──────────
INVULN_ALPHA_FLOOR = 128  # dimmest the ship reaches during invuln (~50% of 255). NEVER 0 — the ship
#   is always at least half-visible. Human spec "~50%" → locked at 128/255 (50.2%).
INVULN_ALPHA_CEIL = (
    255  # brightest point of the pulse = fully opaque (the ship's normal solid look).
)
INVULN_PULSE_PERIOD = 30  # frames per ONE full pulse (bright→floor→bright). 0.5 s @60 FPS = 2 Hz —
#   a clear gentle "breathing" pulse, ~2.5× slower than the old 12-f strobe,
#   well below any flicker-fusion read. Replaces today's 6-f hard half-cycle.

FIRE_CD = 12  # baseline fire cooldown (R7, ~5/s)
PB_SPEED = 10  # player bullet speed
PB_W, PB_H = 4, 12

# ── Asteroids (GDD §6.3) ─────────────────────────────────────────────────────
AST_S_R, AST_L_R = 12, 26
AST_S_SPD = (2.5, 4.0)
AST_L_SPD = (1.5, 2.8)
AST_S_DRIFT, AST_L_DRIFT = 0.5, 0.4
AST_S_SCORE, AST_L_SCORE = 10, 20
AST_S_DMG, AST_L_DMG = 20, 30
AST_CAP = 16  # level_spec §6

# ── Enemy (GDD §6.4) ─────────────────────────────────────────────────────────
EN_R = 13
EN_HP = 2
EN_SCORE = 50
EN_RAM_DMG = 40
EN_ENTRY_SPD = 2  # phase A descent until y >= 120
EN_STRAFE = 2  # phase B horizontal
EN_DESCENT = 0.3  # phase B slow descent
EB_SPEED = 4.5  # enemy bullet aimed speed
EB_R = 5
EB_DMG = 15
EB_CAP = 40  # level_spec §6

# ── v5 enemy roster (GDD §V5.2/§V5.5) ────────────────────────────────────────
# Per-kind: collision r, entry/strafe/descent speed, HP, score, ram dmg, bullet
# family ("RED"/"GREEN"/"CYAN"), bullet speed, fire-cadence multiplier (× the
# ramp base enemy_fire_interval), aim-deviation cone half-angle (degrees).
# REGULAR == today's v1 fighter carried forward (+ the new aim cone, R37).
ENEMY_KINDS = {
    "REGULAR": dict(
        r=13,
        entry=2.0,
        strafe=2.0,
        descent=0.3,
        hp=2,
        score=50,
        ram=40,
        bullet="RED",
        bspeed=4.5,
        fire_mult=1.0,
        cone_deg=12,
    ),
    "HEAVY": dict(
        r=18,
        entry=1.4,
        strafe=1.2,
        descent=0.3,
        hp=4,
        score=80,
        ram=50,
        bullet="GREEN",
        bspeed=4.5,
        fire_mult=1.6,
        cone_deg=6,
    ),
    "SCOUT": dict(
        r=10,
        entry=3.0,
        strafe=3.0,
        descent=0.4,
        hp=1,
        score=60,
        ram=30,
        bullet="CYAN",
        bspeed=7.5,
        fire_mult=1.4,
        cone_deg=3,
    ),
}

# Splitting green pellet (GDD §V5.4): frozen midway distance → 3-red fan.
SPLIT_FRACTION = 0.5  # "midway": fraction of fire-time pellet→player distance
SPLIT_MIN_DIST = 60  # px floor so a point-blank pellet still flies a readable stretch
FAN_HALF_ANGLE = 18  # deg; children at (-18, 0, +18) → exactly 3, center included
CHILD_SPEED = 4.5  # red child speed (= EB_SPEED / pellet speed)

# Enemy-bullet family colors (art_spec §V5.2 final hex). RED reuses v1 BULLET_E.
EB_COLOR_RED = BULLET_E  # #FF5A28 — regular + ALL split children
EB_COLOR_GREEN = (140, 240, 60)  # #8CF03C toxic lime — heavy pellet (drawn larger)
EB_COLOR_CYAN = (45, 205, 255)  # #2DCDFF electric ice — scout streak
EB_COLORS = {
    "RED": EB_COLOR_RED,
    "GREEN": EB_COLOR_GREEN,
    "CYAN": EB_COLOR_CYAN,
    "YELLOW": EB_COLOR_YELLOW,  # v7 boss fan (GDD §V7.12)
    "NOVA": NOVA_BULLET,  # v16 NOVA plasma azure (art_spec §V16.3)
}

# Render-only bullet sizes (collision stays a flat EB_R=5 for every family).
PELLET_DRAW_R = 8  # GREEN pellet drawn r=8 (collision still 5) — "fat & charged"
CYAN_TAIL_LEN = 12  # px length of the scout streak's tail, behind its heading
CYAN_HEAD_R = 4  # px radius of the scout streak's head dot

# Enemy-kind spawn gating (level_spec §V5.1): seconds before HEAVY / SCOUT appear.
HEAVY_GATE = 20
SCOUT_GATE = 50

# ── v6 bombs / panic button (GDD §V6.x, art_spec §V6.5, level_spec §V6.4) ─────
BOMB_START = 2  # charges at run start / after restart (R45; fixed by req)
BOMB_CAP = 4  # max charges; clamp [0, BOMB_CAP] (R45)
BOMB_LOCKOUT = 18  # frames X is ignored after a successful activation (R53; == FLASH_FRAMES)
BOMB_FLUSH_SCORE = 0  # flush awards NO score — silent despawn (R48 ruling, §V6.3)
BOMB_SPAWN_LULL = 0  # post-bomb spawn lull (R55) — level_spec §V6.4 sets it to 0 (no lull)
BOMB_PICKUP_CHARGES = 1  # +1 charge per bomb pickup, clamped to BOMB_CAP (GDD §V6.6)

FLASH_FRAMES = 18  # full-screen activation flash duration, 0.30 s (GDD §V6.5)
FLASH_PEAK_ALPHA = 200  # ~78% peak opacity; linear fade to 0 over FLASH_FRAMES (art_spec §V6.5)
FLASH_COLOR = FLASH_TINT  # #F0F8FF near-white (art_spec overrides GDD §V6.11 default)

# Bomb-count HUD readout — icon + ×N, top-right under the HP bar (art_spec §V6.3).
BOMB_HUD_RIGHT = 588  # right edge — aligned with the HP bar's right edge (468 + 120)
BOMB_HUD_Y = 34  # top of the readout row — 8 px below the HP bar (ends at y=26)
BOMB_ICON_R = 6  # radius of the small bomb-sphere icon
BOMB_PICKUP_POPUP_TEXT = (
    f"+{BOMB_PICKUP_CHARGES} BOMB"  # "+1 BOMB" (story §V6.3); auto-tracks the delta
)

# ── v7 bosses / periodic Mothership (GDD §V7.16) ─────────────────────────────
# Breakpoint (R56) — TIME-based fixed marks; reconciled with AC13 (§V7.2).
BOSS_FIRST_MARK = 75  # seconds of PLAY before the FIRST boss (frame 4500)
BOSS_INTERVAL = 90  # seconds between bosses → marks 75, 165, 255, …
#   trigger when t reaches the next mark AND no boss active; ONE run clock never pauses.

# Boss stats (R59/R60/R61).
BOSS_HP = 120  # player-bullet hits; 1 dmg/bullet (~12–24 s fight, AC13 lever)
BOSS_HP_MAX = BOSS_HP  # bar fills boss_hp / BOSS_HP_MAX (art_spec §V7.3)
BOSS_R = 70  # collision circle radius (huge → always hittable, R60)
BOSS_SPAWN = (300, -80)  # ARRIVAL spawn (off-screen top, centred)
BOSS_ENTRY_SPEED = 2.0  # px/f straight-down entrance; ~240 f (~4 s) to y=400
BOSS_REST_Y = 400  # settles at the screen vertical centre (H/2), R59
BOSS_OSC_AMP = 120  # px; oscillate x in [180, 420] about x=300 (=W/2)
BOSS_OSC_SPEED = 1.5  # px/f constant ping-pong (reverse at bounds)
BOSS_FIRST_STEP_DELAY = 60  # f after settle before moveset step 1 (no attack during entrance)
BOSS_RAM_DMG = 60  # body-contact damage (> HEAVY 50 > REGULAR 40; not a one-shot)
#   boss bullets (yellow fan + red children) reuse EB_DMG = 15 (R61).

# Moveset (R66) — fixed order 1→2→3→4 looping until defeat.
BOSS_STEP_INTERVAL = 150  # f between steps (2.5 s); full 4-step cycle = 600 f = 10 s
MINION_CAP = 14  # max alive boss-minions (= one full 5+2+7 wave; AC49 1st cycle never capped)
BOSS_WAVE = {  # step -> (kind, count) — exact counts (R67/AC49)
    1: ("REGULAR", 5),
    2: ("HEAVY", 2),
    3: ("SCOUT", 7),
}

# Attack-4: yellow fan → 12-red 360° ring (R68) — reuses the v5 frozen split (§V5.4).
YELLOW_FAN_SPREAD = 20  # deg; flanks at ±20° about the boss->player heading (40° wide)
YELLOW_SPEED = 4.5  # px/f (= EB_SPEED); yellow bullets are damaging in flight (EB_DMG=15)
YELLOW_SPLIT_DIST = 200  # px frozen "midway"; split_timer = round(200/4.5) ≈ 44 f
RED_RING_COUNT = 12  # red children total, even 360° ring (headings k*30°, k=0..11)
RED_CHILD_SPEED = 4.5  # px/f (= CHILD_SPEED/EB_SPEED); flat EB_DMG=15; terminal, never re-split
#   the 3 yellow bullets each burst into 4 interleaved ring quarters (ring_phase 0/30/60 + k*90°).

# Reward + bomb rule (R62/R63).
BOSS_KILL_SCORE = 1000  # flat defeat reward (via scoring.award; Score×2 doubles it)
BOMB_BOSS_CHIP = 0  # player bomb during fight: clears minions+bullets, boss IMMUNE (§V7.14)
BOSS_DEFEAT_POPUP_LIFE = 60  # frames the "MOTHERSHIP DOWN" + "+points" popup shows (story §V7.4)

# ── v16 second boss — NOVA (energy-weapon core; projectile-only) — GDD §V16.8 ──
# NOVA reuses the v7 entrance(300,-80)/2.0, rest y=400, osc ±120@1.5, settle+60 VERBATIM
# (BOSS_SPAWN/ENTRY_SPEED/REST_Y/OSC_*). Only the per-boss values below differ; the
# Mothership keeps its v7 numbers untouched. "Deadlier via ATTACKS, not HP-sponge" (R104).
NOVA_HP = 120  # = Mothership; "large" (R60). Deadlier via attacks (R104).
NOVA_R = 60  # collision circle (huge → always hittable R60); compact-core silhouette
NOVA_RAM_DMG = 80  # body contact (> Mothership 60) — deadlier; still < 100 HP (survivable)
NOVA_KILL_SCORE = (
    1500  # flat defeat reward (> Mothership 1000); via scoring.award (Score×2 doubles)
)

# NOVA bullets — ordinary EnemyBullets (existing enemy-bullet × player path), terminal.
NOVA_BULLET_DMG = 25  # > Mothership EB_DMG 15 — HEADLINE deadlier lever (AC92)
NOVA_BULLET_SPEED = 5.5  # > Mothership 4.5 — faster, harder to dodge
NOVA_LANCE_SPEED = 6.0  # px/f, step-3 LANCE (fastest)

# Moveset (R66 structure reused) — 4 steps, fixed order 1→2→3→4 loop. PROJECTILE-ONLY (R103).
NOVA_STEP_INTERVAL = (
    90  # f (1.5 s) between steps (< Mothership 150) — deadlier fire-rate; cycle 360 f
)
NOVA_FIRST_STEP_DELAY = 60  # f after settle before step 1 (mirrors v7 BOSS_FIRST_STEP_DELAY)
NOVA_RING_PHASE_STEP = (
    9  # deg; ring start-angle advances each step → ring precesses (never identical)
)
# step 1 RAKE  — aimed spread : boss->player ± {0,15,30}        -> 5 bullets @ NOVA_BULLET_SPEED
# step 2 BURST — dense ring   : k*15 + ring_phase (k=0..23)     -> 24 bullets @ NOVA_BULLET_SPEED
# step 3 LANCE — aimed stream : boss->player; 4 spaced by GAP_F -> 4 bullets @ NOVA_LANCE_SPEED
# step 4 ARC   — aimed wall   : boss->player ± {0,15,30,45,60}  -> 9 bullets @ NOVA_BULLET_SPEED
NOVA_SPREAD_COUNT = 5
NOVA_SPREAD_STEP_DEG = 15  # spread bullets at ±15, ±30 about the aim
NOVA_RING_COUNT = 24
NOVA_RING_STEP_DEG = 15  # 360/24
NOVA_LANCE_COUNT = 4
NOVA_LANCE_GAP_F = 4  # frames between LANCE bullets (realised as a fixed along-heading spacing)
NOVA_ARC_COUNT = 9
NOVA_ARC_STEP_DEG = 15  # 9 bullets over ±60 = 120-deg arc, centred on the player
# The boss pool / registry (BOSS_POOL + BOSS_SPECS) + selection are defined AFTER the
# boss strings below, since each spec bundles its name/HUD literals.

# ── Particles (GDD §6.7) ─────────────────────────────────────────────────────
PART_LIFE = 20
PART_CAP = 60

# ── v2 bonus pickups & buffs (GDD §V2.2/§V2.4, level_spec §V2.1) ──────────────
BONUS_PICKUP_R = 13  # collide radius (GDD §V2.4)
BONUS_HALF_DIAG = 13  # diamond half-diagonal (26 px point-to-point)
BONUS_SPEED = 2.0  # flat drift, NOT ramp-accelerated
BONUS_CAP = 3  # max on-screen, both spawn paths combined
DRIP_MIN, DRIP_MAX = 600, 840  # drip cadence: randint(600,840) f (12 s ±2 s)
ENEMY_DROP_CHANCE = 0.15  # bullet-kill drop chance (not ram-kills)

REPAIR_HP = 40  # instant heal, clamp to P_MAX_HP, no overheal
REPAIR_POPUP_LIFE = 30  # transient "+40" popup lifetime (frames)
REPAIR_POPUP_TEXT = f"+{REPAIR_HP}"  # auto-tracks REPAIR_HP (story §V2.2)

RAPID_CD = FIRE_CD // 2  # rapid: 12 f → 6 f cooldown (GDD §V2.2)
FAN_ANGLES_DEG = (-12, 0, 12)  # 3-beam spread (GDD §V2.2)
SCORE_MULT = 2  # Score×2 multiplier (R34)

# Timed-buff durations (frames @60 FPS), keyed by BonusKind name. Repair is
# instant and intentionally absent.
BUFF_DURATION = {"FAN": 480, "RAPID": 480, "SHIELD": 300, "SCORE": 600}
# HUD pill stack order — stable BonusKind enum order, Repair excluded (GDD §V2.6).
TIMED_ORDER = ("FAN", "RAPID", "SHIELD", "SCORE")

# Per-kind letter (story §V2.3) and color (art_spec §V2.1) — keyed by name.
# Per-kind letter + color + name. v6 appends a 6th BOMB entry (story §V6.1 glyph
# "B", art_spec §V6.1 violet) — instant pickup, exempt from the timed-pill HUD.
BONUS_LETTERS = {"REPAIR": "+", "FAN": "F", "RAPID": "R", "SHIELD": "S", "SCORE": "2", "BOMB": "B"}
BONUS_COLORS = {
    "REPAIR": BONUS_REPAIR,
    "FAN": BONUS_FAN,
    "RAPID": BONUS_RAPID,
    "SHIELD": BONUS_SHIELD,
    "SCORE": BONUS_SCORE,
    "BOMB": BONUS_BOMB,
}
BONUS_NAMES = {  # canonical labels (not drawn on the HUD)
    "REPAIR": "REPAIR",
    "FAN": "FAN",
    "RAPID": "RAPID",
    "SHIELD": "SHIELD",
    "SCORE": "SCORE ×2",
    "BOMB": "BOMB",
}
# Kind-weight ladder: roll r=randint(0,99); first (threshold >= r) wins. v6 re-slices
# the v2 table (Shield 15→12, Score 15→12) and appends BOMB=6 — the rarest kind, both
# spawn paths sharing this one ladder (level_spec §V6.1). Sums to 100.
#   0–29 Repair · 30–49 Fan · 50–69 Rapid · 70–81 Shield · 82–93 Score · 94–99 BOMB
BONUS_WEIGHTS = (
    (29, "REPAIR"),
    (49, "FAN"),
    (69, "RAPID"),
    (81, "SHIELD"),
    (93, "SCORE"),
    (99, "BOMB"),
)

# ── Smoke-test seeding (GDD §V2.5 / level_spec §V2.5) ────────────────────────
SMOKE_FRAMES = 120
SMOKE_SEED = 1234

# ── SMOKE_TIMELINE — the single source of truth for every headless seed frame +
# their ordering (v9 process-hardening, retro T4/A12). `app.run()` iterates THIS
# table; no other code hard-codes a smoke seed frame. Each row is
# (frame, event, note); `event` keys the seed action dispatched in app._run_smoke_seeds.
# All five v5/v6/v7 seeds must coexist inside the 120-frame budget without colliding,
# so the schedule lives in one place and `smoke_timeline_ok()` proves it stays sane.
SMOKE_TIMELINE = (
    (
        2,
        "bonus",
        "short Rapid pickup in the player's path → full spawn→collect→apply→expire (AC20)",
    ),
    (3, "split", "GREEN pellet already in flight → bursts ~f16 into 3 RED children (AC27)"),
    (
        20,
        "bomb",
        "scripted X key-down edge → flush clears the field + the split children (AC30/32/33)",
    ),
    (
        38,
        "boss_target",
        "2 asteroids + 1 enemy so the FREE arrival clear has a visible target (AC40)",
    ),
    (
        40,
        "boss",
        "force boss: free arrival flush + compressed entrance + yellow→12-red (AC41/49/50/51)",
    ),
)


def _smoke_frame(event):
    """Look up the canonical frame for a SMOKE_TIMELINE event (single source)."""
    return next(f for f, ev, _ in SMOKE_TIMELINE if ev == event)


def smoke_timeline_ok():
    """Ordering invariant (v9): seed frames are strictly increasing, unique, and
    all fall inside the 120-frame smoke budget. A new seed that collides with an
    existing one or overruns the budget trips this — caught by the regression gate
    before it can silently corrupt the headless coverage."""
    frames = [f for f, _, _ in SMOKE_TIMELINE]
    return (
        frames == sorted(frames)
        and len(set(frames)) == len(frames)
        and all(0 <= f < SMOKE_FRAMES for f in frames)
    )


SMOKE_BONUS_KIND = "RAPID"  # force-seed a Rapid in the player's path
SMOKE_BONUS_POS = (300, 700)  # player x, 20 px above (inside 26 px collide)
SMOKE_BONUS_DUR = 60  # shortened so it expires by ~frame 63
SMOKE_SEED_FRAME = _smoke_frame("bonus")  # from SMOKE_TIMELINE (single source)

# v5 split lifecycle seed (GDD §V5.6): one green pellet already in flight, heading
# straight down the player column with a forced short split distance, so it bursts
# early (S=60 → split_timer=round(60/4.5)=13 → splits ~frame 16) and the 3 red
# children update through frame 120 — full fire→travel→split→children path headless.
SMOKE_SPLIT_FRAME = _smoke_frame("split")  # from SMOKE_TIMELINE (single source)
SMOKE_SPLIT_POS = (300, 300)  # above the player, on its x column
SMOKE_SPLIT_HEADING = (0.0, 1.0)  # straight down toward the player
SMOKE_SPLIT_DIST = SPLIT_MIN_DIST  # force the short, early burst

# v6 bomb activation seed (GDD §V6.10): scripted X key-down ~f20 (after the ~f16
# split) — one flush clears the seeded enemy + remaining asteroids + the 3 red
# split children (charge 2→1, flash f20→~f38). Starts at BOMB_START charges, so
# no charge seeding is needed; only the timed press.
SMOKE_BOMB_FRAME = _smoke_frame("bomb")  # from SMOKE_TIMELINE (single source)

# v7 boss seed (GDD §V7.15): force a boss @ ~f40, AFTER the v5 (f16) + v6 (f20)
# seeds. A token target is pre-seeded @f38 so the free arrival clear has something
# visible to remove (AC40). The boss spawns near its rest position (short entrance)
# and runs a COMPRESSED moveset so arrival-clear + entrance + step 1 + the yellow→
# 12-red split all fire inside 120 f. The boss is NOT defeated (HP 120 stands);
# the run still exits 0 after exactly 120 frames.
SMOKE_BOSS_PRESEED_FRAME = _smoke_frame("boss_target")  # SMOKE_TIMELINE (single source)
SMOKE_BOSS_FRAME = _smoke_frame("boss")  # SMOKE_TIMELINE (single source)
SMOKE_BOSS_SPAWN = (300, 360)  # short entrance → settles (~f60) in-budget
SMOKE_BOSS_SPLIT_DIST = 45  # px shortened "midway" → split_timer = round(45/4.5) = 10 f
SMOKE_BOSS_STEP_DELAY = 6  # compressed: first step ~6 f after settle
SMOKE_BOSS_STEP_INTERVAL = 6  # compressed: steps every 6 f → step 4 ~f84, split ~f94
# v16: force which boss the smoke (and pytest) drive — bypasses the uniform pool draw so
# coverage is deterministic (R105/§V16.7). Drives NOVA's projectile-only moveset headlessly.
SMOKE_BOSS_TYPE = "NOVA"  # the forced boss type for the headless seed (must be in BOSS_POOL)

# ── AC13 balance probe (v9, retro T2/A10) ────────────────────────────────────
# A headless instrument (NOT a pass/fail gate): run K deterministic scripted runs
# of the REAL play pipeline under the live difficulty ramp until the auto-pilot
# dies (or a hard cap), then report median / 95th-percentile survival seconds. This
# replaces the 8-increment "AC13 is untestable" stalemate with an actual number
# trend the team can watch across versions. The auto-pilot is the fixed smoke sweep
# (deterministic, non-dodging) so the figure is comparable run-to-run; it is a naive
# lower-bound proxy, not an expert dodger (documented in the probe output).
BALANCE_PROBE_RUNS = 15  # default number of scripted runs (override via CLI arg)
BALANCE_PROBE_CAP_FRAMES = 14400  # 240 s @60 — bound a never-dying run; censored if hit

# ── HUD geometry (art_spec §4.3, §V2.3) ──────────────────────────────────────
HP_BAR = (468, 12, 120, 14)  # (x, y, w, h); Rect built in view
PILL_X, PILL_TOP, PILL_ROW_H = 12, 36, 18
PILL_BOX, PILL_BAR_W, PILL_BAR_H, PILL_BAR_GAP = 14, 40, 6, 4
REPAIR_POPUP_POS = (528, 30)  # centered at HP-bar center x

# Boss health bar — wide, center-top, drains right→left (art_spec §V7.3). Only
# drawn while a boss is active; the center-top band is empty in normal play (AC47).
BOSS_BAR = (140, 52, 320, 16)  # (x, y, w, h); clear of HP bar / pills / bomb readout / score
BOSS_LABEL_CENTER = (300, 50)  # midbottom of the "MOTHERSHIP" label, just above the bar
BOSS_WARN_CENTER = (300, 400)  # centre-screen WARNING banner (ARRIVAL→ENTRANCE, story §V7.3)
BOSS_DEFEAT_CENTER = (300, 400)  # "MOTHERSHIP DOWN" + "+points" popup on defeat (story §V7.4)

# ── Font sizes (art_spec §4.1, §V2.2) ────────────────────────────────────────
FONT_HUD, FONT_BIG, FONT_MID, FONT_SMALL = 28, 64, 32, 22
FONT_PICKUP, FONT_PILL = 22, 18

# ── Strings (story §5 / §V2.3) ───────────────────────────────────────────────
TITLE = "STARSHARD"
PITCH = "Dodge the rocks. Gun the rest. Beat your best."
# v6: rewritten to teach Z=fire / X=bomb; old "FIRE  Space" is a defect (story §V6.4, AC35).
CONTROLS_1 = "MOVE  Arrows / WASD      Z = fire · X = bomb"
# v10 ⚠ REWRITE (story §V10.3): drop the now-duplicate quit clause — the gesture is
# taught once on START via its own arc-anchored START_QUIT_HINT line. Esc still never quits.
CONTROLS_2 = "Esc  Pause"
START_PROMPT = "Press any key to fly"
# v10 (story §V10.2): dedicated START quit-hint line, top-y 600 (arc 56 px below at
# START_ARC_CENTER). Wording is intentionally identical to PAUSE_HINT_QUIT — one mental model.
START_QUIT_HINT = "Hold Q  Quit"
GAMEOVER_TITLE = "GAME OVER"
# v10 ⚠ REWRITE (story §V10.4): Q-hold now quits from GAME_OVER (R77), so the key list
# gains the honest quit hint. No stale "Esc Quit" (v8 R73 holds).
# v12 ⚠ REWRITE (story §V12.3): Restart is now a 0.5 s HOLD gesture (RESTART_HOLD_FRAMES=30),
# so the restart clause teaches the hold; the v10 "Hold Q  Quit" clause is unchanged.
GAMEOVER_KEYS = "Hold R  Restart      Hold Q  Quit"

# v7 boss copy (story §V7.5). Name blessed verbatim; label == name (AC47-safe, ≤12 ch).
BOSS_NAME = "MOTHERSHIP"  # canonical boss name
BOSS_LABEL_TEXT = BOSS_NAME  # drawn on the boss bar (FONT_HUD, magenta)
BOSS_WARN_1 = "WARNING"  # arrival klaxon (ARRIVAL→ENTRANCE, fades before settle)
BOSS_WARN_2 = "MOTHERSHIP INBOUND"  # intro + name reveal
BOSS_DEFEAT_TEXT = "MOTHERSHIP DOWN"  # defeat flavor line; "+{points}" tracks the real award

# v16 NOVA copy (story §V16.5). Name blessed verbatim; label == name (4 chars ≪ AC47 envelope).
NOVA_NAME = "NOVA"  # canonical boss name (code/docs/QA)
NOVA_LABEL_TEXT = NOVA_NAME  # drawn on the NOVA bar (FONT_HUD, NOVA blue)
NOVA_WARN_1 = "WARNING"  # klaxon heading — reuse the boss-agnostic literal
NOVA_WARN_2 = "NOVA INBOUND"  # intro + name reveal (12 chars)
NOVA_DEFEAT_TEXT = "NOVA DOWN"  # defeat flavor line; "+{points}" tracks the real award

# ── Boss pool / registry + uniform-random selection (R99/R100, level_spec §V16.1) ──
# BOSS_POOL is the ORDERED roster (the single source of the line-up — nothing hard-codes
# "two bosses"). A boss SPEC is the per-boss data the unchanged v7 loop reads instead of
# hard-coded Mothership numbers: stats + bar colors + name/HUD strings. The moveset is
# dispatched by `type` in systems/encounter; the body silhouette by `type` in view/render.
# Adding boss #3 = ONE more BOSS_SPECS entry + its type string in BOSS_POOL (N = pool length,
# selection + loop need zero edits — AC86). The Mothership spec = its existing v7 values.
BOSS_SPECS = {
    "MOTHERSHIP": dict(
        hp=BOSS_HP,
        r=BOSS_R,
        ram_dmg=BOSS_RAM_DMG,
        kill_score=BOSS_KILL_SCORE,
        step_interval=BOSS_STEP_INTERVAL,
        first_step_delay=BOSS_FIRST_STEP_DELAY,
        split_dist=YELLOW_SPLIT_DIST,  # Mothership-only (the yellow-fan frozen midway)
        bar_fill=BOSS_BAR_FILL,
        bar_back=BOSS_BAR_BACK,
        bar_edge=BOSS_BAR_EDGE,
        name=BOSS_NAME,
        label=BOSS_LABEL_TEXT,
        warn1=BOSS_WARN_1,
        warn2=BOSS_WARN_2,
        defeat=BOSS_DEFEAT_TEXT,
    ),
    "NOVA": dict(
        hp=NOVA_HP,
        r=NOVA_R,
        ram_dmg=NOVA_RAM_DMG,
        kill_score=NOVA_KILL_SCORE,
        step_interval=NOVA_STEP_INTERVAL,
        first_step_delay=NOVA_FIRST_STEP_DELAY,
        split_dist=YELLOW_SPLIT_DIST,  # unused by NOVA (no yellow fan); kept for a uniform shape
        bar_fill=NOVA_BAR_FILL,
        bar_back=NOVA_BAR_BACK,
        bar_edge=NOVA_BAR_EDGE,
        name=NOVA_NAME,
        label=NOVA_LABEL_TEXT,
        warn1=NOVA_WARN_1,
        warn2=NOVA_WARN_2,
        defeat=NOVA_DEFEAT_TEXT,
    ),
}
BOSS_POOL = ("MOTHERSHIP", "NOVA")  # ordered roster; N = len(BOSS_POOL) (today ½/½)

# ── v8 pause: heading + three hint lines (FONT_SMALL / TEXT_DIM, centered at W//2) ──
PAUSE_TITLE = "PAUSED"  # FONT_BIG 64, PLAYER cyan #50DCFF
PAUSE_HINT_RESUME = "Esc  Resume"  # hint line 1 — second Esc resumes
PAUSE_HINT_QUIT = "Hold Q  Quit"  # hint line 2 — Q held 0.5 s quits
PAUSE_HINT_RESTART = "Hold R  Restart"  # hint line 3 — v12: R is now a 0.5 s hold gesture

# ── v8 pause overlay geometry (art_spec §V8.3, GDD §V8.3/§V8.4/§V8.6) ─────────
PAUSE_DIM_ALPHA = 110  # full-screen dim opacity (< GAME_OVER 160 = temporary-state read)
PAUSE_HEADING_Y = 290  # top of "PAUSED" heading blit (FONT_BIG 48 px → center y 314)
PAUSE_HINT_Y1 = 358  # top of resume hint blit     (FONT_SMALL 18 px → center y 367)
PAUSE_HINT_Y2 = 388  # top of Q-hold hint blit     (FONT_SMALL 18 px → center y 397)
PAUSE_HINT_Y3 = 418  # top of restart hint blit    (FONT_SMALL 18 px → center y 427)
PAUSE_PANEL_Y = 427  # pause_panel_y anchor (= center of hint3)
PAUSE_ARC_R = 22  # Q-hold arc radius in px (GDD §V8.4)
PAUSE_ARC_STROKE = 3  # Q-hold arc stroke width
PAUSE_QUIT_FRAMES = 30  # hold duration to quit (0.5 s @ 60 FPS)

# v12 (GDD §V12.2/§V12.10): hold-R-to-restart reuses the v8 quit threshold VERBATIM —
# a self-documenting alias bound to the single source of truth, so the two gestures stay
# symmetric from one value. Drives fill = r_hold_frames / RESTART_HOLD_FRAMES.
RESTART_HOLD_FRAMES = PAUSE_QUIT_FRAMES  # 30 — coupled to PAUSE_QUIT_FRAMES, not a 2nd literal

# ── v10 Q-hold-to-quit arc centres on START + GAME_OVER (art_spec §V10.4) ─────
# Reuse the v8 arc visual verbatim (PAUSE_ARC_R=22, PAUSE_ARC_STROKE=3, CW from 12
# o'clock, HP_AMBER fill / HP_BACK track). Each centre sits 56 px below its screen's
# quit-hint line (the v8 PAUSE offset). The whole widget is drawn ONLY while held on
# these two screens (draw_pause's always-on track is unchanged). Bounding rects:
#   START    : (278, 643, 44, 44) — clears the START text block (lowest rect ≤ y618)
#   GAME_OVER: (278, 523, 44, 44) — clears GAMEOVER_KEYS (y480–498)
START_ARC_CENTER = (W // 2, 665)  # (300, 665) — 56 px below the START quit-hint (top 600)
GAMEOVER_ARC_CENTER = (W // 2, 545)  # (300, 545) — 56 px below GAMEOVER_KEYS (centre 489)

# ── v14 STATS screen geometry (art_spec §V14a.4) ─────────────────────────────
STATS_TITLE_Y = 130  # midtop of title (FONT_BIG)
STATS_DIV_HEADER_Y = 204  # rule under title
STATS_DIV_HEADLINE_Y = 304  # rule under the highscore headline
STATS_BAND_L = 100  # label rail (midleft x) / divider left
STATS_BAND_R = 500  # value rail (midright x) / divider right
STATS_ROW_CY = (264, 344, 404, 464, 524)  # center-y per row, order = V14a.1
STATS_HINT_Y = 712  # midtop of back hint (FONT_SMALL)

# ── v14 STATS-screen strings (story §V14.1; row labels = R92 fields → human) ──
STATS_TITLE = "LIFETIME STATS"  # FONT_BIG, PLAYER cyan (like START title)
STATS_LBL_HIGHSCORE = "HIGH SCORE"  # FONT_MID, headline row (= GAME_OVER BEST datum)
STATS_LBL_RUNS = "RUNS"  # FONT_MID
STATS_LBL_ENEMIES = "ENEMIES"  # FONT_MID
STATS_LBL_ASTEROIDS = "ASTEROIDS"  # FONT_MID
STATS_LBL_BOSSES = "BOSSES"  # FONT_MID
STATS_HINT = "Tab / Esc  Back"  # FONT_SMALL, TEXT_DIM, back hint

# ── v14 START Tab-stats hint line (story §V14.2; FONT_SMALL / TEXT_DIM, centered, y≈530) ──
START_STATS_HINT = "Tab  Stats"  # START: Tab opens the STATS screen (gdd §V14.3)

# ── v13 Restart-arc shares the Q-arc centre + violet fill (art_spec §V13.2/§V13.3) ──
# R arc now = its screen's Q-arc centre (co-located; overlap on dual-hold is intended).
# Geometry/fill-mapping/idle-visibility all per v12; ONLY centre + fill colour change.
#   fill colour = BONUS_BOMB (#B464F5, reused from v6) — Q fill stays HP_AMBER.
#   PAUSE    R centre = (300, 483) = PAUSE Q-arc centre
#   GAME_OVER R centre = (300, 545) = GAMEOVER_ARC_CENTER
PAUSE_RESTART_ARC_CENTER = (W // 2, PAUSE_PANEL_Y + 56)  # (300, 483)
GAMEOVER_RESTART_ARC_CENTER = (W // 2, 545)  # (300, 545)


# ── Difficulty ramp (level_spec §3) — pure formulas, t = seconds in run ───────
def asteroid_interval(t):
    return max(22, 64 - 0.47 * t)


def enemy_interval(t):
    return max(60, 130 - 0.60 * t)


def enemy_fire_interval(t):
    return max(55, 95 - 0.35 * t)


def enemy_cap(t):
    return min(6, 2 + int(t // 20))


def hazard_speed_bonus(t):
    return min(2.0, 0.020 * t)


def large_chance(t):
    return min(0.40, 0.25 + 0.0017 * t)


def pick_bonus_kind(rng):
    """Roll the §V2.1 weight ladder once; return a BonusKind *name* (str)."""
    r = rng.randint(0, 99)
    for threshold, name in BONUS_WEIGHTS:
        if r <= threshold:
            return name
    return BONUS_WEIGHTS[-1][1]  # unreachable (last threshold is 99)


def pick_boss_type(rng):
    """Uniform i.i.d. pick of one boss type from BOSS_POOL — probability 1/N for N
    entries, independent per spawn event (repeats allowed; no no-repeat/shuffle-bag),
    N read from the pool length so a new boss is one BOSS_POOL entry (R99/R100/§V16.1)."""
    return BOSS_POOL[rng.randrange(len(BOSS_POOL))]


def choose_enemy_kind(t, rng):
    """Pick the kind for one spawning enemy (level_spec §V5.1). Deterministic
    ladder over the ramp bands, folded into the unchanged v1 spawner — variety
    REPLACES a fraction of REGULAR spawns, it never adds to enemy_cap(t). Warmup
    returns REGULAR *without* drawing rng, so the smoke window stays REGULAR-only
    and the §V5.6 seeded pellet is the run's only split (AC27)."""
    if t < HEAVY_GATE:  # Warmup (t<20) — REGULAR only (kind-mix == v1)
        return "REGULAR"
    r = rng.randint(0, 99)
    if t < SCOUT_GATE:  # Heat-up (20–50) — R85 / H15
        return "HEAVY" if r < 15 else "REGULAR"
    if t < 90:  # Squeeze (50–90) — R60 / H15 / Sc25
        if r < 60:
            return "REGULAR"
        if r < 75:
            return "HEAVY"
        return "SCOUT"
    if r < 55:  # Storm (t>=90) — R55 / H15 / Sc30
        return "REGULAR"
    if r < 70:
        return "HEAVY"
    return "SCOUT"


# Fan beam velocities precomputed from FAN_ANGLES_DEG (vx, vy), straight-up = 0°.
FAN_VELOCITIES = tuple(
    (PB_SPEED * math.sin(math.radians(a)), -PB_SPEED * math.cos(math.radians(a)))
    for a in FAN_ANGLES_DEG
)
SINGLE_VELOCITY = ((0.0, float(-PB_SPEED)),)  # baseline single forward shot
