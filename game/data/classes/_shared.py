# -*- coding: utf-8 -*-
"""Features shared verbatim across classes -- defined once (DECISIONS.md
D-005), referenced by id from class LEVELUP manifests."""

FEATURES = {
    "extra_attack": {
        "id": "extra_attack",
        "name": "Extra Attack",
        "class": None,
        "action": "passive",
        "effect": "Attack twice whenever you take the Attack action.",
        "src": "§7 L392",
    },
    "expertise": {
        "id": "expertise",
        "name": "Expertise",
        "class": None,
        "action": "passive",
        "effect": "Double proficiency bonus on a chosen proficient skill.",
        "src": "§7 L393",
    },
    "evasion": {
        "id": "evasion",
        "name": "Evasion",
        "class": None,
        "action": "passive",
        "effect": "On Dexterity saves for half damage, take nothing on a "
                  "success and half on a failure.",
        "src": "§7.2 L461-462",
    },
    "weapon_mastery": {
        "id": "weapon_mastery",
        "name": "Weapon Mastery",
        "class": None,
        "action": "passive",
        "effect": "Use the mastery property of your chosen weapon types.",
        "src": "§10.3 L1192-1194",
    },
}
