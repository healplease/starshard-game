# QA Reports — index / navigation

> Per-run QA verdicts for "Starshard" (owner: **qa-tester**). Owner status: complete. Reports are
> **append-only, one file per increment** (this replaces the old single newest-on-top log). Each file
> records that increment's verdict, commands run, AC checklist, and regression check. Inputs are
> verified against the per-domain specs (`requirements/`, `design/gdd/`, `levels/level_spec/`,
> `art/art_spec/`, `story/story/`) + `game/` (the modular package). Cross-increment *why* → `../history.md`.

## Run reports (newest first)
| File | Increment | Verdict | Covers |
|------|-----------|---------|--------|
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
