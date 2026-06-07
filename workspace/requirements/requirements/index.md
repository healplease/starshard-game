# Requirements — index / navigation

> The requirement set + acceptance criteria for "Starshard" (owner: **business-analyst**). Split by
> increment; requirement IDs (R#) and acceptance criteria (AC#) are **append-only and never renumbered**.
> **All files are live, code-matching contract.** Cross-increment *why* → `../history.md`.

## Files (in build order)
| File | Increment | Requirements / ACs | Status |
|------|-----------|--------------------|--------|
| `v1-base.md` | v1 base | **R1–R22** (MoSCoW) + non-goals + **AC1–AC13**; C1–C3 constraints | shipped ✅ |
| `v2.md` | v2 | **R23–R35** (bonus pickups + modular refactor; C3 line-cap RETIRED) + **AC14–AC21** | shipped ✅ |
| `v5.md` | v5 | **R36–R44** (three enemy types + splitting pellet) + **AC22–AC29** | shipped ✅ |
| `v6.md` | v6 | **R45–R55** (bombs/panic button + Z/X remap) + **AC30–AC38** | shipped ✅ |
| `v7.md` | v7 | **R56–R68** (boss-fight loop + Mothership 4-step moveset) + **AC39–AC52** | shipped ✅ |
| `v8.md` | v8 | **R69–R75** (pause/unpause + Q-hold to quit + pause overlay) + **AC53–AC60** | shipped ✅ |
| `v10.md` | v10 | **R76–R82** (Q-hold-to-quit on START + GAME_OVER; reuses v8 gesture) + **AC61–AC68** | shipped ✅ |
| `v12.md` | v12 | **R83–R91** (hold-R-to-restart on PAUSE + GAME_OVER; two independent hold counters + arcs) + **AC69–AC77** | shipped ✅ |
| `v14.md` | v14 | **R92–R98** (one-file JSON save + 5 lifetime counts + flush contract + corrupt fallback + stats screen) + **AC78–AC85** | shipped ✅ |
| `v16.md` | v16 | **R99–R105** (second boss + uniform-random extensible boss pool; 2 hard constraints: no ship spawning, deadlier attacks) + **AC86–AC93** | in progress |

## Where is …? (topic → file)
- **R1–R22 / AC1–AC13 (base game)** → `v1-base.md`
- **C3 (~500-line cap) — RETIRED** → noted in `v2.md` (was `v1-base.md`)
- **Bonuses / power-ups (R23–R35)** → `v2.md`
- **Enemy types (R36–R44)** → `v5.md`
- **Bombs + control remap (R45–R55)** → `v6.md`
- **Bosses / Mothership boss fights (R56–R68)** → `v7.md`
- **Pause / Q-hold to quit (R69–R75)** → `v8.md`
- **Q-hold-to-quit on START + GAME_OVER (R76–R82)** → `v10.md`
- **Hold-R-to-restart on PAUSE + GAME_OVER (R83–R91)** → `v12.md`
- **Save system + lifetime-stats counts/screen (R92–R98)** → `v14.md`
- **Second boss + random extensible boss pool (R99–R105)** → `v16.md`
- Quick rule: **R1–22→v1 · R23–35→v2 · R36–44→v5 · R45–55→v6 · R56–68→v7 · R69–75→v8 · R76–82→v10 · R83–91→v12 · R92–98→v14 · R99–105→v16**; **AC1–13→v1 · 14–21→v2 · 22–29→v5 · 30–38→v6 · 39–52→v7 · 53–60→v8 · 61–68→v10 · 69–77→v12 · 78–85→v14 · 86–93→v16**.

## Updating this spec
- **New increment:** add `vN.md` (`# vN increment — …`) with the next R#/AC# block (continue the
  numbering — never reuse IDs) + a row + topic-map entry. One-line the why in `../history.md`.
- **Change a shipped requirement:** edit that version's file **in place**; if it changes behavior, the
  downstream specs + `workspace/game/` must follow. Record the why in `../history.md`.
