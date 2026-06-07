# Backlog — project task board

The studio's shared task board across chats. The **Orchestrator** owns it; every role ticks its own
row when finishing. Status: `todo` | `in-progress` | `done` | `blocked`.

> **Board only.** This file is the board + a one-line status. The *why* lives in each domain's
> `history.md`; the cross-role story is in `handoffs.md`. Full v1–v12 detail (per-version task tables
> + status prose) is archived → `../archive/backlog-v1-v12.md`. See `../README.md` for the map.

## Current game state — "Starshard" (v1–v19 shipped & passed QA, as of 2026-06-07)

Top-down auto-scrolling space shooter, modular `pygame-ce` package under `game/`. Shipped capabilities:

- **Core (v1):** ship moves (Arrows/WASD), **Z** fires (cooldown), asteroids/debris + enemy fighters,
  HP + score, START / PLAY / GAME_OVER states. Spec contract: R1–R14, AC1–AC13.
- **Power-ups (v2):** 6 `BonusKind` pickups (Repair / Fan / Rapid / Shield / Score×2 / Bomb), HUD buff
  pills. MVC module split (no line cap). AC14–AC21.
- **Enemies (v5):** REGULAR / HEAVY / SCOUT types + GREEN splitting pellet → 3 RED children. AC22–AC29.
- **Bombs (v6):** **X** = screen-flush + flash (charges start 2 / cap 4, refilled by rarest pickup);
  controls Z=fire / X=bomb. AC30–AC38.
- **Bosses (v7):** Mothership @75 s then +90 s — field-clear, spawn-freeze, 4-step moveset, +1000 reward.
  AC39–AC52.
- **Pause + quit (v8/v10):** **Esc** pauses (full freeze); **hold Q** (~0.5 s, progress arc) quits from
  START / PAUSE / GAME_OVER. AC53–AC68.
- **Polish (v11/v12):** softer invuln pulse (never fully invisible); **hold R** (~0.5 s arc) restarts on
  PAUSE / GAME_OVER. AC69–AC77.
- **Polish (v13):** restart (R) hold-arc co-located on its screen's quit (Q) arc centre (PAUSE 300,483 /
  GAME_OVER 300,545), recolored violet `BONUS_BOMB`; keys told apart by colour not position. Render-only.
- **Save + stats (v14):** one-file versioned JSON save (`game/save.py`, atomic write, %APPDATA%\Starshard
  path, env-overridable for headless) persisting 5 lifetime values — highscore, runs, enemies/asteroids/
  bosses killed; counted at the `scoring.award` destroy sites, flushed **only** on GAME_OVER + hold-Q quit;
  missing/corrupt/unknown-version → zeros. New first-class **STATS** GameState off START (**Tab** toggles
  START⇄STATS, **Esc** backs out; arc-free). AC78–AC85.
- **Second boss + boss pool (v16):** **NOVA**, a projectile-only energy-core boss (4 bullet-only steps;
  spawns **zero** ships) that is **deadlier** than the Mothership on every axis (per-hit 25>15, ram 80>60,
  faster cadence/speed, reward 1500). Every boss-spawn now picks **uniformly at random** from an extensible,
  length-driven registry (`BOSS_POOL`/`BOSS_SPECS`, seedable; future boss = one entry). v7 framing + cadence
  (≈75 s, +90 s) unchanged. AC86–AC93.
- **HP-feedback + bullet-clarity polish (v17):** HP bar fades a **continuous green→amber→red gradient**
  (`hud.hp_bar_color`, supersedes the stepped v1-base §4.3 thresholds); a **subtle red vignette** (`#E63C3C`,
  edge-only falloff + slow breathing pulse) at **HP < 25 %** (render slot 8.5, PLAY only); the **HEAVY green
  pellet** recolored `#8CF03C`→**orchid `#D230DC`** (`EB_COLOR_GREEN`→`EB_COLOR_PURPLE`) to clear the
  Repair/HP green. Render/color only — shapes, sizes, collisions, economy unchanged. No new R#/AC#.
- **Bonus rebalance (v18):** **Fan** nerfed — side beams (±12°) fire at **half** the center cadence (2:1,
  parity resets on collect) and Fan rarer (ladder weight 20→**12**); center beam unchanged. **Rapid retired**
  everywhere; two new timed kinds split its weight 20 → **Overdrive** (`O`, electric-lime `#A6F03C`; cd 12→6 +
  bullet speed 10→12) and **Railgun** (`V`, cyan `#50DCFF`; bullet speed 10→**16** + cd 12→9). **Bullet speed**
  is now a buffable stat; cross-stat stacking = **strongest-wins per stat** (min cd / max speed), bounded +
  clean-reverting; restart resets. Ladder re-sliced to sum 100 over 7 kinds. AC94–AC101.
- **Precise controls (v19):** hold **Shift** = **FOCUS** — ship move speed halved (×0.5, PLAY-only, held-not-
  toggle; firing/bombs/i-frames untouched). Player **damage** hitbox is now an always-on circle `P_HITBOX_R=6`
  (≈50% of `P_R=13`), decoupled from the unchanged ship drawing; **pickup** reach stays generous at `P_R`. All
  bullets **~1.5× larger**, draw==collision every family (`EB_R 5→8`; player bullet `6×18`, coll `r=9`;
  `CYAN_TAIL_LEN 18`). While Shift held in PLAY, a **red 50%-opacity disc** (`#FF2840` @ alpha 128) draws the
  true hitbox (render-only). Enemy/boss body radii unchanged. AC102–AC108.

Contract totals: **R1–R119**, **AC1–AC108**; **pytest suite 117/117** (80 unit / 37 e2e, `workspace/tests/`,
root `pyproject.toml` w/ ruff+pyright). Standing QA docs: `qa/feature_inventory.md`, `qa/test_plan.md`.
(v3 = KB reorg, v4 = QA docs, v9 = process hardening, v15 = test-infra — no game-feature change.)

**Play:** `.\.venv\Scripts\python.exe workspace\game\main.py` — Z fire · X bomb · hold Shift Focus ·
Esc pause · hold Q quit · hold R restart (on PAUSE/GAME_OVER) · Tab stats (on START).

## Current increment — v19: precise controls (focus mode + circular player hitbox + larger bullets) — ✅ SHIPPED (QA PASS 2026-06-07)

New mechanic + balance change. (1) **Precise mode:** hold **SHIFT** (PLAY only) → ship move speed **halved**
(×0.5) for precise dodging; release → normal. (2) **Player hitbox** becomes a **circle ≈50% of the ship's
drawn size**, **always active** (not just in precise mode); the **drawn ship is unchanged**. (3) **Balance:**
**all bullets ~50% larger** (drawn + collision, every projectile family — player & enemy/boss). (4) **Indicator:**
while SHIFT held, draw the actual hitbox as a **red circle @ 50% opacity** on the ship (PLAY only). **Enemy
hitboxes unchanged.** Magnitudes/colors/copy are downstream-role calls. Framing + locked decisions: `brief.md`.

| # | Role | Task | Owner | Status |
|---|---|---|---|---|
| 1 | business-analyst | Formalize: SHIFT precise mode (×0.5 move, PLAY-only, held), always-on circular player hitbox (~50% of ship), all-bullets-~50%-larger balance, precise-mode red hitbox indicator, enemy hitboxes unchanged — as new R#/AC# (requirements vN) | business-analyst | done |
| 2 | lead-game-designer | Design precise-mode feel (held SHIFT, ×0.5, state/interaction rules), the circular-hitbox identity, the red-indicator semantics, and confirm the bullet-size balance intent (GDD vN) | lead-game-designer | done |
| 3 | artist | Define the red hitbox-indicator circle (hue/alpha 50%/blend/render slot) + the ~50%-larger bullet sizes per family (drawn) so visuals match collision; ship draw unchanged (art_spec vN) | artist | done |
| 4 | writer | On-screen control hint for precise mode (SHIFT) if warranted, matching existing hint copy; else confirm no copy change (story vN) | writer | done |
| 5 | level-designer | Lock numbers: precise-mode multiplier (×0.5), player circular-hitbox radius (≈50% of P_R=13 → concrete px), per-family bullet size deltas (≈1.5×, drawn+collision), confirm no tunneling/balance regressions (level_spec vN) | level-designer | done |
| 6 | programmer | Implement: SHIFT precise mode, circular player hitbox + collision swap, ~50% larger bullets (all families), red 50%-opacity indicator on SHIFT, smoke path coverage; ruff+pyright+unit pytest+smoke green | programmer | done |
| 7 | qa-tester | Full rigor: SHIFT halves move & only then shows red circle, hitbox always small/circular/clear of display, all bullets ~50% larger, no tunneling, enemy hitboxes unchanged, no AC1–AC101 regression, suite+smoke green | qa-tester | done (PASS) |

## Last increment — v18: bonus rebalance (Fan nerf + Rapid → two fire/speed bonuses) — ✅ SHIPPED (QA PASS 2026-06-07)

Mechanic + content + economy change. (1) **Fan too strong:** side beams (±12°) fire at **half the center
cadence** (2:1 center:side) and Fan's RNG weight drops (rarer). (2) **Remove Rapid**, add **two** bonus
kinds sharing Rapid's old weight (20): (2a) fire-rate up by the current Rapid amount **+ bullet speed up
a bit**; (2b) **bullet speed up a lot + fire rate up a bit** (easier aiming). Magnitudes/weights/names/
colors are downstream-role calls. Framing + locked decisions: `brief.md`.

| # | Role | Task | Owner | Status |
|---|---|---|---|---|
| 1 | business-analyst | Formalize: Fan side-beam 2:1 cadence + rarer, Rapid removed → two new fire/speed bonus kinds sharing Rapid's weight (effects (2a)/(2b)), as new R#/AC# (requirements vN) | business-analyst | done |
| 2 | lead-game-designer | Design the two new bonuses (identity/feel/duration/stacking) + the Fan side-beam nerf feel; name the bonus kinds conceptually (GDD vN) | lead-game-designer | done |
| 3 | artist | Palette color + HUD pill letter for each of the two new bonus kinds (distinct from each other & the bonus palette); drop Rapid's visual (art_spec vN) | artist | done |
| 4 | writer | On-screen name/label for each new bonus kind (HUD pill + any pickup text), matching the existing bonus copy treatment (story vN) | writer | done |
| 5 | level-designer | Lock numbers: new Fan weight + reweight target (ladder sums 100), 2a/2b weight split, all magnitudes (fire-rate & bullet-speed deltas + base speed), Fan 2:1 ratio confirmation (level_spec vN) | level-designer | done |
| 6 | programmer | Implement: Fan side-beam half-cadence, remove RAPID + add the two kinds (effects/weights/buffs/visuals/copy), reweight ladder, fix SMOKE_BONUS_KIND; ruff+pyright+unit pytest+smoke green | programmer | done |
| 7 | qa-tester | Full rigor: Fan sides fire 2:1 & rarer, Rapid gone, both new bonuses apply correct fire-rate/speed effects, ladder still sums 100, no AC1–AC93 regression, suite+smoke green | qa-tester | done (PASS) |

## Previous increment — v17: HP-feedback + bullet-clarity polish (UI/UX, render-only) — ✅ SHIPPED (QA PASS 2026-06-07)

Three render-only UI/UX improvements (no mechanic/economy/copy change): (1) HP bar fades **green→red
gradually** (replaces the stepped `≥40/<40/<20` thresholds in art_spec v1-base §4.3); (2) a **subtle,
non-distracting red vignette** at **HP < 25 %**; (3) recolor the **HEAVY green pellet** (`#8CF03C`) to a
**non-green** hue — it clashes with the Repair/HP green `#3CD25A`. Color/render only; shapes, sizes,
collisions, and all gameplay numbers unchanged. Framing + locked decisions: `brief.md`.

| # | Role | Task | Owner | Status |
|---|---|---|---|---|
| 1 | artist | Define the HP-bar green→red gradient (endpoints+curve, supersedes v1-base §4.3), the HP<25% red vignette (tint/alpha/falloff/pulse, subtle), and a non-green HEAVY-pellet hue re-verified clear of all entities (art_spec vN) | artist | done |
| 2 | programmer | Implement the three render changes (gradient fill, vignette overlay, new pellet color); ruff+pyright+pytest+smoke green | programmer | done |
| 3 | qa-tester | Verify gradient fades smoothly, vignette appears <25% & stays subtle, pellet no longer green/clash-free, no AC1–AC93 regression, suite+smoke green | qa-tester | done |

Skipped (no impact): business-analyst, lead-game-designer, writer, level-designer.

## Earlier increment — v16: second boss + random boss pool (new content) — ✅ SHIPPED (QA PASS 2026-06-07)

Add a **second boss** and make every boss-spawn pick **uniformly at random** from an **extensible boss
pool** (today: Mothership + new boss; future bosses = one registry entry). Human's hard constraints: the
new boss **spawns no ships/enemies** and has **deadlier attacks** than the Mothership. Boss appearance
cadence (≈75 s then +90 s) and the field-clear/spawn-freeze/reward framing are **unchanged** — only
*which* boss appears is randomized. Framing + locked decisions: `brief.md`.

| # | Role | Task | Owner | Status |
|---|---|---|---|---|
| 1 | business-analyst | Formalize requirements: new boss as content, random extensible-pool selection rule, the 2 hard constraints (no ship spawning, deadlier attacks) → new R#/AC# | business-analyst | done |
| 2 | lead-game-designer | Design the new boss: identity/theme, moveset/attack patterns (deadlier, ship-free), HP, reward, defeat behavior + the pool-selection concept (GDD vN) | lead-game-designer | done |
| 3 | artist | Placeholder shapes + palette for the new boss (distinct from Mothership) + any new attack/projectile visuals (art_spec vN) | artist | done |
| 4 | writer | New boss name + on-screen copy (boss banner / warning), matching Mothership treatment (story vN) | writer | done |
| 5 | level-designer | Random-pool selection rule + extensibility, new boss balance numbers (HP/damage/fire-rate so "deadlier" is concrete), confirm spawn timing unchanged (level_spec vN) | level-designer | done |
| 6 | programmer | Implement: new boss entity + attacks, refactor boss spawn → random pick from extensible pool, wire art/copy/balance; ruff+pyright+unit pytest+smoke green | programmer | done |
| 7 | qa-tester | Full rigor: new boss appears, random selection works & extensible, boss spawns NO ships, attacks deadlier, Mothership parity, no AC1–AC85 regression, suite+smoke green | qa-tester | done |

## Parked (non-blocking)

- **AC13 long runs** — expert pure-dodging can exceed 3 min; tuning levers in `levels/level_spec/`
  §8 / §V2.4. Act only if a human playtest confirms.
- **R35 screen-clear bonus** — deferred since v2 (GDD §V2); non-failing.
