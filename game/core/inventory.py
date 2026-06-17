# -*- coding: utf-8 -*-
"""Inventory and equipment. ONE validation function, reused everywhere
equipping happens, and it explains itself (GDD #15.4 L1523-1528).

Pure Python: no renpy imports. Item identity is the registry id; the party
inventory is a {item_id: count} dict (no item instances exist yet)."""

from core import character as ch

WEAPON_SLOTS = ("mainhand", "offhand")
MAGIC_ONLY_SLOTS = ("head", "gloves", "feet", "cloak", "ring")


def item_kind(registry, item_id):
    if item_id in registry["weapons"]:
        return "weapon"
    if item_id == "shield":
        return "shield"
    if item_id in registry["armor"]:
        return "armor"
    if item_id in registry["consumables"]:
        return "consumable"
    # P3 item categories (data-driven; retires the old "spellbook" special
    # case -- the spellbook now lives in the key_items table, G-037).
    if item_id in registry.get("magic_items", {}):
        return "magic_item"
    if item_id in registry.get("relics", {}):
        return "relic"
    if item_id in registry.get("key_items", {}):
        return "key_item"
    return None


def weapon(registry, item_id):
    return registry["weapons"].get(item_id)


def is_two_handed(registry, item_id):
    w = weapon(registry, item_id)
    return bool(w and "two_handed" in w["properties"])


def is_light(registry, item_id):
    w = weapon(registry, item_id)
    return bool(w and "light" in w["properties"])


def weapon_proficient(registry, char, item_id):
    """Chassis weapon proficiency (#7 chassis lines; gating per GAPS G-018,
    simple/martial mapping per GAPS G-019)."""
    w = weapon(registry, item_id)
    cls = registry["classes"][char["class"]]
    prof = cls["weapons"]
    if prof["base"] == "all":
        return True
    if item_id in registry["weapon_classes"]["simple"]:
        return True
    # a chosen feature option may grant all martial weapons (Divine Order
    # Protector / Primal Order Warden, #7.3 L480 / #7.10 L765)
    if ch.granted_weapon_tier(registry, char) == "martial":
        return True
    plus = prof.get("plus_martial_with_any", [])
    return any(p in w["properties"] for p in plus)


def armor_proficient(registry, char, item_id):
    """Armor/shield proficiency by category (gating per GAPS G-018,
    categories per GAPS G-019)."""
    cls = registry["classes"][char["class"]]
    if item_id == "shield":
        return "shields" in cls["armor"]
    granted = ch.granted_armor_categories(registry, char)
    for category in ("light", "medium", "heavy"):
        if item_id in registry["armor_categories"][category]:
            # heavy armor can be granted by a feature option (Protector /
            # Warden, #7.3 L480 / #7.10 L765)
            return category in cls["armor"] or category in granted
    return False


def validate_equip(registry, char, slot, item_id):
    """THE centralized check (#15.4 L1523-1528). Returns
    {'ok', 'reason', 'confirm', 'displaces': [slots emptied]}.
    Rules: #10.2 L1182-1190 (two-handed, shield, both-Light dual wield),
    #10.4 L1212 (Heavy needs Strength 13), #10.5 (armor Strength gates),
    proficiency gating per GAPS G-018."""
    res = {"ok": True, "reason": None, "confirm": False, "displaces": []}

    def fail(reason):
        res["ok"] = False
        res["reason"] = reason
        return res

    kind = item_kind(registry, item_id)
    if kind is None:
        return fail("Unknown item.")
    str_score = char["abilities"]["str"]

    if slot in MAGIC_ONLY_SLOTS:
        # #10.2 L1188-1190: these five slots are magic items only, and no
        # magic items are authored yet
        return fail("This slot accepts magic equipment, but no item is available yet.")

    if slot == "armor":
        if kind != "armor" or item_id == "shield":
            return fail("Only body armor fits the armor slot.")
        rec = registry["armor"][item_id]
        if rec.get("str_req") and str_score < rec["str_req"]:
            return fail("Requires Strength %d." % rec["str_req"])
        if not armor_proficient(registry, char, item_id):
            return fail("Not proficient with this armor.")
        return res

    if slot == "mainhand":
        if kind != "weapon":
            return fail("Only weapons fit the mainhand.")
        w = weapon(registry, item_id)
        if "heavy" in w["properties"] and str_score < 13:
            return fail("Heavy weapons require Strength 13.")
        if not weapon_proficient(registry, char, item_id):
            return fail("Not proficient with this weapon.")
        if is_two_handed(registry, item_id) and char["equipment"]["offhand"]:
            # #15.4 L1524-1525: clears the offhand, with a confirmation
            res["confirm"] = True
            res["displaces"].append("offhand")
        return res

    if slot == "offhand":
        main = char["equipment"]["mainhand"]
        if main and is_two_handed(registry, main):
            return fail("The mainhand weapon needs both hands.")
        if kind == "shield":
            if not armor_proficient(registry, char, "shield"):
                return fail("Not proficient with shields.")
            return res
        if kind == "weapon":
            # #10.2 L1183-1185: only when BOTH weapons are Light
            if "heavy" in weapon(registry, item_id)["properties"] and \
                    str_score < 13:
                return fail("Heavy weapons require Strength 13.")
            if not weapon_proficient(registry, char, item_id):
                return fail("Not proficient with this weapon.")
            if not is_light(registry, item_id):
                return fail("Offhand weapons must be Light.")
            if not main:
                return fail("Equip a Light mainhand weapon first.")
            if not is_light(registry, main):
                return fail("Both weapons must be Light to dual-wield.")
            return res
        return fail("Only a weapon or shield fits the offhand.")

    return fail("Nothing equips to that slot.")


def equip(registry, char, slot, item_id, inventory):
    """Equip from the party inventory; displaced items return to it.
    Call validate_equip first; this re-checks and raises on violation."""
    res = validate_equip(registry, char, slot, item_id)
    if not res["ok"]:
        raise ValueError(res["reason"])
    if inventory.get(item_id, 0) < 1:
        raise ValueError("Not in inventory.")
    inventory[item_id] -= 1
    if inventory[item_id] == 0:
        del inventory[item_id]
    for displaced_slot in res["displaces"]:
        unequip(registry, char, displaced_slot, inventory)
    if char["equipment"][slot]:
        unequip(registry, char, slot, inventory)
    char["equipment"][slot] = item_id
    return res


def unequip(registry, char, slot, inventory):
    item_id = char["equipment"][slot]
    if item_id:
        inventory[item_id] = inventory.get(item_id, 0) + 1
        char["equipment"][slot] = None
    return item_id


def equip_delta(registry, char, slot, item_id):
    """The simple delta shown on equip ('AC +1', 'd8 -> d10');
    #15.4 L1522-1523."""
    if not validate_equip(registry, char, slot, item_id)["ok"]:
        return ""
    if slot == "armor" or item_id == "shield":
        before = ch.ac(registry, char)
        old_slot, char["equipment"][slot] = char["equipment"][slot], item_id
        after = ch.ac(registry, char)
        char["equipment"][slot] = old_slot
        diff = after - before
        return "AC %+d" % diff if diff else "AC unchanged"
    if slot in WEAPON_SLOTS:
        old = char["equipment"][slot]
        new_dice = weapon(registry, item_id)["dice"]
        if old and old != "shield" and weapon(registry, old):
            return "%s -> %s" % (weapon(registry, old)["dice"], new_dice)
        return new_dice
    return ""


def auto_equip_starting_kit(registry, char, inventory):
    """#10.6: armor to the armor slot, shield to offhand, first weapon to
    mainhand; the rest goes to the shared inventory (DECISIONS D-020)."""
    kit = registry["starting_equipment"][char["class"]]
    for item_id in kit["items"]:
        inventory[item_id] = inventory.get(item_id, 0) + 1
    for item_id in kit["items"]:
        kind = item_kind(registry, item_id)
        if kind == "armor" and not char["equipment"]["armor"]:
            equip(registry, char, "armor", item_id, inventory)
        elif kind == "shield" and not char["equipment"]["offhand"]:
            equip(registry, char, "offhand", item_id, inventory)
        elif kind == "weapon" and not char["equipment"]["mainhand"]:
            if validate_equip(registry, char, "mainhand", item_id)["ok"]:
                equip(registry, char, "mainhand", item_id, inventory)
    # every character starts with 1 Healing Potion (#10.6 L1258-1259)
    for item_id in registry["starting_common"]["per_character_items"]:
        inventory[item_id] = inventory.get(item_id, 0) + 1


def use_consumable(registry, item_id, target_char, dice_roller):
    """Drink/administer a potion (#14.4). The Healing / True Healing type
    gate is enforced here -- the same gate the spell pipeline uses
    (#5.5 L295-297, #9.1 L968-970): only True Healing touches the Downed.
    dice_roller: callable(notation) -> int (core.dice.roll in production).
    Returns {'healed': n} or raises ValueError."""
    item = registry["consumables"][item_id]
    downed = "downed" in target_char["conditions"]
    if downed and item["heal_type"] != "true_healing":
        raise ValueError("Healing cannot revive a Downed character — "
                         "only True Healing can.")
    amount = dice_roller(item["heal"]["dice"])
    if downed:
        target_char["conditions"].remove("downed")
        target_char["hp"] = min(amount, target_char["hp_max"])
    else:
        target_char["hp"] = min(target_char["hp"] + amount,
                                target_char["hp_max"])
    return {"healed": amount}
