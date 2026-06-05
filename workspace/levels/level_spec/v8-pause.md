# v8 increment — Pause / Unpause + Q-hold to Quit — Level Spec

Owner: level-designer · Date: 2026-06-05 · Status: confirmed no-op
Inputs: `workspace/design/gdd/v8-pause.md` (§V8.1, §V8.3, §V8.5, §V8.8),
`workspace/levels/level_spec/v7-bosses.md` (the current locked economy),
`workspace/shared/backlog.md` (v8 row 6 task note).

---

## §V8.1 Verdict: confirmed economy no-op

v8 introduces **no changes** to the level / spawn economy. The existing v1–v7 contracts are
bit-for-bit preserved:

| Economy dimension | v8 change? | Evidence |
|---|---|---|
| **New spawn types** | None | PAUSE state adds zero `BonusKind` entries; no new entity classes; GDD §V8.9 lists only `PAUSE_QUIT_FRAMES = 30` |
| **New pickup kinds** | None | Pickup table remains the v6 6-kind ladder: Repair 30 / Fan 20 / Rapid 20 / Shield 12 / Score×2 12 / BOMB 6 (sums 100) — unchanged |
| **Drip cadence** | Unchanged | `randint(600, 840) f` from v2-economy — not touched |
| **Enemy-drop %** | Unchanged | 15 % per bullet-kill from v2-economy — not touched |
| **On-screen pickup cap** | Unchanged | 3 from v2-economy — not touched |
| **Difficulty ramp formulas** | Unchanged | v1-base.md §3 — not touched |
| **Enemy spawn mix / gates** | Unchanged | v5-spawn-mix.md §V5.1 (HEAVY @20 s / SCOUT @50 s) — not touched |
| **Bomb-pickup scarcity / lull** | Unchanged | `BOMB_SPAWN_LULL = 0`, weight 6 / 100 from v6 — not touched |
| **Boss breakpoint cadence** | Unchanged | TIME: first boss @75 s, then +90 s (v7-bosses.md §V7.1) — not touched |
| **Spawn-freeze/resume rule** | Unchanged | v7-bosses.md §V7.2 skip-no-bank / `BOSS_RESUME_LULL = 0` — not touched |
| **AC13 (1–3 min run)** | Protected | Run clock `w.frame` is frozen during PAUSE (GDD §V8.5 entry #7); all ramp/breakpoint timers reference `w.frame`, not wall-clock — AC13 holds |

---

## §V8.2 Edge case: real-world vs. in-game time during PAUSE

**Observation:** A player who pauses repeatedly extends their real-world session time beyond the
in-game elapsed frames. Because the v1 ramp, boss breakpoints, and AC13 all reference `w.frame`
(not wall-clock), this has **no effect on spawn economy or difficulty**. A pausing player simply
spends more real-world seconds at the same game-state snapshot.

**Ruling:** Not an economy issue. The pause-freeze is structurally correct per GDD §V8.2.2 and
the BA freeze list (R70). AC13's "1–3 min" is measured in playing time (frames), not in-session
elapsed time. No level-spec lever requires adjustment.

---

## §V8.3 Traceability

| Requirement | Coverage |
|---|---|
| R70 — all systems frozen during PAUSE | Confirmed by GDD §V8.5 (8 subsystems named; freeze is structural via `_step_play()` gate) |
| AC13 — run length 1–3 min | Protected: `w.frame` frozen in PAUSE; ramp/breakpoints unchanged |
| All prior level-spec contracts (v1–v7) | Unchanged; this file is additive only |

No new levers, no new constants, no new spawn numbers. This file exists solely to satisfy the
v8 backlog row 6 confirmation requirement. The locked economy from v7-bosses.md remains the
current production contract.
