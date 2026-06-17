# -*- coding: utf-8 -*-
"""Sorcerer class data: chassis, features, and L1-12 LEVELUP manifest (GDD section 7.12; shared progression rules section 6 / section 7 intro)."""

CLASS = {
    "id": "sorcerer",
    "name": "Sorcerer",
    "primary": ["cha"],
    "hit_die": 6,
    "saves": ["con", "cha"],
    "weapons": {"base": "simple"},
    "armor": [],
    "skills": {"choose": 2, "from": ["lore", "guile", "intuition", "presence"]},
    "caster": {"kind": "full", "ability": "cha", "prepared": True},
    "levelup": {
        1: {
            "features": ["sorcerer_innate_sorcery"],
            "choices": [
                {"type": "cantrips", "known_total": 4, "from": "sorcerer"},
            ],
        },
        2: {
            "features": ["sorcerer_font_of_magic", "sorcerer_metamagic"],
            "choices": [
                {"type": "metamagic", "known_total": 2},
            ],
        },
        3: {
            "features": ["sorcerer_draconic_resilience", "sorcerer_draconic_spells"],
            "choices": [],
        },
        4: {
            "features": [],
            "choices": [
                {"type": "asi_or_talent"},
                {"type": "cantrips", "known_total": 5, "from": "sorcerer"},
            ],
        },
        5: {
            "features": ["sorcerer_sorcerous_restoration"],
            "choices": [],
        },
        6: {
            "features": ["sorcerer_elemental_affinity"],
            "choices": [
                {"type": "feature_option", "feature": "sorcerer_elemental_affinity"},
            ],
        },
        7: {
            "features": ["sorcerer_sorcery_incarnate"],
            "choices": [],
        },
        8: {
            "features": [],
            "choices": [
                {"type": "asi_or_talent"},
            ],
        },
        9: {
            "features": [],
            "choices": [],
        },
        10: {
            "features": [],
            "choices": [
                {"type": "metamagic", "known_total": 4},
                {"type": "cantrips", "known_total": 6, "from": "sorcerer"},
            ],
        },
        11: {
            "features": [],
            "choices": [],
        },
        12: {
            "features": ["sorcerer_dragon_wings"],
            "choices": [
                {"type": "asi_or_talent"},
            ],
        },
    },
    "src": "§7.12 L858",
}

FEATURES = {
    "sorcerer_innate_sorcery": {
        "id": "sorcerer_innate_sorcery",
        "name": "Innate Sorcery",
        "class": "sorcerer",
        "action": "bonus",
        "uses": {"amount": 2, "per": "camp"},
        "effect": "Lasts the fight: +1 to your spell save DCs and advantage on your spell attack rolls.",
        "src": "§7.12 L863-864",
    },
    "sorcerer_font_of_magic": {
        "id": "sorcerer_font_of_magic",
        "name": "Font of Magic",
        "class": "sorcerer",
        "action": "bonus",
        "uses": {"amount": "level", "per": "camp"},
        "effect": "Sorcery Points equal to your level. Convert as a Bonus Action: points into slots (tier 1 costs 2, tier 2 costs 3, tier 3 costs 5, tier 4 costs 6, tier 5 costs 7) or a slot into points equal to its tier.",
        "conversion": {
            "points_to_slot": {1: 2, 2: 3, 3: 5, 4: 6, 5: 7},
            "slot_to_points": "tier",
        },
        "src": "§7.12 L865-868",
    },
    "sorcerer_metamagic": {
        "id": "sorcerer_metamagic",
        "name": "Metamagic",
        "class": "sorcerer",
        "action": "passive",
        "uses": None,
        # one option per cast is the base limit (Sorcery Incarnate is the
        # only exception), per owner adjudication, P0 round 2 (G-016)
        "max_per_cast": 1,
        "effect": "Spend Sorcery Points to modify a cast.",
        "options": [
            {
                "id": "distant",
                "name": "Distant",
                "cost": 1,
                "effect": "Touch becomes Distance.",
            },
            {
                "id": "empowered",
                "name": "Empowered",
                "cost": 1,
                "effect": "Reroll up to Charisma-modifier damage dice.",
            },
            {
                "id": "heightened",
                "name": "Heightened",
                "cost": 2,
                "effect": "One target has disadvantage on the save.",
            },
            {
                "id": "quickened",
                "name": "Quickened",
                "cost": 2,
                "effect": "An Action spell becomes a Bonus Action.",
            },
            {
                "id": "transmuted",
                "name": "Transmuted",
                "cost": 1,
                "effect": "Swap the damage type among acid, cold, fire, lightning, poison, thunder.",
            },
            {
                "id": "subtle",
                "name": "Subtle",
                "cost": 1,
                "effect": "The casting is undetectable. No combat use.",
            },
        ],
        "src": "§7.12 L869-877",
    },
    "sorcerer_draconic_resilience": {
        "id": "sorcerer_draconic_resilience",
        "name": "Draconic Resilience",
        "class": "sorcerer",
        "action": "passive",
        "uses": None,
        "effect": "Maximum HP +3, and +1 more per Sorcerer level gained afterward; while unarmored, base AC = 10 + Dexterity modifier + Charisma modifier.",
        "src": "§7.12 L878-880",
    },
    "sorcerer_draconic_spells": {
        "id": "sorcerer_draconic_spells",
        "name": "Draconic Spells",
        "class": "sorcerer",
        "action": "passive",
        "uses": None,
        "effect": "These spells are always prepared.",
        "grants_spells": [
            {"spell": "searing_burst", "at_level": 3},
            {"spell": "dread_apparition", "at_level": 5},
            {"spell": "bestial_curse", "at_level": 7},
            {"spell": "conjure_elemental", "at_level": 9},
        ],
        "src": "§7.12 L881-882",
    },
    "sorcerer_sorcerous_restoration": {
        "id": "sorcerer_sorcerous_restoration",
        "name": "Sorcerous Restoration",
        "class": "sorcerer",
        "action": "passive",
        "uses": {"amount": 1, "per": "camp"},
        "effect": "When you finish a Breather, regain expended Sorcery Points up to half your Sorcerer level (rounded down).",
        "src": "§7.12 L884-886",
    },
    "sorcerer_elemental_affinity": {
        "id": "sorcerer_elemental_affinity",
        "name": "Elemental Affinity",
        "class": "sorcerer",
        "action": "passive",
        "uses": None,
        "effect": "Choose acid, cold, fire, lightning, or poison: you have resistance to it, and add your Charisma modifier to one damage roll of your spells of that type.",
        "options": [
            {
                "id": "acid",
                "name": "Acid",
                "effect": "Resistance to acid; add your Charisma modifier to one damage roll of your acid spells.",
            },
            {
                "id": "cold",
                "name": "Cold",
                "effect": "Resistance to cold; add your Charisma modifier to one damage roll of your cold spells.",
            },
            {
                "id": "fire",
                "name": "Fire",
                "effect": "Resistance to fire; add your Charisma modifier to one damage roll of your fire spells.",
            },
            {
                "id": "lightning",
                "name": "Lightning",
                "effect": "Resistance to lightning; add your Charisma modifier to one damage roll of your lightning spells.",
            },
            {
                "id": "poison",
                "name": "Poison",
                "effect": "Resistance to poison; add your Charisma modifier to one damage roll of your poison spells.",
            },
        ],
        "src": "§7.12 L887-889",
    },
    "sorcerer_sorcery_incarnate": {
        "id": "sorcerer_sorcery_incarnate",
        "name": "Sorcery Incarnate",
        "class": "sorcerer",
        "action": "passive",
        "uses": None,
        "effect": "While Innate Sorcery is active you may use two Metamagic options on one spell; you may restore an Innate Sorcery use for 2 Sorcery Points.",
        "src": "§7.12 L890-892",
    },
    "sorcerer_dragon_wings": {
        "id": "sorcerer_dragon_wings",
        "name": "Dragon Wings",
        "class": "sorcerer",
        "action": "bonus",
        "uses": {"amount": 1, "per": "camp"},
        "effect": "Wings unfurl for the rest of the fight: free lane changes without provoking, and ranged attacks against you have disadvantage. Restore the use for 3 Sorcery Points.",
        "src": "§7.12 L894-897",
    },
}
