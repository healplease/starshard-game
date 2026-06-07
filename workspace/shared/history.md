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

## Programmer invariants (living note — added 2026-06-05 retro; Programmer fills/maintains)
> Cuts the per-session re-orientation cost (re-deriving the loop/World contract from code each increment).
- **PLAY pipeline order (§V2.7):** `encounter.update` → `bombs.update` (BEFORE the damage step) → physics →
  `combat.resolve` → `spawning.update` → `buffs.tick` → `scoring.survival_tick` → `w.frame += 1`.
  (Always confirm against `app.py._step_play`.)
- **What lives on `World`:** charge pool (start 2 / cap 4), `flash_timer` / `bomb_lockout`, `boss` (its own
  field — NOT in `enemies`, which is why the boss is flush-**IMMUNE by construction**), run `frame`.
- **Counter-intuitive rulings (don't re-litigate — see the linked history):** bomb flush score = 0;
  bomb-vs-boss immunity by construction; aim cone 0 ≡ the v1 dead-on shot (regression-safe).
- **Smoke seeds → `config.SMOKE_TIMELINE` is the single source of truth (v9).** Ordered rows
  `(frame, event, note)`; `app._run_smoke_seeds()` iterates it and `config.smoke_timeline_ok()` asserts the
  frames are strictly increasing + in-budget. Adding a seed = one row edit. Current chain:
  bonus @f2, split @f3, bomb @f20, boss_target @f38, boss @f40 (split bursts ~f16) — all inside 120 f.
- **v9 headless gates (run these, not just the smoke):** `qa/regression_harness.py` (the durable AC1–AC60
  suite — extend by adding an `@test(...)` fn), `main.py --event-script` (pause/bomb/quit through the real
  `_handle_events`), `main.py --balance-probe [K]` (AC13 survival figures). The Q-hold quit now ends the loop
  via `app.quit_via_qhold` + `running=False` (was an inline `sys.exit`) so it's observable to a harness.

## Retrospective — post-v8 process review (Manager, 2026-06-05)
- Facilitated a full-team retro (8 role cards → `shared/retrospective.md`). **Headline:** the *authoring*
  pipeline is excellent (clean specs, reuse compounding, low token cost, zero rework); the
  **verification/feedback half** is the weak side — QA passed 8/8 first-try, the FAIL + upstream loops never
  fired, and no visual/feel AC has ever been seen in a live window. Human + Manager approved the full action
  register. **Manager-now (applied this session):** one-line-handoff reinforce + a **BLOCKER** upstream
  handoff type + **SKIP** for no-impact rows (`CLAUDE.md` / `handoffs.md`); a **required Open-values
  delegation table** + decision-criterion-on-tension (BA role); **lever-ownership + no-placeholder
  color/alpha** (Designer/Artist roles); **QA independence + a negative test** (qa-tester role); the
  **volume-neutral re-slice** named move (`level_spec/index.md`); a **copy-surface map** (`story/index.md`);
  and this **Programmer-invariants** stub. **Routed to a v9 — process-hardening increment (Programmer):**
  a committed, growing `qa/regression_harness.py`; a `SMOKE_TIMELINE` source of truth + headless
  `--event-script` event injection; a render-smoke + `string_widths` gate; the AC13 `--balance-probe`; plus
  a periodic human playtest checkpoint.

## v9 — Process hardening tooling (programmer, 2026-06-05)
- Built the four retro-routed verification gates without changing any v1–v8 game behaviour (smoke still
  exits 0 / exactly 120 f). **(A11)** `qa/regression_harness.py` — the durable, growing behavioural suite
  (49 checks spanning AC1–AC60), driving the REAL systems/entities/app/view + the real `App._handle_events`,
  replacing the per-increment scratch harnesses; exits 0 iff all pass. **(A12/A13)** `config.SMOKE_TIMELINE`
  is now the single source of truth for every headless seed frame + ordering (`smoke_timeline_ok()`), and
  `app.run()` got an `event_script` mode that posts scripted KEYDOWN through the real `_handle_events` —
  exposed as `main.py --event-script` (a 5-check pause/bomb/quit gate) and reused by the harness. The v8
  Q-hold quit was refactored from an inline `sys.exit(0)` to `quit_via_qhold`+`running=False` (same live
  behaviour, now observable). A `_q_held()` seam lets the scripted gate drive the held-Q quit that
  `pygame.key.get_pressed()` can't fake headlessly. **(A14)** the harness adds a render-smoke (one frame per
  GameState, asserts no draw raises + key HUD rects don't overlap — the AC47 anti-collision made a real
  gate) and a `string_widths` check (each UI literal fits its panel + every glyph is in the font). **(A10)**
  `main.py --balance-probe [K]` runs K deterministic scripted games of the pure play pipeline under the live
  ramp → median / p95 survival seconds (naive non-dodging lower bound; first reading: median ~48 s, p95 ~75 s
  over 15 runs). **Proof the FAIL loop works:** 3 planted defects (flush no-op / boss-bar overlap / oversized
  label) made the event, regression, render-rect, and width gates go red — while the **smoke gate stayed
  green on the behavioural defect**, exactly the retro T1 finding that "exit 0" can't see input-path bugs.

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

## Maintenance — "new page" + lazier/leaner roles (Manager, 2026-06-06)
- 2026-06-06 (manager): Human asked to (a) make the roles **lazier** — scale effort to the change, think
  and speak less; (b) have the **Orchestrator scope the handoff queue** to only the lanes a change touches
  (the trigger was BA + Level-designer being run for a pure UI/UX change); and (c) make the deliverable
  **docs more concise** — but only **after** archiving most of the current scope to "turn a new page".
- **Archive first (the new page).** Collapsed the three always-loaded hot-path files to a lean baseline,
  moving all closed detail to `../archive/` verbatim (nothing lost): handoffs entries **34–94 (v6–v12)** →
  `handoffs-v6-v12.md`; the full **v1–v12 backlog** task tables + status prose → `backlog-v1-v12.md`; the
  v7–v12 orchestrator framings → `brief-increments-v7-v12.md`. `shared/backlog.md` now = a **current
  game-state capability summary** (v1–v12 one-liners + R/AC totals + play command) + parked items;
  `shared/handoffs.md` reset to an empty active log (numbering continues from 94); `shared/brief.md`
  trimmed to theme + constraints + a pointer. Archive `README.md` + `workspace/README.md` map updated.
- **Orchestrator scoping (role + CLAUDE.md).** Added a "scope the handoff queue" responsibility + a
  **change-shape → roles** table to `roles/orchestrator.md` (UI/UX tweak skips BA + Level-designer;
  render-only = Artist→Programmer→QA; copy-only = Writer→Programmer→QA; bug fix = Programmer→QA), a
  **right-size-QA** instruction, and reinforced it in the `CLAUDE.md` pipeline note. QA is never skipped
  but its rigor scales.
- **Lazier behaviour (CLAUDE.md + roles).** New first ground rule: *"Be lazy on purpose — scale effort to
  the change; speak short."* Softened the always-on rituals: the BA Open-values table is now "when the
  increment delegates numbers" (a sentence suffices for small ones); QA's independent-probe + negative-test
  is now **full-rigor for new mechanics / lazy-pass for small-UI** (smoke gate never skipped).
- **Concise docs (done last, per the human's "sensitive — leave to the end").** Added a concise-spec
  instruction to `CLAUDE.md` STEP 4.1: a spec is a contract not an essay; state the value + at most a
  one-line why, push reasoning to `history.md` — **fewer words, never fewer facts; numbers/rules/strings
  stay exact.** No existing canonical spec content was rewritten (only the *guidance* for future specs).
- **No spec/code touched; all "Read first" paths still resolve** (backlog/handoffs/brief kept their paths,
  just leaner; role folders unmoved).

## v15 — Test-infrastructure contract: pytest suite + ruff/pyright (Manager, 2026-06-06)
- 2026-06-06 (v15, manager): A **process/tooling** increment (no game change, like v9). Human: the
  one-off scratch-script testing + the 1,514-line `qa/regression_harness.py` monolith "stuns agents";
  replace it with a real **pytest** suite (e2e fixtures for QA, unit tests for Programmer) + a
  **ruff/pyright** autofixer the Programmer runs after changes. Kickoff locked: **port all 75 checks then
  delete** (zero coverage loss), **pyright "basic"**, **lint non-blocking**, **smoke + pytest blocking**.
  The Manager owns `workspace/` structure, so it defines the layout/split/process (authorized exception to
  the usual "don't invent process" guardrail). The full canonical contract is `qa/test_plan.md` §2 — this
  note is just the *why* behind the load-bearing choices:
- **`tests/` under `workspace/`, `pyproject.toml` at the repo ROOT.** Tests sit beside `game/` (where they
  import `from game...`); a single root `pyproject.toml` with `pythonpath=["workspace"]` lets a bare
  `python -m pytest` / `ruff` / `pyright` run from the root (where `.venv` already is) with no path args,
  matching existing muscle memory. `conftest.py` ports the harness's headless-env + temp-save pin (lines
  34–46 — so **no test touches the real save**) and its `fresh_world`/`make_fonts`/`ensure_pygame` helpers.
- **The unit-vs-e2e boundary (43 unit / 32 e2e = 75).** Discriminator: a check is **unit** iff it asserts
  pure logic on `World`/entities/systems/`config`/`save` built directly (no `App`, no event loop, no blit;
  font `.size()` for width math is allowed); **e2e** iff it builds `App`, drives
  `_handle_events`/`_step_play`/`run_event_script`/`App.run`, calls `balance_probe`, or blits/asserts
  rendered layout. Derived mechanically from the harness (which markers each `_t_*` touches), so it's
  reproducible, not taste. Borderline rulings recorded in §2.4 so Programmer/QA don't re-litigate: AC10/
  AC13/AC85 → e2e (they build App / run balance_probe even though they test world/save logic); AC20 →
  unit (systems-only seeded lifecycle); `pulse` → e2e (reads alpha off a rendered surface); string-widths
  → unit but rect/arc-overlap geometry → e2e (it validates *rendered* layout).
- **Migration is port-then-delete with a hard parity floor.** Programmer ports the 43 unit checks first
  and **leaves the monolith in place** as the safety net; QA ports the 32 e2e checks, runs the full suite,
  and deletes `regression_harness.py` **only after** pytest collects ≥75 and all pass. If parity can't be
  shown, the harness stays and QA files a BLOCKER. **Blocking = smoke exit 0 + pytest green only**;
  ruff/pyright residuals are reported, never block (pragmatic for the existing untyped codebase).
- **Realigned docs (no game spec touched):** `roles/programmer.md` (before-handoff ruff+pyright+unit-pytest
  +smoke gate; DoD adds unit-green + a test for new logic), `roles/qa-tester.md` (full pytest = the
  regression gate, ≥75 floor, e2e lane ownership), `CLAUDE.md` (new "Tests & tooling" ground rule),
  `workspace/README.md` (tests/ + root pyproject in the map), `qa/test_plan.md` (§2 = the contract; old
  regression section renumbered §2A = the *what-must-pass* coverage map; §3 checklists unchanged). No test
  code built yet — that's Programmer (row 2) then QA (row 3).
- 2026-06-06 (v15, programmer — row 2): scaffolded the unit lane. **Built:** root `pyproject.toml`
  (pytest `testpaths`/`pythonpath=["workspace"]`/`-q`; ruff E,F,I @ line-length 100 over game+tests;
  pyright basic over game+tests), `workspace/tests/conftest.py` (SDL-dummy + `STARSHARD_SAVE_PATH` pinned
  at import time before `game` loads; `fresh_world`/`fonts`/`pygame_init`/`screen`/`tmp_save_path`
  fixtures), and 11 unit files porting all 43 checks per the §2.4 map. **Installed** ruff 0.15.16 +
  pyright 1.1.410 into `.venv` (added to `requirements.txt` with nodeenv/typing_extensions). **Gates:**
  unit pytest 43/43 green; `main.py --smoke-test` exit 0. **Non-blocking residuals (reported, not fixed):**
  ruff = 1 (F821 false-positive on the `"BonusKind"` forward-ref string in `game/entities/bonus.py` —
  pre-existing game code, not touched); pyright = 17 (11 in pre-existing `game/` code, 6 in
  `test_enemies.py`) — all the same root cause: `config.ENEMY_KINDS` is a heterogeneous dict so its values
  infer as `float | str`, breaking `>`/`+` on the numeric entries. Left the monolith in place per the
  port-then-delete rule — QA proves ≥75 parity then deletes it (row 3).

## v11 — Softer invulnerability pulse (programmer, 2026-06-05)
- Art-only render tweak per `art_spec/v11.md` — no gameplay/economy/copy change; i-frame & Shield
  durations untouched. `_draw_player` (`game/view/render.py`) no longer early-returns on the "off" half
  of a hard 6-f blink (the old `(blink_timer//6)%2` strobe 255→0→255). It now splits two paths:
  **(1)** *not invulnerable* → draw the ship straight to `screen` at full opacity (the cheap common path,
  zero surface cost); **(2)** *invulnerable* → a smooth **cosine** alpha pulse `phase=(blink_timer%30)/30`,
  `osc=0.5+0.5*cos(2π·phase)`, `alpha=128+(255−128)·osc` → 128↔255 over a 30-f cycle, driven off
  `blink_timer` so it tracks remaining i-frames/Shield and snaps back to solid the instant invuln ends
  (handled by path 1 — no end-of-pulse special case). **Render mechanism (§V11.5):** the ship is drawn onto
  a **size-once** module-level `SRCALPHA` surface (`_PLAYER_SURF`, 32×34, local centre (16,17) — like the v6
  flash surface, never per-frame alloc); the alpha is applied via `surf.fill((255,255,255,alpha),
  BLEND_RGBA_MULT)` — **NOT** `set_alpha`, which is a silent no-op on a per-pixel SRCALPHA surface (the §V11.5
  gotcha). **Shield ring (§V11.4):** drawn **solid, every frame, OUTSIDE the alpha surface** straight to
  `screen` while `shield_active` — it no longer rides the (removed) early-return, so the old ring strobe is
  gone and the 5-s-Shield-vs-i-frame tell stays crisp. Three `INVULN_*` consts added to `config.py`
  (`ALPHA_FLOOR=128`, `ALPHA_CEIL=255`, `PULSE_PERIOD=30`). **Verification:** new `v11/pulse` regression test
  reads the actual alpha off `_PLAYER_SURF` (ceil@phase0, floor@phase0.5, never leaves [128,255], >3 distinct
  values across a cycle = smooth, solid-when-not-invuln); harness ALL PASS (60 checks), smoke exits 0/120 f,
  no AC1–AC68 regression. Console-encoding note: harness labels stay ASCII (the cp1252 Windows console can't
  print `↔`/`↔`).


## v12 — Hold-R-to-restart (mirror the Q-hold gesture on PAUSE + GAME_OVER) (2026-06-05)
- 2026-06-05 (v12 programmer): Restart (R) converted from an instant `K_r` KEYDOWN press to a 0.5 s HELD
  gesture on PAUSE + GAME_OVER, mirroring the v8/v10 Q-hold-to-quit. **Two independent counters:** added
  `self.r_hold_frames` on `App` beside `q_hold_frames` (UI state, not World); each gesture is driven by its
  OWN held-key seam (`_q_held()` for Q, new `_r_held()` for R) and its own `+=1` / `=0` branch — they never
  read each other's key and never share a variable (the §V12.3 #1-risk "counter cross-talk" guard).
  **Activation moved off the edge (§V12.5):** removed the two `K_r` KEYDOWN restart branches from
  `_handle_events` (a single R tap no longer restarts), and drive restart from a new `_restart_hold_step()`
  called in the main loop under `if running and self.state in (PAUSE, GAME_OVER)` — the `running` guard gives
  quit-precedence on a same-frame Q+R tie (§V12.3.1), and the `(PAUSE, GAME_OVER)`-only guard (NOT the Q
  block's START+PAUSE+GAME_OVER) enforces R90 START/PLAY exclusion (§V12.8). Factoring the R logic into
  `_restart_hold_step()` (vs fully inline) keeps the Q block untouched and makes the gesture unit-testable via
  the `_r_held` event-script seam. **Reset spine (§V12.4):** paired `self.r_hold_frames = 0` beside every
  existing `q_hold_frames = 0` across all six transitions (START→PLAY, PLAY↔PAUSE Esc, PLAY→GAME_OVER death,
  and the rewritten R-restart #5/#6 which zero BOTH atomically) so a partial R-hold can never carry into a new
  screen or pre-fill an arc. **Two arcs (§V12.7):** generalised the v8/v10 arc body into
  `hud.draw_hold_arc(screen, center, hold_frames, threshold)` (track always drawn, fill while >0);
  `draw_quit_arc` is now a thin wrapper, `draw_pause` draws BOTH the Q arc (300,483) and the R arc (200,483)
  with tracks always-on, and `draw_gameover_restart_arc` draws the R widget only-while-held at (200,545),
  mirroring `draw_gameover_quit_arc`. **Config:** one new alias `RESTART_HOLD_FRAMES = PAUSE_QUIT_FRAMES`
  (=30, coupled to one source of truth, §V12.10) + the two Artist arc-centre consts; rewrote
  `PAUSE_HINT_RESTART`→"Hold R  Restart" and `GAMEOVER_KEYS`→"Hold R  Restart      Hold Q  Quit" (Writer
  literals). **Verification:** smoke exits 0 / exactly 120 f (×3 + `-m game.main` + compileall + `--event-script`
  5/5); regression harness **65/65** (6 new v12: render-smoke PAUSE+GAME_OVER with both arcs in all 4 hold
  combos; R-rect vs Q-rect-and-text anti-collision; Q/R independence; START/PLAY exclusion; cancel-on-release;
  and an end-to-end real-loop Esc→PAUSE→hold-R-30 f→PLAY-with-both-counters-zero); strengthened the v10
  reset-spine to assert BOTH counters zero and rewrote the v8 R74 + spine #5/#6 from the removed K_r tap to the
  held path; added "v12" to `_GROUP_ORDER`. No AC1–AC68 regression.

**v13 (2026-06-06, programmer).** Co-located the R-restart arc onto its screen Q-quit arc centre (PAUSE (300,483), GAME_OVER (300,545)) in config.py, and added a `fill_color` param to `draw_hold_arc` (default HP_AMBER) so the R calls pass BONUS_BOMB violet while Q stays amber. R is drawn after Q on both screens (already the call order), so violet wins on dual-hold. Hold timing/semantics & idle-visibility untouched; smoke gate green.

## v14 — Save system (one-file JSON) + lifetime-stats screen (programmer, 2026-06-06)
- **New `game/save.py`** (pure stdlib I/O, no pygame/game imports → no cycle). `Store` = the R94
  process-lifetime object: `version` + the five frozen snake_case ints (`highscore, runs, enemies_killed,
  asteroids_destroyed, bosses_killed`). `load()` never raises (R96): missing/unreadable/unparseable JSON,
  a non-object root, or an unknown `version` → all-zeros; a partly-valid object recovers each count field
  independently (missing / non-int / **bool is not int** / negative → that field 0). `save()` is atomic —
  write `path+'.tmp'` then `os.replace()` (atomic on Win+POSIX) so a crash mid-write keeps the old file (R95).
  **Path (R92):** `default_save_path()` = `%APPDATA%\Starshard\stats.json` (Win) / `~/Library/Application
  Support/Starshard/` (mac) / `$XDG_DATA_HOME|~/.local/share/Starshard/` (Linux). `resolve_path(override,
  headless)` order = explicit arg → `STARSHARD_SAVE_PATH` env → headless temp → real path (**R98/AC85**).
- **Store wiring.** `World.__init__` holds a default `Store()` (so a bare world in tests always has a home
  for the counters); `reset_run()` deliberately never touches it (R94 — counters carry across restarts).
  `App.__init__` loads the disk store once; `_new_world` points `world.store` at it AND seeds
  `world.best = store.highscore` so GAME_OVER's BEST line shows the **persisted lifetime** high (V14.6) with
  no `draw_gameover` signature change — the existing `max(w.best,w.score)` keeps it current. (The flush does
  NOT write `world.best`, else `balance_probe`'s shared-temp flushes would pollute AC10's `best==123`.)
- **Counters (R93) at the award sites only.** `combat.py` step 1 `a.hits<=0` → `+1 asteroids_destroyed`
  (1 per rock, large=1); step 2 `e.hp<=0` → `+1 enemies_killed` (incl. boss minions); `encounter.on_defeat`
  → `+1 bosses_killed` (never enemies). Bomb/arrival clears + ram-consumes have no award site → never count.
  `runs += 1` at the two run-begin transitions only: `_handle_events` START→PLAY (non-Q/non-Tab) and
  `_restart_hold_step` restart; NOT on Esc-resume.
- **Flush (R95) at exactly two points:** `_flush_store()` (record_highscore + atomic save) called on the
  PLAY→GAME_OVER frame in `_step_play`, and just before the hold-Q quit ends the loop. No pause/resume/restart
  or per-event writes; idempotent.
- **STATS screen.** New `GameState.STATS` (peer off START). `_handle_events`: Tab carved out of "any key
  starts" → STATS; Esc/Tab back to START; both transitions zero both hold counters (V14.5); no other key acts
  in STATS (V14.3). `_draw` STATS branch renders starfield + `hud.draw_stats(screen, store)` only (no world,
  no in-run HUD; main loop runs no `_step_play` in STATS). `hud.draw_stats` = title + 2 dividers + 5-row
  two-rail ledger + back hint per art §V14a.5; `draw_start` gains the `START_STATS_HINT` "Tab  Stats" line at
  y530. Config got the §V14a.6 geometry block + the Writer's 7 STATS strings + `START_STATS_HINT`.
- **Headless safety.** `main.py` sets `STARSHARD_SAVE_PATH` to a temp file for every headless mode (covers
  `balance_probe`'s non-headless `App()`); the harness pins + clears its own temp save at startup. Smoke run
  confirmed to NOT create the real `%APPDATA%\Starshard\` dir.
- **Verification.** Regression harness **75/75** (10 new v14: fresh-install/round-trip/corrupt+partial/
  unknown-version, count-accuracy, runs-semantics, flush-triggers, highscore-max+Score×2, headless-safe,
  STATS render-smoke non-overlap, Tab/Esc nav). Smoke + `--event-script` (5/5) + `--balance-probe` all exit 0.
  **Also fixed a pre-existing v12 `AC71` red** (NOT introduced by v14): v13 deliberately **co-located** the
  R+Q arcs but left the v12 "arcs must not overlap" assertion in place (HEAD was silently 64/65, not the
  backlog's "65/65"). Updated that one sub-assertion to assert **co-location** per the v13 §V13.2 locked
  design. cp1252 console note: kept v14 test labels ASCII (a `→` in a label crashes the Windows print).
