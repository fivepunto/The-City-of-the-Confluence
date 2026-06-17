"""game.data -- THE registry (CLAUDE.md: "One registry").

Every feature, spell, talent, item, and condition exists once, as data, in
this package. All UI text, tooltips, level-up cards, and combat behavior
read from it. Records store ONLY what the engine consumes -- numbers, ids,
tags, hook shapes, and short player-facing strings (GDD #16.5, L1654-1659).
Every record cites its doc line via "src": "§<section> L<line>" pointing at
docs/gdd.md.

No renpy imports anywhere in this package.
"""

from data import core_rules
from data import conditions as _conditions
from data import talents as _talents
from data import equipment as _equipment
from data import enemies as _enemies
from data import economy as _economy
from data import class_ui as _class_ui
from data import display as _display
from data import locations as _locations
from data import quests as _quests
from data import shop as _shop
from data import relics as _relics
from data import expedition as _expedition
from data.classes import CLASSES, FEATURES
from data.spells import SPELLS, UPCAST_RULES

REGISTRY = {
    # section 2 / 3 / 4.1 / 6 / 12.1 core tables
    "core": {
        "point_buy": core_rules.POINT_BUY,
        "xp_thresholds": core_rules.XP_THRESHOLDS,
        "damage_types": core_rules.DAMAGE_TYPES,
        "human": core_rules.HUMAN,
        "slot_table_full": core_rules.SLOT_TABLE_FULL,
        "slot_table_half": core_rules.SLOT_TABLE_HALF,
        "pact_slots": core_rules.PACT_SLOTS,
        "prepared_spells": core_rules.PREPARED_SPELLS,
        "rest_rules": core_rules.REST_RULES,
    },
    "skills": core_rules.SKILLS,
    "conditions": _conditions.CONDITIONS,
    "talents": _talents.TALENTS,
    "fighting_styles": _talents.FIGHTING_STYLES,
    "weapons": _equipment.WEAPONS,
    "weapon_properties": _equipment.WEAPON_PROPERTIES,
    "weapon_classes": _equipment.WEAPON_CLASSES,
    "armor": _equipment.ARMOR,
    "armor_categories": _equipment.ARMOR_CATEGORIES,
    "masteries": _equipment.MASTERIES,
    "equipment_slots": _equipment.EQUIPMENT_SLOTS,
    "rarities": _equipment.RARITIES,
    "starting_equipment": _equipment.STARTING_EQUIPMENT,
    "starting_common": _equipment.STARTING_COMMON,
    "consumables": _equipment.CONSUMABLES,
    "camp_upgrades": _equipment.CAMP_UPGRADES,
    "enemies": _enemies.ENEMIES,
    "intent_vocab": _enemies.INTENT_VOCAB,
    "summons": _enemies.SUMMON_STATBLOCKS,
    "summon_rules": _enemies.SUMMON_RULES,
    "economy": _economy.ECONOMY,
    "classes": CLASSES,
    "class_ui": _class_ui.CLASS_UI,
    "display": _display.DISPLAY,
    "features": FEATURES,
    "spells": SPELLS,
    "upcast_rules": UPCAST_RULES,
    # section 13 / 14 / 15.5 / 15.8 city & free-mode tables (P3). Content is
    # owner-authored (GAPS G-038..G-040); the records ship as placeholders.
    "districts": _locations.DISTRICTS,
    "locations": _locations.LOCATIONS,
    "hotspots": _locations.HOTSPOTS,
    "quests": _quests.QUESTS,
    "shops": _shop.SHOPS,
    "relics": _relics.RELICS,
    "magic_items": _relics.MAGIC_ITEMS,
    "key_items": _relics.KEY_ITEMS,
    # section 12 / 13 camp & expedition tables (P4). Content owner-authored
    # (GAPS G-043/G-044); records ship as placeholders.
    "regions": _expedition.REGIONS,
    "expedition_map": _expedition.EXPEDITION_NODES,
}
