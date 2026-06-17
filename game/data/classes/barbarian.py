# -*- coding: utf-8 -*-
"""Barbarian class data: chassis, class features, and L1-12 levelup manifest.

Transcribed from GDD section 7.5 (shared context: section 6 and the
section 7 intro).
"""

CLASS = {
    "id": "barbarian",
    "name": "Barbarian",
    "primary": ["str"],
    "hit_die": 12,
    "saves": ["str", "con"],
    "weapons": {"base": "all"},
    "armor": ["light", "medium", "shields"],
    "skills": {"fixed": ["athletics", "presence"]},
    "caster": None,
    "unarmored_defense": {"base": 10, "add": ["dex", "con"], "shield_allowed": True},
    "levelup": {
        1: {
            "features": ["barbarian_rage", "weapon_mastery"],
            "choices": [
                {"type": "weapon_mastery", "known_total": 3},
            ],
        },
        2: {
            "features": ["barbarian_danger_sense", "barbarian_reckless_attack"],
            "choices": [],
        },
        3: {
            "features": ["barbarian_frenzy"],
            "choices": [],
        },
        4: {
            "features": [],
            "choices": [
                {"type": "asi_or_talent"},
            ],
        },
        5: {
            "features": ["extra_attack", "barbarian_fast_movement"],
            "choices": [],
        },
        6: {
            "features": ["barbarian_mindless_rage"],
            "choices": [],
        },
        7: {
            "features": ["barbarian_feral_instinct", "barbarian_instinctive_pounce"],
            "choices": [],
        },
        8: {
            "features": [],
            "choices": [
                {"type": "asi_or_talent"},
            ],
        },
        9: {
            "features": ["barbarian_brutal_strike"],
            "choices": [],
        },
        10: {
            "features": ["barbarian_retaliation"],
            "choices": [],
        },
        11: {
            "features": ["barbarian_relentless_rage"],
            "choices": [],
        },
        12: {
            "features": ["barbarian_persistent_rage"],
            "choices": [
                {"type": "asi_or_talent"},
            ],
        },
    },
    "src": "§7.5 L555",
}

FEATURES = {
    "barbarian_rage": {
        "id": "barbarian_rage",
        "name": "Rage",
        "class": "barbarian",
        "action": "bonus",
        "uses": {
            "amount": {"by_level": {1: 2, 3: 3, 6: 4, 12: 5}},
            "per": "camp",
        },
        "effect": "While raging: resistance to bludgeoning, piercing, and slashing damage; +2 damage on Strength-based attacks (+3 from level 9); advantage on Strength checks and saves; no spellcasting or concentration.",
        "by_level": {1: 2, 9: 3},
        "src": "§7.5 L560-564",
    },
    "barbarian_danger_sense": {
        "id": "barbarian_danger_sense",
        "name": "Danger Sense",
        "class": "barbarian",
        "action": "passive",
        "uses": None,
        "effect": "Advantage on Dexterity saves.",
        "src": "§7.5 L566",
    },
    "barbarian_reckless_attack": {
        "id": "barbarian_reckless_attack",
        "name": "Reckless Attack",
        "class": "barbarian",
        "action": "free",
        "uses": None,
        "effect": "When you attack, you may attack recklessly: advantage on your Strength-based attacks this turn, but attacks against you have advantage until your next turn.",
        "src": "§7.5 L567-569",
    },
    "barbarian_frenzy": {
        "id": "barbarian_frenzy",
        "name": "Frenzy",
        "class": "barbarian",
        "action": "passive",
        "uses": None,
        "effect": "When you use Reckless Attack while raging, the first target you hit with a Strength-based attack that turn takes extra damage equal to your Rage damage bonus in d6s (2d6; 3d6 from level 9), of the attack's damage type.",
        "by_level": {3: 2, 9: 3},
        "src": "§7.5 L570-573",
    },
    "barbarian_fast_movement": {
        "id": "barbarian_fast_movement",
        "name": "Fast Movement",
        "class": "barbarian",
        "action": "free",
        "uses": {"amount": 1, "per": "turn"},
        "effect": "Once per turn, change lanes for free, without provoking.",
        "src": "§7.5 L575-576",
    },
    "barbarian_mindless_rage": {
        "id": "barbarian_mindless_rage",
        "name": "Mindless Rage",
        "class": "barbarian",
        "action": "passive",
        "uses": None,
        "effect": "Immune to Charmed and Frightened while raging.",
        "src": "§7.5 L577",
    },
    "barbarian_feral_instinct": {
        "id": "barbarian_feral_instinct",
        "name": "Feral Instinct",
        "class": "barbarian",
        "action": "passive",
        "uses": None,
        "effect": "Advantage on initiative.",
        "src": "§7.5 L578",
    },
    "barbarian_instinctive_pounce": {
        "id": "barbarian_instinctive_pounce",
        "name": "Instinctive Pounce",
        "class": "barbarian",
        "action": "free",
        "uses": None,
        "effect": "When you enter Rage, immediately change lanes free.",
        "src": "§7.5 L579",
    },
    "barbarian_brutal_strike": {
        "id": "barbarian_brutal_strike",
        "name": "Brutal Strike",
        "class": "barbarian",
        "action": "free",
        "uses": None,
        "effect": "When attacking recklessly you may forgo the advantage on one attack to add 1d10 damage and one effect: Forceful Blow or Hamstring Blow.",
        "options": [
            {
                "id": "forceful_blow",
                "name": "Forceful Blow",
                "effect": "Push the target into its Backline.",
            },
            {
                "id": "hamstring_blow",
                "name": "Hamstring Blow",
                "effect": "The target is Pinned.",
            },
        ],
        "src": "§7.5 L580-583",
    },
    "barbarian_retaliation": {
        "id": "barbarian_retaliation",
        "name": "Retaliation",
        "class": "barbarian",
        "action": "reaction",
        "uses": None,
        "effect": "When an enemy in your melee reach damages you, make one melee attack against it. Free, resolves automatically.",
        "src": "§7.5 L584-585",
    },
    "barbarian_relentless_rage": {
        "id": "barbarian_relentless_rage",
        "name": "Relentless Rage",
        "class": "barbarian",
        "action": "passive",
        "uses": None,
        "effect": "When you would be Downed while raging, make a Constitution save (DC 10) to drop to 1 HP instead. The DC rises by 5 each use and resets at Camp.",
        "src": "§7.5 L586-589",
    },
    "barbarian_persistent_rage": {
        "id": "barbarian_persistent_rage",
        "name": "Persistent Rage",
        "class": "barbarian",
        "action": "passive",
        "uses": None,
        "effect": "Your Rage ends only when you choose to end it or when you are Downed.",
        "src": "§7.5 L590-591",
    },
}
