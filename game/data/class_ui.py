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
        "desc": "The cleanest weapon specialist. Fighters wear any armor, "
                "use every weapon, heal themselves with Second Wind, and can "
                "take an extra Action with Action Surge. Straightforward, "
                "durable, and excellent for learning combat.",
        "src": "§7.1 L399",
    },
    "rogue": {
        "id": "rogue",
        "desc": "A precise skirmisher built around Sneak Attack: strike with "
                "advantage or while an ally threatens the target to deal heavy "
                "extra damage. Rogues also gain more skill power than anyone "
                "for locks, stealth, clues, and conversations.",
        "src": "§7.2 L433",
    },
    "cleric": {
        "id": "cleric",
        "desc": "A divine anchor for the party. Clerics prepare many spells, "
                "heal efficiently, unlock True Healing to revive Downed allies, "
                "and use Channel Divinity for burst healing, radiant damage, "
                "or turning undead.",
        "src": "§7.3 L474",
    },
    "wizard": {
        "id": "wizard",
        "desc": "The broadest spellcaster. Wizards start with a spellbook, "
                "learn new spells every level, copy more at Camp, and recover "
                "spent spell slots on a Breather. Fragile, but unmatched for "
                "damage and utility options.",
        "src": "§7.4 L521",
    },
    "barbarian": {
        "id": "barbarian",
        "desc": "A high-health bruiser who enters Rage to resist physical "
                "damage, hit harder with Strength attacks, and shrug off fear "
                "or charm later on. Best when kept in the Frontline and played "
                "aggressively.",
        "src": "§7.5 L555",
    },
    "ranger": {
        "id": "ranger",
        "desc": "A flexible hunter with weapons, survival skills, and half "
                "casting. Rangers mark a quarry for extra weapon damage, gain "
                "expertise in a chosen skill, and improve Camp hunting during "
                "expeditions.",
        "src": "§7.6 L593",
    },
    "warlock": {
        "id": "warlock",
        "desc": "A pact caster with few spell slots, but every slot refreshes "
                "on a Breather and is automatically cast at its highest tier. "
                "Eldritch Lash is reliable at will, and a Warlock grants the "
                "party one extra Breather per Camp.",
        "src": "§7.7 L629",
    },
    "bard": {
        "id": "bard",
        "desc": "A charismatic support caster and skill generalist. Bards "
                "hand out Inspiration dice, weaken enemy rolls with Cutting "
                "Words, add half proficiency to untrained skills, and later "
                "learn spells from outside their normal list.",
        "src": "§7.8 L688",
    },
    "paladin": {
        "id": "paladin",
        "desc": "A heavily armored front-liner with divine support. Paladins "
                "heal from a Lay on Hands pool, smite with radiant damage, "
                "recover Channel Divinity on Breathers, and protect allies in "
                "their lane with auras.",
        "src": "§7.9 L725",
    },
    "druid": {
        "id": "druid",
        "desc": "A nature caster with primal Aspects. Druids can fight through "
                "Bear, Hawk, Serpent, or Stag stances, cast a broad spell list, "
                "summon allies, and recover magic on Breathers. Flexible, but "
                "has many moving parts.",
        "src": "§7.10 L759",
    },
    "monk": {
        "id": "monk",
        "desc": "A fast unarmored martial artist powered by Focus Points. "
                "Monks strike with Dexterity, spend Focus on Flurry, defense, "
                "or movement, deflect weapon blows, and dart between lanes "
                "more freely than most classes.",
        "src": "§7.11 L813",
    },
    "sorcerer": {
        "id": "sorcerer",
        "desc": "An innate caster with fewer spells than a Wizard but more "
                "ways to shape them. Sorcery Points fuel Metamagic, slot "
                "conversion, and later dragon wings. Fragile, explosive, and "
                "best for players who want spell control.",
        "src": "§7.12 L858",
    },
}
