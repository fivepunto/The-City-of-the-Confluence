# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

> **Read the rules doc first.** 
> the iron rules (never invent rules/story; DATA vs GUIDANCE; one registry;
> rollback discipline), the visual identity, and the palette. This file is the
> *engineering* companion: how the code is laid out, how it boots, and how to
> run checks. When the two overlap, the Desktop doc wins.
>
> 

## What this is

A visual-novel / RPG hybrid in **Ren'Py 8.5.3**, adapted from the D&D 5.2 SRD.
The engine is built; remaining work is content authoring, the post-roll
interrupt pass, and refinement/polish.

## Commands

- **Lint:** from the SDK dir, `sh renpy.sh "<project>" lint` (SDK is
  `C:\Users\suhel\Documents\renpy-8.5.3-sdk`; in WSL run `renpy.sh`, not the
  `.exe`). Dummy-driver GL errors under WSL are environmental, not failures.
- **Content validation:** there is **no `tests/` suite**. Validation is
  in-engine — the debug hub's **"Validate content"** button runs
  `registry.validate(REG)`, re-derives the spell-slice matrix against GDD 9.2,
  and scans player-facing DISPLAY strings for abbreviations. A dev-mode `init`
  assert (`game/script.rpy`) runs the structural `registry.validate(REG)` on
  every boot (`config.developer` is auto-True in an unpacked project).
- **Prefer `renpy-mcp`** for lint/compile, screen inspection, story-flow,
  asset/translation checks, and live screenshots over guessing from filenames.
  Keep lint, MCP checks, and the content validator green.

## Architecture

The hard boundary: **`game/data/` + `game/core/` are pure Python with no
`renpy` imports**; the `.rpy` files are the Ren'Py layer (screens + boot glue).
This is what lets the engine be validated headlessly and keeps rules out of
screens.

### The registry (`game/data/`)
`game/data/__init__.py` assembles the single `REGISTRY` dict from sub-modules
(`classes/`, `spells/`, `talents.py`, `equipment.py`, `enemies.py`,
`conditions.py`, `economy.py`, `locations.py`, `quests.py`, `shop.py`,
`relics.py`, `expedition.py`, `core_rules.py`, plus `display.py`/`class_ui.py`
for player-voiced strings). **Every** feature, spell, talent, item, condition,
and content record exists exactly once here, as data. All UI text and combat
behavior read from it.

### Registry access (`game/core/registry.py`)
Pure functions over the assembled registry — **it never imports `game.data`**,
so there's no import cycle and fixtures can be fed in. Holds the ID tuples
(`ABILITY_IDS`, `CASTER_CLASS_IDS`, …), scaling resolvers (`by_level`,
`levelup`), the derived spell-slice matrix (`derive_slice_matrix`), and
`validate(registry)`.

### The event pipeline (`game/core/hooks.py` + `combat.py`)
The **only** way features/items/reactions affect combat. A feature *is* its
hook record (`{event, priority, condition, effect, prompt, cost}`) in
`HOOK_LIBRARY`, keyed by registry feature/trait id. The combat loop
(`combat.py`) **never names a class** — it builds one initiative-sorted list of
all combatants (both sides interleaved, never two team arrays) and fires events
from the `EVENTS` vocabulary; hooks react. Reaction prompts route through an
`ask_fn` callable supplied by the UI (headless tests script it). All randomness
goes through seedable `core/dice.py`.

### Derived stats are never stored
AC, proficiency, save mods, initiative — recompute from the registry on read
(`core/character.py`, `core/rules.py`).

### Game state (`game/core/state.py`)
`new_game_state(REG)` builds the save dict (party of ≤4 with `[0]` = MC,
follower pool, shared inventory, gold, supplies, day phase, region, quests,
relationships). Ren'Py owns the single instance in its store so saves/rollback
see it. `SAVE_VERSION` + `migrate_state` backfill keys for old saves; new keys
are read with `.get(key, default)` instead of a migration layer. The
`after_load` label calls `migrate_state`.

Other core modules: `inventory.py`, `combat.py`, `quests.py`, `shop.py`,
`rest.py`, `stepper.py` (creation/level-up choice flow), `checks.py`, `dice.py`,
`ui_options.py` (`player_text` → the player-voiced display layer).

### Boot (`game/script.rpy`)
`init 1 python` imports the core modules under canonical aliases (`bch`,
`binv`, `bstate`, `bui`, `bdice`, `bchecks`, `bquests`, `bshop`, `brest`) and
sets `REG = data.REGISTRY`. These aliases are defined **once** here and reused
by every screen file. `label start` → `p1_hub` is the prototype's hub menu
(create character, city, expedition, test combat, sheet, level-up, debug hub).

### Ren'Py screen layer (`game/*.rpy`)
One screen file per surface: `creation.rpy` + `choice_steps.rpy` (character
creation), `charsheet.rpy`, `inventory_screen.rpy`, `levelup.rpy`,
`combat_screen.rpy` (the lane combat loop, runs with rollback blocked),
`city.rpy`/`location_screen.rpy`/`shop_screen.rpy` (city & free mode),
`camp.rpy`/`expedition.rpy` (camp & expedition), `quest_tab.rpy`, `hud.rpy`,
`dialogue.rpy`, `prologue.rpy`, `debug_hub.rpy`, `toast.rpy`.

### Shared UI components (`game/style.rpy` + `game/gui.rpy`)
All colors/sizes/spacing are constants in `gui.rpy`; shared component
screens/styles live in `style.rpy` — `breach_panel`, `breach_modal`,
`section_header`, `breach_list_row`, `hp_bar`, `breach_tag`, `breach_resource`,
`attribute_allocator`, `tab_bar`, etc. Every screen composes these; **never
hardcode a hex/pixel value or duplicate a component** (same severity as
duplicating rules text — see `../../CLAUDE.md` → "Visual & GUI discipline").

## Debug hub
`game/debug_hub.rpy` is the testing console (reachable from `p1_hub`): give
XP/gold/items, jump to combat, set day phase, seed the RNG, run the content
validator, reproduce UI/combat states. Use and extend it for verification.
