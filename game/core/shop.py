# -*- coding: utf-8 -*-
"""Shop buy/sell logic (GDD #15.8 L1608-1612, #14.3 L1424-1428,
#14.5 L1453-1456). Pure Python: no renpy imports.

All pricing rules read the economy rule FLAGS from the registry
(REGISTRY["economy"][k]["value"]) -- the ratios, the confirm threshold, and
the "never sold" gates are DATA, never hardcoded here (CLAUDE.md DATA-vs-
GUIDANCE). The #14.5 rarity price BANDS are tuning GUIDANCE and are NOT
encoded as a table anywhere; the single source of a buy price is the item
record's own `price` field.

Rollback (GDD #16.1 L1583-1588): the .rpy layer owns block_rollback(); the
buy() and sell() docstrings note that callers must block_rollback() after
the purchase/sale resolves. Core never imports or mentions renpy.
"""

from core import state as st


def _econ(registry, key):
    """Read one economy rule flag's value (#14.5 / #14.3)."""
    return registry["economy"][key]["value"]


def _record(registry, item_id):
    """The priced/valued record for an item across the catalogues that carry
    one, or None. Order is deliberate: a single id lives in exactly one
    table, so the first hit is authoritative."""
    for table in ("consumables", "magic_items", "camp_upgrades", "relics",
                  "key_items"):
        rec = registry.get(table, {}).get(item_id)
        if rec is not None:
            return rec
    return None


def _rarity(registry, item_id):
    """The item's rarity if it carries one (relics and magic_items do),
    else None. Consumables/weapons/armor/camp upgrades have no rarity."""
    for table in ("magic_items", "relics"):
        rec = registry.get(table, {}).get(item_id)
        if rec is not None:
            return rec.get("rarity")
    return None


def buy_price(registry, item_id):
    """The buy price, sourced ONLY from the item record's `price` field
    (consumables, magic_items, camp_upgrades). Raises ValueError when the
    item carries no price (#15.8 L1608-1612)."""
    for table in ("consumables", "magic_items", "camp_upgrades"):
        rec = registry.get(table, {}).get(item_id)
        if rec is not None and "price" in rec:
            return int(rec["price"])
    raise ValueError("no buy price for %s" % item_id)


def sell_credit(registry, item_id):
    """Gold credited for selling one of this item (#14.5 L1453): relics at
    FULL listed value (sell_value * relic_sell_ratio); gear (magic_items)
    at HALF (price * gear_sell_ratio), floored. Everything else -- weapons,
    armor (no value in the registry, owner content G-040), consumables, key
    items -- is NOT sellable and returns None."""
    relic = registry.get("relics", {}).get(item_id)
    if relic is not None:
        return int(relic["sell_value"] * _econ(registry, "relic_sell_ratio"))
    gear = registry.get("magic_items", {}).get(item_id)
    if gear is not None:
        return int(gear["price"] * _econ(registry, "gear_sell_ratio"))
    return None


def can_sell(registry, item_id):
    """(ok, reason). Rejects (#14.3 L1426, #15.4 L1553):
      - key items flagged sellable False (quest items refuse to be sold);
      - Very Rare items, while economy very_rare_sold_by_vendors is False;
      - +3 items (plus_bonus >= 3), while plus_three_items_sold is False;
      - anything with no sell credit ("cannot be sold here").
    Otherwise (True, "")."""
    key_item = registry.get("key_items", {}).get(item_id)
    if key_item is not None and not key_item.get("sellable", False):
        return (False, "Quest items cannot be sold.")

    rarity = _rarity(registry, item_id)
    if rarity == "very_rare" and not _econ(registry,
                                           "very_rare_sold_by_vendors"):
        return (False, "Very Rare items are never sold.")

    gear = registry.get("magic_items", {}).get(item_id)
    if gear is not None and gear.get("plus_bonus", 0) >= 3 \
            and not _econ(registry, "plus_three_items_sold"):
        return (False, "+3 items are never sold.")

    if sell_credit(registry, item_id) is None:
        return (False, "This cannot be sold here.")

    return (True, "")


def needs_sell_confirm(registry, item_id):
    """True when the item's rarity is at or above the economy confirm
    threshold (sell_confirm_min_rarity = "rare"), using REGISTRY["rarities"]
    for the ordering (#14.5 L1453-1454). Items without a rarity -> False."""
    rarity = _rarity(registry, item_id)
    if rarity is None:
        return False
    order = registry["rarities"]
    threshold = _econ(registry, "sell_confirm_min_rarity")
    if rarity not in order or threshold not in order:
        return False
    return order.index(rarity) >= order.index(threshold)


def stock_remaining(registry, state, shop_id, item_id):
    """Remaining stock for an item at a shop. The stock entry's count is the
    cap (None = unlimited). The running remaining persists per visit in
    state["shops"][shop_id][item_id], defaulting to the cap when untouched
    (#15.8 L1610-1611). Returns int, or None for unlimited."""
    cap = None
    for entry in registry["shops"][shop_id]["stock"]:
        if entry["item_id"] == item_id:
            cap = entry.get("count")
            break
    if cap is None:
        return None
    return state.get("shops", {}).get(shop_id, {}).get(item_id, cap)


def shop_listing(registry, state, shop_id):
    """A render-ready row per stock entry: {item_id, record, price,
    remaining, sold_out}. remaining None => unlimited => never sold_out
    (#15.8 L1608-1612)."""
    rows = []
    for entry in registry["shops"][shop_id]["stock"]:
        item_id = entry["item_id"]
        # tolerate a mis-authored stock entry with no buy price (relics and
        # key items carry no `price`): skip it rather than let ValueError
        # escape and break the whole shop render.
        try:
            price = buy_price(registry, item_id)
        except ValueError:
            continue
        remaining = stock_remaining(registry, state, shop_id, item_id)
        rows.append({
            "item_id": item_id,
            "record": _record(registry, item_id),
            "price": price,
            "remaining": remaining,
            "sold_out": remaining == 0,
        })
    return rows


def buy(registry, state, shop_id, item_id):
    """Purchase one unit from a shop's stock (#15.8 L1608-1612). Validates
    the item is stocked and not sold out, charges buy_price via spend_gold
    (which raises on insufficient gold), grants the item, and decrements a
    limited stock entry (initialising state["shops"] from the cap on the
    first buy). Returns the price paid. Raises ValueError on out-of-stock.

    Caller must block_rollback() after this resolves (#16.1 L1583-1588)."""
    cap = None
    stocked = False
    for entry in registry["shops"][shop_id]["stock"]:
        if entry["item_id"] == item_id:
            stocked = True
            cap = entry.get("count")
            break
    if not stocked:
        raise ValueError("%s is not stocked here" % item_id)

    remaining = stock_remaining(registry, state, shop_id, item_id)
    if remaining == 0:
        raise ValueError("%s is sold out" % item_id)

    price = buy_price(registry, item_id)
    st.spend_gold(state, price)        # raises 'not enough gold'
    st.add_item(state, item_id)

    if cap is not None:
        shops = state.setdefault("shops", {})
        shop = shops.setdefault(shop_id, {})
        shop[item_id] = shop.get(item_id, cap) - 1

    return price


def sell(registry, state, item_id, count=1):
    """Sell `count` of an owned item back to the vendor (#14.5 L1453).
    Enforces can_sell (raising its reason when blocked), removes the items
    from inventory (remove_item raises if not owned), then credits
    sell_credit * count via add_gold. Returns the gold credited.

    No buyback is recorded (economy buyback False) and there is no Sell-All
    path (economy sell_all_button False) -- neither is implemented here.

    Caller must block_rollback() after this resolves (#16.1 L1583-1588)."""
    ok, reason = can_sell(registry, item_id)
    if not ok:
        raise ValueError(reason)
    st.remove_item(state, item_id, count)   # raises if not enough owned
    credit = sell_credit(registry, item_id) * count
    st.add_gold(state, credit)
    return credit
