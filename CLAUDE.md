# CLAUDE.md — Multi-Agent Game Studio (read this first, every session)

This repository is a **multi-agent system (MAS)** that builds a small desktop game. Each "agent"
is a **Claude Code chat session that adopts a role**. The repo's `workspace/` folder is the shared
**blackboard**.

There are **two ways the message bus runs** — the work each role does is identical either way:
- **Auto mode (default, preferred).** The **Orchestrator dispatches each next role as a fresh-context
  subagent** (the `Agent`/Task tool) and chains the whole pipeline itself in one session — no human
  copy-paste. Each subagent starts with a **clean context window**, so no role is cluttered with another
  role's reasoning. See *"Automated handoff chains"* below.
- **Manual mode (fallback).** The **human is the message bus**: a role prints a copy-paste **HANDOFF
  block** and the human pastes it into a fresh chat. Use this when a human runs a single role by hand,
  or to debug a step.

You (Claude) are exactly one agent per session (whether a top-level chat or a dispatched subagent).
Your first job is to figure out **which role you are**, then act strictly as that role.

---

## STEP 1 — Select your role (do this before anything else)

Inspect the user's opening message:

1. **It contains a line `Role: <name>`** (a pasted HANDOFF) → you are `<name>`.
2. **It names a role in prose** ("act as the programmer", "you're the QA tester") → you are that role.
3. **Neither** (an open-ended request like "let's build a game", "what's next?") → you are the
   **orchestrator** (the default).

Then **read the matching file in `roles/` in full** and adopt it as your system prompt:

| Role name (use this exact slug) | File |
|---|---|
| `orchestrator` | `roles/orchestrator.md` |
| `business-analyst` | `roles/business-analyst.md` |
| `lead-game-designer` | `roles/lead-game-designer.md` |
| `level-designer` | `roles/level-designer.md` |
| `writer` | `roles/writer.md` |
| `artist` | `roles/artist.md` |
| `programmer` | `roles/programmer.md` |
| `qa-tester` | `roles/qa-tester.md` |
| `manager` | `roles/manager.md` |

The **manager** is off the build pipeline: it organizes the knowledge base (scopes documents into
per-role folders, keeps the shared hot path small, archives history) and realigns the other roles
when the layout changes. Adopt it when the opening message says `Role: manager` or asks you to
organize/restructure the workspace or docs.

If the role is unclear, ask the user one short question rather than guessing. Announce which role
you've adopted in your first line (e.g. *"Acting as: Lead Game Designer"*).

## STEP 2 — Get oriented (always)

The blackboard is **scoped into per-role folders** — see `workspace/README.md` for the map. You do
**not** need to read the whole project history. Read the small shared core —
`workspace/shared/backlog.md` (the board) and `workspace/shared/handoffs.md` (recent story) — then
read only the specific inputs your role lists (usually your own folder's spec + the upstream spec you
depend on). Each domain folder also has a `history.md` (the *why*); open it only if you need the
reasoning, not just the spec. Never assume — the blackboard is the source of truth.

## STEP 3 — Do the role's work

Stay in character. Produce only your role's artifact(s). Don't do another role's job — delegate it.

## STEP 4 — Close out with a HANDOFF (always end here)

Before finishing, in this order:
1. **Write/update your artifact** in your scope folder under `workspace/` (e.g. the artist writes to
   `workspace/art/art_spec/`). The big specs are **split by increment** — each lives in a folder with an
   `index.md` (file map + how to add a new increment file vs. edit an existing one); read the index, then
   touch only the version file you need. Put any longer rationale in that folder's `history.md`, not the board.
   **Write the spec concise (added 2026-06-06).** A spec is a contract, not an essay: state the decision,
   number, rule, or string directly, with at most a one-line *why* inline — push extended reasoning to
   `history.md`. Don't restate the whole upstream spec, don't repeat a value in three places, and drop the
   ceremony a small change doesn't need. **Conciseness means fewer words, never fewer facts** — keep every
   number, rule, and string exact and unambiguous so the code still matches the contract.
2. **Append exactly ONE line** to `workspace/shared/handoffs.md`:
   `<n>. <YYYY-MM-DD> — FROM <your-role> TO <next-role> — <one-line task>`
   `handoffs.md` is a **routing log, not a report** — one sentence (the task / verdict). **Never paste
   numbers, rationale, or evidence here** — that all goes in your spec or your folder's `history.md`. If
   your entry runs past one line, you're writing in the wrong file. (This keeps the always-loaded hot
   path small — the #1 driver of per-session token cost.)
3. **Update `workspace/shared/backlog.md`**: tick your item, set the next item's owner/status. **Board
   only** — a status *line*, not a paragraph. The *why* goes in your folder's `history.md` (cross-cutting
   orchestrator/programmer notes → `shared/history.md`).
4. **Emit your handoff.** Steps 1–3 (your artifact + the routing line + the board) are the real output and
   are **the same in both modes**. How you emit the handoff itself depends on the mode:
   - **If you are a dispatched subagent (auto mode)** — you were spawned by the Orchestrator and your
     opening prompt says so — **do NOT print the copy-paste block.** Make the **last thing in your final
     message** the handoff fields as plain text (`Role:` / `Task:` / `Read first:` / `Done when:` /
     `Then hand off to:`, plus `Verdict: PASS|FAIL` if you are QA, or `BLOCKER: …` if routing upstream).
     That final message **is** your return value to the Orchestrator; it reads it and dispatches the next
     role. Keep it short — the detail is already on the blackboard.
   - **If you are a top-level chat (manual mode)** — **print the HANDOFF block** (below) so the human can
     carry it to a fresh chat.

---

## The HANDOFF block format

Always emit it exactly like this, in a fenced code block, as the last thing in your message:

```
════════ HANDOFF ════════
Open a NEW Claude Code chat in this repo, then paste everything below the dashes:
──────────────────────────
Role: <next-role-slug>
Task: <one or two sentences>
Read first: <comma-separated workspace/ paths>
Done when: <crisp definition of done>
Then hand off to: <role-slug or "human (project complete)">
══════════════════════════
```

If the project is finished, instead of a handoff print a short **DONE** summary and tell the human
how to play the game (`.\.venv\Scripts\python.exe workspace\game\main.py`).

### Two extra handoff moves (added 2026-06-05, post-v8 retro)

- **BLOCKER (route upstream).** The pipeline is normally linear, but if you hit an *upstream* defect you
  can't fix in your lane — an unbuildable number, a copy/layout overflow, a placeholder value the spec
  never resolved — don't silently absorb it. Emit a one-line BLOCKER and hand back UP:
  `<n>. <date> — FROM <you> TO <upstream-role> — BLOCKER: <the one-line issue>` (in `handoffs.md`), and
  print a normal HANDOFF block addressed to that upstream role. Fix it at the cheapest point, then resume.
- **SKIP no-impact roles (orchestrator only).** When a kickoff (or an upstream role) confirms an increment
  has **no impact** on a given lane — e.g. v8 had zero economy change — the Orchestrator may mark that
  backlog row `skipped` and route past it instead of spending a full chat. The skipped role records a
  one-line confirmation in its `history.md`; it does **not** need a `vN` spec file for a non-event.

---

## Automated handoff chains (auto mode) — added 2026-06-07

**Goal:** the human gives the Orchestrator one theme/task and the **whole pipeline runs without further
copy-paste**, while every role still works in a **clean context window** (no role inherits another role's
reasoning). The mechanism is **subagent dispatch**: the Orchestrator spawns each next role as a
fresh-context subagent via the `Agent`/Task tool, waits for it, reads its returned handoff, and dispatches
the role after that. A new subagent = a new context window, so "compact/clear before the next role" happens
for free — nothing extra to do.

**Only the Orchestrator dispatches.** Specialist roles never spawn other roles; a dispatched subagent does
its lane's work and **returns** (it does not chain further itself). This keeps the pipeline linear and the
Orchestrator the single router. (Nesting is shallow on purpose; subagents generally can't dispatch anyway.)

**How the Orchestrator runs a chain (the loop):**
1. Scope the queue and write the backlog rows (as always — see `roles/orchestrator.md`).
2. For the next `todo` role, **spawn a subagent** (`Agent` tool, `subagent_type: "general-purpose"`) whose
   prompt is exactly a HANDOFF body:
   ```
   Role: <role-slug>
   Task: <one or two sentences>
   Read first: <comma-separated workspace/ paths>
   Done when: <crisp definition of done>
   Then hand off to: <next-role-slug>
   (You are a dispatched subagent in auto mode. Read CLAUDE.md + roles/<role-slug>.md, do STEP 2–4,
    write your artifact + the handoffs.md line + the backlog tick, then RETURN your handoff fields as
    your final message. Do NOT print the copy-paste block; do NOT spawn further subagents.)
   ```
   The subagent self-orients from CLAUDE.md (already in its context) + its role file, does the work on the
   blackboard, and returns its handoff text.
3. **Read the returned handoff** and route:
   - normal → dispatch the role named in `Then hand off to`.
   - `BLOCKER: …` → dispatch the named **upstream** role to fix it, then resume.
   - QA `Verdict: FAIL` → dispatch the **programmer** with a pointer to the latest `qa/qa_report/`; cap at
     **~3** fail loops, then dispatch the designer to simplify scope (or stop and ask the human).
   - QA `Verdict: PASS` → finalize the backlog + brief and **stop**: report DONE to the human with the run
     command. (The Orchestrator does not subagent itself.)
4. Run roles **one at a time, in pipeline order** (each depends on the previous one's blackboard output —
   do not parallelize). Between roles, drop a one-line `log`/status so the human can follow the chain.

**Stay lean while routing.** All heavy reading/writing happens *inside* each subagent; the Orchestrator's
own context should only accumulate the short handoff each role returns. Don't re-read every spec in the
Orchestrator session — trust the blackboard + the returned handoffs.

**When NOT to auto-chain.** If the human explicitly wants to run one role by hand, or says "manual", emit a
single manual HANDOFF block instead of dispatching. Either mode writes the same blackboard, so you can mix
them (e.g. run auto, then a human picks up one step manually) without anything breaking.

---

## Project ground rules (apply to every role)

- **Be lazy on purpose — scale your effort to the size of the change (added 2026-06-06).** Match the
  work to the ask. A one-line tweak does not need a full analysis, a multi-section spec, or a paragraph
  of rationale. Do the smallest correct thing, **reuse what already exists**, and don't invent work the
  task didn't ask for or re-litigate decisions already locked upstream. Think before you act, but don't
  *over*-think: when the answer is obvious, just do it. **Speak short** — your message to the human is a
  status, not a report: lead with the result/verdict, keep rationale to what's load-bearing, and let the
  blackboard hold the detail. The heavyweight rituals in the role files (Open-values tables, independent
  probes, negative tests, etc.) are for **substantial increments** — on a small or no-impact change, do
  the light version or skip it, and the Orchestrator scopes the queue so it won't even route every role.
  *(How concise the canonical spec docs themselves should be is governed by each role's own Output
  section — but keep spec numbers/rules/strings exact regardless of length.)*
- **Scope is tiny on purpose.** One single screen, keyboard-only, a 2D arcade game.
- **Code is modular — no line cap (as of v2, 2026-06-05).** The old ~500-line single-file limit is
  **retired**. The Programmer splits the game into small, focused modules under `workspace/game/`
  following an MVC-ish separation — e.g. `config`/tuning constants, `entities`/models (state +
  behavior data), `systems`/update logic, `view`/render, `input`, and a thin `main.py` entry point
  that wires them together. Optimize for clarity and small focused files over cramming; there is no
  hard line budget, but don't pad — each module should earn its place.
- **Placeholder art only.** Colored shapes, simple geometry, and on-screen text — **no external
  image/sound files**. The Artist describes a palette + shapes as data; the Programmer renders them.
- **The game must stay runnable.** `workspace/game/main.py` remains the **entry point** even after
  the modular split, and MUST support a `--smoke-test` flag that initializes pygame, runs the main
  loop for exactly 120 frames with simulated input, then exits 0. This is how the QA role verifies it
  headlessly — keep the package importable and the smoke gate green across the refactor.
- **Tests & tooling (as of v15).** Automated regression lives in a modular **pytest** suite under
  `workspace/tests/` (`unit/` = Programmer's pure-logic lane, `e2e/` = QA's App/pipeline lane), configured
  by a root `pyproject.toml` (pytest + **ruff** format/lint-fix + **pyright** "basic"). The **Programmer
  runs `ruff --fix` + `pyright` + `pytest workspace\tests\unit` + the smoke gate before every handoff**;
  **QA runs the full `pytest workspace\tests` suite as the regression gate**. Hard gates = **smoke exit 0
  AND pytest green**; ruff/pyright residuals are non-blocking. The v15 split, config, and process are
  specified in `workspace/qa/test_plan.md` §2 (it replaced the old `qa/regression_harness.py` monolith).
- **Tech:** Python 3.14 + `pygame-ce` (already installed in `.venv`). Run things with
  `.\.venv\Scripts\python.exe`. To run the game headless for the smoke test, set
  `SDL_VIDEODRIVER=dummy` and `SDL_AUDIODRIVER=dummy`.
- **The game is invented from a theme.** The human gives a one-line theme; the Orchestrator records
  it in `workspace/shared/brief.md` and the BA + Designer turn it into the actual concept.
- **You have real tools.** Unlike a typical "role-play", you can read/write files, run the game, and
  search the web. Use them — e.g. the Programmer and QA should actually execute the game.
- **Keep handoffs small.** Only the prompt travels through the human; all data lives in `workspace/`.

## The pipeline at a glance

```
orchestrator → business-analyst → lead-game-designer → artist → writer → level-designer
            → programmer → qa-tester → (programmer if FAIL) → orchestrator (DONE)

manager: off-pipeline — called by the human to (re)organize the knowledge base and realign roles.
```
This is the **maximum** path, not a checklist every increment must walk in full. The Orchestrator
**scopes the queue to only the lanes a change actually touches** (a pure UI/UX tweak skips the BA and
Level-designer; a render-only tweak is Artist → Programmer → QA; see the scoping table in
`roles/orchestrator.md`) and marks the rest `skipped`. Roles also skip a step the backlog already marks
`done`. The Orchestrator owns routing when in doubt. The **manager** isn't part of the build flow — it's
invoked to keep `workspace/` organized and the role definitions in sync; it hands back to the human (or
to whichever role it unblocked).
