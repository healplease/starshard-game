# QA Reports — index / navigation

> Per-run QA verdicts for "Starshard" (owner: **qa-tester**). Owner status: complete. Reports are
> **append-only, one file per increment** (this replaces the old single newest-on-top log). Each file
> records that increment's verdict, commands run, AC checklist, and regression check. Inputs are
> verified against the per-domain specs (`requirements/`, `design/gdd/`, `levels/level_spec/`,
> `art/art_spec/`, `story/story/`) + `game/` (the modular package). Cross-increment *why* → `../history.md`.

## Run reports (newest first)
| File | Increment | Verdict | Covers |
|------|-----------|---------|--------|
| `v16.md` | v16 — second boss NOVA + uniform-random extensible boss pool | ✅ PASS | AC86–AC93: extensible length-driven pool (AC86), uniform seedable pick (AC87, probe ≈½/½ over 3000 seeds), cadence unchanged (AC88), shared v7 framing (AC89), NOVA distinct (AC90), **zero ships** across a full fight (AC91, probe max enemies=0), **deadlier** every axis 25>15/80>60/90<150f (AC92); full `pytest` = **91 (75→91, +16)** green, smoke `main.py`+`-m game.main` exit 0 + compileall clean; Mothership parity + no AC1–AC85 regression (AC93) |
| `v15.md` | v15 — pytest suite + ruff/pyright tooling (port-then-delete the harness) | ✅ PASS | 32 e2e checks ported → `tests/e2e/`; full `pytest workspace/tests` = **75 (43 unit / 32 e2e)** green; smoke `main.py`+`-m game.main` exit 0 + compileall clean; parity old-75 ↔ new-75 proven; `regression_harness.py` deleted (zero coverage loss) |
| `v14.md` | v14 — one-file JSON save system + lifetime-stats screen | ✅ PASS | AC78–AC85 + STATS nav + 2 QA-authored probes (pause/resume-no-flush, idempotent double-flush) + code reads of every award/flush/runs site; real save provably untouched; harness 75/75; no AC1–AC77 regression |
| `v12.md` | v12 — hold-R-to-restart on PAUSE + GAME_OVER | ✅ PASS | AC69–AC77 + 11 QA-authored probes (GAME_OVER hold-R e2e, die-with-R-held #1-risk, both-Q+R independence, exact-29/30 boundary, negative PLAY-exclusion); harness 65/65; no AC1–AC68 regression |
| `v11.md` | v11 — softer invulnerability pulse | ✅ PASS | smooth 128↔255 cosine pulse via real-surface alpha; harness 59/59; no AC1–AC68 regression |
| `v10.md` | v10 — Q-hold-to-quit on START + GAME_OVER | ✅ PASS | AC61–AC68 + 11 QA-authored probes (exact-30 boundary, die-with-Q-held end-to-end, negative PLAY test); no v1–v9 regression |
| `v9.md` | v9 — process hardening (verification + feedback loops) | ✅ PASS | gates green + FAIL loop proven (3 planted defects) + A15 live playtest; no v1–v8 regression |
| `v8.md` | v8 — Pause / Unpause + Q-hold to Quit | ✅ PASS | AC53–AC60 + no v1/v2/v5/v6/v7 regression |
| `v7.md` | v7 — bosses / periodic Mothership boss fights | ✅ PASS | AC39–AC52 + no v1/v2/v5/v6 regression |
| `v6.md` | v6 — bombs / panic button + Z/X remap | ✅ PASS | AC30–AC38 + no v1/v2/v5 regression |
| `v5.md` | v5 — three-enemy roster + splitting pellet | ✅ PASS | AC22–AC29 + no v1/v2 regression |
| `v2.md` | v2 — bonuses + modular refactor | ✅ PASS | AC14–AC21 + no v1 regression |
| `v1.md` | v1 — base game | ✅ PASS | AC1–AC13 (AC13 tuning caveat, non-blocking) |

## Related QA docs (standing, NOT per-run — still in `../`)
- **`../test_plan.md`** — the smoke-test plan + regression-test plan + per-feature checklists.
- **`../feature_inventory.md`** — the 32-feature inventory (F1–F32) traced to R#/AC#/module.

## Updating
- **New increment:** after verifying, add `vN.md` (`## <date> (vN) — Verdict: …`) + a row above.
  One-line the FROM-qa-tester handoff in `../../shared/handoffs.md`; the *why* goes in `../history.md`.
- A **FAIL** verdict routes back to the programmer (per `CLAUDE.md`) — record it in the same `vN.md`.
