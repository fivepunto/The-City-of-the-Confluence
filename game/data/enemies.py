# -*- coding: utf-8 -*-
"""Enemy statblocks and intent scripts (GDD 11.1-11.2), the intent-script
vocabulary (GDD 16.3), and pending summon statblocks (GDD 9.12)."""

ENEMIES = {
    "standard_wolf": {
        "id": "standard_wolf",
        "name": "Standard Wolf",
        "xp": 50,
        "abilities": {"str": 14, "dex": 15, "con": 12, "int": 3, "wis": 12, "cha": 6},
        "save_proficiencies": [],
        "ac": 13,
        "hp": 11,
        "initiative_bonus": 2,
        "lane_preference": "frontline",
        "tags": ["wolf"],
        "attacks": [
            {
                "id": "bite",
                "name": "Bite",
                "to_hit": 4,
                "dice": "2d4+2",
                "damage_type": "piercing",
                "rider": {
                    "save": {"ability": "str", "dc": 11},
                    "condition": "staggered",
                },
            },
        ],
        "traits": [
            {
                "id": "pack_tactics",
                "name": "Pack Tactics",
                "effect": "Advantage on attack rolls while another wolf is in the same lane.",
            },
        ],
        "intent": [
            {"if": "round==1", "do": "move(frontline)"},
            {"if": "party_frontline_empty", "do": "attack(bite)", "target": "random_backline"},
            {"if": "always", "do": "attack(bite)", "target": "nearest_frontline"},
        ],
        "region": None,
        "src": "§11.2 L1293-1302, §16.3 L1662-1664",
    },
    "young_wolf": {
        "id": "young_wolf",
        "name": "Young Wolf",
        "xp": 25,
        "abilities": {"str": 13, "dex": 14, "con": 10, "int": 3, "wis": 11, "cha": 6},
        "save_proficiencies": [],
        "ac": 12,
        "hp": 7,
        "initiative_bonus": 2,
        # frontline per owner adjudication, P0 round 2 (G-017)
        "lane_preference": "frontline",
        "tags": ["wolf"],
        "attacks": [
            {
                "id": "bite",
                "name": "Bite",
                "to_hit": 3,
                "dice": "1d4+1",
                "damage_type": "piercing",
                "rider": None,
            },
        ],
        "traits": [],
        "intent": [
            {"if": "round==1", "do": "move(frontline)"},
            {"if": "party_frontline_empty", "do": "attack(bite)", "target": "random_backline"},
            {"if": "always", "do": "attack(bite)", "target": "nearest_frontline"},
        ],
        "region": None,
        "src": "§11.2 L1304-1308, §16.3 L1662-1664",
    },
}

INTENT_VOCAB = {
    "predicates": [
        "always",
        "round == n",
        "hp_below(0.5)",
        "party_frontline_empty",
        "ally_count_below(n)",
        "has_condition(x)",
        "cooldown_ready(ability)",
        "target_exists(selector)",
    ],
    "actions": [
        "attack(name)",
        "cast(spell, tier)",
        "move(line)",
        "telegraph(ability)",
        "flee",
    ],
    "selectors": [
        "nearest_frontline",
        "lowest_hp",
        "random_backline",
        "marked",
        "last_attacker",
        "healer_first",
    ],
    "src": "§16.3 L1652-1658",
}

# Summons do not roll initiative; a summon acts immediately after its
# summoner in the turn order and leaves the order when it ends. Summons are
# never Downed: at 0 HP they simply end (GDD 9.12; owner adjudication,
# P0 round 2, G-004).
SUMMON_RULES = {
    "no_initiative_roll": True,
    "acts_immediately_after_summoner": True,
    "leaves_order_when_ended": True,
    "never_downed": True,
    "src": "§9.12 L1164-1166",
}

SUMMON_STATBLOCKS = {
    "spirit_beast": {
        "id": "spirit_beast",
        "name": "Spirit Beast",
        "for_spell": "conjure_beast",
        # canonical per owner adjudication, P0 round 2 (G-004)
        "statblock": {
            "abilities": {"str": 14, "dex": 15, "con": 12, "int": 3,
                          "wis": 12, "cha": 6},
            "ac": 13,
            "hp": 15,
            "attacks": [
                {
                    "id": "bite",
                    "name": "Bite",
                    "to_hit": 4,
                    "dice": "2d4+2",
                    "damage_type": "piercing",
                    "rider": None,
                },
            ],
            "traits": [
                {
                    "id": "spirit_form",
                    "name": "Spirit Form",
                    "effect": "At 0 HP the summon simply ends — summons are never Downed.",
                },
            ],
        },
        "pending": False,
        "src": "§9.12 L1155-1162",
    },
    "guardian": {
        "id": "guardian",
        "for_spell": "conjure_guardian",
        "statblock": None,
        "pending": True,
        "src": "§9.12 L1149-1152",
    },
    "stalker": {
        "id": "stalker",
        "for_spell": "conjure_stalker",
        "statblock": None,
        "pending": True,
        "src": "§9.12 L1149-1152",
    },
    "elemental": {
        "id": "elemental",
        "for_spell": "conjure_elemental",
        "statblock": None,
        "pending": True,
        "src": "§9.12 L1149-1152",
    },
    "champion": {
        "id": "champion",
        "for_spell": "conjure_champion",
        "statblock": None,
        "pending": True,
        "src": "§9.12 L1150-1152",
    },
}
