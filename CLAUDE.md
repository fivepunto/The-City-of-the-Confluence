# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A visual-novel / RPG hybrid ("The City of the Confluence") built in **Ren'Py 8.5.3**,
adapting the **D&D 5.2 SRD**. The rules engine is built and largely complete; the
live work is content authoring, refinement, and polish. Mechanical coverage is a
deliberate **vertical slice**: character levels 1–3 and structured spell tiers 0–2.
Features outside the slice keep their data records but are intentionally *not* wired
into the engine (the deferred list lives at the bottom of `game/core/hooks.py`).

## The authoritative design doc lives OUTSIDE this repo

Records and comments cite a Game Design Document via `src` strings like `"§7.1 L399"`
(section-sign glyph + line number) pointing at `docs/gdd.md`. **That file is not in
this repository** — `docs/` does not exist, and no runtime code path reads it; the
`src` strings are inert provenance metadata. The canonical rules, story, palette, and
visual identity live in an external owner-authored doc (referred to in code as the
"Desktop doc" / "rules doc"). The iron rules it sets — **never invent rules or story;
DATA vs GUIDANCE; one registry; rollback discipline** — are enforced throughout the
code. Do not fabricate rules text, lore, or numbers to fill a gap; surface the gap
instead. Placeholder content is tracked inline with `G-0xx` GAP ids (e.g. districts
G-038, quests G-039, expedition G-043/G-044).

## The hard boundary (read this first)

**`game/data/` and `game/core/` are pure Python with zero `renpy` imports.** The
`.rpy` files are the Ren'Py layer (screens + boot glue). Imports flow one way: `.rpy`
imports `core`/`data`, never the reverse, and `core/registry.py` doesn't even import
`game.data`. This boundary is what lets the whole rules engine be validated headlessly
and keeps rules logic out of screens. Preserve it: if you find yourself wanting `import
renpy` under `core/` or `data/`, the logic belongs in the `.rpy` layer instead.

## Commands

A headless **pytest suite** lives in `tests/` (the pure-Python core + data
registry import without Ren'Py): `python -m pytest tests/` runs it; with pytest
absent, the test functions are plain `assert`s you can call directly. It covers
`registry.validate`/`content_problems`, builds every class to the level cap via a
first-legal chooser, and regression-guards combat-rule fixes. Beyond that,
verification is in-engine and via the Ren'Py MCP server. There is no `make`/build
config.

- **Prefer the `renpy-mcp` tools** (configured in `.mcp.json`, SDK at
  `/home/fivepunto/renpy/renpy-8.5.3-sdk`) for lint, compile, screen inspection,
  story-flow, asset/translation checks, and live screenshots — e.g.
  `mcp__renpy-mcp__lint_project`, `compile_project`, `live_screenshot`. Don't guess
  from filenames when a tool can answer.
- **Raw lint (fallback):** `/home/fivepunto/renpy/renpy-8.5.3-sdk/renpy.sh
  /mnt/c/Users/suhel/Desktop/Project/The-City-of-the-Confluence lint`. Under WSL run
  `renpy.sh`, not the `.exe`; dummy-driver GL errors are environmental, not failures.
- **Boot-time structural check (automatic):** in an unpacked project `config.developer`
  is auto-True, so `game/script.rpy` runs `assert registry.validate(REG) == []` on every
  boot. Players in a packaged build never hit it.
- **Full content validation (in-engine):** the debug hub's **"Validate content"** button
  runs `core.registry.content_problems(REG)` — structural `validate()` **plus** a
  re-derive of the spell-slice matrix against the GDD §9.2 access counts **plus** a scan
  for unresolved authoring placeholders (`"TO BE WRITTEN"`, etc.). Note: it is *not* an
  abbreviation/jargon scan — `AC`/`DC`/dice notation are intentionally allowed because
  the UI shows BG3-style mechanical tooltips (some stale "voice scan" naming remains).

Keep lint, MCP checks, and the content validator green.

## The registry — single source of truth (`game/data/`)

`game/data/__init__.py` assembles one `REGISTRY` dict from sub-modules (`classes/`,
`spells/`, `talents.py`, `equipment.py`, `enemies.py`, `conditions.py`, `economy.py`,
`locations.py`, `quests.py`, `shop.py`, `relics.py`, `expedition.py`, `core_rules.py`,
plus `display.py`/`class_ui.py` for player-voiced strings). **Every** feature, spell,
talent, item, condition, and content record exists exactly once, here, as data. Records
store only what the engine consumes — numbers, ids, tags, hook shapes, short
player-facing strings — and each carries a `§`-prefixed `src` citation. `validate()`
enforces that `src` convention and requires every class's `levelup` table to cover
exactly levels **1–12** (the global level cap).

- **Class record** (`data/classes/<class>.py:CLASS`): `id, name, primary, hit_die,
  saves, weapons, armor, skills, caster` and the central `levelup` manifest —
  `{level: {"features": [...], "choices": [...]}}`. Each class file also exports a
  sibling `FEATURES` dict keyed by the feature ids its `levelup` references.
- **Spell record** (`data/spells/tierN.py:SPELLS`): `id, name, tier, roles, classes,
  range, area, action, concentration, attack, save, damage/heal/summon, upcast, effect,
  src`. Spell→class access is **derived** from each spell's `classes` tag (the printed
  §9.2 matrix is derived, the tags are the source of truth).

## Rules-engine core (`game/core/`)

- **`registry.py`** — pure functions over the assembled registry; imports nothing.
  Holds the ID tuples (`ABILITY_IDS`, `CASTER_CLASS_IDS`, `SPELL_ROLES`), scaling
  resolvers (`by_level`, `levelup`), `derive_slice_matrix`, the structural `validate()`,
  and the fuller `content_problems()`. Because it never imports `game.data`, tests/
  fixtures can feed in a registry.
- **Derived stats are never stored.** AC, proficiency, save mods, skill mods, and
  initiative are recomputed from the registry on every read (`character.py`, `rules.py`).
  The **only** stored exception is `hp`/`hp_max` (via `recompute_hp_max`, re-run on any
  Con-affecting change), per the GDD §16.4 schema.
- **`character.py`** — the schema (`new_character`), all derived-stat getters, and the
  **choice engine**: `manifest_choices`/`level_up` return pending choice dicts; the `.rpy`
  caller collects picks and feeds each back through `apply_choice`, which validates and
  raises `ValueError` on illegal picks (and can return follow-up choices). Picks are
  final — no respec.
- **`dice.py`** — all randomness flows through one seedable module-level RNG
  (`dice.seed()`); the debug hub seeds it for reproducible fights. Advantage/disadvantage
  never stack and adv+dis cancels to net 0; callers pass the already-netted `+1/0/-1`.
- **`checks.py`** — the single composition point of `character.skill_mod` into
  `dice.d20_test`; read `result['success']`/`result['margin']`, never reinterpret a raw
  roll elsewhere.

## The combat event/hook pipeline — the heart of the engine

`game/core/hooks.py` (~89KB) + `game/core/combat.py` (~55KB). Hooks are the **only** way
features/items/reactions modify combat.

- **A feature *is* its hook record.** `_h()` builds records `{event, condition, effect,
  ability_id, ...}` (the `ability_id` — the registry source id — is load-bearing, read
  by the prompt/preferences system; `priority`, `cost`, `prompt`, `title`, `cost_text`
  are optional). Records live in `HOOK_LIBRARY` keyed by feature/trait id;
  `hooks_for()` resolves a combatant's owner ids from `char['features']` + `style_`/`inv_`/
  `talent_` prefixes (PCs) or `trait_` ids (enemies), and always appends the universal
  listeners `_universal_sap` / `_universal_turn_flags`.
- **`combat.fire(registry, combat, event, ctx)` is the single pipeline primitive.** It
  asserts `event in EVENTS` (a 30-entry tuple at `combat.py:20`, so typos fail loudly),
  then mutates a shared `ctx` dict through **three channels in order**: ongoing spell
  effects (`combat['effects']` via `effects_on_event`), then priority-sorted feature
  hooks, plus inline condition/flag reads. Hooks communicate *only* by mutating `ctx`
  (`ctx['bonus_damage']`, `to_hit_bonus`, `crit_range`, `adv`/`dis`, ...).
- **The combat loop never names a class.** It builds one initiative-sorted `combat['order']`
  over all combatants (both sides interleaved in one `combat['combatants']` dict keyed by
  `cid`; `combatants_on(side)` filters it — never two team arrays). Branching is on
  *features*, never class identity. Three combatant kinds share one shape: `pc`, `enemy`
  (statblock deep-copied from registry), and `summon`.
- **Reaction prompts route through an `ask_fn`** supplied by the UI, held in module state
  (`combat._ASK_FN`, not in the pickled combat dict) via `set_ask_fn`/`begin(ask_fn)`. The
  UI passes `breach_ask_reaction` (`combat_screen.rpy`); headless tests script it. A
  `cost=='reaction'` hook is gated on reaction availability + the prompt.
- **Player actions are split across both modules.** `combat.py` owns `player_attack`,
  `player_move`, `player_use_item`, `flee`, `enemy_take_turn`, turn advance/begin;
  `hooks.py` owns `use_ability` (over `ABILITY_IMPL`) and `cast_spell` (over
  `SPELL_RESOLVERS`/`SPELL_RIDERS`/`SPELL_GATES`). Action economy is never pre-committed:
  the use/slot/action is spent only *after* the impl returns ok, so a refused resolution
  costs nothing.

## Game state & saves (`game/core/state.py`)

`new_game_state(registry)` builds the save dict — 17 top-level keys: `save_version,
party` (≤4, `[0]` = MC), `follower_pool, inventory` (shared `{item_id: count}`), `gold,
supplies, day_phase, region, breach_region, location, quests, relationships, shops,
breathers, camp_upgrades, expedition_node, in_expedition, flags`. Ren'Py owns the single
instance as the store variable **`gs`** (`default gs = None` in `script.rpy`), so
saves/rollback see it; the pure-Python core takes `state` as a parameter and never holds
it. Static definitions live in the registry; runtime progress lives in `state` (e.g. a
quest's objectives are in `registry['quests']`, its progress in `state['quests'][id]`).

Migration: `SAVE_VERSION` + `migrate_state` (called from the `after_load` label) backfill
keys; in practice new keys are read with `state.get(key, default)` rather than a migration
layer, so `migrate_state` is mostly a version re-stamp.

## Rollback discipline (the anti-save-scum mechanism)

Combat runs with rollback **blocked imperatively** — `combat_encounter`
(`combat_screen.rpy`) calls `renpy.block_rollback()` at build and after every engine step
(each loop iter, each resolve, each dispatch, finish, loot). There is no
`config.rollback_enabled` switch. A mid-fight save is structurally impossible: the
transient `combat` dict is non-None only during the encounter, and the Save buttons are
gated `sensitive (combat is None)` (`screens.rpy`). The pure-Python state systems
(`quests.py`, `shop.py`, `rest.py`) **require the `.rpy` caller to call
`renpy.block_rollback()` after any committed mutation** (quest progress, buy/sell, rest)
— this is the only thing preventing players from rolling back to undo progress. When you
add a state-committing action, block rollback in the `.rpy` layer right after it.

## Ren'Py layer (`game/*.rpy`)

- **Boot (`script.rpy`):** `init 1 python` imports core modules under canonical aliases
  defined **once** here — `bch, binv, bstate, bui, bdice, bchecks, bquests, bshop, brest`
  — and sets `REG = data.REGISTRY`. Out-of-combat screen files reuse these aliases with
  zero `from core import` lines. (Exceptions: the rollback-blocked combat loop and the
  debug hub import their own engine handles on top — `bcombat`/`bhooks` in
  `combat_screen.rpy`.) `label start` → `p1_hub` is the prototype hub menu.
- **One screen file per surface:** `creation.rpy` + `choice_steps.rpy` (creation),
  `charsheet.rpy`, `inventory_screen.rpy`, `levelup.rpy`, `combat_screen.rpy` (the lane
  combat loop), `city.rpy`/`location_screen.rpy`/`shop_screen.rpy`,
  `camp.rpy`/`expedition.rpy`, `quest_tab.rpy`, `hud.rpy`, `dialogue.rpy`, `prologue.rpy`,
  `debug_hub.rpy`, `toast.rpy`. The combat screen returns an **intent tuple** (e.g.
  `('attack', cid, reckless)`, `('cast', spell, cid, lane)`); `breach_combat_dispatch`
  shape-guards it and calls the engine. UI targeting helpers only *mirror* engine
  predicates — they never resolve rules themselves.
- **The choice flow stepper (`core/stepper.py`):** one function, `run_choices`, drives
  *both* creation and level-up; the Ren'Py `present` callback shows the `choice_step`
  screen. It mutates the working char in place, supports Back, and prepends follow-up
  choices to the queue.
- **Player-voiced text:** the `.rpy` layer calls the `breach_player_text(registry,
  category, rec_id, fallback)` shim (`script.rpy`) → `core.ui_options.player_text`, always
  passing the record's raw `effect`/`desc` as fallback. Authored prose lives in
  `data/display.py` (`DISPLAY`) and `data/class_ui.py`; `ui_options` only routes/composes
  the BG3-style mechanical tooltips. `ui_options.options_for` is the single presenter that
  turns a level-up/creation choice record into selectable options.

## Visual & GUI discipline (`game/gui.rpy` + `game/style.rpy`)

All colors, sizes, spacing, geometry, fonts, and the shared gold nineslice frames are
constants in `gui.rpy`. Reusable component screens/styles live in `style.rpy`:
`breach_panel`, `breach_modal`, `section_header`, `breach_list_row`, `hp_bar`,
`breach_tag`, `breach_resource`, `attribute_allocator`, `tab_bar`, `breach_panel_button`.
**Never hardcode a hex/pixel value or duplicate a component** — compose these (same
severity as duplicating rules text). Three font tiers are kept independent (interface =
IBM Plex Sans Condensed, dialogue = Spectral, display = Cinzel); changing one token
re-skins exactly one tier. Any site rendering a data-driven registry name **must** pass
it through `breach_lit` (`style.rpy`) — Ren'Py runs `[]`/`{}` markup on shown text, so an
unescaped name will be eval'd and crash; the shared components already call `breach_lit`
internally, so pass them raw strings.

## Debug hub (`game/debug_hub.rpy`)

The testing console, reachable from `p1_hub`. Give XP/gold/items, jump to combat, set day
phase, seed the RNG, run the content validator, browse the registry, and fabricate test
followers (it drives the real creation + level-up choice machinery with a first-legal
auto-chooser). It uses plain default styling, deliberately exempt from the GUI discipline
above. Use and extend it for verification.
