# -*- coding: utf-8 -*-
"""Item categories the city/economy layer adds on top of weapons, armor, and
consumables: RELICS (GDD #14.2 L1414-1418), KEY_ITEMS (#15.4 L1553), and a
small placeholder MAGIC_ITEMS table (#10.7 L1262-1264, #14.3 L1426). DATA only.

OWNER CONTENT (GAPS G-040): the concrete relics and magic items -- names,
flavour, named alt-uses, the exact stock, and prices within the #14.5 bands --
are owner-authored. Per DATA-vs-GUIDANCE (#16.5, CLAUDE.md), prices/values are
stored as LITERAL numbers on each record; the #14.5 rarity price BANDS and the
income curve are tuning guidance and must NEVER be encoded as a data block.
The SYSTEM ships against bracketed-placeholder records so the shop's
sell/buy/confirm/reject rules are exercisable; placeholder names are NOT added
to the doc-integrity name check.

RELICS (income, sell-only at the vendor -- #14.2 frames them as the loop's
point; G-040): {id, name, rarity, sell_value(literal), alt_use(hook id|None),
src}. Sold at full listed value (economy.relic_sell_ratio = 1.0).

MAGIC_ITEMS (vendor stock + loot -- equippable gear): {id, name, rarity, slot,
price(literal), plus_bonus(int), effect(player string), src}. Sold back at
50% (economy.gear_sell_ratio); Very Rare and +3 are never vendor-sold
(economy.very_rare_sold_by_vendors / plus_three_items_sold = False).

KEY_ITEMS (#15.4 L1553 "quest items refuse" to be discarded/sold): {id, name,
src, sellable: False}. Includes 'spellbook' so inventory.item_kind stops
special-casing the literal id (G-037).
"""

RELICS = {
    "relic_a": {
        "id": "relic_a",
        "name": "[Relic A]",              # owner-authored (G-040)
        "rarity": "common",
        "sell_value": 75,                 # literal, within Common 50-100 (guidance)
        "alt_use": None,
        "src": "§14.2 L1414-1418",
    },
    "relic_b": {
        "id": "relic_b",
        "name": "[Relic B]",
        "rarity": "uncommon",
        "sell_value": 300,                # within Uncommon 200-500 (guidance)
        "alt_use": None,
        "src": "§14.2 L1414-1418",
    },
    "relic_c": {
        "id": "relic_c",
        "name": "[Relic C]",
        "rarity": "rare",
        "sell_value": 2000,               # within Rare 1500-4000 (guidance)
        "alt_use": None,                  # a named alt-use is owner content
        "src": "§14.2 L1414-1418",
    },
}

MAGIC_ITEMS = {
    "magic_item_a": {
        "id": "magic_item_a",
        "name": "[Magic Item A]",         # owner-authored (G-040)
        "rarity": "uncommon",
        "slot": "ring",
        "price": 350,
        "plus_bonus": 1,
        "effect": "[TO BE WRITTEN BY THE PROJECT OWNER]",
        "src": "§10.7 L1262-1264",
    },
    "magic_item_b": {
        "id": "magic_item_b",
        "name": "[Magic Item B]",
        "rarity": "rare",
        "slot": "cloak",
        "price": 1800,
        "plus_bonus": 2,
        "effect": "[TO BE WRITTEN BY THE PROJECT OWNER]",
        "src": "§10.7 L1262-1264",
    },
    "magic_item_c": {
        "id": "magic_item_c",
        "name": "[Magic Item C]",
        "rarity": "very_rare",            # vendors never sell these (#14.3 L1426)
        "slot": "head",
        "price": 6000,
        "plus_bonus": 0,
        "effect": "[TO BE WRITTEN BY THE PROJECT OWNER]",
        "src": "§10.7 L1262-1264",
    },
}

KEY_ITEMS = {
    "spellbook": {
        "id": "spellbook",
        "name": "Spellbook",
        "sellable": False,
        "src": "§10.6 L1259",
    },
    "key_item_a": {
        "id": "key_item_a",
        "name": "[Key Item A]",           # owner-authored
        "sellable": False,
        "src": "§15.4 L1553",
    },
}
