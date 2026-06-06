# QA — change log (qa-tester)

> Per-domain history. The current report is `qa_report.md` (append-only, newest section on top — it
> already keeps its own dated verdicts). This file holds the one-line routing decisions for this
> domain. The cross-role story lives in `../shared/handoffs.md`.

- 2026-06-05 (v1): VERDICT **PASS**. Smoke gate green (exit 0 / 120 f / 3× stable, ~2.3 s, no hang). All
  MUST R1–R14 verified by driving the real game logic + render paths headlessly. AC1–AC12 PASS; SHOULD
  R15–R18 + COULD R19 work. AC13 PASS with a non-blocking tuning caveat (expert pure-dodging can exceed
  3 min; level_spec §8 levers IF a human playtest confirms). → orchestrator.
- 2026-06-05 (v2): VERDICT **PASS**. Smoke gate green after the refactor (exit 0 / exactly 120 f / 3× +
  `-m game.main` + `compileall` clean) AND now lifecycle-exercising — the §V2.5 seed Rapid is collected @f2
  → cooldown 12→6 while active → expires @f61 → reverts. **AC14–AC21 all PASS** (32 logic assertions +
  render probe). R34 Score×2 verified; R35 not built (deferred, non-failing). **No v1 regression** (AC1–AC13
  re-confirmed against the new package; AC13 long-run caveat unchanged & non-blocking). Package modular
  (21 files / 1222 lines, 36-line main.py, C3 retired). No FAIL → no route-back. → orchestrator (declare v2 DONE).
- 2026-06-05 (v4): standing QA docs (NOT a per-run verdict). Authored `feature_inventory.md` (32 features
  F1–F32 → R#/AC#/module, incl. intentional gaps R35/R20/R22 and the parked AC13 caveat) + `test_plan.md`
  (smoke plan / regression plan / per-feature checklists). Re-ran the smoke gate → **exit 0** (confirms the
  documented expected result). No game code touched; `qa_report.md` left untouched as the per-run log.
  Writing the checklists surfaced **no defect** → no route-back to programmer. → orchestrator (declare v4 DONE).
  Rationale for keeping these separate from `qa_report.md`: the report is an append-only *verdict* log;
  these are durable *method/map* docs that outlive any single run (per the human's v4 request).
- 2026-06-06 (v14): VERDICT **PASS** (full report → `qa_report/v14.md`). Save system + STATS screen.
  Beyond re-running the author's harness (75/75), independently read every award/flush/runs/nav site in
  the live code and authored two negative-style probes (pause/resume writes no file; a GAME_OVER→quit
  double-flush doesn't double-count). Proved the real `%APPDATA%\Starshard\stats.json` is byte-identical
  before/after smoke ×2 + event-script + balance (AC85). Confirmed the programmer's pre-existing-v12-AC71
  fix is sound (co-location assertion now matches the locked v13 design, not masking a regression). No
  FAIL → no route-back. → orchestrator (declare v14 DONE).
