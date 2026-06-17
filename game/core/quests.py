# -*- coding: utf-8 -*-
"""Quest state machine (GDD #15.5 L1555-1563). Pure Python; no renpy.

A quest's STATIC definition (category, title, giver, location, ordered
objectives, rewards) lives in registry["quests"]; its RUNTIME progress
lives in state["quests"][quest_id]:

  {"status": "active" | "completed" | "failed",   # #15.5 L1559
   "current_objective_index": int,
   "completed_objectives": [objective_id, ...],
   "flags": {}}

Concluded quests (completed/failed) disappear from the active view
entirely (#15.5 L1559-1561), so the mandatory "Quest completed/failed"
toast is the ONLY end-of-quest signal -- but the toast itself is the .rpy
layer's job; this module only flips state.

Rollback note (GDD #16.1): callers must renpy.block_rollback() after any
mutation here (start/advance/conclude) so the player cannot un-progress a
quest via rollback. This module never imports or calls renpy.

All readers use state.get("quests", {}) for old-save safety (#16.4)."""


def _quests(state):
    return state.setdefault("quests", {})


def is_active(state, quest_id):
    """True iff this quest exists and its status is 'active' (#15.5 L1559)."""
    rec = state.get("quests", {}).get(quest_id)
    return bool(rec) and rec.get("status") == "active"


def start_quest(registry, state, quest_id):
    """Begin a quest: create its runtime record at the first objective
    (#15.5 L1556-1558). Raises ValueError on an unknown id or one already
    started (no restart -- concluded quests stay concluded, #15.5 L1559)."""
    if quest_id not in registry["quests"]:
        raise ValueError("unknown quest %s" % quest_id)
    quests = _quests(state)
    if quest_id in quests:
        raise ValueError("quest %s already started" % quest_id)
    quests[quest_id] = {
        "status": "active",
        "current_objective_index": 0,
        "completed_objectives": [],
        "flags": {},
    }
    return quests[quest_id]


def advance_objective(registry, state, quest_id):
    """Cross off the current objective and move to the next one (#15.5
    L1558: past objectives log, crossed out). The LAST objective is NOT
    advanced past -- it is closed by conclude_quest. Raises ValueError if
    the quest is not active or there is no further objective."""
    if not is_active(state, quest_id):
        raise ValueError("quest %s is not active" % quest_id)
    rec = _quests(state)[quest_id]
    objs = registry["quests"][quest_id]["objectives"]
    idx = rec["current_objective_index"]
    if idx >= len(objs) - 1:
        raise ValueError("no further objectives")
    rec["completed_objectives"].append(objs[idx]["id"])
    rec["current_objective_index"] = idx + 1
    return rec


def conclude_quest(registry, state, quest_id, outcome="completed"):
    """End a quest (#15.5 L1559-1561). outcome is 'completed' or 'failed';
    the final (current) objective is recorded as done and the status flips.
    The quest then leaves the active view -- the conclusion toast that fires
    is the .rpy layer's responsibility (#15.5 L1560-1561). Raises ValueError
    on a bad outcome or a quest that is not active."""
    if outcome not in ("completed", "failed"):
        raise ValueError("outcome must be 'completed' or 'failed'")
    if not is_active(state, quest_id):
        raise ValueError("quest %s is not active" % quest_id)
    rec = _quests(state)[quest_id]
    objs = registry["quests"][quest_id]["objectives"]
    idx = rec["current_objective_index"]
    if 0 <= idx < len(objs):
        final_id = objs[idx]["id"]
        if final_id not in rec["completed_objectives"]:
            rec["completed_objectives"].append(final_id)
    if outcome == "completed":
        # grant the authored reward (#15.5 / #14.2): gold + items into the
        # shared state. Empty/absent rewards grant nothing; the module stays
        # renpy-free, so callers block_rollback after conclude_quest.
        rewards = registry["quests"][quest_id].get("rewards")
        if rewards and (rewards.get("gold") or rewards.get("items")):
            from core import state as st
            if rewards.get("gold"):
                st.add_gold(state, rewards["gold"])
            for iid in rewards.get("items", []):
                st.add_item(state, iid)
    rec["status"] = outcome
    return rec


def active_quests(registry, state):
    """The left column of the quest tab (#15.5 L1556-1557): active quest ids
    grouped Main / Side / Companion, in registry order, EXCLUDING concluded
    quests (#15.5 L1559 -- they disappear from the tab entirely)."""
    groups = {"main": [], "side": [], "companion": []}
    runtime = state.get("quests", {})
    for quest_id, static in registry["quests"].items():
        rec = runtime.get(quest_id)
        if not rec or rec.get("status") != "active":
            continue
        category = static["category"]
        if category in groups:
            groups[category].append(quest_id)
    return groups


def quest_view(registry, state, quest_id):
    """The right pane of the quest tab (#15.5 L1557-1562): a render dict
    merging the static definition with runtime progress. current_objective
    is the bolded line shown only while active; past_objectives is the
    crossed-out log; rewards show only when authored (#15.5 L1561)."""
    static = registry["quests"][quest_id]
    rec = state.get("quests", {}).get(quest_id, {})
    status = rec.get("status")
    objs = static["objectives"]
    by_id = {o["id"]: o["text"] for o in objs}

    current = None
    if status == "active":
        idx = rec.get("current_objective_index", 0)
        if 0 <= idx < len(objs):
            current = objs[idx]["text"]

    past = [by_id.get(oid, "") for oid in rec.get("completed_objectives", [])]

    # Rewards show ONLY when the quest authored a real promise (#15.5 L1561):
    # an empty/zero reward (no gold and no items) is "no promise" -> None, so
    # the tab never renders a hollow "Reward: —" line.
    rewards = static.get("rewards")
    if not (rewards and (rewards.get("gold") or rewards.get("items"))):
        rewards = None

    return {
        "id": static["id"],
        "category": static["category"],
        "title": static["title"],
        "giver": static["giver"],
        "location": static["location"],
        "status": status,
        "current_objective": current,
        "past_objectives": past,
        "rewards": rewards,
    }
