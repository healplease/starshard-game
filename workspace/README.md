# workspace/ — the shared blackboard (map)

This is the studio's shared memory. It's organized so **each role loads only its own scope plus the
small shared core** — not the whole project history. The Manager owns this structure.

## Layout

```
workspace/
  README.md            ← you are here (the map)
  shared/              ← read by everyone, kept small
    brief.md             the theme + current-increment framing
    backlog.md           the task board (board only — no long narrative)
    handoffs.md          the agent-to-agent log (recent increments)
    history.md           cross-cutting orchestrator + programmer notes
    (Specs are SPLIT BY INCREMENT into a folder per artifact — each has an index.md you read first.)
  requirements/        ← business-analyst's scope
    requirements/        index.md + v1-base / v2 / v5 / v6  (R1–R55, ACs)
    history.md           dated decision notes (the "why")
  design/              ← lead-game-designer's scope
    gdd/                 index.md + v1-base / v2-bonuses / v5-enemies / v6-bombs
    history.md
  art/                 ← artist's scope
    art_spec/            index.md + v1-base / v2-bonus-pickups / v5-enemy-bullets / v6-bomb-flash
    history.md
  story/               ← writer's scope
    story/               index.md + v1-base / v2 / v5 / v6
    history.md
  levels/              ← level-designer's scope
    level_spec/          index.md + v1-base / v2-economy / v5-spawn-mix / v6-bomb-economy
    history.md
  qa/                  ← qa-tester's scope
    qa_report/           index.md + v1 / v2 / v5 / v6  (per-run verdicts)
    test_plan.md         standing: smoke + regression plans + per-feature checklists
    feature_inventory.md standing: 32 features F1–F32 → R#/AC#/module
    history.md
  archive/             ← frozen history; you rarely need to open this
    handoffs-v1.md, handoffs-v2-v5.md, brief-increments-v2-v5.md, project-log-v1.md, README.md
  game/                ← the programmer's artifact (the actual game; unchanged)
```

## How to use it (per role)

- **Always start with** `shared/backlog.md` (what's the state?) and `shared/handoffs.md` (what just
  happened?). Both are deliberately short.
- **Then open your own spec folder's `index.md`** — e.g. the artist reads `art/art_spec/index.md`. The
  index is the heading file: it lists the per-increment files, a **topic → file** map, and the rule for
  updating. Read it, then open only the version file(s) you need (usually the increment you're working on
  + any base section it builds on). Same for the upstream spec(s) your role depends on (e.g. the artist
  also reads `design/gdd/index.md`). Your `roles/<role>.md` "Read first" lists the exact paths.
- **Need the reasoning behind a decision?** Open that domain's `history.md` — but only if you need the
  *why*. The spec files alone are enough to do the work.
- **Don't read `archive/`** unless you're specifically digging into old increments.

## Rules

- **Specs are canonical and match the shipped code.** Don't rewrite numbers/rules casually — for a new
  increment add a `vN…md` file in your spec folder and a row in its `index.md` (see the index's "Updating"
  note); to correct a shipped feature, edit that version's file in place.
- **Keep the hot path small.** New narrative goes to the right `history.md`, not into `backlog.md`.
- **Restructuring is the Manager's job.** Other roles add to their own files; the Manager reorganizes
  across folders and realigns the role definitions when the layout changes.
