# Retrospective — Starshard MAS process (after v8)

**Facilitated by:** manager · **Date:** 2026-06-05 · **Scope:** the *working process* (the multi-agent
system itself), not the game's features. All 8 non-manager roles filled a card (Good / Bad / Improve /
Actions). This file is the review artifact; **no process changes are applied until the human + manager
sign off** (see the Action Register at the bottom).

---

## Part 1 — The cards (verbatim, one per role)

### Retro card — orchestrator
**Well:** blackboard-as-memory let every fresh chat re-orient in one read across 8 increments; framing
the breakpoint-vs-AC13 tension *early* (handoff 45) forced a recorded decision; reuse-routing compounded
(v7 reuses v6 flush + v5 split); hot-path discipline held after the Manager re-tightened it.
**Bad:** 8 first-try QA passes is a yellow flag — the `programmer ← qa` feedback edge has **never once
fired**, so "triage QA failures" is untested; the pipeline is strictly linear with no upstream path;
human-bus overhead is heavy even for v8 (a whole chat to write "no-op"); AC13 carried unchanged 8×.
**Actions:** require QA to log one negative test/increment; add a one-line BLOCKER handoff type to route
defects upstream; let kickoff declare a SKIP set for no-impact rows; convert any 2+-increment parked item
into a forced decision handoff.

### Retro card — business-analyst
**Well:** append-only R#/AC# numbering (R1→R75, AC1→AC60) gave every role a stable contract + one-glance
index map; the **Open-values delegation table** (§26/§32) froze behaviour while handing every number to the
right owner — best pattern we have; per-increment vN.md kept the hot path cheap; flagging cross-cutting
tensions instead of resolving them worked.
**Bad:** AC13 was never headless-testable yet stayed on the books, generating "keep AC13" work every
increment; own handoff/history lines bloated past the one-line rule (entries 36, 46); requirement files
trended verbose (same ruling restated 4×); "reuse v6/v5" was asserted but only verifiable downstream.
**Actions:** standardize the Open-values table as a required artifact; add a "BA-ruling vs Delegated-value"
header; replace AC13's untestable wording with a headless-measurable proxy or downgrade it; hold self to
one-line handoffs.

### Retro card — lead-game-designer
**Well:** the BA's delegation table → my LOCK → paste-ready const block was the biggest accelerator (8
increments, zero re-design loops); "reuse don't duplicate" made v7 nearly free; Designer-sets-number /
LD-tunes-AC13 was a stable split; spec-split kept read cost low.
**Bad:** breakpoint-vs-AC13 landed with the whole resolution delegated but **no playtest data** — a real
balance call made from a paper model, still parked; own handoff lines bled detail (entries 47, 57); I
over-specified the programmer's implementation (v8 §V8.10 ships pygame `draw.arc` math); **no feedback loop
ever closed on a design number** — zero signal on whether any feel value is right.
**Actions:** add a human PLAYTEST gate after QA-PASS for feel/balance increments; split the GDD template into
locked "Numbers & intent" vs non-binding "Implementation note"; require a delegated *tension* to ship a
one-line decision criterion; enforce one-line handoffs + link history anchors.

### Retro card — artist
**Well:** "palette as data" (named RGB consts pasted verbatim) → zero art-side QA failures v1–v8; the
in-spec anti-clash audit travels with the file (picked the violet bomb hue in seconds); reuse-first kept
surface tiny (v8 added **zero** new palette entries); index+split meant loading only my slice.
**Bad:** the Designer/Artist lever boundary blurred every increment and was renegotiated in prose — v6 flash
forced a placeholder-override dance ("§V6.11 placeholders superseded by §V6.5"); layout geometry arrived
half-resolved (v8 `pause_panel_y+56`) without being flagged as mine to close; "optional/cuttable" polish
notes are write-only — no signal on what the Programmer actually kept.
**Actions:** add a Designer↔Artist lever-ownership mini-table to the GDD template; **forbid placeholder
color/alpha in the GDD** (leave cells literally `ARTIST`); surface unresolved layout formulas under an
"Artist must resolve:" header; have the Programmer log a one-line "polish kept/cut" note to art/history.md.

### Retro card — writer
**Well:** spec-split + topic map made control-scheme rewrites safe (found every stale "Space-fire" literal
for the v6 Z/X remap); Artist handoffs arrived with exact width budgets; the "bless the glyph" pattern kept
3 roles in lockstep; single-source popups (`+40`, `+1 BOMB`, `+{points}`) can't lie when balance retunes.
**Bad:** my hints are blocked on upstream key-names being locked first, but that dependency isn't surfaced
on the board; width-safety is eyeballed (`~11 px/char`), never measured — a missing `·`/`×` glyph would
escape; spent copy-words defending uncontested choices; "no in-game controls overlay exists" re-asserted
defensively each increment because the copy surface isn't catalogued.
**Actions:** add a `string_widths` smoke assertion (render each UI literal, assert width ≤ panel + glyph in
font); maintain a "copy surface map" (string → screen → render site) in story/index.md; standardize a
`⚠ REWRITE` tag for strings that replace shipped ones; have the Designer name the locked key consts my
hints depend on.

### Retro card — level-designer
**Well:** the **volume-neutral re-slice** became a reusable low-risk tool (v6 BOMB=6: Shield/Score 15→12,
table still sums 100, ramp bit-for-bit); the "state whether the v1 ramp is touched" rule made the job
auditable; hot-path discipline lowered my per-session cost; lock-a-number/own-the-tuning gave QA a
deterministic fallback.
**Bad:** AC13's caveat has been "parked, extended" 4× (v2/v5/v6/v7) and **never validated** — accumulating
analytical IOUs; confirming a no-op (v8) still cost a full handoff + a file for a non-event; smoke-seed
coexistence (f16→f20→f40 in 120 f) is re-derived by hand each increment; the breakpoint decision authority
was split across GDD and my spec.
**Actions:** add a headless `--balance-probe` (K scripted runs → median/95th survival time) to end the AC13
stalemate; give no-op increments a lighter "LD confirm inline" path; promote the smoke-seed timeline to one
shared table; codify the volume-neutral re-slice as a named template move in level_spec/index.md.

### Retro card — programmer
**Well:** modular MVC (post-v2) → new features land as a new file + one wire-in line (v6 bombs, v7 boss);
clean seams made reuse cheap (factored `bombs.trigger_flush` for the free boss arrival; boss attack-4
reuses the v5 frozen split); the `--smoke-test` 120-f gate with deterministic seeding is the best process
asset — never shipped a build to QA I hadn't watched exercise the new path; the 5 upstream specs arrived
already reconciled, so my step was nearly mechanical.
**Bad:** re-derived the §V2.7 pipeline order + "what lives on World" from code every session (the handoff
carries the task, not the mental model); the smoke-seed schedule is a fragile shared timeline crowding the
same 120 frames, documented only in comments; the handoff carries the decision but not the "why-not" (re-
questioned settled rulings like bomb-vs-boss immunity); **no FAIL loop ever fired**, so the route-back is an
untested process.
**Actions:** add a `SMOKE_TIMELINE` block (config.py or game/SMOKE.md) as the single source of truth for
seed frames + ordering; keep a ~15-line "Programmer invariants" section in shared/history.md; let "Read
first" flag the one decision file when a ruling is counter-intuitive; have QA cite the exact failing AC# +
seed frame in any FAIL.

### Retro card — qa-tester
**Well:** the headless smoke gate (exit 0 / exactly 120 f / 3× + `-m` + compileall, fixed seed 1234) was a
fast deterministic no-human filter with zero flakiness; seeded hooks exercised real lifecycles (split/flush/
boss) not just "didn't crash"; standing docs (feature_inventory F1–F32, test_plan) gave a stable regression
map; per-increment qa_report split kept verdicts self-contained.
**Bad:** **every increment PASSed first try — the FAIL loop never fired**, and QA verifies artifacts the
implementer shaped (seeds + AC probes authored by the Programmer); the smoke gate structurally can't reach
new features' real input paths (v8 PAUSE verified by *source inspection*, not a paused frame); **no live-
window verification ever happened** — visual ACs (AC47 anti-collision, α=110 vs 160, the arc) confirmed by
reading constants; regression coverage thinned to "exit 0 + constant-grep" by v8; scratch harnesses built
and thrown away every increment (v1/v2 probes re-coded from memory 4×).
**Actions:** commit a persistent `qa/regression_harness.py` that accumulates AC1–AC60; add a headless
`--event-script` mode that feeds scripted KEYDOWN through the real `_handle_events` (so pause/bomb/quit are
behaviorally tested); make QA author its own seed + one adversarial probe per feature, separate from the
Programmer's; add a "render-smoke" (blit one frame per state, assert no draw raises + key rects don't
overlap); insert one human live-playtest checkpoint per ~2 increments for feel/contrast ACs.

---

## Part 2 — Manager synthesis (cross-cutting themes)

Ranked by **convergence** (how many roles independently raised it) × productivity impact.

| # | Theme | Raised by | So what |
|---|-------|-----------|---------|
| **T1** | **QA never fails → the feedback loop is untested & not independent.** 8/8 first-try passes; seeds/probes authored by the implementer; FAIL route-back never exercised. | qa, orchestrator, programmer | Highest-confidence finding. A gate that has never caught anything isn't proven able to. Decouple QA's probes from the Programmer; require a negative test; behaviorally test input paths. |
| **T2** | **AC13 (long-run difficulty) parked & unvalidated for 8 increments.** Generates a "keep AC13" tax every increment for a thing QA can't measure. | BA, level-designer, orchestrator, designer | Either make it headless-measurable (`--balance-probe`) or formally downgrade it. Stop carrying it forever. |
| **T3** | **Visual/feel ACs are never actually seen.** No live window; contrast/layout/arc confirmed by reading constants; design feel-numbers get zero signal back. | qa, designer, artist | Add a render-smoke gate + a periodic human playtest checkpoint. |
| **T4** | **Smoke-seed timeline is a fragile shared resource re-derived by hand.** f16→f20→f40 crowding 120 f, documented only in comments. | programmer, level-designer, qa | One owned `SMOKE_TIMELINE` source of truth with an ordering check. |
| **T5** | **Roles violate the one-line handoff rule themselves** (BA 36/46, Designer 47/57). The #1 token-cost driver. | BA, designer | Re-enforce by convention; push rationale to history.md. |
| **T6** | **No-op / light increments pay the full 8-chat tax** (v8 LD chat wrote "nothing changed"). | orchestrator, level-designer | Let the Orchestrator declare a SKIP set / inline-confirm for no-impact rows. |
| **T7** | **Linear pipeline has no upstream escape hatch.** Downstream roles silently absorb upstream defects instead of routing them back. | orchestrator, programmer, designer | Add a one-line BLOCKER handoff type. |
| **T8** | **Lever-ownership boundary (esp. Designer↔Artist) renegotiated every increment;** GDD ships placeholder color/alpha the Artist must override. | artist, designer | Lever-ownership mini-table in the GDD template; forbid placeholder color/alpha. |
| **T9** | **Scratch QA/regression harnesses built & deleted each increment** — repeated effort, silent risk of dropping a check. | qa, programmer | Commit a growing `qa/regression_harness.py`. |
| **T10** | **Programmer re-orientation cost** — pipeline order & World contract re-derived from code each session. | programmer | A ~15-line "Programmer invariants" note in shared/history.md. |
| **T11** | **Width-safety / copy surface eyeballed, not catalogued.** | writer | `string_widths` smoke assertion + a copy-surface map in story/index.md. |
| **T12** | **The Open-values delegation table is the team's best pattern** — make it required, not organic. | BA, designer | Codify it in the requirements/GDD templates. |

**The headline:** the *authoring* pipeline is excellent (clean specs, reuse compounding, low token cost,
zero rework). The **verification + feedback** half is the weak side — QA is real but not adversarial or
independent, visual/feel ACs go unseen, and the FAIL/upstream loops have never fired. The most valuable
process investment is hardening verification, not the (already-smooth) authoring chain.

---

## Part 3 — Action register (for human + manager sign-off)

Split by owner. **Nothing here is applied until approved.** "Manager-now" = doc/role/CLAUDE.md edits the
Manager can make this session. "Route to Programmer" = code/tooling, best bundled as a small **v9 — process
hardening** increment. "Decision" = needs a human call.

| ID | Action | Theme | Owner | Status |
|----|--------|-------|-------|--------|
| A1 | Enforce one-line handoffs/history by convention (rationale → history.md) | T5 | Manager-now | proposed |
| A2 | Make the **Open-values delegation table** a required BA artifact; add "BA-ruling vs Delegated-value" header | T12 | Manager-now | proposed |
| A3 | Add a Designer↔Artist **lever-ownership mini-table** to the GDD template; **forbid placeholder color/alpha** (cells = `ARTIST`); surface unresolved layout formulas under "Artist must resolve:" | T8 | Manager-now | proposed |
| A4 | Add a one-line **BLOCKER** upstream-handoff type to CLAUDE.md + handoffs format | T7 | Manager-now | proposed |
| A5 | Let the Orchestrator mark no-impact rows **SKIP / confirm-inline** (lighter path than a full chat+file) | T6 | Manager-now | proposed |
| A6 | Require QA to author its **own seed + one adversarial/negative probe** per feature, independent of the Programmer; cite exact AC# + seed frame on FAIL | T1 | Manager-now (rule) + Programmer (event mode) | proposed |
| A7 | Codify the **volume-neutral re-slice** as a named template move in level_spec/index.md | T2/economy | Manager-now | proposed |
| A8 | Maintain a **"Programmer invariants"** note (pipeline order, World contract, seed-schedule pointer) in shared/history.md | T10 | Manager-now (stub) + Programmer (fill) | proposed |
| A9 | Maintain a **copy-surface map** (string → screen → render site) in story/index.md | T11 | Manager-now | proposed |
| A10 | **AC13 decision:** add a headless `--balance-probe` to measure run length, OR downgrade AC13 to a non-binding design note | T2 | Decision → then Programmer/BA | proposed |
| A11 | Commit a persistent, growing **`qa/regression_harness.py`** (accumulates AC1–AC60) | T9 | Route to Programmer | proposed |
| A12 | Add a **`SMOKE_TIMELINE`** single source of truth (config block + ordering check) | T4 | Route to Programmer | proposed |
| A13 | Add headless **event-injection** (`--event-script`) so pause/bomb/quit are behaviorally tested | T1 | Route to Programmer | proposed |
| A14 | Add a **render-smoke** (one frame per state: no draw raises + key rects don't overlap) + a **`string_widths`** assertion | T3/T11 | Route to Programmer | proposed |
| A15 | Insert a **human playtest checkpoint** (~1 per 2 increments) for feel/contrast/visual ACs | T3 | Decision (human cadence) | proposed |

> **Sign-off log (2026-06-05, human + manager):** ALL actions approved.
> - **Applied this session (Manager-owned):** A1 (one-line handoff reinforce), A2 (required Open-values
>   table + decision-criterion-on-tension → `roles/business-analyst.md`), A3 (lever-ownership + no
>   placeholder color/alpha → `roles/lead-game-designer.md` + `roles/artist.md`), A4 (BLOCKER upstream
>   handoff → `CLAUDE.md` + `handoffs.md`), A5 (SKIP no-impact rows → `CLAUDE.md`), A6 (QA independence +
>   negative test → `roles/qa-tester.md`), A7 (named volume-neutral re-slice → `level_spec/index.md`),
>   A8 (Programmer-invariants stub → `shared/history.md`), A9 (copy-surface map → `story/index.md`).
> - **AC13 (A10):** chose **make it measurable** → `--balance-probe` routed to the Programmer in v9.
> - **Routed to v9 — process hardening (Programmer):** A11 regression harness, A12/A13 SMOKE_TIMELINE +
>   `--event-script`, A14 render-smoke + `string_widths`, A15 human playtest checkpoint. See `backlog.md` v9.
