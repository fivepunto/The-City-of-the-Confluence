# -*- coding: utf-8 -*-
"""Ranger class data: chassis, class features, and the L1-12 LEVELUP manifest.

Transcribed from GDD section 7.6 (with shared context from sections 6 and 7).
"""

CLASS = {
    "id": "ranger",
    "name": "Ranger",
    "primary": ["dex", "wis"],
    "hit_die": 10,
    "saves": ["str", "dex"],
    "weapons": {"base": "all"},
    "armor": ["light", "medium", "shields"],
    "skills": {
        "choose": 3,
        "from": ["athletics", "intuition", "deduction", "lore", "awareness", "trickery"],
    },
    "caster": {"kind": "half", "ability": "wis", "prepared": True},
    "levelup": {
        1: {
            "features": ["ranger_favored_enemy", "weapon_mastery"],
            "choices": [
                {"type": "weapon_mastery", "known_total": 3},
            ],
        },
        2: {
            "features": ["ranger_deft_explorer"],
            "choices": [
                {"type": "expertise", "choose": 1},
                {"type": "fighting_style", "or_feature": "ranger_druidic_warrior"},
            ],
        },
        3: {
            "features": ["ranger_hunters_lore", "ranger_hunters_prey"],
            "choices": [
                {"type": "feature_option", "feature": "ranger_hunters_prey"},
            ],
        },
        4: {
            "features": [],
            "choices": [
                {"type": "asi_or_talent"},
            ],
        },
        5: {
            "features": ["extra_attack"],
            "choices": [],
        },
        6: {
            "features": ["ranger_roving"],
            "choices": [],
        },
        7: {
            "features": ["ranger_defensive_tactics"],
            "choices": [
                {"type": "feature_option", "feature": "ranger_defensive_tactics"},
            ],
        },
        8: {
            "features": [],
            "choices": [
                {"type": "asi_or_talent"},
            ],
        },
        9: {
            "features": ["expertise"],
            "choices": [
                {"type": "expertise", "choose": 2},
            ],
        },
        10: {
            "features": ["ranger_tireless"],
            "choices": [],
        },
        11: {
            "features": ["ranger_superior_hunters_prey"],
            "choices": [],
        },
        12: {
            "features": ["ranger_relentless_hunter"],
            "choices": [
                {"type": "asi_or_talent"},
            ],
        },
    },
    "src": "§7.6 L593",
}

FEATURES = {
    "ranger_favored_enemy": {
        "id": "ranger_favored_enemy",
        "name": "Favored Enemy",
        "class": "ranger",
        "action": "passive",
        "uses": {"amount": {"by_level": {1: 2, 5: 3, 9: 4}}, "per": "camp"},
        "effect": "Quarry's Mark is always prepared, and you may cast it without a slot 2 times per Camp (3 at level 5, 4 at level 9).",
        "grants_spells": [{"spell": "quarrys_mark", "at_level": 1}],
        "src": "§7.6 L599-600",
    },
    "ranger_deft_explorer": {
        "id": "ranger_deft_explorer",
        "name": "Deft Explorer",
        "class": "ranger",
        "action": "passive",
        "uses": None,
        "effect": "Expertise in one skill, and advantage on Camp hunting checks.",
        "src": "§7.6 L602-603",
    },
    "ranger_druidic_warrior": {
        "id": "ranger_druidic_warrior",
        "name": "Druidic Warrior",
        "class": "ranger",
        "action": "passive",
        "uses": None,
        "effect": "Learn 2 cantrips from the Druid's set.",
        "src": "§7.6 L604-605",
    },
    "ranger_hunters_lore": {
        "id": "ranger_hunters_lore",
        "name": "Hunter's Lore",
        "class": "ranger",
        "action": "passive",
        "uses": None,
        "effect": "While a creature bears your Quarry's Mark, its resistances, immunities, and vulnerabilities are revealed in its tooltip.",
        "src": "§7.6 L606-607",
    },
    "ranger_hunters_prey": {
        "id": "ranger_hunters_prey",
        "name": "Hunter's Prey",
        "class": "ranger",
        "action": "passive",
        "uses": None,
        "effect": "Choose one (swappable at each rest).",
        "options": [
            {
                "id": "colossus_slayer",
                "name": "Colossus Slayer",
                "effect": "Once per turn, +1d8 damage against a target that is missing HP.",
            },
            {
                "id": "horde_breaker",
                "name": "Horde Breaker",
                "effect": "Once per turn, an extra attack against a different enemy in your target's lane.",
            },
        ],
        "swappable": "rest",
        "src": "§7.6 L608-611",
    },
    "ranger_roving": {
        "id": "ranger_roving",
        "name": "Roving",
        "class": "ranger",
        "action": "passive",
        "uses": None,
        "effect": "Your retreats (Frontline → Backline) never provoke opportunity attacks.",
        "src": "§7.6 L614-615",
    },
    "ranger_defensive_tactics": {
        "id": "ranger_defensive_tactics",
        "name": "Defensive Tactics",
        "class": "ranger",
        "action": "passive",
        "uses": None,
        "effect": "Choose one (swappable at each rest).",
        "options": [
            {
                "id": "escape_the_horde",
                "name": "Escape the Horde",
                "effect": "Opportunity attacks against you have disadvantage.",
            },
            {
                "id": "multiattack_defense",
                "name": "Multiattack Defense",
                "effect": "After a creature hits you, its further attacks against you this turn have disadvantage.",
            },
        ],
        "swappable": "rest",
        "src": "§7.6 L616-619",
    },
    "ranger_tireless": {
        "id": "ranger_tireless",
        "name": "Tireless",
        "class": "ranger",
        "action": "action",
        "uses": {"amount": "wis_mod", "per": "camp"},
        "effect": "As an Action, gain 1d8 + Wisdom modifier temporary HP.",
        "src": "§7.6 L621-622",
    },
    "ranger_superior_hunters_prey": {
        "id": "ranger_superior_hunters_prey",
        "name": "Superior Hunter's Prey",
        "class": "ranger",
        "action": "passive",
        "uses": {"amount": 1, "per": "turn"},
        "effect": "Once per turn, when you damage your marked quarry, the Mark's bonus damage also strikes a second creature in the quarry's lane.",
        "src": "§7.6 L623-625",
    },
    "ranger_relentless_hunter": {
        "id": "ranger_relentless_hunter",
        "name": "Relentless Hunter",
        "class": "ranger",
        "action": "passive",
        "uses": None,
        "effect": "Taking damage cannot break your concentration on Quarry's Mark.",
        "src": "§7.6 L626-627",
    },
}
