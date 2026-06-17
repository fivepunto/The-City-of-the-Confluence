# -*- coding: utf-8 -*-
"""Fighter class data: chassis, class features, and LEVELUP manifest (GDD section 7.1; shared context sections 6 and 7)."""

CLASS = {
    "id": "fighter",
    "name": "Fighter",
    "primary": ["str", "dex"],
    "hit_die": 10,
    "saves": ["str", "con"],
    "weapons": {"base": "all"},
    "armor": ["light", "medium", "heavy", "shields"],
    "skills": {
        "choose": 2,
        "from": ["athletics", "agility", "lore", "intuition", "awareness", "presence"],
    },
    "caster": None,
    "levelup": {
        1: {
            "features": ["fighter_second_wind", "weapon_mastery"],
            "choices": [
                {"type": "fighting_style"},
                {"type": "weapon_mastery", "known_total": 4},
            ],
        },
        2: {
            "features": ["fighter_action_surge", "fighter_tactical_mind"],
            "choices": [],
        },
        3: {
            "features": ["fighter_improved_critical", "fighter_remarkable_athlete"],
            "choices": [],
        },
        4: {
            "features": [],
            "choices": [
                {"type": "asi_or_talent"},
                {"type": "weapon_mastery", "known_total": 5},
            ],
        },
        5: {
            "features": ["extra_attack", "fighter_tactical_shift"],
            "choices": [],
        },
        6: {
            "features": [],
            "choices": [{"type": "asi_or_talent"}],
        },
        7: {
            "features": [],
            # fighting styles are permanent (owner adjudication, P1 review, D1)
            "choices": [{"type": "fighting_style"}],
        },
        8: {
            "features": [],
            "choices": [{"type": "asi_or_talent"}],
        },
        9: {
            "features": ["fighter_indomitable", "fighter_tactical_master"],
            "choices": [],
        },
        10: {
            "features": ["fighter_heroic_warrior"],
            "choices": [{"type": "weapon_mastery", "known_total": 6}],
        },
        11: {
            "features": ["fighter_two_extra_attacks"],
            "choices": [],
        },
        12: {
            "features": ["fighter_studied_attacks"],
            "choices": [{"type": "asi_or_talent"}],
        },
    },
    "src": "§7.1 L399",
}

FEATURES = {
    "fighter_second_wind": {
        "id": "fighter_second_wind",
        "name": "Second Wind",
        "class": "fighter",
        "action": "bonus",
        "uses": {
            "amount": {"by_level": {1: 2, 4: 3, 10: 4}},
            "per": "camp",
            "regain_one_per_breather": True,
        },
        "effect": "Heal yourself 1d10 + Fighter level.",
        "src": "§7.1 L405-406",
    },
    "fighter_action_surge": {
        "id": "fighter_action_surge",
        "name": "Action Surge",
        "class": "fighter",
        "action": "free",
        "uses": {"amount": 1, "per": "breather"},
        "effect": "Gain one extra Action this turn; it cannot be used to cast a spell.",
        "src": "§7.1 L409-410",
    },
    "fighter_tactical_mind": {
        "id": "fighter_tactical_mind",
        "name": "Tactical Mind",
        "class": "fighter",
        "action": "free",
        "uses": None,
        "effect": "When you fail an ability check, you may spend a Second Wind use to add 1d10 to it; if it still fails, the use is not spent.",
        "src": "§7.1 L411-412",
    },
    "fighter_improved_critical": {
        "id": "fighter_improved_critical",
        "name": "Improved Critical",
        "class": "fighter",
        "action": "passive",
        "uses": None,
        "effect": "Your attacks crit on 19–20.",
        "src": "§7.1 L413",
    },
    "fighter_remarkable_athlete": {
        "id": "fighter_remarkable_athlete",
        "name": "Remarkable Athlete",
        "class": "fighter",
        "action": "passive",
        "uses": None,
        "effect": "Advantage on initiative and Athletics checks; after you score a critical hit, you may change lanes for free without provoking.",
        "src": "§7.1 L414-416",
    },
    "fighter_tactical_shift": {
        "id": "fighter_tactical_shift",
        "name": "Tactical Shift",
        "class": "fighter",
        "action": "passive",
        "uses": None,
        "effect": "When you use Second Wind, you may change lanes for free without provoking.",
        "src": "§7.1 L419-420",
    },
    "fighter_indomitable": {
        "id": "fighter_indomitable",
        "name": "Indomitable",
        "class": "fighter",
        "action": "free",
        "uses": {"amount": 1, "per": "camp"},
        "effect": "When you fail a saving throw, reroll it with a bonus equal to your Fighter level; you must keep the new roll.",
        "src": "§7.1 L422-423",
    },
    "fighter_tactical_master": {
        "id": "fighter_tactical_master",
        "name": "Tactical Master",
        "class": "fighter",
        "action": "passive",
        "uses": None,
        "effect": "When attacking with a mastery weapon, you may replace its property with Push, Sap, or Slow for that attack.",
        "src": "§7.1 L424-425",
    },
    "fighter_heroic_warrior": {
        "id": "fighter_heroic_warrior",
        "name": "Heroic Warrior",
        "class": "fighter",
        "action": "passive",
        "uses": None,
        "effect": "At the start of each of your combat turns, gain Heroic Inspiration (the combat-only reroll) if you don't already have it.",
        "src": "§7.1 L426-427",
    },
    "fighter_two_extra_attacks": {
        "id": "fighter_two_extra_attacks",
        "name": "Two Extra Attacks",
        "class": "fighter",
        "action": "passive",
        "uses": None,
        "effect": "Three attacks per Attack action.",
        "src": "§7.1 L428",
    },
    "fighter_studied_attacks": {
        "id": "fighter_studied_attacks",
        "name": "Studied Attacks",
        "class": "fighter",
        "action": "passive",
        "uses": None,
        "effect": "When you miss a creature, you have advantage on your next attack against it before the end of your next turn.",
        "src": "§7.1 L429-431",
    },
}
