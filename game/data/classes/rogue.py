# -*- coding: utf-8 -*-
"""Rogue class data: chassis, class features, and LEVELUP manifest L1-12.

Transcribed from GDD section 7.2 (with shared context from sections 6 and 7).
"""

CLASS = {
    "id": "rogue",
    "name": "Rogue",
    "primary": ["dex"],
    "hit_die": 8,
    "saves": ["dex", "int"],
    "weapons": {"base": "simple", "plus_martial_with_any": ["finesse", "light"]},
    "armor": ["light"],
    "skills": {
        "choose": 4,
        "from": [
            "agility",
            "athletics",
            "guile",
            "intuition",
            "presence",
            "deduction",
            "awareness",
            "trickery",
        ],
    },
    "caster": None,
    "levelup": {
        1: {
            "features": ["expertise", "rogue_sneak_attack", "weapon_mastery"],
            "choices": [
                {"type": "expertise", "choose": 2},
                {"type": "weapon_mastery", "known_total": 3},
            ],
        },
        2: {
            "features": ["rogue_cunning_action"],
            "choices": [],
        },
        3: {
            "features": [
                "rogue_steady_aim",
                "rogue_fast_hands",
                "rogue_second_story_work",
            ],
            "choices": [],
        },
        4: {
            "features": [],
            "choices": [{"type": "asi_or_talent"}],
        },
        5: {
            "features": ["rogue_cunning_strike", "rogue_uncanny_dodge"],
            "choices": [],
        },
        6: {
            "features": [],
            "choices": [{"type": "expertise", "choose": 2}],
        },
        7: {
            "features": ["evasion", "rogue_reliable_talent"],
            "choices": [],
        },
        8: {
            "features": [],
            "choices": [{"type": "asi_or_talent"}],
        },
        9: {
            "features": ["rogue_supreme_sneak"],
            "choices": [],
        },
        10: {
            "features": [],
            "choices": [{"type": "asi_or_talent"}],
        },
        11: {
            "features": ["rogue_improved_cunning_strike"],
            "choices": [],
        },
        12: {
            "features": ["rogue_daze"],
            "choices": [{"type": "asi_or_talent"}],
        },
    },
    "src": "§7.2 L433",
}

FEATURES = {
    "rogue_sneak_attack": {
        "id": "rogue_sneak_attack",
        "name": "Sneak Attack",
        "class": "rogue",
        "action": "passive",
        "uses": {"amount": 1, "per": "turn"},
        "effect": (
            "Once per turn, a hit with a Finesse or ranged weapon deals +1d6 "
            "damage if you have advantage on the attack, OR a conscious ally "
            "is in melee reach of the target and you don't have disadvantage. "
            "Sneak Attack dice double on a critical hit."
        ),
        "by_level": {1: 1, 3: 2, 5: 3, 7: 4, 9: 5, 11: 6},
        "src": "§7.2 L439-443",
    },
    "rogue_cunning_action": {
        "id": "rogue_cunning_action",
        "name": "Cunning Action",
        "class": "rogue",
        "action": "bonus",
        "uses": None,
        "effect": "As a Bonus Action, choose one: Slip or Hide.",
        "options": [
            {
                "id": "slip",
                "name": "Slip",
                "effect": "Change lanes without provoking.",
            },
            {
                "id": "hide",
                "name": "Hide",
                "effect": "If you are in your Backline, gain the Hidden condition.",
            },
        ],
        "src": "§7.2 L445-447",
    },
    "rogue_steady_aim": {
        "id": "rogue_steady_aim",
        "name": "Steady Aim",
        "class": "rogue",
        "action": "bonus",
        "uses": None,
        "effect": (
            "Advantage on your next attack this turn; you cannot change lanes "
            "this turn."
        ),
        "src": "§7.2 L448-449",
    },
    "rogue_fast_hands": {
        "id": "rogue_fast_hands",
        "name": "Fast Hands",
        "class": "rogue",
        "action": "passive",
        "uses": None,
        "effect": "You may take the Use Item action as a Bonus Action.",
        "src": "§7.2 L450",
    },
    "rogue_second_story_work": {
        "id": "rogue_second_story_work",
        "name": "Second-Story Work",
        "class": "rogue",
        "action": "passive",
        "uses": None,
        "effect": "Advantage on traversal and climbing checks.",
        "src": "§7.2 L451",
    },
    "rogue_cunning_strike": {
        "id": "rogue_cunning_strike",
        "name": "Cunning Strike",
        "class": "rogue",
        "action": "passive",
        "uses": None,
        "effect": (
            "When you deal Sneak Attack damage, you may trade dice for "
            "effects."
        ),
        "save_dc": "8 + Dexterity modifier + proficiency",
        "options": [
            {
                "id": "poison",
                "name": "Poison",
                "cost": 1,
                "save": "con",
                "effect": "Constitution save or Poisoned.",
            },
            {
                "id": "trip",
                "name": "Trip",
                "cost": 1,
                "save": "dex",
                "effect": "Dexterity save or Staggered.",
            },
            {
                "id": "withdraw",
                "name": "Withdraw",
                "cost": 1,
                "effect": (
                    "After the attack, change lanes free without provoking."
                ),
            },
            {
                "id": "stealth_attack",
                "name": "Stealth Attack",
                "cost": 1,
                "granted_by": "rogue_supreme_sneak",
                "effect": (
                    "If you attack from Hidden, the attack does not reveal "
                    "you (Backline only)."
                ),
            },
            {
                "id": "daze",
                "name": "Daze",
                "cost": 2,
                "save": "con",
                "granted_by": "rogue_daze",
                "effect": (
                    "Constitution save or, on its next turn, the target may "
                    "either move or act — not both."
                ),
            },
        ],
        "src": "§7.2 L453-458",
    },
    "rogue_uncanny_dodge": {
        "id": "rogue_uncanny_dodge",
        "name": "Uncanny Dodge",
        "class": "rogue",
        "action": "reaction",
        "uses": {"amount": "level_div_3", "per": "camp"},
        "effect": "When an attack hits you, halve its damage.",
        "src": "§7.2 L459-460",
    },
    "rogue_reliable_talent": {
        "id": "rogue_reliable_talent",
        "name": "Reliable Talent",
        "class": "rogue",
        "action": "passive",
        "uses": None,
        "effect": (
            "On ability checks using skills you are proficient in, treat any "
            "d20 roll of 9 or lower as a 10."
        ),
        "src": "§7.2 L463-464",
    },
    "rogue_supreme_sneak": {
        "id": "rogue_supreme_sneak",
        "name": "Supreme Sneak",
        "class": "rogue",
        "action": "passive",
        "uses": None,
        "effect": (
            "A new Cunning Strike option, Stealth Attack (costs 1d6): if you "
            "attack from Hidden, the attack does not reveal you (Backline "
            "only)."
        ),
        "src": "§7.2 L465-467",
    },
    "rogue_improved_cunning_strike": {
        "id": "rogue_improved_cunning_strike",
        "name": "Improved Cunning Strike",
        "class": "rogue",
        "action": "passive",
        "uses": None,
        "effect": (
            "Apply up to two Cunning Strike effects on one Sneak Attack, "
            "paying each cost."
        ),
        "src": "§7.2 L468-469",
    },
    "rogue_daze": {
        "id": "rogue_daze",
        "name": "Daze",
        "class": "rogue",
        "action": "passive",
        "uses": None,
        "effect": (
            "A new Cunning Strike option (costs 2d6): Constitution save or, "
            "on its next turn, the target may either move or act — not both."
        ),
        "src": "§7.2 L470-472",
    },
}
