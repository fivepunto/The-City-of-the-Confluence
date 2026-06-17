# -*- coding: utf-8 -*-
"""Global game state (GDD #16.4 L1676-1677): active party (4), follower
pool, shared inventory, gold, supplies, day phase, region, quests,
relationships.

Pure Python; Ren'Py owns the single instance in its store (so saves and
rollback see it) and calls these helpers.

Runtime sub-schemas (the GDD names these fields but specifies only their
DISPLAY, not their save shape -- conservative defaults, GAPS G-034/G-035):
  state["quests"][quest_id] = {
      "status": "active" | "completed" | "failed",   # #15.5 L1559
      "current_objective_index": int,
      "completed_objectives": [objective_id, ...],
      "flags": {},
  }
  Concluded quests (completed/failed) leave the active view; the conclusion
  toast is the only end-of-quest signal (#15.5 L1559-1561).
  state["relationships"][npc_id] = int   # signed standing; no tiers exist
      in the GDD yet, so the raw value is surfaced and NOTHING is inferred.
  state["region"]   = district id | None  (current district, city map #13.2)
  state["breach_region"] = Breach region id | None  (current expedition
      region; drives the hunt difficulty, #12.2 L1346-1347 / #13.2)
  state["location"] = location/hotspot id | None (current sub-location,
      #13 L1399-1400)
  state["shops"][shop_id] = {item_id: remaining_count} -- per-shop stock
      decremented on purchase so "X in stock"/sold-out persists per visit
      (#15.8 L1610-1611). Only stock-limited items appear here.
All readers of the newer keys use state.get(key, default) so saves made
before these keys existed still load (no migration layer)."""


SAVE_VERSION = 1   # bump when a save-shape migration is added (see migrate_state)


def new_game_state(registry):
    return {
        "save_version": SAVE_VERSION,
        "party": [],            # up to 4 character dicts; [0] is the MC
        "follower_pool": [],    # benched followers (P5 recruits them)
        "inventory": {},        # {item_id: count} -- shared (#10.2 L1179)
        "gold": registry["starting_common"]["party_gold"],  # #10.6 L1259
        "supplies": 0,
        "day_phase": "morning",  # #12.3 L1354-1359
        "region": None,         # current district id (#13.2 L1396-1398)
        "breach_region": None,  # current Breach region id in the expedition (#12.2/#13.2)
        "location": None,       # current sub-location id (#13 L1399-1400)
        "quests": {},
        "relationships": {},
        "shops": {},            # {shop_id: {item_id: remaining}} (#15.8)
        # P4 camp & expedition (#12 / #13). Breather/Supply CAPACITIES are
        # derived on read (Warlock presence / Pack-Frame ownership), not here.
        "breathers": 0,         # Breathers used since the last Camp (#12.1)
        "camp_upgrades": [],    # owned upgrade ids (#14.3); flags, not counts
        "expedition_node": None,  # current node in the Breach (#13.2)
        "in_expedition": False,   # True while in the Breach (HUD mode)
        "flags": {},
    }


def migrate_state(state):
    """After-load save migration seam (called from the after_load label).
    Backfills keys added after a save was made and stamps the current
    SAVE_VERSION. Existing readers already use state.get(key, default), so
    this is currently a no-op stamp; add per-version backfills here as the
    schema evolves."""
    if state is None:
        return state
    # version = state.get("save_version", 0)
    # (future) if version < N: ...backfill the keys added in version N...
    state["save_version"] = SAVE_VERSION
    return state


def party_member(state, char_id):
    for char in state["party"]:
        if char["id"] == char_id:
            return char
    return None


def add_to_party(state, char):
    if len(state["party"]) >= 4:
        raise ValueError("the active party is four members")
    state["party"].append(char)


def add_item(state, item_id, count=1):
    state["inventory"][item_id] = state["inventory"].get(item_id, 0) + count


def remove_item(state, item_id, count=1):
    have = state["inventory"].get(item_id, 0)
    if have < count:
        raise ValueError("not enough %s" % item_id)
    if have == count:
        del state["inventory"][item_id]
    else:
        state["inventory"][item_id] = have - count


def spend_gold(state, amount):
    if state["gold"] < amount:
        raise ValueError("not enough gold")
    state["gold"] -= amount


def add_gold(state, amount):
    """Credit gold: sells (#14.5 L1454), quest rewards (#14.2 L1419),
    and loot grants. Mirror of spend_gold so all gold flows one way."""
    if amount < 0:
        raise ValueError("add_gold takes a non-negative amount")
    state["gold"] += amount


def set_day_phase(state, phase):
    """morning | afternoon | evening (#12.3 L1354-1359). The clamp/advance
    rules of the day clock are P4; this is the thin setter the HUD and the
    debug hub write through."""
    state["day_phase"] = phase


def set_region(state, region_id):
    """Current district (#13.2). Entering a district from the city map."""
    state["region"] = region_id


def set_breach_region(state, region_id):
    """Current Breach region (#13.2). Entering / inside the expedition; the
    hunt difficulty is read from this region (#12.2 L1346-1347)."""
    state["breach_region"] = region_id


def set_location(state, location_id):
    """Current sub-location within a district (#13 L1399-1400)."""
    state["location"] = location_id


def add_supplies(state, count=1, cap=None):
    """Gain Supply Caches (#12.2 L1342-1344, #14.2). Hard-blocks above the
    carry capacity -- the caller passes the DERIVED cap (rest.supply_capacity:
    3, or 4 with the Pack-Frame); capacity is never stored."""
    if count < 0:
        raise ValueError("add_supplies takes a non-negative count")
    new_total = state.get("supplies", 0) + count
    if cap is not None and new_total > cap:
        raise ValueError("supply caches full")
    state["supplies"] = new_total


def spend_supplies(state, count=1):
    """Consume Supply Caches (a wilds Camp burns 1, #12.2 L1342)."""
    if state.get("supplies", 0) < count:
        raise ValueError("not enough supplies")
    state["supplies"] -= count
