# archive/ — frozen history (you rarely need to read this)

This folder holds the project's older narrative, moved out of the hot path so no role has to load it
just to start working. Nothing here is required to build or play the game.

| File | What it is |
|------|-----------|
| `handoffs-v1.md` | The v1 handoff log (entries 1–9). The active log is `../shared/handoffs.md`. |
| `handoffs-v2-v5.md` | The v2–v5 handoff log (entries 10–33: bonuses, KB reorg, QA docs, enemy types). |
| `handoffs-v6-v12.md` | The v6–v12 handoff log (entries 34–94: bombs, bosses, pause/quit, invuln pulse, hold-R). |
| `handoffs-v13-v19.md` | The v13–v19 handoff log (entries 95–152: arc co-location, save/stats, pytest suite, NOVA boss, HP polish, bonus rebalance, precise controls). |
| `backlog-v1-v12.md` | The full v1–v12 backlog detail (per-version task tables + status prose), frozen 2026-06-06. |
| `backlog-v13-v19.md` | The v16–v19 backlog task tables, frozen 2026-06-07 (v13–v15 folded into the live summary). |
| `project-log-v1.md` | The original v1 "Status summary" prose, verbatim. |
| `brief-increments-v2-v5.md` | The orchestrator's kickoff framings for the v2 + v5 increments. |
| `brief-increments-v7-v12.md` | The orchestrator's kickoff framings for the v7–v12 increments. |
| `brief-increments-v13-v19.md` | The orchestrator's kickoff framing for v19 (v13–v18 framings were not retained separately). |

**Rule (for the Manager):** when an increment closes, its detailed narrative is distributed to each
domain's `history.md` and its handoffs are archived here. The live `shared/backlog.md` keeps only the
board; per-domain `history.md` files keep the *why*. Append, don't rewrite, what lands here.
