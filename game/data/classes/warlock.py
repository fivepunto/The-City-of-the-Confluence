# -*- coding: utf-8 -*-
"""Warlock class data: chassis, features, and LEVELUP manifest (GDD section 7.7;
shared progression context from sections 6 and 7)."""

CLASS = {
    "id": "warlock",
    "name": "Warlock",
    "primary": ["cha"],
    "hit_die": 8,
    "saves": ["wis", "cha"],
    "weapons": {"base": "simple"},
    "armor": ["light"],
    "skills": {"choose": 2, "from": ["lore", "guile", "presence", "deduction"]},
    "caster": {"kind": "pact", "ability": "cha", "prepared": True},
    "levelup": {
        1: {
            "features": ["warlock_pact_magic", "warlock_eldritch_invocations"],
            "choices": [
                {"type": "cantrips", "known_total": 2, "from": "warlock"},
                {"type": "invocations", "known_total": 1, "swap_one": True},
            ],
        },
        2: {
            "features": ["warlock_magical_cunning"],
            "choices": [
                {"type": "invocations", "known_total": 3, "swap_one": True},
            ],
        },
        3: {
            "features": ["warlock_dark_ones_blessing", "warlock_fiend_spells"],
            "choices": [],
        },
        4: {
            "features": [],
            "choices": [
                {"type": "asi_or_talent"},
                {"type": "cantrips", "known_total": 3, "from": "warlock"},
            ],
        },
        5: {
            "features": [],
            "choices": [
                {"type": "invocations", "known_total": 5, "swap_one": True},
            ],
        },
        6: {
            "features": ["warlock_dark_ones_own_luck"],
            "choices": [],
        },
        7: {
            "features": [],
            "choices": [
                {"type": "invocations", "known_total": 6, "swap_one": True},
            ],
        },
        8: {
            "features": [],
            "choices": [
                {"type": "asi_or_talent"},
            ],
        },
        9: {
            "features": ["warlock_contact_patron"],
            "choices": [
                {"type": "invocations", "known_total": 7, "swap_one": True},
            ],
        },
        10: {
            "features": ["warlock_fiendish_resilience"],
            "choices": [
                {"type": "cantrips", "known_total": 4, "from": "warlock"},
            ],
        },
        11: {
            "features": ["warlock_mystic_arcanum"],
            "choices": [
                {"type": "mystic_arcanum", "choose": 1, "tier": 6},
            ],
        },
        12: {
            "features": ["warlock_hurl_through_hell"],
            "choices": [
                {"type": "asi_or_talent"},
                {"type": "invocations", "known_total": 8, "swap_one": True},
            ],
        },
    },
    "src": "§7.7 L629",
}

FEATURES = {
    "warlock_pact_magic": {
        "id": "warlock_pact_magic",
        "name": "Pact Magic",
        "class": "warlock",
        "action": "passive",
        "uses": None,
        "effect": "All pact slots are the same tier, and that tier climbs as you level. All pact slots recharge on a Breather. Every spell you cast automatically upcasts to the slot's tier.",
        "src": "§7.7 L633-639",
    },
    "warlock_eldritch_invocations": {
        "id": "warlock_eldritch_invocations",
        "name": "Eldritch Invocations",
        "class": "warlock",
        "action": "passive",
        "uses": None,
        "effect": "Passive magical augments. One may be swapped at each level-up.",
        "options": [
            {
                "id": "agonizing_blast",
                "name": "Agonizing Blast",
                "effect": "Add Charisma modifier to Eldritch Lash damage.",
            },
            {
                "id": "repelling_lash",
                "name": "Repelling Lash",
                "effect": "Once per turn, an Eldritch Lash hit pushes the target to its Backline.",
            },
            {
                "id": "grasping_lash",
                "name": "Grasping Lash",
                "effect": "Once per turn, a Lash hit pulls the target to its Frontline.",
            },
            {
                "id": "armor_of_shadows",
                "name": "Armor of Shadows",
                "effect": "Unarmored base AC = 13 + Dexterity modifier.",
            },
            {
                "id": "witchsight",
                "name": "Witchsight",
                "effect": "You may target Hidden and Veiled enemies normally.",
            },
            {
                "id": "eldritch_mind",
                "name": "Eldritch Mind",
                "effect": "Advantage on concentration saves.",
            },
            {
                "id": "pact_of_the_blade",
                "name": "Pact of the Blade",
                "effect": "Your mainhand weapon becomes your pact weapon: attack with Charisma; counts as magical.",
            },
            {
                "id": "thirsting_blade",
                "name": "Thirsting Blade",
                "effect": "Extra Attack with the pact weapon.",
                "min_level": 5,
                "requires": "pact_of_the_blade",
            },
            {
                "id": "lifedrinker",
                "name": "Lifedrinker",
                "effect": "The pact weapon deals +1d6 necrotic; once per turn, heal that amount.",
                "min_level": 9,
                "requires": "pact_of_the_blade",
            },
            {
                "id": "pact_of_the_tome",
                "name": "Pact of the Tome",
                "effect": "Learn 2 extra cantrips from ANY class's set.",
            },
            {
                "id": "fiendish_vigor",
                "name": "Fiendish Vigor",
                "effect": "At will, as an Action: gain 2d4 temporary HP.",
            },
            {
                "id": "beguiling_influence",
                "name": "Beguiling Influence",
                "effect": "Proficiency in Guile and Presence.",
            },
        ],
        "src": "§7.7 L646-661",
    },
    "warlock_magical_cunning": {
        "id": "warlock_magical_cunning",
        "name": "Magical Cunning",
        "class": "warlock",
        "action": "passive",
        "uses": None,
        "effect": "Having a Warlock in the party grants the whole party one additional Breather per Camp (3 instead of 2). Multiple Warlocks do not stack.",
        "src": "§7.7 L662-664",
    },
    "warlock_dark_ones_blessing": {
        "id": "warlock_dark_ones_blessing",
        "name": "Dark One's Blessing",
        "class": "warlock",
        "action": "passive",
        "uses": None,
        "effect": "When you reduce an enemy to 0 HP, or an enemy in your melee reach drops, gain temporary HP equal to your Charisma modifier + Warlock level.",
        "src": "§7.7 L665-667",
    },
    "warlock_fiend_spells": {
        "id": "warlock_fiend_spells",
        "name": "Fiend Spells",
        "class": "warlock",
        "action": "passive",
        "uses": None,
        "effect": "The fire line is always prepared and not counted against prepared spells, unlocking as the pact-slot tier reaches each spell's tier.",
        "grants_spells": [
            {"spell": "searing_burst", "tier": 1},
            {"spell": "scorch_line", "tier": 2},
            {"spell": "fireburst", "tier": 3},
            {"spell": "flamewall", "tier": 4},
            {"spell": "creeping_miasma", "tier": 5},
        ],
        "src": "§7.7 L668-671",
    },
    "warlock_dark_ones_own_luck": {
        "id": "warlock_dark_ones_own_luck",
        "name": "Dark One's Own Luck",
        "class": "warlock",
        "action": "free",
        "uses": {"amount": "cha_mod", "per": "camp"},
        "effect": "After seeing one of your ability check or saving throw rolls, add 1d10 to it. Once per roll.",
        "src": "§7.7 L673-675",
    },
    "warlock_contact_patron": {
        "id": "warlock_contact_patron",
        "name": "Contact Patron",
        "class": "warlock",
        "action": "passive",
        "uses": None,
        "effect": "At Camp, the Warlock can commune with their patron — occasional information, occasional demands.",
        "src": "§7.7 L676-678",
    },
    "warlock_fiendish_resilience": {
        "id": "warlock_fiendish_resilience",
        "name": "Fiendish Resilience",
        "class": "warlock",
        "action": "passive",
        "uses": None,
        "effect": "After each rest, choose a damage type other than force; you have resistance to it until you choose another.",
        "swappable": "rest",
        "src": "§7.7 L679-680",
    },
    "warlock_mystic_arcanum": {
        "id": "warlock_mystic_arcanum",
        "name": "Mystic Arcanum",
        "class": "warlock",
        "action": "passive",
        "uses": {"amount": 1, "per": "camp"},
        "effect": "Choose one tier 6 spell from the Warlock slice; cast it once per Camp without a slot.",
        "src": "§7.7 L642-643, §7.7 L681",
    },
    "warlock_hurl_through_hell": {
        "id": "warlock_hurl_through_hell",
        "name": "Hurl Through Hell",
        "class": "warlock",
        "action": "free",
        "uses": {"amount": 1, "per": "camp"},
        "effect": "Once per turn when you hit a creature, force a Charisma save; on a failure the target is removed from combat until the end of your next turn and takes 8d10 psychic damage on return. Once per Camp; restorable by spending a pact slot.",
        "src": "§7.7 L682-686",
    },
}
