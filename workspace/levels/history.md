# Level / Difficulty Spec — change log (level-designer)

> Per-domain history. The current spec is `level_spec.md` (canonical). This file holds the dated
> decision notes for this domain only. The cross-role story lives in `../shared/handoffs.md`.

- 2026-06-05 (v1): level_spec.md created — tuned the ramp for 1–3 min runs (AC13). Key OVERRIDES of
  GDD §7.2/§7.3: asteroid spawn `max(22,64−0.47·t)`; enemy threat now RAMPS (fixed GDD's
  instant-saturation) via cap `min(6,2+t//20)` (2→6) and fire interval `max(55,95−0.35·t)`; enemy
  spawn `max(60,130−0.60·t)`; large-rock chance drifts 25→40%; speed bonus CONFIRMED at +2.0. NEW
  asteroid cap 16. ADDED +1 pt/sec survival bonus (kills still dominate). Tuning levers in §8 if QA finds it off.
- 2026-06-05 (v2): level_spec.md v2 section added — bonus **spawn economy** all **CONFIRM GDD §V2.5**
  (defaults proved sound). Drip cadence `randint(600,840) f` (12 s ±2 s, first draw at run start → first
  bonus ~10–14 s in); enemy-drop **15 %** on **bullet-kills only** (ram-kills don't drop — already cost HP);
  kind weights **R30/F20/Ra20/S15/Sc15** as a cumulative `r∈[0,99]` ladder, shared by both paths; on-screen
  **cap 3** (both paths, skip-no-bank, missed = no penalty). **AC13 analysis:** Repair self-limits (clamps
  at full HP → lifts the LOW tail, doesn't extend experts); Shield (5 s, 15 %) is the only real high-tail
  extender + the first "too LONG" lever; Fan/Rapid are self-paying (collect diverts from dodging); Score×2
  survival-neutral. Net shift bounded → **v1 ramp (§3) left UNCHANGED** per v1-QA's "don't touch unless
  playtest confirms." v2 lever order in §V2.4 (Shield-weight 15→10 first, then cadence/drop, then v1 §8).
  **Smoke seed CONFIRMED** (R28/R33/AC20): Rapid @(300,700) = player x, 20 px above → already inside the 26 px
  collide range → collects ~f3 regardless of sweep; duration forced 60 f → expires ~f63; full
  spawn→collect→apply→expire+revert well inside 120 f; normal drip (720 f) can't fire in 120 f so the seed is
  the sole clean lifecycle.
- 2026-06-05 (v5): level_spec.md v5 section added — enemy-**kind** spawn mix folded into the UNCHANGED v1
  spawner (kind chosen at the instant `enemy_cap(t)`/`enemy_spawn_interval(t)` fire; **replaces** a REGULAR
  slot, never adds count). Band weights **Warmup R100 · Heat-up R85/H15 · Squeeze R60/H15/Sc25 · Storm
  R55/H15/Sc30**; gates `HEAVY_GATE=20 s` / `SCOUT_GATE=50 s`; deterministic `choose_enemy_kind(t,rng)`
  ladder. **AC13:** variety = texture not volume (HEAVY tanky → over-represented but low weight; SCOUT 1-HP
  fragile → self-limited despite high weight; the split/accuracy nudge the high tail down, SCOUT gate guards
  the low tail). v2 enemy-drop (15 %/bullet-kill) unchanged for all kinds. **AC27 smoke split** confirmed
  intact (smoke = t 0–2 s = Warmup = REGULAR-only). v1 ramp + v2 economy left UNCHANGED.
- 2026-06-05 (v7): level_spec/v7-bosses.md added — **CONFIRM** the Designer's locked boss pacing (TIME breakpoint,
  `BOSS_FIRST_MARK=75 s` mid-Squeeze before the median death, `BOSS_INTERVAL=90 s` → bosses 2+ are the expert tail;
  option (a)+(b), no AC13 re-tune). **Own the freeze/resume contract:** gate the v1 asteroid + v5 enemy + v2 drip
  spawners' *emit* on `not boss_active`, **skip-no-bank** (timers free-run, NO backlog dump → resume can't flood);
  resume immediate on DEFEAT at current `t`, **`BOSS_RESUME_LULL = 0`** (mirrors v6's lull-0). **Fight economy:** bonus
  drip **FROZEN**, minion pickup-drops **SUPPRESSED** (no farm), minion **SCORE ON** (normal v5 50/80/60) — score is
  AC13-orthogonal because the gate is TIME not points. **+1000 reward CONFIRM** (12.5× HEAVY; Score×2→2000; points-only,
  AC13-orthogonal). **AC13 held (median):** the run clock never pauses during the fight (GDD §V7.3), so the fight swaps
  ~12–24 s of storm for an equally-dangerous economy-frozen boss arena (no discount); only the ~5 s entrance is genuinely
  calmer, bounded + one-shot for the median run → parked "AC13 long runs" caveat **extended** (non-blocking). `BOSS_HP=120`
  = primary AC13 lever (v7 lever order: HP↓ → marks↑ → §V2.4/v1 §8). **Smoke** confirmed coexistent: the TIME gate
  (f4500) never fires in 120 f, so the forced boss @f40 is the sole boss, strictly after the v5 split (f16) + v6 bomb
  (f20); free arrival flush leaves charge=1 (AC40); freeze exercised f40→120; exits 0. v1 ramp + v2/v5/v6 economy
  UNCHANGED (only paused-and-resumed around the boss).
- 2026-06-05 (v10): level_spec/v10.md added — **confirmed economy no-op** (mirrors the v8 verdict). v10 extends
  the v8 Q-hold-to-quit gesture to START + GAME_OVER, both **UI-only states where `w.frame` and all spawners are
  idle**. Zero new spawn types / pickup kinds / ramp deltas / timing changes; GDD §V10.9 adds zero design consts
  (reuses the v8 set). The new R79 reset-on-transition zeroes only a **UI hold counter** (`App.q_hold_frames`),
  never a ramp/breakpoint timer. **AC13 protected:** gesture excluded from PLAY (R81) so the run clock never
  advances under it. v1 ramp + v2/v5/v6 economy + v7 boss pacing all UNCHANGED. No vN balance lever introduced.
- 2026-06-05 (v12): level_spec/v12.md added — **confirmed economy no-op** (mirrors the v8/v10 verdict). v12
  converts Restart (R) from an instant press to a **held gesture** on PAUSE + GAME_OVER, both **UI-only states
  where `w.frame` isn't advancing** (frozen on PAUSE, idle on GAME_OVER). Zero new spawn types / pickup kinds /
  ramp deltas / timing changes; GDD §V12.10 adds **one** const — `RESTART_HOLD_FRAMES = PAUSE_QUIT_FRAMES`
  (a UI-threshold alias coupled to the v8 value) — and zero economy values. The new R88 reset-on-transition
  zeroes a **second UI hold counter** (`App.r_hold_frames`), never a ramp/breakpoint timer; `reset_run()`
  semantics unchanged (same v1 R13 / v8 R74 reset, so fresh-run economy is identical). **AC13 protected:**
  gesture excluded from START + PLAY (R90) so the run clock never advances under it. v1 ramp + v2/v5/v6 economy
  + v7 boss pacing all UNCHANGED. No vN balance lever introduced.
- 2026-06-07 (v16): level_spec/v16-second-boss.md added — **OWN the pool-selection rule:** uniform **i.i.d. 1/N per
  spawn event** (today ½ Mothership / ½ NOVA), independent (repeats allowed — no shuffle-bag), picked once at ARRIVAL,
  **N read from pool length** so boss #3 = one entry with zero selection/loop edits (R99/R100); seedable/forceable so
  tests pin a boss. **CONFIRM cadence UNCHANGED** — TIME 75 s / +90 s exactly as v7 §V7.1; selection rides the existing
  breakpoint, adds no timing (R101/AC88). **FINALIZE/LOCK NOVA balance** (all Designer-set, confirmed from the pacing
  side): `NOVA_HP=120` (= Mothership; deadlier via attacks not HP-sponge), `NOVA_R=60` (tighter target **offset** by
  no-minion focus-fire → fight stays in the v7 ~12–24 s band), `NOVA_RAM_DMG=80` (>60, <100 HP survivable),
  `NOVA_BULLET_DMG=25` (>15 — headline AC92 lever, 4 hits from full), speed 5.5/lance 6.0 (>4.5), `NOVA_STEP_INTERVAL=90`
  (<150 f, 1.67× cadence), densities RAKE5/BURST24/LANCE4/ARC9 (~7/s vs 1.5/s ≈4.7× denser, ring precesses +9°/step),
  `NOVA_KILL_SCORE=1500` (1.5× Mothership; Score×2→3000). **AC13 held (median, unchanged from v7):** same HP/band; the
  deadlier attacks bound run length on the **short** side only (more in-fight deaths), never lengthen; cadence + reward
  AC13-orthogonal (time-gate, points-only). Pool selection is AC13-orthogonal — both entries same fight band, so
  run-length distribution is independent of the die roll. **Levers if unwinnable** (R104 caveat, deadliest-first per GDD
  §V16.5): widen `NOVA_STEP_INTERVAL` 90→110 → drop `NOVA_RING_COUNT` 24→18 → lower bullet speed → trim ram (never drop
  `NOVA_BULLET_DMG` below 16). **Smoke:** TIME gate (f4500) never fires in 120 f → forced `SMOKE_BOSS_TYPE="NOVA"` seed
  is the sole boss; NOVA's no-minion fight = a *stricter* freeze than the Mothership's (zero hostiles but its bullets);
  no cadence/economy change. v1 ramp + v2/v5/v6 economy + Mothership v7 values all UNCHANGED (v16 only inserts a
  selection step + one pool entry).
- 2026-06-05 (v6): level_spec.md v6 section added — bomb-charge pickup **spawn weight = `BOMB = 6`** (rarest
  kind; 5–8 % band; < Shield/Score 15), folded into the v2 kind table by **re-slicing**, not adding volume:
  Shield 15→12, Score×2 15→12 (Repair/Fan/Rapid untouched) → table still sums 100, so **drip cadence /
  enemy-drop % / on-screen cap are bit-for-bit v2**. **Why those source kinds:** protect Repair (low-tail
  compressor), trim Shield (the only high-tail extender — AC13-helpful, offsets the bomb's own survival aid),
  take the rest from survival-neutral Score×2. **Both paths** (drip + enemy-drop) via the single shared 6-kind
  ladder — not drip-only (cleanest fold; 6 % already scarce; refill-as-offense reads well). Expected ~0.3–0.6
  bomb pickups *collected*/run → a refill ~every 2–3 runs; reaching cap 4 uncommon (matches GDD §V6.8). **R55
  lull → `BOMB_SPAWN_LULL = 0`** (no explicit lull — the flush + 18-f flash + natural post-flush spawn cadence
  ~0.5–1.5 s already pay off; 0 keeps v6 strictly AC13-neutral on the lengthening side; lull stays a §V6.5
  lever). **AC37 smoke** re-confirmed: the seeded activation uses the *starting* 2 charges + scripted X @~f20,
  so it's weight-independent (no drip fires in 120 f; the v2/v5 seeds bypass the roll). v1 ramp + v2 economy +
  v5 mix all left UNCHANGED. v6 lever order in §V6.5 (BOMB weight 6↔4/8 first, then lull, then §V2.4 / v1 §8).
