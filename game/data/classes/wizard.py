# -*- coding: utf-8 -*-
"""Wizard class data: chassis, class features, and L1-12 LEVELUP manifest.

Transcribed from GDD section 7.4 (with shared vocabulary from sections 6
and 7 intro).
"""

CLASS = {
    "id": "wizard",
    "name": "Wizard",
    "primary": ["int"],
    "hit_die": 6,
    "saves": ["int", "wis"],
    "weapons": {"base": "simple"},
    "armor": [],
    "skills": {"choose": 2, "from": ["lore", "deduction", "intuition", "awareness"]},
    "caster": {"kind": "full", "ability": "int", "prepared": True},
    "levelup": {
        1: {
            "features": [
                "wizard_spellbook",
                "wizard_arcanists_eye",
                "wizard_arcane_recovery",
            ],
            "choices": [
                {"type": "cantrips", "known_total": 3, "from": "wizard"},
                {"type": "spellbook_init", "choose": 6, "tier": 1},
            ],
        },
        2: {
            "features": ["wizard_scholar"],
            "choices": [
                {"type": "expertise", "choose": 1, "from": ["lore", "deduction"]},
                {"type": "spellbook_add", "count": 2},
            ],
        },
        3: {
            "features": ["wizard_savant_of_ruin", "wizard_potent_cantrip"],
            "choices": [
                {"type": "spellbook_add", "count": 2},
            ],
        },
        4: {
            "features": [],
            "choices": [
                {"type": "asi_or_talent"},
                {"type": "cantrips", "known_total": 4, "from": "wizard"},
                {"type": "spellbook_add", "count": 2},
            ],
        },
        5: {
            "features": ["wizard_memorize_spell"],
            "choices": [
                {"type": "spellbook_add", "count": 2},
            ],
        },
        6: {
            "features": ["wizard_empowered_ruin"],
            "choices": [
                {"type": "spellbook_add", "count": 2},
            ],
        },
        7: {
            "features": [],
            "choices": [
                {"type": "spellbook_add", "count": 2},
            ],
        },
        8: {
            "features": [],
            "choices": [
                {"type": "asi_or_talent"},
                {"type": "spellbook_add", "count": 2},
            ],
        },
        9: {
            "features": [],
            "choices": [
                {"type": "spellbook_add", "count": 2},
            ],
        },
        10: {
            "features": ["wizard_greater_recovery"],
            "choices": [
                {"type": "cantrips", "known_total": 5, "from": "wizard"},
                {"type": "spellbook_add", "count": 2},
            ],
        },
        11: {
            "features": [],
            "choices": [
                {"type": "spellbook_add", "count": 2},
            ],
        },
        12: {
            "features": ["wizard_overchannel"],
            "choices": [
                {"type": "asi_or_talent"},
                {"type": "spellbook_add", "count": 2},
            ],
        },
    },
    "src": "§7.4 L521",
}

FEATURES = {
    "wizard_spellbook": {
        "id": "wizard_spellbook",
        "name": "The spellbook",
        "class": "wizard",
        "action": "passive",
        "uses": None,
        "copy_cost_per_tier": 50,
        "effect": "Starts with 6 tier-1 spells from the Wizard slice (pick 6 of the 7 available); gains 2 free spells per level (of castable tiers). Spells found on scrolls or in enemy spellbooks can be copied in at Camp for 50 gold × the spell's tier.",
        "src": "§7.4 L526-530",
    },
    "wizard_arcanists_eye": {
        "id": "wizard_arcanists_eye",
        "name": "Arcanist's Eye",
        "class": "wizard",
        "action": "passive",
        "uses": None,
        "effect": "Advantage on Lore checks concerning magic, arcana, and relics.",
        "src": "§7.4 L531-532",
    },
    "wizard_arcane_recovery": {
        "id": "wizard_arcane_recovery",
        "name": "Arcane Recovery",
        "class": "wizard",
        "action": "free",
        "uses": {"amount": 1, "per": "camp"},
        "effect": "Once per Camp, on a Breather, recover expended spell slots whose tiers total half your Wizard level (rounded up).",
        "src": "§7.4 L533-534",
    },
    "wizard_scholar": {
        "id": "wizard_scholar",
        "name": "Scholar",
        "class": "wizard",
        "action": "passive",
        "uses": None,
        "effect": "Expertise in Lore or Deduction.",
        "src": "§7.4 L535",
    },
    "wizard_savant_of_ruin": {
        "id": "wizard_savant_of_ruin",
        "name": "Savant of Ruin",
        "class": "wizard",
        "action": "passive",
        "uses": None,
        "effect": "Copying Damage-role spells into your book costs half; whenever you unlock a new spell tier, add one Damage-role spell of that tier to the book for free.",
        "src": "§7.4 L536-538",
    },
    "wizard_potent_cantrip": {
        "id": "wizard_potent_cantrip",
        "name": "Potent Cantrip",
        "class": "wizard",
        "action": "passive",
        "uses": None,
        "effect": "Your damage cantrips deal half damage on a miss or a successful save (riders don't apply).",
        "src": "§7.4 L539-540",
    },
    "wizard_memorize_spell": {
        "id": "wizard_memorize_spell",
        "name": "Memorize Spell",
        "class": "wizard",
        "action": "free",
        "uses": {"amount": 1, "per": "breather"},
        "effect": "On a Breather, swap one prepared spell for another from your book.",
        "src": "§7.4 L542-543",
    },
    "wizard_empowered_ruin": {
        "id": "wizard_empowered_ruin",
        "name": "Empowered Ruin",
        "class": "wizard",
        "action": "passive",
        "uses": None,
        "effect": "Add your Intelligence modifier to one damage roll of each Damage-role spell you cast.",
        "src": "§7.4 L544-545",
    },
    "wizard_greater_recovery": {
        "id": "wizard_greater_recovery",
        "name": "Greater Recovery",
        "class": "wizard",
        "action": "passive",
        "uses": None,
        "effect": "Arcane Recovery now restores slot tiers totaling your full Wizard level (still once per Camp; nothing above tier 5).",
        "src": "§7.4 L546-547",
    },
    "wizard_overchannel": {
        "id": "wizard_overchannel",
        "name": "Overchannel",
        "class": "wizard",
        "action": "free",
        "uses": None,
        "effect": "When you cast a Damage spell of tiers 1–5, you may choose to deal maximum damage. The first use per Camp is free; each repeat before the next Camp deals 2d12 necrotic damage to you per tier of the spell, ignoring resistance, and the self-damage grows by 1d12 per repeat.",
        "src": "§7.4 L549-553",
    },
}
