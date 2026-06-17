# -*- coding: utf-8 -*-
"""Paladin class data: chassis, features, and L1-12 LEVELUP manifest (GDD section 7.9; ASI levels per section 6)."""

CLASS = {
    "id": "paladin",
    "name": "Paladin",
    "primary": ["str", "cha"],
    "hit_die": 10,
    "saves": ["wis", "cha"],
    "weapons": {"base": "all"},
    "armor": ["light", "medium", "heavy", "shields"],
    "skills": {"choose": 2, "from": ["athletics", "intuition", "presence", "lore"]},
    "caster": {"kind": "half", "ability": "cha", "prepared": True},
    "levelup": {
        1: {
            "features": ["weapon_mastery", "paladin_lay_on_hands"],
            "choices": [
                {"type": "weapon_mastery", "known_total": 3},
            ],
        },
        2: {
            "features": ["paladin_paladins_smite"],
            "choices": [
                {"type": "fighting_style", "or_feature": "paladin_blessed_warrior"},
            ],
        },
        3: {
            "features": ["paladin_channel_divinity", "paladin_devotion_spells"],
            "choices": [],
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
            "features": ["paladin_aura_of_protection"],
            "choices": [],
        },
        7: {
            "features": ["paladin_aura_of_devotion"],
            "choices": [],
        },
        8: {
            "features": [],
            "choices": [
                {"type": "asi_or_talent"},
            ],
        },
        9: {
            "features": ["paladin_abjure_foes"],
            "choices": [],
        },
        10: {
            "features": ["paladin_aura_of_courage"],
            "choices": [],
        },
        11: {
            "features": ["paladin_radiant_strikes"],
            "choices": [],
        },
        12: {
            "features": ["paladin_smite_of_protection"],
            "choices": [
                {"type": "asi_or_talent"},
            ],
        },
    },
    "src": "§7.9 L725",
}

FEATURES = {
    "paladin_lay_on_hands": {
        "id": "paladin_lay_on_hands",
        "name": "Lay on Hands",
        "class": "paladin",
        "action": "bonus",
        "uses": {
            "amount": {"by_level": {
                1: 5, 2: 10, 3: 15, 4: 20, 5: 25, 6: 30,
                7: 35, 8: 40, 9: 45, 10: 50, 11: 55, 12: 60,
            }},
            "per": "camp",
        },
        "effect": "Bonus Action: spend any amount from a healing pool of 5 × Paladin level (refilled at Camp) to heal that much, or spend 5 to cure Poisoned. This is ordinary Healing — it cannot revive a Downed ally.",
        "src": "§7.9 L730-734",
    },
    "paladin_blessed_warrior": {
        "id": "paladin_blessed_warrior",
        "name": "Blessed Warrior",
        "class": "paladin",
        "action": "passive",
        "uses": None,
        "effect": "Learn 2 cantrips from the Cleric's set.",
        "src": "§7.9 L735-736",
    },
    "paladin_paladins_smite": {
        "id": "paladin_paladins_smite",
        "name": "Paladin's Smite",
        "class": "paladin",
        "action": "passive",
        "uses": {"amount": 1, "per": "camp"},
        "effect": "The spell Radiant Smite is always prepared, plus one free cast per Camp.",
        "grants_spells": [
            {"spell": "radiant_smite", "tier": 1},
        ],
        "src": "§7.9 L737-738",
    },
    "paladin_channel_divinity": {
        "id": "paladin_channel_divinity",
        "name": "Channel Divinity",
        "class": "paladin",
        "action": "action",
        "uses": {"amount": 2, "per": "camp", "regain_one_per_breather": True},
        "effect": "2 uses; regain 1 per Breather. Spend a use on one option.",
        "options": [
            {
                "id": "sacred_weapon",
                "name": "Sacred Weapon",
                # part of taking the Attack action, no separate cost, per
                # owner adjudication, P0 round 2 (G-014)
                "action": "attack_action_rider",
                "effect": "Your weapon gains your Charisma modifier to attack rolls for the rest of the fight.",
            },
            {
                "id": "divine_sense",
                "name": "Divine Sense",
                "effect": "Reveals disguised or hidden Fiends and Undead.",
            },
        ],
        "src": "§7.9 L739-742",
    },
    "paladin_devotion_spells": {
        "id": "paladin_devotion_spells",
        "name": "Devotion Spells",
        "class": "paladin",
        "action": "passive",
        "uses": None,
        "effect": "Always prepared, not counted against prepared spells: Benediction, Warding Aegis, Vital Surge, Ironhide, Spirit Ring, Rekindle.",
        "grants_spells": [
            {"spell": "benediction", "tier": 1},
            {"spell": "warding_aegis", "tier": 1},
            {"spell": "vital_surge", "tier": 2},
            {"spell": "ironhide", "tier": 2},
            {"spell": "spirit_ring", "tier": 3},
            {"spell": "rekindle", "tier": 3},
        ],
        "src": "§7.9 L743-745",
    },
    "paladin_aura_of_protection": {
        "id": "paladin_aura_of_protection",
        "name": "Aura of Protection",
        "class": "paladin",
        "action": "passive",
        "uses": None,
        "effect": "You and allies in your lane add your Charisma modifier to all saving throws.",
        "src": "§7.9 L748-749",
    },
    "paladin_aura_of_devotion": {
        "id": "paladin_aura_of_devotion",
        "name": "Aura of Devotion",
        "class": "paladin",
        "action": "passive",
        "uses": None,
        "effect": "Allies in your lane are immune to Charmed.",
        "src": "§7.9 L751",
    },
    "paladin_abjure_foes": {
        "id": "paladin_abjure_foes",
        "name": "Abjure Foes",
        "class": "paladin",
        "action": "action",
        "uses": None,
        "effect": "Action plus one Channel Divinity use: one enemy lane makes a Wisdom save or is Frightened and Pinned.",
        "src": "§7.9 L752-753",
    },
    "paladin_aura_of_courage": {
        "id": "paladin_aura_of_courage",
        "name": "Aura of Courage",
        "class": "paladin",
        "action": "passive",
        "uses": None,
        "effect": "Allies in your lane are immune to Frightened.",
        "src": "§7.9 L754",
    },
    "paladin_radiant_strikes": {
        "id": "paladin_radiant_strikes",
        "name": "Radiant Strikes",
        "class": "paladin",
        "action": "passive",
        "uses": None,
        "effect": "Your melee hits deal +1d8 radiant.",
        "src": "§7.9 L755",
    },
    "paladin_smite_of_protection": {
        "id": "paladin_smite_of_protection",
        "name": "Smite of Protection",
        "class": "paladin",
        "action": "passive",
        "uses": None,
        "effect": "When you cast Radiant Smite, allies in your lane gain +2 AC until your next turn.",
        "src": "§7.9 L756-757",
    },
}
