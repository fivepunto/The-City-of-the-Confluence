# -*- coding: utf-8 -*-
"""Druid class data: chassis, class features, and LEVELUP manifest. GDD section 7.10 (shared context: sections 6 and 7 intro)."""

CLASS = {
    "id": "druid",
    "name": "Druid",
    "primary": ["wis"],
    "hit_die": 8,
    "saves": ["int", "wis"],
    "weapons": {"base": "simple"},
    "armor": ["light", "medium", "shields"],
    "skills": {"choose": 2, "from": ["lore", "intuition", "awareness"]},
    "caster": {"kind": "full", "ability": "wis", "prepared": True},
    "levelup": {
        1: {
            "features": ["druid_primal_order"],
            "choices": [
                {"type": "cantrips", "known_total": 2, "from": "druid"},
                {"type": "feature_option", "feature": "druid_primal_order"},
            ],
        },
        2: {
            "features": ["druid_aspects", "druid_wild_companion"],
            "choices": [
                {"type": "aspects", "known_total": 2},
            ],
        },
        3: {
            "features": ["druid_circle"],
            "choices": [
                {"type": "circle"},
            ],
        },
        4: {
            "features": [],
            "choices": [
                {"type": "asi_or_talent"},
                {"type": "cantrips", "known_total": 3, "from": "druid"},
            ],
        },
        5: {
            "features": ["druid_wild_resurgence"],
            "choices": [],
        },
        6: {
            "features": ["druid_natural_recovery"],
            "choices": [
                {"type": "aspects", "known_total": 3},
            ],
        },
        7: {
            "features": ["druid_elemental_fury"],
            "choices": [
                {"type": "feature_option", "feature": "druid_elemental_fury"},
            ],
        },
        8: {
            "features": [],
            "choices": [
                {"type": "asi_or_talent"},
            ],
        },
        9: {
            "features": [],
            "choices": [],
        },
        10: {
            "features": ["druid_natures_ward"],
            "choices": [
                {"type": "aspects", "known_total": 4},
                {"type": "cantrips", "known_total": 4, "from": "druid"},
            ],
        },
        11: {
            "features": [],
            "choices": [],
        },
        12: {
            "features": ["druid_primal_unity"],
            "choices": [
                {"type": "asi_or_talent"},
            ],
        },
    },
    "src": "§7.10 L759-762",
}

FEATURES = {
    "druid_primal_order": {
        "id": "druid_primal_order",
        "name": "Primal Order",
        "class": "druid",
        "action": "passive",
        "uses": None,
        "effect": "Choose one primal order: Magician or Warden.",
        "options": [
            {
                "id": "magician",
                "name": "Magician",
                "effect": "One extra cantrip, and add your Wisdom modifier to nature- and magic-related Lore checks.",
                # the engine has a single Lore skill (no nature/magic
                # sub-tag), so the Wisdom bonus applies to Lore checks; the
                # prose narrowing stays guidance (DATA vs GUIDANCE, #16.5)
                "grants": {"cantrips": 1,
                           "skill_bonus": {"skills": ["lore"], "ability": "wis"}},
            },
            {
                "id": "warden",
                "name": "Warden",
                "effect": "Martial weapons and heavy armor.",
                "grants": {"weapons": "martial", "armor": ["heavy"]},
            },
        ],
        "src": "§7.10 L763-765",
    },
    "druid_aspects": {
        "id": "druid_aspects",
        "name": "Aspects",
        "class": "druid",
        "action": "bonus",
        "uses": {"amount": {"by_level": {2: 2, 6: 3}}, "per": "camp"},
        "effect": "As a Bonus Action, expend a use to assume a primal stance. While an Aspect is active you cannot cast leveled spells (cantrips are fine; existing concentration persists). An Aspect lasts until dismissed or until you are Downed.",
        "options": [
            {
                "id": "bear",
                "name": "Bear",
                "effect": "Gain temporary HP equal to 2 × your level; claw attacks (d8 + Wisdom modifier, melee); advantage on Strength checks.",
            },
            {
                "id": "hawk",
                "name": "Hawk",
                "effect": "Talon dive (d6 + Wisdom modifier, ranged attack); advantage on Awareness.",
            },
            {
                "id": "serpent",
                "name": "Serpent",
                "effect": "Fang attack (d6 + Wisdom modifier, melee; Constitution save or Poisoned); advantage on Agility.",
            },
            {
                "id": "stag",
                "name": "Stag",
                "effect": "One free lane change each turn without provoking; +2 AC.",
            },
        ],
        "src": "§7.10 L766-778",
    },
    "druid_wild_companion": {
        "id": "druid_wild_companion",
        "name": "Wild Companion",
        "class": "druid",
        "action": "free",
        "uses": {"amount": 1, "per": "combat"},
        "effect": "A nature-spirit familiar — cosmetic, plus one free Help action per combat (Help grants an ally advantage on its next roll).",
        "src": "§7.10 L779-780",
    },
    "druid_circle": {
        "id": "druid_circle",
        "name": "Circle",
        "class": "druid",
        "action": "passive",
        "uses": None,
        "effect": "Choose one Druid Circle.",
        "options": [
            {
                "id": "circle_of_the_ruined_world",
                "name": "Circle of the Ruined World",
                "effect": "Ruin Spells: always prepared beyond your slice, unlocking as tiers do. Land's Aid: expend an Aspect use — one enemy lane takes 2d6 necrotic (Constitution save for half) AND one ally heals 2d6.",
                "grants_spells": [
                    {"spell": "sickening_ray", "tier": 1},
                    {"spell": "spike_field", "tier": 2},
                    {"spell": "withering_ray", "tier": 3},
                    {"spell": "blightburst", "tier": 4},
                    {"spell": "creeping_miasma", "tier": 5},
                ],
            },
            {
                "id": "circle_of_the_wild",
                "name": "Circle of the Wild",
                "effect": "+1 Aspect use, and each Aspect deepens: Bear gains resistance to bludgeoning/piercing/slashing while its temporary HP lasts · Hawk's talons gain the Vex mastery and you may target Hidden enemies · Serpent's Poisoned save is made at disadvantage · Stag grants a further +1 AC (total +3 in Stag).",
            },
            {
                "id": "circle_of_the_shepherd",
                "name": "Circle of the Shepherd",
                "effect": "Your Wild Companion's Help becomes 2 per combat; your summoned creatures arrive with +2 HP per Druid level. Totem: once per Camp, Bonus Action — plant a spirit totem in one of your lanes: allies there heal 1d6 at the start of their turns for 3 rounds.",
            },
        ],
        "src": "§7.10 L781-797",
    },
    "druid_wild_resurgence": {
        "id": "druid_wild_resurgence",
        "name": "Wild Resurgence",
        "class": "druid",
        "action": "free",
        "uses": None,
        "effect": "Once per turn, spend a spell slot to regain one Aspect use; once per Camp, convert an Aspect use into a tier 1 slot.",
        "src": "§7.10 L799-800",
    },
    "druid_natural_recovery": {
        "id": "druid_natural_recovery",
        "name": "Natural Recovery",
        "class": "druid",
        "action": "passive",
        "uses": {"amount": 1, "per": "camp"},
        "effect": "Once per Camp, on a Breather, recover spell slots whose tiers total half your Druid level (rounded up).",
        "src": "§7.10 L801-802",
    },
    "druid_elemental_fury": {
        "id": "druid_elemental_fury",
        "name": "Elemental Fury",
        "class": "druid",
        "action": "passive",
        "uses": None,
        "effect": "Choose one: Potent or Primal Strike.",
        "options": [
            {
                "id": "potent",
                "name": "Potent",
                "effect": "Add Wisdom modifier to cantrip damage.",
            },
            {
                "id": "primal_strike",
                "name": "Primal Strike",
                "effect": "+1d8 on weapon and Aspect attacks.",
            },
        ],
        "src": "§7.10 L803-804",
    },
    "druid_natures_ward": {
        "id": "druid_natures_ward",
        "name": "Nature's Ward",
        "class": "druid",
        "action": "passive",
        "uses": None,
        "effect": "Immune to Poisoned, plus a Circle-keyed bonus: Ruined World — resistance to necrotic · Wild — resistance to poison while an Aspect is active · Shepherd — your summons share your immunities and resistances.",
        "src": "§7.10 L805-808",
    },
    "druid_primal_unity": {
        "id": "druid_primal_unity",
        "name": "Primal Unity",
        "class": "druid",
        "action": "passive",
        "uses": None,
        "effect": "You may cast leveled spells while an Aspect is active.",
        "src": "§7.10 L810-811",
    },
}
