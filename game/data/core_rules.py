# -*- coding: utf-8 -*-
"""Core rules data transcribed from docs/gdd.md.

Covers: section 2 (proficiency bonus), section 3 (point buy, human traits),
section 4.1 (skills), section 5.3 (damage types), section 6 (XP thresholds),
section 7 (spell slot tables, pact magic, prepared-spell counts),
sections 12.1 and 12.3 (rest rules and day clock).
"""

POINT_BUY = {
    "points": 27,
    "costs": {8: 0, 9: 1, 10: 2, 11: 3, 12: 4, 13: 5, 14: 7, 15: 9},
    "min": 8,
    "max": 15,
    "src": "§3 L127-130",
}

PROFICIENCY_BY_LEVEL = {
    "by_level": {1: 2, 5: 3, 9: 4},
    "src": "§2.5 L85-86",
}

XP_THRESHOLDS = {
    "by_level": [0, 300, 900, 2700, 6500, 14000, 23000, 34000, 48000,
                 64000, 85000, 100000],
    "src": "§6 L370-372",
}

DAMAGE_TYPES = {
    "types": ["bludgeoning", "piercing", "slashing", "fire", "cold",
              "lightning", "thunder", "acid", "poison", "necrotic",
              "radiant", "force", "psychic"],
    "src": "§5.3 L246-248",
}

SKILLS = {
    "athletics": {
        "id": "athletics",
        "name": "Athletics",
        "ability": "str",
        "desc": "Climbing, forcing, grappling, raw physical effort",
        "src": "§4.1 L158",
    },
    "trickery": {
        "id": "trickery",
        "name": "Trickery",
        "ability": "dex",
        "desc": "Covert handwork: picking locks and pockets, sleight of hand, sneaking",
        "src": "§4.1 L159",
    },
    "agility": {
        "id": "agility",
        "name": "Agility",
        "ability": "dex",
        "desc": "Athletic reflexes: balancing, tumbling, dodging",
        "src": "§4.1 L160",
    },
    "lore": {
        "id": "lore",
        "name": "Lore",
        "ability": "int",
        "desc": "Recall: history, religion, arcana, nature knowledge",
        "src": "§4.1 L161",
    },
    "deduction": {
        "id": "deduction",
        "name": "Deduction",
        "ability": "int",
        "desc": "Reasoning: investigating, connecting clues",
        "src": "§4.1 L162",
    },
    "intuition": {
        "id": "intuition",
        "name": "Intuition",
        "ability": "wis",
        "desc": "Reading people: motives, lies, moods",
        "src": "§4.1 L163",
    },
    "awareness": {
        "id": "awareness",
        "name": "Awareness",
        "ability": "wis",
        "desc": "Reading the environment: spotting, listening, tracking, survival",
        "src": "§4.1 L164",
    },
    "presence": {
        "id": "presence",
        "name": "Presence",
        "ability": "cha",
        "desc": "Overt influence: persuasion, command, intimidation",
        "src": "§4.1 L165",
    },
    "guile": {
        "id": "guile",
        "name": "Guile",
        "ability": "cha",
        "desc": "Covert influence: deception, misdirection",
        "src": "§4.1 L166",
    },
}

HUMAN = {
    "id": "human",
    "name": "Human",
    "traits": {
        "resourceful": {
            "id": "resourceful",
            "name": "Resourceful",
            "effect": "One use of Heroic Inspiration per long rest. Heroic "
                      "Inspiration is a combat-only resource: spend it to "
                      "reroll one of your own d20 rolls in combat. It can "
                      "never be used on dialogue or exploration checks.",
        },
        "skillful": {
            "id": "skillful",
            "name": "Skillful",
            "effect": "Proficiency in one skill of the player's choice.",
        },
        "versatile": {
            "id": "versatile",
            "name": "Versatile",
            "effect": "One Talent chosen from this starter list: Alert, "
                      "Skilled, Lucky, Magic Initiate, Tough, Field Medic.",
            "choices": ["alert", "skilled", "lucky", "magic_initiate",
                        "tough", "field_medic"],
        },
    },
    "src": "§3 L136-142",
}

SLOT_TABLE_FULL = {
    "by_level": {
        1: {1: 2},
        2: {1: 3},
        3: {1: 4, 2: 2},
        4: {1: 4, 2: 3},
        5: {1: 4, 2: 3, 3: 2},
        6: {1: 4, 2: 3, 3: 3},
        7: {1: 4, 2: 3, 3: 3, 4: 1},
        8: {1: 4, 2: 3, 3: 3, 4: 2},
        9: {1: 4, 2: 3, 3: 3, 4: 3, 5: 1},
        10: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2},
        11: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1},
        12: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1},
    },
    "src": "§7 L394-395, §6 L376",
}

SLOT_TABLE_HALF = {
    "by_level": {
        1: {1: 2},
        2: {1: 2},
        3: {1: 3},
        4: {1: 3},
        5: {1: 4, 2: 2},
        6: {1: 4, 2: 2},
        7: {1: 4, 2: 3},
        8: {1: 4, 2: 3},
        9: {1: 4, 2: 3, 3: 2},
        10: {1: 4, 2: 3, 3: 2},
        11: {1: 4, 2: 3, 3: 3},
        12: {1: 4, 2: 3, 3: 3},
    },
    "src": "§7.6 L597-598",
}

PACT_SLOTS = {
    "slots_by_level": {1: 1, 2: 2, 11: 3},
    "tier_by_level": {1: 1, 3: 2, 5: 3, 7: 4, 9: 5},
    "recharge": "breather",
    "src": "§7.7 L633-639",
}

PREPARED_SPELLS = {
    "by_class": {
        "wizard": [4, 5, 6, 7, 9, 10, 11, 12, 14, 15, 16, 16],
        "cleric": [4, 5, 6, 7, 9, 10, 11, 12, 14, 15, 16, 16],
        "druid": [4, 5, 6, 7, 9, 10, 11, 12, 14, 15, 16, 16],
        "bard": [4, 5, 6, 7, 9, 10, 11, 12, 14, 15, 16, 16],
        "sorcerer": [2, 4, 6, 7, 9, 10, 11, 12, 14, 15, 16, 16],
        "warlock": [2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 11, 11],
        "paladin": [2, 3, 4, 5, 6, 6, 7, 7, 9, 9, 10, 10],
        "ranger": [2, 3, 4, 5, 6, 6, 7, 7, 9, 9, 10, 10],
    },
    "index": "level-1",
    "src": "§7.4 L530, §7.7 L640",
}

REST_RULES = {
    "breathers_per_camp": 2,
    "breathers_with_warlock": 3,
    "warlocks_do_not_stack": True,
    "recovery_dice_pool": "level",
    "recovery_die_heals": "hit_die_plus_con_mod",
    "camp_restores_all": True,
    "camp_clears_conditions": True,
    "day_phases": ["morning", "afternoon", "evening"],
    "breather_advances_phase": True,
    "phase_clamps_at_evening": True,
    "camp_resets_to_morning": True,
    "src": "§12.1 L1319-1336, §12.3 L1354-1359",
}
