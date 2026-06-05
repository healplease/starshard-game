# Handoffs — v1 increment (archived)

Frozen. These are the v1 handoffs (entries 1–9), moved out of the active log to keep
`../shared/handoffs.md` lean. The active increment's handoffs live there.

Format: `<n>. <YYYY-MM-DD> — FROM <role> TO <role> — <one-line task>`

---

1. 2026-06-05 — FROM orchestrator TO business-analyst — Turn the space auto-scroller shooter theme (see brief.md) into concrete requirements.
2. 2026-06-05 — FROM business-analyst TO lead-game-designer — Requirements (MoSCoW + non-goals + acceptance criteria) in requirements.md; design the GDD from R1–R22.
3. 2026-06-05 — FROM lead-game-designer TO artist — GDD.md complete (all R1–R14 with concrete numbers; ramp/start/i-frames/feedback specced). Formalize the placeholder palette + shapes from §10.
4. 2026-06-05 — FROM artist TO writer — art_spec.md complete (12-color palette + paste-ready shapes/geometry for every entity, HUD, health-bar thresholds, particles, fonts). Write the Start-screen + Game Over UI copy.
5. 2026-06-05 — FROM writer TO level-designer — story.md complete (exact verbatim strings + paste-ready constants block for every art_spec §4 text slot: Start title/pitch/controls/prompt, HUD score/HP, Game Over heading/score/best/restart-quit). Spec the level/difficulty ramp (level_spec.md).
6. 2026-06-05 — FROM level-designer TO programmer — level_spec.md complete (programmer-ready ramp formulas, sampled curve table, spawn rules, ramping enemy cap 2→6, ramping fire interval, large-rock drift 25→40%, asteroid cap 16, +1/s time bonus; tuned for 1–3 min runs / AC13). Implement workspace/game/main.py per GDD + level_spec.
7. 2026-06-05 — FROM programmer TO qa-tester — main.py complete (499 lines, shapes/text only; all R1–R14 + R15–R19; full level_spec ramp; --smoke-test exits 0 after 120 headless frames, verified 3× + warning-free compile). Run & verify AC1–AC13 and write qa_report.md (FAIL → back to programmer).
8. 2026-06-05 — FROM qa-tester TO orchestrator — PASS. Smoke gate green (exit 0, 120 f, 3× stable); all MUST R1–R14 verified by real runs; SHOULD R15–R18 + COULD R19 work. AC1–AC13 all PASS (AC13 with a non-blocking tuning caveat: expert pure-dodging can exceed 3 min — levers in qa_report.md). See workspace/qa_report.md. Declare project DONE.
9. 2026-06-05 — FROM orchestrator TO human (project complete) — DONE. "Starshard" shipped v1: all MUST R1–R14 verified, SHOULD R15–R18 + COULD R19 working, smoke gate green, backlog fully ticked. Play with `.\.venv\Scripts\python.exe workspace\game\main.py`. One non-blocking polish item parked: AC13 expert pure-dodging can exceed 3 min (level_spec §8 levers) IF a human playtest confirms.
