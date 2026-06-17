# -*- coding: utf-8 -*-
"""Player-facing class descriptions for the creation screen (GDD #7;
owner adjudication, P1 review, D9). Tooltip-class UI text -- allowed in
data (#16.5). One authored sentence-or-two of playstyle per class, written
for someone who has never played a tabletop RPG. The primary attribute,
durability word, and weapon/armor lines are DERIVED from the chassis in
the screen helpers, not stored here."""

CLASS_UI = {
    "fighter": {
        "id": "fighter",
        "desc": "A versatile front-line warrior — the most reliable weapon "
                "user in the game, strong in any armor, and able to keep "
                "swinging when others tire. The easiest class to learn.",
        "src": "§7.1 L399",
    },
    "rogue": {
        "id": "rogue",
        "desc": "A precise skirmisher who deals a burst of extra damage "
                "whenever an ally distracts the target, and trains in more "
                "skills than anyone for exploration and conversation.",
        "src": "§7.2 L433",
    },
    "cleric": {
        "id": "cleric",
        "desc": "A divine healer and protector — the earliest and best at "
                "reviving fallen allies, with holy magic that punishes the "
                "undead. The safest anchor for a new party.",
        "src": "§7.3 L474",
    },
    "wizard": {
        "id": "wizard",
        "desc": "A scholarly spellcaster with the deepest spellbook and the "
                "widest range of magic — but very fragile. Keep it behind "
                "the front line and let the spells do the work.",
        "src": "§7.4 L521",
    },
    "barbarian": {
        "id": "barbarian",
        "desc": "A raging bruiser with the most health in the game and "
                "damage resistance while enraged. Simple and tough: charge "
                "into the front and hit hard.",
        "src": "§7.5 L555",
    },
    "ranger": {
        "id": "ranger",
        "desc": "A wilderness hunter who marks a quarry for extra damage, "
                "fights well at range with a bow, and keeps the party fed "
                "and supplied on expeditions.",
        "src": "§7.6 L593",
    },
    "warlock": {
        "id": "warlock",
        "desc": "A pact spellcaster with few but powerful spells that "
                "recharge after every short rest, plus an at-will magical "
                "blast. Having one along grants the party an extra rest "
                "each camp.",
        "src": "§7.7 L629",
    },
    "bard": {
        "id": "bard",
        "desc": "A charismatic support caster who inspires allies to "
                "succeed and can learn a little of every kind of magic. The "
                "most flexible class in and out of a fight.",
        "src": "§7.8 L688",
    },
    "paladin": {
        "id": "paladin",
        "desc": "A holy knight in heavy armor — a sturdy front-liner who "
                "heals by touch, smites foes with radiant power, and shields "
                "nearby allies with protective auras.",
        "src": "§7.9 L725",
    },
    "druid": {
        "id": "druid",
        "desc": "A shapeshifting nature caster who takes on primal animal "
                "forms in battle and wields the magic of the broken world. "
                "Flexible, but the most to manage.",
        "src": "§7.10 L759",
    },
    "monk": {
        "id": "monk",
        "desc": "A nimble martial artist who fights unarmed in a flurry of "
                "strikes, deflects blows, and darts across the battlefield. "
                "Wears no armor — speed and discipline are its defense.",
        "src": "§7.11 L813",
    },
    "sorcerer": {
        "id": "sorcerer",
        "desc": "An innate spellcaster brimming with raw magic — fewer "
                "spells than a wizard, but the most at-will cantrips and the "
                "power to bend a spell in the moment. Fragile.",
        "src": "§7.12 L858",
    },
}
