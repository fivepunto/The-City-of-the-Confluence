# -*- coding: utf-8 -*-
"""Bard class data: chassis, class features, and LEVELUP manifest L1-12.

Transcribed from GDD section 7.8 (shared context: sections 6 and 7 intro).
"""

CLASS = {
    "id": "bard",
    "name": "Bard",
    "primary": ["cha"],
    "hit_die": 8,
    "saves": ["dex", "cha"],
    "weapons": {"base": "simple"},
    "armor": ["light"],
    "skills": {"choose": 3, "from": "any"},
    "caster": {"kind": "full", "ability": "cha", "prepared": True},
    "levelup": {
        1: {
            "features": ["bard_bardic_inspiration"],
            "choices": [
                {"type": "cantrips", "known_total": 2, "from": "bard"},
            ],
        },
        2: {
            "features": ["expertise", "bard_jack_of_all_trades"],
            "choices": [
                {"type": "expertise", "choose": 2},
            ],
        },
        3: {
            "features": ["bard_bonus_proficiencies", "bard_cutting_words"],
            "choices": [
                {"type": "skills", "choose": 2, "from": "any"},
            ],
        },
        4: {
            "features": [],
            "choices": [
                {"type": "asi_or_talent"},
                {"type": "cantrips", "known_total": 3, "from": "bard"},
            ],
        },
        5: {
            "features": ["bard_font_of_inspiration"],
            "choices": [],
        },
        6: {
            "features": ["bard_magical_discoveries"],
            "choices": [
                {
                    "type": "spells_always_prepared",
                    "choose": 2,
                    "from": ["cleric", "druid", "wizard"],
                    "swap_one_per_levelup": True,
                },
            ],
        },
        7: {
            "features": ["bard_countercharm"],
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
            "choices": [
                {"type": "expertise", "choose": 2},
            ],
        },
        10: {
            "features": ["bard_magical_secrets"],
            "choices": [
                {
                    "type": "cantrips",
                    "known_total": 4,
                    "from": ["bard", "cleric", "druid", "wizard"],
                },
            ],
        },
        11: {
            "features": [],
            "choices": [],
        },
        12: {
            "features": ["bard_peerless_skill"],
            "choices": [
                {"type": "asi_or_talent"},
            ],
        },
    },
    "src": "§7.8 L688",
}

FEATURES = {
    "bard_bardic_inspiration": {
        "id": "bard_bardic_inspiration",
        "name": "Bardic Inspiration",
        "class": "bard",
        "action": "bonus",
        "uses": {"amount": "cha_mod", "per": "camp"},
        "effect": (
            "Bonus Action: give a party member an Inspiration die. "
            "A character holds at most one die; it lasts until spent or "
            "until the next Camp. When the holder fails any d20 test — "
            "attack, save, or skill check, in or out of combat — they may "
            "roll the die and add it, potentially flipping the result."
        ),
        "by_level": {1: 6, 5: 8, 10: 10},
        "src": "§7.8 L694-702",
    },
    "bard_font_of_inspiration": {
        "id": "bard_font_of_inspiration",
        "name": "Font of Inspiration",
        "class": "bard",
        "action": "passive",
        "uses": None,
        "effect": "Regain all Inspiration uses on a Breather.",
        "src": "§7.8 L703",
    },
    "bard_jack_of_all_trades": {
        "id": "bard_jack_of_all_trades",
        "name": "Jack of All Trades",
        "class": "bard",
        "action": "passive",
        "uses": None,
        "effect": (
            "Add half your proficiency bonus (rounded down) to ability "
            "checks using skills you are NOT proficient in."
        ),
        "src": "§7.8 L707-708",
    },
    "bard_bonus_proficiencies": {
        "id": "bard_bonus_proficiencies",
        "name": "Bonus Proficiencies",
        "class": "bard",
        "action": "passive",
        "uses": None,
        "effect": "Gain 2 additional skill proficiencies.",
        "src": "§7.8 L709",
    },
    "bard_cutting_words": {
        "id": "bard_cutting_words",
        "name": "Cutting Words",
        "class": "bard",
        "action": "reaction",
        "uses": None,
        "effect": (
            "Reaction: when a visible creature deals damage or succeeds on "
            "an attack or check, expend an Inspiration use and SUBTRACT the "
            "die from their roll."
        ),
        "src": "§7.8 L710-712",
    },
    "bard_magical_discoveries": {
        "id": "bard_magical_discoveries",
        "name": "Magical Discoveries",
        "class": "bard",
        "action": "passive",
        "uses": None,
        "effect": (
            "Learn 2 spells from the Cleric, Druid, or Wizard slices — "
            "always prepared; swap one at each level-up."
        ),
        "swappable": "levelup",
        "src": "§7.8 L714-715",
    },
    "bard_countercharm": {
        "id": "bard_countercharm",
        "name": "Countercharm",
        "class": "bard",
        "action": "reaction",
        "uses": None,
        "effect": (
            "Reaction: when an ally fails a save against Charmed or "
            "Frightened, they reroll it with advantage."
        ),
        "src": "§7.8 L716-717",
    },
    "bard_magical_secrets": {
        "id": "bard_magical_secrets",
        "name": "Magical Secrets",
        "class": "bard",
        "action": "passive",
        "uses": None,
        "effect": (
            "Your prepared list may now draw freely from the combined "
            "Bard + Cleric + Druid + Wizard slices."
        ),
        "src": "§7.8 L718-719",
    },
    "bard_peerless_skill": {
        "id": "bard_peerless_skill",
        "name": "Peerless Skill",
        "class": "bard",
        "action": "free",
        "uses": None,
        "effect": (
            "When you fail a check or attack roll, expend an Inspiration "
            "use and add the die; if the roll still fails, the use is not "
            "expended."
        ),
        "src": "§7.8 L721-723",
    },
}
