# Shared / cross-cutting — change log (orchestrator + programmer)

> Decision notes that don't belong to a single spec folder: orchestrator routing/kickoff/closeout and
> the programmer's build notes. Per-domain notes live in each role folder's own `history.md`. The
> one-line cross-role story lives in `handoffs.md` (active) and `../archive/handoffs-v1.md` (older).

## v1 — "Starshard" (shipped & passed QA, 2026-06-05)
- 2026-06-05 (kickoff): Theme chosen — top-down auto-scrolling 2D space shooter (working title
  "Starshard"). Player ship dodges asteroids/debris and fights enemy ships; arcade score + lives.
  Scope guardrails reaffirmed: single screen, keyboard-only, shapes-only art, `--smoke-test` required.
  (v1 ground rule: main.py < ~500 lines — **later retired in v2**.) Full v1 status summary archived in
  `../archive/project-log-v1.md`.
- 2026-06-05 (v1 programmer): single `workspace/game/main.py` implemented (499 lines, shapes/text only,
  no asset files). All MUST R1–R14; SHOULD R15 (full level_spec ramp), R16 (start screen), R17 (flash +
  death particles), R18 (i-frames); COULD R19 (session BEST). `--smoke-test` exits 0 after exactly 120
  headless frames, 3× stable, warning-free on Python 3.14 / pygame-ce 2.5.7.
- 2026-06-05 (v1 orchestrator): project **DONE / shipped v1**. No FAIL → no route-back. Parked one
  non-blocking item: AC13 expert pure-dodging can exceed 3 min (level_spec §8 levers IF a playtest confirms).

## v2 — Pickup bonuses + modular MVC refactor (shipped 2026-06-05)
- 2026-06-05 (v2 kickoff, orchestrator): Human requested **pickup bonuses/power-ups** (repair, spread/fan
  fire, rapid fire, shield/invuln — designer may add more) and **retiring the ~500-line cap** in favor of a
  modular MVC-ish split of `workspace/game/`. Updated CLAUDE.md ground rules (cap retired, smoke-test
  preserved) and brief.md (v2 increment section). Pipeline: BA → designer → artist → writer → level-designer
  → programmer (refactor + feature) → QA → orchestrator.
- 2026-06-05 (v2 programmer): single `main.py` refactored into the GDD §V2.9 MVC package under
  `workspace/game/` — `config` / `world` (+GameState/BonusKind enums) / `input` / `entities`
  (player,hazards,projectiles,bonus+registry,fx) / `systems` (spawning,physics,combat,buffs,scoring) /
  `view` (render,hud) + a **thin `main.py`**; `app.py` owns the state machine + loop + smoke harness.
  ~1205 lines / 19 files at handoff (no cap; C3 retired). Dep direction respected — only systems/app mutate
  World, view is read-only. **All v2 MUST built** (R23 diamond pickup; R24 Repair +40 clamp/no-overheal;
  R25 Fan 3 beams; R26 Rapid cd 12→6; R27 Shield full-invuln + ring; R28 both spawn paths drip+15%-bullet-kill
  cap 3; R29 buff-pill HUD + "+40" popup; R30 independent timers + hard refresh; R31 expiry→revert +
  `reset_run()` cleanup; **R34 Score×2**). **R33 smoke gate green** + Rapid lifecycle from the §V2.5 seed
  (seeded f2 → collected f2 → cd 6 → expired f61 → reverted cd 12), 3× stable + `-m game.main` clean.
  v1 R1–R18 + smoke gate intact (no regression).
- 2026-06-05 (v2 orchestrator): v2 **DONE / shipped**. QA PASS, no FAIL → no route-back. Package modular
  (21 files / 1222 lines, 36-line main.py, C3 retired). Two non-blocking items parked IF a human playtest
  confirms: (1) AC13 expert pure-dodging can exceed 3 min — level_spec §8 / §V2.4 levers; (2) R35
  screen-clear bonus deferred (GDD §V2, non-failing).

## v3 — Knowledge-base reorganization (Manager, 2026-06-05)
- 2026-06-05 (v3, manager): New **manager** role introduced. Reorganized the flat `workspace/` into
  per-role scope folders (requirements/ design/ art/ story/ levels/ qa/ + shared/ + archive/), keeping
  every spec body verbatim so it still matches the shipped code. Pulled the growing narrative out of the
  hot path: the old `backlog.md` "Notes/decisions" + "Status summary" prose was distributed into each
  domain's `history.md` (and this file); v1 handoffs moved to `../archive/`. Goal: a role now loads its
  own small spec + `shared/` instead of the whole project history. See `../README.md` for the map.

## v4 — Standing QA documentation (shipped 2026-06-05)
- 2026-06-05 (v4, orchestrator → qa): Human asked for **durable QA docs** (separate from the per-run
  `qa_report.md`). QA produced `qa/feature_inventory.md` (**32 features F1–F32** across v1+v2 traced to
  R#/AC#/module, incl. the intentional gaps R35/R20/R22) and `qa/test_plan.md` (the 120-f smoke plan +
  the full v1+v2 regression plan + per-feature checklists). No game code changed; smoke gate re-run →
  exit 0; checklist authoring surfaced **no defects** → no route-back. Orchestrator declared v4 DONE.

## v5 — Three enemy types (shipped 2026-06-05)
- 2026-06-05 (v5, orchestrator): Human wanted **enemy variety** — keep the existing enemy but add an aim
  *deviation*, plus a HEAVY (bigger/slower, GREEN splitting pellet → 3 RED fan children) and a SCOUT
  (faster/fragile, fast accurate CYAN). Framed in `brief.md` (v5). Pipeline BA → … → programmer → QA.
- 2026-06-05 (v5, programmer): Built on the modular package — `config.ENEMY_KINDS` (REGULAR/HEAVY/SCOUT)
  + split constants + RED/GREEN/CYAN hex + `choose_enemy_kind(t,rng)`. **One** aim routine with a per-shot
  `uniform(−cone,+cone)` so **cone 0 ≡ the v1 dead-on shot** (regression-safe); HEAVY's GREEN pellet
  freezes heading + split distance at fire time → exactly 3 RED children at (−18°,0°,+18°), terminal/no
  re-split/no homing. Kind chosen *inside* the unchanged v1 spawner (replaces a slot, never adds count).
  `--smoke-test` exits 0 / exactly 120 f AND seeds a split that bursts ~f15 (AC27). v1/v2 intact.
- 2026-06-05 (v5, orchestrator): v5 **DONE / shipped**. QA PASS (AC22–AC29), no FAIL → no route-back.
  AC13 long-run caveat carried, still non-blocking (variety = texture not volume; level_spec §V5.4 levers).

## v6 — Bombs (panic button) + control remap Z=fire / X=bomb (shipped 2026-06-05)
- 2026-06-05 (v6, orchestrator): Human wanted a **panic-button bomb** — X flushes the screen (all
  enemies + asteroids + ALL enemy bullets) with a brief full-screen flash; charges start **2**,
  refilled only by a **scarce pickup** (+1), 0-charge = no-op; plus a **Z-fire / X-bomb remap**. Framed
  in `brief.md` (v6). Pipeline BA → … → programmer → QA.
- 2026-06-05 (v6, programmer): New `systems/bombs.py` runs each PLAY frame **before** the §V2.7 damage
  step (the "I bombed in time" guarantee — a same-frame bomb on a contact bullet costs 0 HP). X key-down
  edge with `charges>0` + no 18-f lockout → −1 + **flush** (pure list-clear of enemies/asteroids/ebullets,
  so green pellets & red children fall out automatically; silent, `BOMB_FLUSH_SCORE=0`) + `flash_timer=18`
  + `bomb_lockout=18`; spares player bullets + all 6 pickups + cosmetics. Charge pool on `World` (start 2 /
  cap 4 / clamp [0,4]; `reset_run`→2). 6th `BonusKind.BOMB` = +1 clamped (collect-at-full WASTED, no pill).
  Kind ladder re-sliced **R30/F20/Ra20/S12/Sc12/BOMB6** (volume-neutral; drip/enemy-drop/cap bit-for-bit
  v2). **Fire = Z** (Space a silent alias), **bomb = X**; `CONTROLS_1` teaches "Z = fire · X = bomb".
  Violet `×N` HUD readout top-right; full-screen `#F0F8FF` flash @200 linear-fade. `--smoke-test` exits 0
  / exactly 120 f and scripts X @f20 to flush the v5 split children. v1/v2/v5 intact.
- 2026-06-05 (v6, orchestrator): v6 **DONE / shipped**. QA PASS (R45–R54, AC30–AC38), no FAIL → no
  route-back. AC13 long-run caveat carried, still non-blocking (bomb is a survival tool, no score, folded
  into the QA-passed ramp); R35 screen-clear still deferred.
- 2026-06-05 (v7, programmer): Boss encounter built as a **boss sub-state inside PLAY** (no new
  `GameState`). New `entities/boss.py` (the Mothership: own HP / own +1000 reward / two-state
  ENTRANCE→ACTIVE lifecycle / per-instance moveset cadence + split-dist levers so the smoke seed can
  compress it) + new `systems/encounter.py` (the manager: TIME trigger at marks 75/165/255…; free+silent
  **arrival flush** via the **factored** `bombs.trigger_flush(arm_flash=True)` — clears
  enemies/asteroids/ebullets, NO `charges-=1`/lockout, so it costs no charge; spawn the boss off-screen-top
  AFTER the clear; ENTRANCE glide at 2.0 px/f → snap to y=400 → ACTIVE; ping-pong oscillation x∈[180,420];
  the fixed 4-step moveset 5 REGULAR→2 HEAVY→7 SCOUT→yellow fan, looping every 150 f, gated by
  `MINION_CAP=14`; `on_defeat` awards +1000 through `scoring.award` (Score×2 doubles → popup tracks the
  real amount) and drops `world.boss` → freeze lifts). **Spawn-freeze** = gate each emit in
  `spawning.update` on `world.boss is None` (timers free-run, **skip-no-bank**), minion pickup-drops
  suppressed in combat while boss-active (minion **score on**). **Boss collisions** folded into §V2.7:
  player-bullet × boss r=70 → −1 HP (boss is NOT a v5 Enemy — own HP, no kind-score); player × boss body →
  60 ram (first-hit-wins, honours i-frames/shield; boss persists). **Bomb-vs-boss**: the flush clears
  minions+bullets but the boss lives in `world.boss` (a separate field), so it's IMMUNE by construction
  (`BOMB_BOSS_CHIP=0`). **Attack-4 reuses the v5 frozen split**: 3 YELLOW `EnemyBullet`s (new family, new
  `ring_phase` field) each freeze `split_timer=round(split_dist/4.5)`; on maturity `split_yellow` replaces
  each with 4 RED children at absolute headings `ring_phase+{0,90,180,270}°` → the union is the even 12-red
  360° ring {0,30,…,330}. **Smoke** (`SMOKE_BOSS_*` @f40, after v5 f16 + v6 f20): token target @f38 →
  free arrival clear @f40 (charge stays **1**) → compressed entrance (spawn (300,360), settles ~f59) →
  compressed moveset (step 1 = 5 REGULAR, …, step 4 yellow fan ~f84, split dist 45 → 12-red ~f94, children
  update to f120); boss NOT defeated (HP 120 stands); **exits 0 / exactly 120 f**. Logic probes confirm
  AC39–AC52; v5/v6 chained seeds + v1/v2 economy unchanged (no AC1–AC38 regression).

## Maintenance — knowledge-base cleanup (Manager, 2026-06-05)
- 2026-06-05 (manager): Token-cost cleanup of the shared hot path after v6 shipped. Archived the closed
  increments' handoffs **v2–v5 (entries 10–33)** to `../archive/handoffs-v2-v5.md` (v1 was already in
  `handoffs-v1.md`); the active `shared/handoffs.md` now holds only the **latest** increment (v6).
  Distilled the v4/v5/v6 cross-cutting narrative into this file (above), then collapsed the
  `shared/backlog.md` **Status** section back to **board-only** — one short status line per shipped
  version — moving the prose "why" here. **No spec or game code touched** (the gdd/art/level/requirements/
  qa specs remain the canonical, code-matching contract; each role still loads only its own). Strengthened
  the **one-line-handoff** convention in `handoffs.md` + `CLAUDE.md` STEP 4 to stop the essay-handoff
  bloat from recurring. Trimmed `brief.md` to theme/constraints + the latest increment's framing; older
  increment framings (v2, v5) moved to `../archive/brief-increments-v2-v5.md`. Every role's "Read first"
  paths still resolve (they point at `shared/` + each role's own spec, none of which moved).
- 2026-06-05 (manager, **spec-splitting**): Split the six big per-domain specs — `design/gdd.md` (1047 L),
  `art/art_spec.md` (909), `levels/level_spec.md` (826), `requirements/requirements.md` (701),
  `qa/qa_report.md` (408), `story/story.md` (441) — each into a **per-increment folder** (e.g.
  `design/gdd/` → `v1-base.md` / `v2-bonuses.md` / `v5-enemies.md` / `v6-bombs.md`) with an **`index.md`**
  navigation header (file map + topic→file lookup + the update rule). Content was sliced **verbatim by
  line range** (byte-for-byte; line counts re-summed to the originals — no spec text rewritten), then the
  monolith removed. Chose the **version axis, not topic**, because every section is live code-matching
  contract and a topic-merge would mean rewriting numbers (forbidden without re-verifying vs `game/`).
  Realigned all eight `roles/*.md` "Read first"/Output paths, `CLAUDE.md` STEP 4, and `workspace/README.md`
  to the folder/`index.md` paths. The `qa/test_plan.md` + `qa/feature_inventory.md` standing docs were left
  as-is (topical, not version-append). Net: a build role now opens a small `index.md` + only the increment
  file(s) it needs, instead of a 700–1050-line monolith.
