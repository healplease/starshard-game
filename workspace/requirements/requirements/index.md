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
| `v7.md` | v7 | **R56–R68** (boss-fight loop + Mothership 4-step moveset) + **AC39–AC52** | in progress |

## Where is …? (topic → file)
- **R1–R22 / AC1–AC13 (base game)** → `v1-base.md`
- **C3 (~500-line cap) — RETIRED** → noted in `v2.md` (was `v1-base.md`)
- **Bonuses / power-ups (R23–R35)** → `v2.md`
- **Enemy types (R36–R44)** → `v5.md`
- **Bombs + control remap (R45–R55)** → `v6.md`
- **Bosses / Mothership boss fights (R56–R68)** → `v7.md`
- Quick rule: **R1–22→v1 · R23–35→v2 · R36–44→v5 · R45–55→v6 · R56–68→v7**; **AC1–13→v1 · 14–21→v2 · 22–29→v5 · 30–38→v6 · 39–52→v7**.

## Updating this spec
- **New increment:** add `vN.md` (`# vN increment — …`) with the next R#/AC# block (continue the
  numbering — never reuse IDs) + a row + topic-map entry. One-line the why in `../history.md`.
- **Change a shipped requirement:** edit that version's file **in place**; if it changes behavior, the
  downstream specs + `workspace/game/` must follow. Record the why in `../history.md`.
