# -*- coding: utf-8 -*-
"""Equipment data transcribed from GDD section 10 (slots, masteries, weapons,
armor, starting equipment, rarity bands), section 14.3 (camp upgrades), and
section 14.4 (the potion line)."""

WEAPON_PROPERTIES = {
    "finesse": {
        "id": "finesse",
        "name": "Finesse",
        "effect": "Use either Strength or Dexterity for attack and damage rolls, whichever is better.",
        "src": "§10.4 L1210",
    },
    "light": {
        "id": "light",
        "name": "Light",
        "effect": "Can be used in the off hand when both your mainhand and offhand weapons are Light.",
        "src": "§10.4 L1210",
    },
    "heavy": {
        "id": "heavy",
        "name": "Heavy",
        "effect": "Requires Strength 13 to equip. This applies to heavy bows as well as melee weapons.",
        "str_req": 13,
        "src": "§10.4 L1211",
    },
    "two_handed": {
        "id": "two_handed",
        "name": "Two-Handed",
        "effect": "Requires both hands. Equipping it clears your offhand slot.",
        "src": "§10.4 L1212, §10.2 L1182",
    },
    "thrown": {
        "id": "thrown",
        "name": "Thrown",
        "effect": "Can be used for ranged attacks.",
        "src": "§10.4 L1212",
    },
    "ranged": {
        "id": "ranged",
        "name": "Ranged",
        "effect": None,
        "src": "§10.4 L1212",
    },
}

MASTERIES = {
    "vex": {
        "id": "vex",
        "name": "Vex",
        "effect": "On hit, your next attack against the same target has advantage.",
        "src": "§10.3 L1195-1196",
    },
    "sap": {
        "id": "sap",
        "name": "Sap",
        "effect": "On hit, the target has disadvantage on its next attack.",
        "src": "§10.3 L1197",
    },
    "nick": {
        "id": "nick",
        "name": "Nick",
        "effect": "When dual-wielding Light weapons, the offhand attack is part of your Attack action instead of costing your Bonus Action.",
        "src": "§10.3 L1198-1199",
    },
    "graze": {
        "id": "graze",
        "name": "Graze",
        "effect": "On miss, still deal damage equal to the attack ability modifier.",
        "src": "§10.3 L1200",
    },
    "cleave": {
        "id": "cleave",
        "name": "Cleave",
        "effect": "Once per turn on a melee hit, attack a second enemy in the same lane. The second hit does not add your ability modifier to damage.",
        "src": "§10.3 L1201-1202",
    },
    "push": {
        "id": "push",
        "name": "Push",
        "effect": "On hit, push the target from its Frontline to its Backline.",
        "src": "§10.3 L1203",
    },
    "slow": {
        "id": "slow",
        "name": "Slow",
        "effect": "On a damaging hit, the target becomes Pinned and cannot change lanes on its next turn.",
        "src": "§10.3 L1204-1205",
    },
    "topple": {
        "id": "topple",
        "name": "Topple",
        "effect": "On hit, the target makes a Constitution save against DC 8 + your attack ability modifier + proficiency. On failure, it becomes Staggered.",
        "src": "§10.3 L1206-1207",
    },
}

WEAPONS = {
    "dagger": {
        "id": "dagger",
        "name": "Dagger",
        "price": 2,                      # D&D 5.2 SRD
        "dice": "1d4",
        "damage_type": "piercing",
        "properties": ["finesse", "light", "thrown"],
        "mastery": "nick",
        "src": "§10.4 L1216",
    },
    "mace": {
        "id": "mace",
        "name": "Mace",
        "price": 5,                      # D&D 5.2 SRD
        "dice": "1d6",
        "damage_type": "bludgeoning",
        "properties": [],
        "mastery": "sap",
        "src": "§10.4 L1217",
    },
    "quarterstaff": {
        "id": "quarterstaff",
        "name": "Quarterstaff",
        "price": 1,                      # SRD 2 sp, rounded up (gold-only economy)
        "dice": "1d8",
        "damage_type": "bludgeoning",
        "properties": ["two_handed"],
        "mastery": "topple",
        "src": "§10.4 L1218",
    },
    "spear": {
        "id": "spear",
        "name": "Spear",
        "price": 1,                      # D&D 5.2 SRD
        "dice": "1d6",
        "damage_type": "piercing",
        "properties": ["thrown"],
        "mastery": "sap",
        "src": "§10.4 L1219",
    },
    "handaxe": {
        "id": "handaxe",
        "name": "Handaxe",
        "price": 5,                      # D&D 5.2 SRD
        "dice": "1d6",
        "damage_type": "slashing",
        "properties": ["light", "thrown"],
        "mastery": "vex",
        "src": "§10.4 L1220",
    },
    "sickle": {
        "id": "sickle",
        "name": "Sickle",
        "price": 1,                      # D&D 5.2 SRD
        "dice": "1d4",
        "damage_type": "slashing",
        "properties": ["light"],
        "mastery": "nick",
        "src": "§10.4 L1221",
    },
    "shortbow": {
        "id": "shortbow",
        "name": "Shortbow",
        "price": 25,                     # D&D 5.2 SRD
        "dice": "1d6",
        "damage_type": "piercing",
        "properties": ["ranged", "two_handed"],
        "mastery": "vex",
        "src": "§10.4 L1222",
    },
    "sling": {
        "id": "sling",
        "name": "Sling",
        "price": 1,                      # SRD 1 sp, rounded up (gold-only economy)
        "dice": "1d4",
        "damage_type": "bludgeoning",
        "properties": ["ranged"],
        "mastery": "slow",
        "src": "§10.4 L1223",
    },
    "shortsword": {
        "id": "shortsword",
        "name": "Shortsword",
        "dice": "1d6",
        "damage_type": "piercing",
        "properties": ["finesse", "light"],
        "mastery": "vex",
        "src": "§10.4 L1224",
    },
    "scimitar": {
        "id": "scimitar",
        "name": "Scimitar",
        "dice": "1d6",
        "damage_type": "slashing",
        "properties": ["finesse", "light"],
        "mastery": "nick",
        "src": "§10.4 L1225",
    },
    "rapier": {
        "id": "rapier",
        "name": "Rapier",
        "dice": "1d8",
        "damage_type": "piercing",
        "properties": ["finesse"],
        "mastery": "vex",
        "src": "§10.4 L1226",
    },
    "longsword": {
        "id": "longsword",
        "name": "Longsword",
        "dice": "1d8",
        "damage_type": "slashing",
        "properties": [],
        "mastery": "sap",
        "src": "§10.4 L1227",
    },
    "battleaxe": {
        "id": "battleaxe",
        "name": "Battleaxe",
        "dice": "1d8",
        "damage_type": "slashing",
        "properties": [],
        "mastery": "topple",
        "src": "§10.4 L1228",
    },
    "warhammer": {
        "id": "warhammer",
        "name": "Warhammer",
        "dice": "1d8",
        "damage_type": "bludgeoning",
        "properties": [],
        "mastery": "push",
        "src": "§10.4 L1229",
    },
    "flail": {
        "id": "flail",
        "name": "Flail",
        "dice": "1d8",
        "damage_type": "bludgeoning",
        "properties": [],
        "mastery": "sap",
        "src": "§10.4 L1230",
    },
    "greatsword": {
        "id": "greatsword",
        "name": "Greatsword",
        "dice": "2d6",
        "damage_type": "slashing",
        "properties": ["heavy", "two_handed"],
        "mastery": "graze",
        "src": "§10.4 L1231",
    },
    "greataxe": {
        "id": "greataxe",
        "name": "Greataxe",
        "dice": "1d12",
        "damage_type": "slashing",
        "properties": ["heavy", "two_handed"],
        "mastery": "cleave",
        "src": "§10.4 L1232",
    },
    "maul": {
        "id": "maul",
        "name": "Maul",
        "dice": "2d6",
        "damage_type": "bludgeoning",
        "properties": ["heavy", "two_handed"],
        "mastery": "topple",
        "src": "§10.4 L1233",
    },
    "longbow": {
        "id": "longbow",
        "name": "Longbow",
        "dice": "1d8",
        "damage_type": "piercing",
        "properties": ["heavy", "ranged", "two_handed"],
        "mastery": "slow",
        "src": "§10.4 L1234",
    },
    "hand_crossbow": {
        "id": "hand_crossbow",
        "name": "Hand Crossbow",
        "dice": "1d6",
        "damage_type": "piercing",
        "properties": ["light", "ranged"],
        "mastery": "vex",
        "src": "§10.4 L1235",
    },
    "heavy_crossbow": {
        "id": "heavy_crossbow",
        "name": "Heavy Crossbow",
        "dice": "1d10",
        "damage_type": "piercing",
        "properties": ["heavy", "ranged", "two_handed"],
        "mastery": "push",
        "src": "§10.4 L1236",
    },
}

ARMOR = {
    "leather": {
        "id": "leather",
        "name": "Leather",
        "price": 10,                     # D&D 5.2 SRD
        "base_ac": 11,
        "dex_cap": None,
        "str_req": None,
        "trickery_disadvantage": False,
        "src": "§10.5 L1241",
    },
    "studded_leather": {
        "id": "studded_leather",
        "name": "Studded Leather",
        "price": 45,                     # D&D 5.2 SRD
        "base_ac": 12,
        "dex_cap": None,
        "str_req": None,
        "trickery_disadvantage": False,
        "src": "§10.5 L1242",
    },
    "chain_shirt": {
        "id": "chain_shirt",
        "name": "Chain Shirt",
        "base_ac": 13,
        "dex_cap": 2,
        "str_req": None,
        "trickery_disadvantage": False,
        "src": "§10.5 L1243",
    },
    "breastplate": {
        "id": "breastplate",
        "name": "Breastplate",
        "base_ac": 14,
        "dex_cap": 2,
        "str_req": None,
        "trickery_disadvantage": False,
        "src": "§10.5 L1244",
    },
    "half_plate": {
        "id": "half_plate",
        "name": "Half Plate",
        "base_ac": 15,
        "dex_cap": 2,
        "str_req": None,
        "trickery_disadvantage": True,
        "src": "§10.5 L1245",
    },
    "chain_mail": {
        "id": "chain_mail",
        "name": "Chain Mail",
        "base_ac": 16,
        "dex_cap": 0,
        "str_req": 13,
        "trickery_disadvantage": True,
        "src": "§10.5 L1246",
    },
    "plate": {
        "id": "plate",
        "name": "Plate",
        "base_ac": 18,
        "dex_cap": 0,
        "str_req": 15,
        "trickery_disadvantage": True,
        "src": "§10.5 L1247",
    },
    "shield": {
        "id": "shield",
        "name": "Shield",
        "ac_bonus": 2,
        "slot": "offhand",
        "src": "§10.5 L1248",
    },
}

EQUIPMENT_SLOTS = [
    {"id": "head", "magic_only": True, "src": "§10.2 L1180, §10.2 L1188-1190"},
    {"id": "armor", "magic_only": False, "src": "§10.2 L1180, §10.2 L1187"},
    {"id": "feet", "magic_only": True, "src": "§10.2 L1180, §10.2 L1188-1190"},
    {"id": "gloves", "magic_only": True, "src": "§10.2 L1180, §10.2 L1188-1190"},
    {"id": "ring", "magic_only": True, "src": "§10.2 L1180, §10.2 L1188-1190"},
    {"id": "mainhand", "magic_only": False, "src": "§10.2 L1180"},
    {"id": "offhand", "magic_only": False, "src": "§10.2 L1181"},
    {"id": "cloak", "magic_only": True, "src": "§10.2 L1181, §10.2 L1188-1190"},
]

RARITIES = ["common", "uncommon", "rare", "very_rare"]

STARTING_EQUIPMENT = {
    "fighter": {
        "items": ["chain_mail", "longsword", "shield"],
        "src": "§10.6 L1251",
    },
    "barbarian": {
        "items": ["chain_shirt", "greataxe"],
        "src": "§10.6 L1251-1252",
    },
    "rogue": {
        "items": ["leather", "rapier"],
        "src": "§10.6 L1252",
    },
    "monk": {
        "items": ["quarterstaff"],
        "src": "§10.6 L1252-1253",
    },
    "ranger": {
        "items": ["studded_leather", "longbow"],
        "src": "§10.6 L1253",
    },
    "paladin": {
        "items": ["chain_mail", "longsword", "shield"],
        "src": "§10.6 L1254",
    },
    "cleric": {
        "items": ["chain_shirt", "mace", "shield"],
        "src": "§10.6 L1254",
    },
    "druid": {
        "items": ["leather", "quarterstaff"],
        "src": "§10.6 L1255",
    },
    "wizard": {
        "items": ["quarterstaff", "spellbook"],
        "src": "§10.6 L1255",
    },
    "sorcerer": {
        "items": ["rapier"],
        "src": "§10.6 L1256",
    },
    "warlock": {
        "items": ["leather", "rapier"],
        "src": "§10.6 L1256",
    },
    "bard": {
        "items": ["leather", "rapier"],
        "src": "§10.6 L1256-1257",
    },
}

STARTING_COMMON = {
    "per_character_items": ["healing_potion"],
    "party_gold": 50,
    "src": "§10.6 L1258-1259",
}

CONSUMABLES = {
    "healing_potion": {
        "id": "healing_potion",
        "name": "Healing Potion",
        "price": 50,
        "heal": {"dice": "2d8"},
        "heal_type": "healing",
        "stock_limited": False,
        "effect": "Restore 2d8 HP to a living target. Cannot revive a Downed character.",
        "src": "§14.4 L1444",
    },
    "greater_healing_potion": {
        "id": "greater_healing_potion",
        "name": "Greater Healing Potion",
        "price": 250,
        "heal": {"dice": "4d8"},
        "heal_type": "healing",
        "stock_limited": False,
        "effect": "Restore 4d8 HP to a living target. Cannot revive a Downed character.",
        "src": "§14.4 L1445",
    },
    "superior_healing_potion": {
        "id": "superior_healing_potion",
        "name": "Superior Healing Potion",
        "price": 600,
        "heal": {"dice": "6d8"},
        "heal_type": "healing",
        "stock_limited": False,
        "effect": "Restore 6d8 HP to a living target. Cannot revive a Downed character.",
        "src": "§14.4 L1446",
    },
    "phoenix_draught": {
        "id": "phoenix_draught",
        "name": "Phoenix Draught",
        "price": 400,
        "heal": {"dice": "3d8"},
        "heal_type": "true_healing",
        "stock_limited": True,
        "effect": "True Healing. Revive a Downed ally and restore 3d8 HP. This is the only consumable that can revive.",
        "src": "§14.4 L1447",
    },
}

CAMP_UPGRADES = {
    "provisioners_pack_frame": {
        "id": "provisioners_pack_frame",
        "name": "Provisioner's Pack-Frame",
        "price": 300,
        "effect": "Increase Supply Cache capacity by 1.",
        "src": "§14.3 L1430",
    },
    "fieldwrights_tent": {
        "id": "fieldwrights_tent",
        "name": "Fieldwright's Tent",
        "price": 400,
        "recovery_dice_bonus": 2,        # engine value (#14.3 L1431)
        "effect": "Each party member gains 2 additional Recovery Dice per Camp.",
        "src": "§14.3 L1431",
    },
    "cooks_kit": {
        "id": "cooks_kit",
        "name": "Cook's Kit",
        "price": 250,
        "effect": "When a Camp hunting check succeeds, each party member also heals HP equal to their own level.",
        "src": "§14.3 L1432",
    },
}

# Weapon and armor categories, canonical per owner adjudication, P1
# (G-019); the #10.4/#10.5 tables now carry matching Category columns.
WEAPON_CLASSES = {
    "simple": ["dagger", "mace", "quarterstaff", "spear", "handaxe",
               "sickle", "shortbow", "sling"],
    "martial": ["shortsword", "scimitar", "rapier", "longsword", "battleaxe",
                "warhammer", "flail", "greatsword", "greataxe", "maul",
                "longbow", "hand_crossbow", "heavy_crossbow"],
    "src": "§10.4 L1214-1242",
}

ARMOR_CATEGORIES = {
    "light": ["leather", "studded_leather"],
    "medium": ["chain_shirt", "breastplate", "half_plate"],
    "heavy": ["chain_mail", "plate"],
    "src": "§10.5 L1238-1248",
}
