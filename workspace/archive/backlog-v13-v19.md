# Backlog — archived increment detail (v13–v19)

Frozen 2026-06-07 when the studio turned a new page for v20. These are the per-increment task tables
that were in `../shared/backlog.md`; moved out of the hot path once shipped. The live board keeps only
the capability summary + the current increment + parked items. Earlier detail (v1–v12) is in
`backlog-v1-v12.md`. All of these shipped & passed QA; canonical specs live in each role folder.

> v13/v14/v15 detail was already condensed into the live board's capability summary at ship time
> (v15 was test-infra, v3/v4/v9 were KB/QA/process); their full task tables were not retained
> separately. The v16–v19 tables below are preserved verbatim.

---

## v16: second boss + random boss pool (new content) — ✅ SHIPPED (QA PASS 2026-06-07)

Add a **second boss** and make every boss-spawn pick **uniformly at random** from an **extensible boss
pool** (today: Mothership + new boss; future bosses = one registry entry). Human's hard constraints: the
new boss **spawns no ships/enemies** and has **deadlier attacks** than the Mothership. Boss appearance
cadence (≈75 s then +90 s) and the field-clear/spawn-freeze/reward framing are **unchanged** — only
*which* boss appears is randomized.

| # | Role | Task | Owner | Status |
|---|---|---|---|---|
| 1 | business-analyst | Formalize requirements: new boss as content, random extensible-pool selection rule, the 2 hard constraints (no ship spawning, deadlier attacks) → new R#/AC# | business-analyst | done |
| 2 | lead-game-designer | Design the new boss: identity/theme, moveset/attack patterns (deadlier, ship-free), HP, reward, defeat behavior + the pool-selection concept (GDD vN) | lead-game-designer | done |
| 3 | artist | Placeholder shapes + palette for the new boss (distinct from Mothership) + any new attack/projectile visuals (art_spec vN) | artist | done |
| 4 | writer | New boss name + on-screen copy (boss banner / warning), matching Mothership treatment (story vN) | writer | done |
| 5 | level-designer | Random-pool selection rule + extensibility, new boss balance numbers (HP/damage/fire-rate so "deadlier" is concrete), confirm spawn timing unchanged (level_spec vN) | level-designer | done |
| 6 | programmer | Implement: new boss entity + attacks, refactor boss spawn → random pick from extensible pool, wire art/copy/balance; ruff+pyright+unit pytest+smoke green | programmer | done |
| 7 | qa-tester | Full rigor: new boss appears, random selection works & extensible, boss spawns NO ships, attacks deadlier, Mothership parity, no AC1–AC85 regression, suite+smoke green | qa-tester | done |

## v17: HP-feedback + bullet-clarity polish (UI/UX, render-only) — ✅ SHIPPED (QA PASS 2026-06-07)

Three render-only UI/UX improvements (no mechanic/economy/copy change): (1) HP bar fades **green→red
gradually** (replaces the stepped `≥40/<40/<20` thresholds in art_spec v1-base §4.3); (2) a **subtle,
non-distracting red vignette** at **HP < 25 %**; (3) recolor the **HEAVY green pellet** (`#8CF03C`) to a
**non-green** hue — it clashes with the Repair/HP green `#3CD25A`. Color/render only; shapes, sizes,
collisions, and all gameplay numbers unchanged.

| # | Role | Task | Owner | Status |
|---|---|---|---|---|
| 1 | artist | Define the HP-bar green→red gradient (endpoints+curve, supersedes v1-base §4.3), the HP<25% red vignette (tint/alpha/falloff/pulse, subtle), and a non-green HEAVY-pellet hue re-verified clear of all entities (art_spec vN) | artist | done |
| 2 | programmer | Implement the three render changes (gradient fill, vignette overlay, new pellet color); ruff+pyright+pytest+smoke green | programmer | done |
| 3 | qa-tester | Verify gradient fades smoothly, vignette appears <25% & stays subtle, pellet no longer green/clash-free, no AC1–AC93 regression, suite+smoke green | qa-tester | done |

Skipped (no impact): business-analyst, lead-game-designer, writer, level-designer.

## v18: bonus rebalance (Fan nerf + Rapid → two fire/speed bonuses) — ✅ SHIPPED (QA PASS 2026-06-07)

Mechanic + content + economy change. (1) **Fan too strong:** side beams (±12°) fire at **half the center
cadence** (2:1 center:side) and Fan's RNG weight drops (rarer). (2) **Remove Rapid**, add **two** bonus
kinds sharing Rapid's old weight (20): (2a) fire-rate up by the current Rapid amount **+ bullet speed up
a bit**; (2b) **bullet speed up a lot + fire rate up a bit** (easier aiming).

| # | Role | Task | Owner | Status |
|---|---|---|---|---|
| 1 | business-analyst | Formalize: Fan side-beam 2:1 cadence + rarer, Rapid removed → two new fire/speed bonus kinds sharing Rapid's weight (effects (2a)/(2b)), as new R#/AC# (requirements vN) | business-analyst | done |
| 2 | lead-game-designer | Design the two new bonuses (identity/feel/duration/stacking) + the Fan side-beam nerf feel; name the bonus kinds conceptually (GDD vN) | lead-game-designer | done |
| 3 | artist | Palette color + HUD pill letter for each of the two new bonus kinds (distinct from each other & the bonus palette); drop Rapid's visual (art_spec vN) | artist | done |
| 4 | writer | On-screen name/label for each new bonus kind (HUD pill + any pickup text), matching the existing bonus copy treatment (story vN) | writer | done |
| 5 | level-designer | Lock numbers: new Fan weight + reweight target (ladder sums 100), 2a/2b weight split, all magnitudes (fire-rate & bullet-speed deltas + base speed), Fan 2:1 ratio confirmation (level_spec vN) | level-designer | done |
| 6 | programmer | Implement: Fan side-beam half-cadence, remove RAPID + add the two kinds (effects/weights/buffs/visuals/copy), reweight ladder, fix SMOKE_BONUS_KIND; ruff+pyright+unit pytest+smoke green | programmer | done |
| 7 | qa-tester | Full rigor: Fan sides fire 2:1 & rarer, Rapid gone, both new bonuses apply correct fire-rate/speed effects, ladder still sums 100, no AC1–AC93 regression, suite+smoke green | qa-tester | done (PASS) |

## v19: precise controls (focus mode + circular player hitbox + larger bullets) — ✅ SHIPPED (QA PASS 2026-06-07)

New mechanic + balance change. (1) **Precise mode:** hold **SHIFT** (PLAY only) → ship move speed **halved**
(×0.5) for precise dodging; release → normal. (2) **Player hitbox** becomes a **circle ≈50% of the ship's
drawn size**, **always active** (not just in precise mode); the **drawn ship is unchanged**. (3) **Balance:**
**all bullets ~50% larger** (drawn + collision, every projectile family — player & enemy/boss). (4) **Indicator:**
while SHIFT held, draw the actual hitbox as a **red circle @ 50% opacity** on the ship (PLAY only). **Enemy
hitboxes unchanged.**

| # | Role | Task | Owner | Status |
|---|---|---|---|---|
| 1 | business-analyst | Formalize: SHIFT precise mode (×0.5 move, PLAY-only, held), always-on circular player hitbox (~50% of ship), all-bullets-~50%-larger balance, precise-mode red hitbox indicator, enemy hitboxes unchanged — as new R#/AC# (requirements vN) | business-analyst | done |
| 2 | lead-game-designer | Design precise-mode feel (held SHIFT, ×0.5, state/interaction rules), the circular-hitbox identity, the red-indicator semantics, and confirm the bullet-size balance intent (GDD vN) | lead-game-designer | done |
| 3 | artist | Define the red hitbox-indicator circle (hue/alpha 50%/blend/render slot) + the ~50%-larger bullet sizes per family (drawn) so visuals match collision; ship draw unchanged (art_spec vN) | artist | done |
| 4 | writer | On-screen control hint for precise mode (SHIFT) if warranted, matching existing hint copy; else confirm no copy change (story vN) | writer | done |
| 5 | level-designer | Lock numbers: precise-mode multiplier (×0.5), player circular-hitbox radius (≈50% of P_R=13 → concrete px), per-family bullet size deltas (≈1.5×, drawn+collision), confirm no tunneling/balance regressions (level_spec vN) | level-designer | done |
| 6 | programmer | Implement: SHIFT precise mode, circular player hitbox + collision swap, ~50% larger bullets (all families), red 50%-opacity indicator on SHIFT, smoke path coverage; ruff+pyright+unit pytest+smoke green | programmer | done |
| 7 | qa-tester | Full rigor: SHIFT halves move & only then shows red circle, hitbox always small/circular/clear of display, all bullets ~50% larger, no tunneling, enemy hitboxes unchanged, no AC1–AC101 regression, suite+smoke green | qa-tester | done (PASS) |
