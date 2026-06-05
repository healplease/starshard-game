# Level / Difficulty Spec — index / navigation

> Spawn economy, difficulty ramp, and balance for "Starshard" (owner: **level-designer**). Split by
> increment; **the v1 ramp is UNCHANGED by every later increment** — each one *appends* a spawn slice
> without touching the curve. **All files are live, code-matching contract.** Cross-increment *why* →
> `../history.md`.

## Files (in build order)
| File | Increment | Covers (sections) | Status |
|------|-----------|-------------------|--------|
| `v1-base.md` | v1 base | §1 GDD-default tuning · §2 run-reset values · **§3 difficulty curve (formulas — core)** · §4 spawn rules · §5 milestones/phases · §6 entity caps · §7 survival-bonus · **§8 tuning levers (AC13)** · §9 traceability | shipped ✅ |
| `v2-economy.md` | v2 | **§V2.1 bonus spawn numbers** (drip cadence / enemy-drop % / kind weights / cap) · §V2.2 buff economy/run · §V2.3 AC13 balance · §V2.4 levers · §V2.5 smoke seed · §V2.6 traceability | shipped ✅ |
| `v5-spawn-mix.md` | v5 | **§V5.1 enemy-kind spawn mix** (per-band weights + gates) · §V5.2 realized-mix self-balance · §V5.3 AC13 · §V5.4 levers · §V5.5 smoke coexistence · §V5.6 traceability | shipped ✅ |
| `v6-bomb-economy.md` | v6 | **§V6.1 bomb-pickup weight** (BOMB=6, re-slice of the v2 table) · §V6.2 bomb economy/run · §V6.3 AC13 · §V6.4 `BOMB_SPAWN_LULL=0` · §V6.5 levers · §V6.6 smoke · §V6.7 traceability | shipped ✅ |
| `v7-bosses.md` | v7 | **§V7.1 breakpoint cadence** (75 s / +90 s, CONFIRM) · **§V7.2 spawn-freeze/resume** (skip-no-bank, `BOSS_RESUME_LULL=0`) · §V7.3 fight economy (drip frozen / minion-drops suppressed / minion-score ON) · §V7.4 +1000 reward · §V7.5 AC13 (`BOSS_HP=120` lever) · §V7.6 levers · §V7.7 smoke coexistence · §V7.8 traceability | spec ✅ |
| `v8-pause.md` | v8 | **§V8.1 verdict** (confirmed no-op — zero spawn/pickup/ramp/timing changes) · §V8.2 edge case (real-world vs in-game time, non-issue) · §V8.3 traceability | confirmed no-op ✅ |
| `v10.md` | v10 | **§V10.1 verdict** (confirmed no-op — Q-hold-to-quit on START+GAME_OVER, UI-only, no spawn/pickup/ramp/timing change) · §V10.2 edge case (UI counter, not a game clock) · §V10.3 traceability | confirmed no-op ✅ |

## Where is …? (topic → file)
- **Difficulty ramp formulas (the curve)** → `v1-base.md` §3 (untouched by v2/v5/v6)
- **AC13 (1–3 min run length) levers** → `v1-base.md` §8 (+ per-increment AC13 sections §V2.3, §V5.3, §V6.3)
- **Run-reset / starting values** → `v1-base.md` §2
- **Bonus pickup spawn rates / kind weights** → `v2-economy.md` §V2.1 → **re-sliced** in `v6-bomb-economy.md` §V6.1 (adds BOMB=6)
- **Enemy-kind spawn mix + gates (HEAVY@20s/SCOUT@50s)** → `v5-spawn-mix.md` §V5.1
- **Bomb-pickup scarcity + post-bomb lull** → `v6-bomb-economy.md` §V6.1, §V6.4
- **Boss breakpoint cadence (when a boss fires)** → `v7-bosses.md` §V7.1 (TIME: 75 s, then +90 s)
- **Spawn-freeze + resume during a boss fight** → `v7-bosses.md` §V7.2 (skip-no-bank, no resume lull)
- **Boss-fight economy (drip / minion drops / minion score / +1000 reward)** → `v7-bosses.md` §V7.3, §V7.4
- **v8 Pause economy impact** → `v8-pause.md` §V8.1 (confirmed no-op — no new spawns/pickups/ramp/timing)
- **v10 START/GAME_OVER Q-hold-to-quit economy impact** → `v10.md` §V10.1 (confirmed no-op — UI-only gesture, no spawn/pickup/ramp/timing)

## Updating this spec
- **New increment:** add `vN-<topic>.md` (`# vN increment — …`) + a row + topic-map entry; **state
  explicitly whether the v1 ramp / prior economy is touched** (so far: never). One-line in `../history.md`.
- **Named move — the *volume-neutral re-slice* (retro-blessed 2026-06-05).** To add a pickup/enemy *kind*
  without touching volume: re-slice the existing weight table so it **still sums to 100**, name the **source
  kinds** you took from, and state the **AC13 reason** for each (protect the low-tail compressor, trim the
  high-tail extender). No new spawn path, no extra volume → drip cadence / enemy-drop % / cap stay
  bit-for-bit. This is how v5 re-slid enemy kind and v6 folded in `BOMB=6` — reuse it as a fill-in-the-template
  operation with built-in AC13 protection.
- **Fix shipped balance:** edit that version's file **in place** (keep it matching `workspace/game/`
  spawn/config) and record the why in `../history.md`. The weights/formulas are the contract.
