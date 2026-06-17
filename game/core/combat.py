# -*- coding: utf-8 -*-
"""The combat engine (GDD #5). Pure Python; the Ren'Py combat screen loop
reads and writes the combat state dict this module builds (CLAUDE.md).

Core shape: ONE initiative-sorted list of all combatants, both sides
interleaved -- never two team arrays (#5.1 L210-213). All randomness goes
through core.dice (seedable). Reaction prompts route through an ask_fn
callable supplied by the UI (#5.2 L236-239); headless tests script it.
"""

import copy

from core import dice, rules
from core import registry as reg
from core import character as ch

LANES = ("front", "back")

# #16.2 L1611-1619: the event vocabulary, verbatim.
EVENTS = (
    "combat_start", "round_start", "turn_start", "turn_end",
    "initiative_rolled", "attack_declared", "attack_roll", "attack_hit",
    "attack_miss", "crit", "damage_dealt", "damage_taken", "hp_zero",
    "downed", "revived", "save_prompted", "save_rolled", "save_failed",
    "save_passed", "cast_declared", "cast_resolved",
    "line_change_declared", "line_changed", "condition_applied",
    "condition_removed", "heal", "enemy_killed", "ally_targeted_in_line",
    "breather", "camp_sleep",
)


# ---------------------------------------------------------------------------
# construction

def _pc_combatant(registry, char, lane):
    return {
        "cid": "pc_" + char["id"],
        "side": "party",
        "kind": "pc",
        "name": char["name"],
        "char": char,
        "stats": None,
        "lane": lane,
        "hp": char["hp"],
        "hp_max": char["hp_max"],
        "temp_hp": char.get("temp_hp", 0),
        "conditions": {},
        "acted": {"action": False, "bonus": False, "reaction": False},
        "downed": False,
        "dead": False,
        "concentration": None,
        "revived_round": None,
        "flags": {},
    }


def _enemy_combatant(registry, enemy_id, n):
    rec = registry["enemies"][enemy_id]
    # statblocks speak "frontline"/"backline" (#11.1); the engine's lane
    # ids are "front"/"back"
    lane = {"frontline": "front", "backline": "back"}.get(
        rec.get("lane_preference") or "front", "front")
    return {
        "cid": "en_%s_%d" % (enemy_id, n),
        "side": "enemy",
        "kind": "enemy",
        "name": rec["name"] if n == 1 else "%s %d" % (rec["name"], n),
        "char": None,
        "stats": copy.deepcopy(rec),
        "lane": lane,
        "hp": rec["hp"],
        "hp_max": rec["hp"],
        "temp_hp": 0,
        "conditions": {},
        "acted": {"action": False, "bonus": False, "reaction": False},
        "downed": False,
        "dead": False,
        "concentration": None,
        "revived_round": None,
        "intent_state": {"cooldowns": {}},
        "telegraph": None,
        "flags": {},
    }


def build_combat(registry, party, enemy_ids, flee_allowed=False,
                 party_lanes=None):
    """party: the active party char dicts (the player controls every member,
    #5.1 L204-205). enemy_ids: registry enemy ids (duplicates allowed).
    Party members start in their Frontline by default; an encounter may pass
    party_lanes = {char_id: "front"|"back"} to author per-member starting
    lanes (a split party, or a Backline ambush) -- owner adjudication, P2
    (#5.4). Enemies start per their statblock lane preference."""
    party_lanes = party_lanes or {}
    combat = {
        "combatants": {},
        "order": [],
        "turn": 0,
        "round": 1,
        "log": [],
        "floats": [],
        "over": None,
        "flee_allowed": flee_allowed,
        # ongoing spell effects (#9.5/#9.6 buff/debuff rows): entries
        # {id, spell, source, kind, lane, side, target, data} consulted
        # by the hooks effects layer at the pipeline ctx points
        "effects": [],
        "effect_seq": 0,
    }
    for char in party:
        lane = party_lanes.get(char["id"], "front")
        c = _pc_combatant(registry, char, lane)
        combat["combatants"][c["cid"]] = c
    counts = {}
    for enemy_id in enemy_ids:
        counts[enemy_id] = counts.get(enemy_id, 0) + 1
        c = _enemy_combatant(registry, enemy_id, counts[enemy_id])
        combat["combatants"][c["cid"]] = c
    _roll_initiative(registry, combat)
    return combat


def _initiative_mod(registry, c):
    if c["kind"] == "pc":
        return ch.initiative_mod(c["char"])
    return c["stats"]["initiative_bonus"]


def _roll_initiative(registry, combat):
    """1d20 + Dex mod, once, fixed for the whole fight. Ties: higher Dex
    modifier wins; still tied, a coin flip (#5.1 L206-209)."""
    rolls = {}
    for cid, c in combat["combatants"].items():
        mod = _initiative_mod(registry, c)
        roll = dice.d(20) + mod
        # tie-break (#5.1 L206-209): higher Dex mod, then a distinct random
        # key so equal (roll, dex) combatants get a decisive, unbiased order
        # instead of a shared 1-or-2 coin that ties ~50% and otherwise falls
        # back to insertion order.
        tiebreak = dice.d(1 << 30)
        rolls[cid] = (roll, _dex_mod(c), tiebreak)
        c["initiative"] = roll
    combat["order"] = sorted(rolls, key=lambda cid: rolls[cid], reverse=True)
    fire(registry, combat, "initiative_rolled", {"order": list(combat["order"])})
    log(combat, "Initiative: " + ", ".join(
        "%s %d" % (combat["combatants"][cid]["name"],
                   combat["combatants"][cid]["initiative"])
        for cid in combat["order"]))


def _dex_mod(c):
    if c["kind"] == "pc":
        return ch.ability_mod(c["char"], "dex")
    return rules.ability_modifier(c["stats"]["abilities"]["dex"])


def _ability_mod(c, ability):
    if c["kind"] == "pc":
        return ch.ability_mod(c["char"], ability)
    return rules.ability_modifier(c["stats"]["abilities"][ability])


# ---------------------------------------------------------------------------
# logging / event pipeline

def log(combat, text):
    combat["log"].append(text)


def float_text(combat, cid, text, kind="info"):
    """Floating combat text events; the screen drains this list (#15.6)."""
    combat["floats"].append({"cid": cid, "text": text, "kind": kind})


def fire(registry, combat, event, ctx):
    """Fire one pipeline event (#16.2): collect hooks, sort by priority,
    apply. Hooks may mutate ctx. Reaction-costed hooks respect the
    one-Reaction-per-round rule and the ask/always/never prompt setting."""
    assert event in EVENTS, event
    from core import hooks as hk
    ctx = dict(ctx)
    ctx["event"] = event
    # ongoing spell effects read/modify the same ctx points (#16.2)
    hk.effects_on_event(registry, combat, event, ctx)
    for hook, owner in hk.hooks_for(registry, combat, event):
        if combat["over"]:
            break
        if not hk.check_condition(registry, combat, hook, owner, ctx):
            continue
        if hook.get("cost") == "reaction":
            if owner["acted"]["reaction"] or not _can_react(owner):
                continue
            if not _prompt_allows(registry, combat, hook, owner, ctx):
                continue
            owner["acted"]["reaction"] = True
        hk.run_effect(registry, combat, hook, owner, ctx)
    return ctx


def _can_react(c):
    """Downed, dead, and act-blocking conditions forbid reactions; Tripped
    explicitly keeps them (#5.7 L330-331)."""
    if c["downed"] or c["dead"]:
        return False
    for cond in ("asleep", "paralyzed", "stunned", "turned"):
        if cond in c["conditions"]:
            return False
    if "addled" in c["flags"]:
        return False
    return True


def _prompt_allows(registry, combat, hook, owner, ctx):
    """ask/always/never per #5.2 L236-241. PCs may override per ability via
    reaction_preferences; 'ask' routes through the UI ask_fn (False when
    headless and unscripted)."""
    mode = hook.get("prompt", "always")
    if owner["kind"] == "pc":
        mode = owner["char"]["reaction_preferences"].get(
            hook.get("ability_id", ""), mode)
    if mode == "never":
        return False
    if mode == "always":
        return True
    if _ASK_FN[0] is None:
        return False
    return bool(_ASK_FN[0](_prompt_card(registry, combat, hook, owner, ctx)))


def _prompt_card(registry, combat, hook, owner, ctx):
    return {
        "owner": owner["cid"],
        "ability_id": hook.get("ability_id", ""),
        "title": hook.get("title", hook.get("ability_id", "Reaction")),
        "trigger": ctx.get("event"),
        "cost": hook.get("cost_text", "Reaction"),
        "ctx": ctx,
    }


# ---------------------------------------------------------------------------
# predicates -- targeting, lanes, status

def standing(c):
    return not (c["downed"] or c["dead"])


def combatants_on(combat, side, lane=None, alive_only=True):
    out = []
    for cid in combat["order"]:
        c = combat["combatants"][cid]
        if c["side"] != side:
            continue
        if alive_only and not standing(c):
            continue
        if lane and c["lane"] != lane:
            continue
        out.append(c)
    return out


def frontline_empty(combat, side):
    """Recomputed continuously: the moment a Frontline empties mid-fight,
    melee reaches the Backline (#5.4 L268-271)."""
    return not combatants_on(combat, side, "front")


def melee_reach(combat, attacker, target):
    """THE one predicate every 'in melee reach' feature uses (#5.4
    L285-287): could the attacker legally melee the target right now?"""
    if attacker["side"] == target["side"]:
        return False
    if not standing(attacker) or not standing(target):
        return False
    if attacker["lane"] != "front":
        return False        # melee cannot attack from the Backline (L272)
    if target["lane"] == "front":
        return True
    return frontline_empty(combat, target["side"])   # exposed Backline


def targetable(combat, attacker, target, melee):
    """Returns (ok, reason). Reasons feed the greyed-out hover text
    (#15.6 L1555-1558)."""
    if target["dead"]:
        return False, "Already down."
    if target["downed"]:
        return False, "Downed — untargetable."       # #5.5 L295-296
    if "hidden" in target["conditions"]:
        return False, "Hidden — cannot be single-targeted."   # #5.6 L317
    if melee and not melee_reach(combat, attacker, target):
        if attacker["lane"] != "front":
            return False, "Melee attacks cannot be made from the Backline."
        return False, "Cannot reach targets behind the Frontline."
    return True, None


def melee_capable(registry, c):
    """Has a melee attack available (used for opportunity attacks)."""
    if not standing(c):
        return False
    if c["kind"] == "pc":
        weapon = c["char"]["equipment"]["mainhand"]
        if weapon:
            w = registry["weapons"][weapon]
            return "ranged" not in w["properties"]
        return True   # unarmed strike
    return bool(c["stats"]["attacks"]) and \
        not c["stats"].get("ranged_only", False)


def can_act(c):
    """Condition gate on taking a turn (#5.6)."""
    if c["downed"] or c["dead"]:
        return False
    for cond in ("asleep", "paralyzed", "stunned", "turned"):
        if cond in c["conditions"]:
            return False
    return True


# ---------------------------------------------------------------------------
# the turn loop

def current(combat):
    return combat["combatants"][combat["order"][combat["turn"]]]


# The reaction-prompt asker is module state, NOT part of the combat dict:
# the combat state must stay save/pickle-clean. The UI label re-sets it
# every loop iteration; headless tests pass it to begin().
_ASK_FN = [None]


def set_ask_fn(fn):
    _ASK_FN[0] = fn


def begin(registry, combat, ask_fn=None):
    set_ask_fn(ask_fn)
    fire(registry, combat, "combat_start", {})
    fire(registry, combat, "round_start", {"round": 1})
    _start_turn(registry, combat)


def _start_turn(registry, combat):
    actor = current(combat)
    if not standing(actor) or _skips_turn(combat, actor):
        return advance_turn(registry, combat)
    actor["acted"]["action"] = False
    actor["acted"]["bonus"] = False
    # Reaction refreshes per ROUND (#5.2 L232) -- at the owner's turn start
    actor["acted"]["reaction"] = False
    # turn-scoped self-flags expire at the owner's next turn start
    # (attack_action_taken gates the Martial Arts Bonus-Action unarmed
    # strike, #7.11 L819)
    for flag in ("free_moves_used", "reckless_open", "patient_defense",
                 "surge_extra", "attack_action_taken",
                 "attack_action_remaining"):
        actor["flags"].pop(flag, None)
    tick_source_turn_start(registry, combat, actor)
    ctx = fire(registry, combat, "turn_start", {"actor": actor["cid"]})
    # Tripped: the Action is consumed standing up; standing in the
    # Frontline provokes (#5.7 L332-335)
    if "tripped" in actor["conditions"]:
        _stand_up(registry, combat, actor)
    _tick_conditions(registry, combat, actor, "turn_start")
    return ctx


def _skips_turn(combat, actor):
    """Revived characters resume acting on their normal turn the round
    AFTER revival (#5.5 L297-299)."""
    if actor["revived_round"] is not None and \
            actor["revived_round"] == combat["round"]:
        return True
    return False


def _stand_up(registry, combat, actor):
    actor["acted"]["action"] = True
    if actor["lane"] == "front":
        _provoke_opportunity_attacks(registry, combat, actor)
    if not standing(actor):
        return
    remove_condition(registry, combat, actor, "tripped")
    log(combat, "%s stands up." % actor["name"])


def advance_turn(registry, combat):
    if combat["over"]:
        return
    actor = current(combat)
    if standing(actor):
        _tick_conditions(registry, combat, actor, "turn_end")
        fire(registry, combat, "turn_end", {"actor": actor["cid"]})
    combat["turn"] += 1
    if combat["turn"] >= len(combat["order"]):
        combat["turn"] = 0
        combat["round"] += 1
        fire(registry, combat, "round_start", {"round": combat["round"]})
    # skip dead/downed combatants; bounded so a degenerate order (every
    # combatant non-standing without combat["over"] set) raises loudly
    # instead of recursing into a RecursionError
    scanned = 0
    while True:
        if combat["over"]:
            return
        nxt = current(combat)
        if not (nxt["dead"] or nxt["downed"]):
            break
        scanned += 1
        if scanned > len(combat["order"]):
            raise RuntimeError(
                "advance_turn: no standing combatant in the order but "
                "combat is not over (round=%s)." % combat["round"])
        combat["turn"] += 1
        if combat["turn"] >= len(combat["order"]):
            combat["turn"] = 0
            combat["round"] += 1
            fire(registry, combat, "round_start", {"round": combat["round"]})
    return _start_turn(registry, combat)


def end_turn(registry, combat):
    return advance_turn(registry, combat)


# ---------------------------------------------------------------------------
# conditions

def apply_condition(registry, combat, target, cond_id, source=None,
                    data=None):
    """Apply per the registry condition record. The Stagger->Trip ladder is
    gated here: a trip effect only works on a Staggered target (#5.7
    L326-328) -- callers attempt 'tripped' and the gate decides."""
    if cond_id == "tripped":
        if "staggered" not in target["conditions"]:
            return False
        remove_condition(registry, combat, target, "staggered")
    if cond_id == "turned" and not _is_undead(target):
        return False                                  # #5.6 L318
    if cond_id == "hidden" and target["lane"] != "back":
        return False                                  # Backline-only, L317
    target["conditions"][cond_id] = {
        "source": source["cid"] if source else None,
        "data": data or {},
    }
    fire(registry, combat, "condition_applied",
         {"target": target["cid"], "condition": cond_id,
          "source": source["cid"] if source else None})
    float_text(combat, target["cid"], cond_id.capitalize(), "condition")
    log(combat, "%s is %s." % (target["name"], cond_id.capitalize()))
    return True


def remove_condition(registry, combat, target, cond_id):
    if cond_id in target["conditions"]:
        del target["conditions"][cond_id]
        fire(registry, combat, "condition_removed",
             {"target": target["cid"], "condition": cond_id})


def _is_undead(c):
    if c["kind"] == "pc":
        return False
    return "undead" in (c["stats"].get("tags") or [])


def _tick_conditions(registry, combat, c, moment):
    """Duration & repeating-save bookkeeping at turn boundaries."""
    for cond_id in list(c["conditions"]):
        entry = c["conditions"][cond_id]
        data = entry["data"]
        until = data.get("until")
        if moment == "turn_start" and until == "target_turn_start":
            remove_condition(registry, combat, c, cond_id)
            continue
        if moment == "turn_end" and until == "target_turn_end":
            remove_condition(registry, combat, c, cond_id)
            continue
        if moment == "turn_end" and data.get("repeat_save"):
            # Paralyzed/Poisoned (and authored effects) repeat their save
            # at the end of the target's turns (#5.6 L309, L316)
            spec = data["repeat_save"]
            result = saving_throw(registry, combat, c, spec["ability"],
                                  spec["dc"])
            if result["success"]:
                remove_condition(registry, combat, c, cond_id)


def tick_source_turn_start(registry, combat, source):
    """Effects that last 'until the start of the source's next turn'
    (Staggered #5.6 L313; Gravewhisper's heal denial #9.4)."""
    for c in combat["combatants"].values():
        for cond_id in list(c["conditions"]):
            entry = c["conditions"][cond_id]
            if entry["data"].get("until") == "source_next_turn" and \
                    entry["source"] == source["cid"]:
                remove_condition(registry, combat, c, cond_id)
        if c["flags"].get("no_heal_src") == source["cid"]:
            c["flags"].pop("no_heal_src", None)


# ---------------------------------------------------------------------------
# saving throws & damage

def save_mod_of(registry, c, ability):
    if c["kind"] == "pc":
        return ch.save_mod(c["char"], ability)
    # saving-throw modifiers equal the ability modifiers unless a
    # proficient save is listed (#11.1 L1286-1287); a listed proficient
    # save carries its own authored total in stats["save_bonuses"]
    # (D-025: the engine adds nothing on its own)
    authored = c["stats"].get("save_bonuses") or {}
    if ability in authored:
        return authored[ability]
    return rules.ability_modifier(c["stats"]["abilities"][ability])


def saving_throw(registry, combat, target, ability, dc, advantage=0):
    """#2.7 / #2.2. Stunned auto-fails Strength and Dexterity saves
    (#5.6 L315). Hooks (Rage, Danger Sense...) may grant advantage via
    the save_prompted ctx."""
    ctx = fire(registry, combat, "save_prompted",
               {"target": target["cid"], "ability": ability, "dc": dc,
                "advantage": advantage, "adv": [], "dis": []})
    # adv/dis aggregate and cancel to net 0 when both are present (#2.2),
    # matching attacks; the `advantage` scalar seeds the baseline so callers
    # that pre-net (or a hook that still writes the scalar) keep working.
    _base = ctx.get("advantage", advantage)
    _has_adv = bool(ctx.get("adv")) or _base > 0
    _has_dis = bool(ctx.get("dis")) or _base < 0
    advantage = (1 if _has_adv else 0) - (1 if _has_dis else 0)
    # rolled lane modifiers (Benediction +1d4 / Malediction -1d4 to
    # saves, #9.5 L1041/L1045) aggregate through the ctx
    save_bonus = ctx.get("save_bonus", 0)
    if "stunned" in target["conditions"] and ability in ("str", "dex"):
        result = {"success": False, "total": None, "die": None,
                  "auto": "stunned"}
    else:
        result = dice.d20_test(
            save_mod_of(registry, target, ability) + save_bonus, dc,
            advantage)
    ctx = fire(registry, combat, "save_rolled",
               {"target": target["cid"], "ability": ability, "dc": dc,
                "result": result})
    result = ctx["result"]
    fire(registry, combat,
         "save_passed" if result["success"] else "save_failed",
         {"target": target["cid"], "ability": ability, "dc": dc})
    float_text(combat, target["cid"],
               "%s save %s" % (ability.upper(),
                               "OK" if result["success"] else "failed"),
               "save")
    return result


def _resist_sets(registry, combat, c):
    """(resistances, vulnerabilities, immunities) damage-type sets."""
    resist, vuln, immune = set(), set(), set()
    if c["kind"] != "pc":
        resist |= set(c["stats"].get("resistances", []))
        vuln |= set(c["stats"].get("vulnerabilities", []))
        immune |= set(c["stats"].get("immunities", []))
    if "raging" in c["flags"]:
        # Rage: resistance to bludgeoning, piercing, slashing (#7.5 L560-561)
        resist |= {"bludgeoning", "piercing", "slashing"}
    # Ironhide: resistance to one damage type while concentrated (#9.6 L1061)
    for eff in combat.get("effects", ()):
        if eff["kind"] == "resist" and eff["target"] == c["cid"]:
            resist.add(eff["data"]["type"])
    return resist, vuln, immune


def deal_damage(registry, combat, source, target, amount, dtype,
                tags=None):
    """#5.3 L243-246: flat modifiers first (already in amount), then
    resistance (half), then vulnerability (double); immunity negates;
    none stack. Temp HP absorbs first (#5.3 L251-252)."""
    ctx = fire(registry, combat, "damage_dealt",
               {"source": source["cid"] if source else None,
                "target": target["cid"], "amount": amount, "type": dtype,
                "tags": tags or []})
    amount = ctx["amount"]
    resist, vuln, immune = _resist_sets(registry, combat, target)
    if dtype in immune:
        amount = 0
    else:
        if dtype in resist:
            amount = amount // 2
        if dtype in vuln:
            amount = amount * 2
    absorbed = min(target["temp_hp"], amount)
    target["temp_hp"] -= absorbed
    hp_loss = amount - absorbed
    target["hp"] = max(0, target["hp"] - hp_loss)
    if source is not None:
        target["flags"]["last_attacker"] = source["cid"]
    float_text(combat, target["cid"], "-%d %s" % (amount, dtype), "damage")
    log(combat, "%s takes %d %s damage." % (target["name"], amount, dtype))
    if "asleep" in target["conditions"] and amount > 0:
        remove_condition(registry, combat, target, "asleep")   # wakes, L308
    if "turned" in target["conditions"] and amount > 0:
        remove_condition(registry, combat, target, "turned")   # ends, L318
    ctx2 = fire(registry, combat, "damage_taken",
                {"source": source["cid"] if source else None,
                 "target": target["cid"], "amount": amount, "type": dtype})
    _check_concentration(registry, combat, target, amount)
    if target["hp"] <= 0 and standing(target):
        _hit_zero(registry, combat, source, target)
    return amount


def _check_concentration(registry, combat, c, damage):
    """Con save, DC 10 or half the damage, whichever is higher (#5.6
    L321); failure ends the effect."""
    if not c["concentration"] or damage <= 0:
        return
    dc = rules.concentration_save_dc(damage)
    result = saving_throw(registry, combat, c, "con", dc)
    if not result["success"]:
        break_concentration(registry, combat, c)


def break_concentration(registry, combat, c):
    conc = c["concentration"]
    if not conc:
        return
    from core import hooks as hk
    c["concentration"] = None
    log(combat, "%s loses concentration on %s." % (c["name"], conc["name"]))
    for tid in conc.get("targets", []):
        target = combat["combatants"].get(tid)
        if target and conc.get("condition") and \
                conc["condition"] in target["conditions"]:
            remove_condition(registry, combat, target, conc["condition"])
    # registered ongoing effects end with the concentration (#5.6 L321)
    for eid in list(conc.get("effects", [])):
        hk.remove_effect(registry, combat, eid)
    # a concentration-bound summon leaves the order (#9.6 L1068, #9.12)
    summon_cid = conc.get("summon")
    if summon_cid:
        summon = combat["combatants"].get(summon_cid)
        if summon and not summon["dead"]:
            _end_summon(registry, combat, summon)


def _remove_from_order(combat, cid):
    """Drop one cid from the initiative order, keeping the turn pointer on
    the same combatant (summons leave the order when they end, #9.12
    L1164-1166)."""
    if cid not in combat["order"]:
        return
    idx = combat["order"].index(cid)
    combat["order"].remove(cid)
    # turn indexes the current actor. Removing an entry at or before `turn`
    # shifts later entries down, so step the pointer back one to keep the next
    # advance_turn on the right combatant. >= covers both the after-current and
    # is-current cases.
    if combat["turn"] >= idx:
        combat["turn"] -= 1
    # clamp out-of-range. KNOWN DEFENSIVE EDGE: if the CURRENT actor is removed
    # while at index 0 (turn == idx == 0), the step-back yields -1 and is
    # clamped to 0; the next advance_turn then fires turn_end for whichever
    # combatant shifted into slot 0 and skips it for that round. This path is
    # not reached in normal play -- summons leave the order when they die on
    # another combatant's turn, not as the index-0 current actor -- so it is
    # left as a documented limitation rather than restructure advance_turn's
    # turn_end/turn_start timing.
    if combat["order"] and not (0 <= combat["turn"] < len(combat["order"])):
        combat["turn"] = 0


def _end_summon(registry, combat, summon):
    """The summon simply ends: never Downed (#9.12 L1161-1162), leaves the
    order (#9.12 L1164-1166)."""
    summon["dead"] = True
    summon["conditions"].clear()
    _remove_from_order(combat, summon["cid"])
    log(combat, "%s fades away." % summon["name"])


def _hit_zero(registry, combat, source, target):
    fire(registry, combat, "hp_zero",
         {"target": target["cid"],
          "source": source["cid"] if source else None})
    if target["hp"] > 0:
        return   # a hook intervened (Relentless Rage class of effects)
    break_concentration(registry, combat, target)
    if target["kind"] == "summon":
        # Spirit Form: at 0 HP the summon simply ends -- summons are
        # never Downed (#9.12 L1161-1162); ending it releases the
        # summoner's concentration
        summoner = combat["combatants"].get(target["flags"].get("summoner"))
        _end_summon(registry, combat, target)
        if summoner and summoner["concentration"] and \
                summoner["concentration"].get("summon") == target["cid"]:
            summoner["concentration"]["summon"] = None
            break_concentration(registry, combat, summoner)
        return
    if target["side"] == "party":
        # Downed, never dead in combat (#5.5 L295-297)
        target["downed"] = True
        target["conditions"].clear()
        fire(registry, combat, "downed", {"target": target["cid"]})
        log(combat, "%s is Downed!" % target["name"])
        if all(c["downed"] for c in
               combat["combatants"].values()
               if c["side"] == "party" and c["kind"] == "pc"):
            combat["over"] = {"result": "defeat"}     # #5.5 L300
            log(combat, "The whole party is down. The game is over.")
    else:
        target["dead"] = True                          # #5.5 L301
        target["conditions"].clear()
        fire(registry, combat, "enemy_killed", {"target": target["cid"],
             "source": source["cid"] if source else None})
        log(combat, "%s dies." % target["name"])
        if not combatants_on(combat, "enemy"):
            _victory(registry, combat)


def _victory(registry, combat):
    # fled enemies (#5.9) are not defeated -- exclude them from the XP tally
    xp = sum(c["stats"]["xp"] for c in combat["combatants"].values()
             if c["side"] == "enemy" and not c.get("fled"))
    combat["over"] = {"result": "victory", "xp": xp}
    log(combat, "Victory! %d XP." % xp)


def heal(registry, combat, source, target, amount, heal_type="healing"):
    """The hard type gate (#5.5 L295-297, #9.1 L968-970): only True
    Healing touches the Downed. Returns the points restored or None when
    the gate refuses. Marks the source as a healer this combat -- any heal
    spell OR healing feature, self or ally -- for the healer_first intent
    selector (#16.3, owner adjudication P2 / G-025)."""
    if target["dead"]:
        return None
    if source is not None and source["side"] == "party":
        source["flags"]["healed_this_combat"] = True
    if target["downed"]:
        if heal_type != "true_healing":
            return None
        target["downed"] = False
        target["revived_round"] = combat["round"]
        target["hp"] = min(amount, target["hp_max"])
        fire(registry, combat, "revived", {"target": target["cid"]})
        fire(registry, combat, "heal",
             {"target": target["cid"], "amount": amount, "type": heal_type})
        log(combat, "%s is revived at %d HP!" % (target["name"], target["hp"]))
        float_text(combat, target["cid"], "+%d" % target["hp"], "heal")
        return target["hp"]
    healed = min(amount, target["hp_max"] - target["hp"])
    if "no_heal_src" in target["flags"]:
        healed = 0    # Gravewhisper/Withering Ray-style denial
    target["hp"] += healed
    fire(registry, combat, "heal",
         {"target": target["cid"], "amount": healed, "type": heal_type})
    float_text(combat, target["cid"], "+%d" % healed, "heal")
    return healed


def grant_temp_hp(combat, target, amount):
    """Doesn't stack -- keep the higher value (#5.3 L251-252)."""
    target["temp_hp"] = max(target["temp_hp"], amount)


def bloodied(c):
    """At or below half maximum HP (#5.3 L249-250) -- a flag, not a
    penalty."""
    return standing(c) and c["hp"] * 2 <= c["hp_max"]


# ---------------------------------------------------------------------------
# attacks

def weapon_of(registry, c):
    """The acting weapon record (mainhand) or None for unarmed."""
    if c["kind"] != "pc":
        return None
    wid = c["char"]["equipment"]["mainhand"]
    return registry["weapons"][wid] if wid else None


def _advantage_state(registry, combat, attacker, target, melee, ctx):
    """Aggregate advantage/disadvantage; multiple sources never stack and
    both present fully cancel (#2.2 L60-63)."""
    adv, dis = set(ctx.get("adv", [])), set(ctx.get("dis", []))
    tcond = target["conditions"]
    if "paralyzed" in tcond or "stunned" in tcond or "tripped" in tcond:
        adv.add("helpless target")
    if "staggered" in tcond:
        adv.add("staggered target")                     # #5.6 L313
    if "reckless_open" in target["flags"]:
        adv.add("reckless target")                      # #7.5 L568-569
    if "patient_defense" in target["flags"]:
        dis.add("patient defense")
    if "frightened" in attacker["conditions"]:
        dis.add("frightened")                           # #5.6 L311
    if "poisoned" in attacker["conditions"]:
        dis.add("poisoned")                             # #5.6 L316
    if "hidden" in attacker["conditions"]:
        adv.add("attacking from Hidden")                # #5.6 L317
    if adv and dis:
        return 0, adv, dis
    return (1 if adv else (-1 if dis else 0)), adv, dis


def _is_monk_weapon(registry, weapon):
    """Monk weapons = the Monk's weapon list: simple weapons plus martial
    weapons with the Light property (#7.11 L814-815; reading per GAPS
    G-032)."""
    return weapon["id"] in registry["weapon_classes"]["simple"] or \
        "light" in weapon["properties"]


def _attack_bonus(registry, attacker, weapon):
    """Keyed to the monk_martial_arts FEATURE record, never the class
    (CLAUDE.md: no class logic in the combat loop)."""
    if attacker["kind"] != "pc":
        return None   # enemies carry flat to_hit per attack
    char = attacker["char"]
    martial_arts = ch.has_feature(char, "monk_martial_arts")
    if weapon is None:
        ability = "str"
        if martial_arts:
            ability = "dex"       # Martial Arts (#7.11 L817-819)
        return ch.ability_mod(char, ability) + ch.proficiency(char), ability
    props = weapon["properties"]
    ability = "str"
    if "ranged" in props:
        # ranged weapons attack with Dexterity (GAPS G-023 default)
        ability = "dex"
    elif "finesse" in props:
        if ch.ability_mod(char, "dex") >= ch.ability_mod(char, "str"):
            ability = "dex"
    if martial_arts and _is_monk_weapon(registry, weapon):
        if ch.ability_mod(char, "dex") > ch.ability_mod(char, ability):
            ability = "dex"       # Monk weapons use Dex (#7.11 L817-818)
    return ch.ability_mod(char, ability) + ch.proficiency(char), ability


def _weapon_damage_dice(registry, attacker, weapon):
    if weapon is None:
        char = attacker["char"]
        if char and ch.has_feature(char, "monk_martial_arts"):
            # the Martial Arts die from the feature record (#7.11 L817-818)
            feat = registry["features"]["monk_martial_arts"]
            die = reg.by_level(feat["by_level"], char["level"])
            return "1d%d" % die
        return "1"   # plain unarmed: 1 + Str (GAPS G-024 default)
    return weapon["dice"]


def attack(registry, combat, attacker, target, opportunity=False,
           unarmed=False, attack_id=None):
    """One weapon/natural attack, #2.4 + #5.3 + #5.4. Returns a result
    dict. The caller handles action economy; opportunity attacks come
    through the reaction pipeline. unarmed=True forces an unarmed strike
    regardless of the equipped weapon (Flurry of Blows / the Martial
    Arts Bonus-Action strike, #7.11 L819-824). attack_id names which natural
    attack a non-pc uses (intent attack(<id>)); defaults to the first entry."""
    # Charmed cannot attack the charmer (#5.6 L310): hard-refuse so neither the
    # enemy AI nor any player path can resolve an attack on the recorded source.
    _charm = attacker["conditions"].get("charmed")
    if _charm and _charm.get("source") == target["cid"]:
        return {"ok": False, "reason": "Charmed — cannot attack the charmer."}
    weapon = None if unarmed else weapon_of(registry, attacker)
    melee = True
    if attacker["kind"] == "pc" and weapon and \
            "ranged" in weapon["properties"]:
        melee = False
    ok, reason = targetable(combat, attacker, target, melee)
    if not ok:
        return {"ok": False, "reason": reason}

    # the acting ability is computed BEFORE attack_declared so hooks can
    # key off it (Reckless Attack is Strength-based only, #7.5 L567-568)
    if attacker["kind"] == "pc":
        bonus, ability = _attack_bonus(registry, attacker, weapon)
        dmg_mod = ch.ability_mod(attacker["char"], ability)
    else:
        _atks = attacker["stats"]["attacks"]
        atk = next((a for a in _atks if a.get("id") == attack_id), _atks[0])
        bonus, dmg_mod, ability = atk["to_hit"], 0, None

    ctx = fire(registry, combat, "attack_declared",
               {"attacker": attacker["cid"], "target": target["cid"],
                "melee": melee, "opportunity": opportunity,
                "weapon": weapon, "ability": ability,
                "adv": [], "dis": [], "bonus_damage": [],
                "crit_range": 20, "to_hit_bonus": 0})

    # auto-crit vs sleepers: the first HIT against a sleeper is an automatic
    # critical (#5.6 L308); paralyzed: melee HITS against it are automatic
    # criticals (L309). This makes a landed hit a critical -- it does NOT
    # make the attack auto-hit; the attacker still rolls to beat AC (Asleep
    # grants no advantage, Paralyzed grants advantage via _advantage_state).
    auto_crit = ("asleep" in target["conditions"]) or \
                ("paralyzed" in target["conditions"] and melee)

    advantage, adv_src, dis_src = _advantage_state(
        registry, combat, attacker, target, melee, ctx)
    # attacking out of Hidden grants advantage (consumed above by
    # _advantage_state) and THEN reveals the attacker (#5.6 L317): strip
    # Hidden only AFTER the advantage state is read, or the promised
    # advantage is lost.
    if "hidden" in attacker["conditions"]:
        remove_condition(registry, combat, attacker, "hidden")
    kept, rolls = dice.d20(advantage)
    ctx2 = fire(registry, combat, "attack_roll",
                {"attacker": attacker["cid"], "target": target["cid"],
                 "die": kept, "ctx": ctx})
    kept = ctx2["die"]

    bonus += ctx.get("to_hit_bonus", 0)

    target_ac = _ac_of(registry, combat, target)
    total = kept + bonus
    # a hit lands on a nat 20 or by beating AC; auto_crit upgrades a landed
    # hit to a critical but never forces the hit itself (#5.6 L308-309)
    hit = (kept != 1) and (kept == 20 or total >= target_ac)
    crit = hit and (kept >= ctx.get("crit_range", 20) or auto_crit)

    if not hit:
        fire(registry, combat, "attack_miss",
             {"attacker": attacker["cid"], "target": target["cid"],
              "weapon": weapon, "ctx": ctx})
        float_text(combat, target["cid"], "Miss", "miss")
        log(combat, "%s misses %s (%d vs AC %d)."
            % (attacker["name"], target["name"], total, target_ac))
        return {"ok": True, "hit": False, "crit": False, "roll": kept,
                "total": total}

    if crit:
        fire(registry, combat, "crit",
             {"attacker": attacker["cid"], "target": target["cid"]})
        float_text(combat, target["cid"], "CRIT!", "crit")

    # damage: all dice twice on a crit (feature dice included), modifiers
    # once (#2.4 L79-81)
    if attacker["kind"] == "pc":
        dice_str = _weapon_damage_dice(registry, attacker, weapon)
        dtype = weapon["damage_type"] if weapon else "bludgeoning"
    else:
        dice_str, dtype = atk["dice"], atk["damage_type"]
    hit_ctx = fire(registry, combat, "attack_hit",
                   {"attacker": attacker["cid"], "target": target["cid"],
                    "melee": melee, "crit": crit, "weapon": weapon,
                    "ability": (ability if attacker["kind"] == "pc" else None),
                    "bonus_damage": list(ctx.get("bonus_damage", [])),
                    "damage_mod_bonus": 0, "min_die": 1,
                    "advantage_used": bool(adv_src) and not dis_src,
                    "disadvantage_used": bool(dis_src) and not adv_src})

    if attacker["flags"].pop("no_damage_mod_once", None):
        dmg_mod = 0      # Cleave's second attack carries no ability mod
    total_damage = _roll_damage(dice_str, crit,
                                min_die=hit_ctx.get("min_die", 1))
    total_damage += dmg_mod + hit_ctx.get("damage_mod_bonus", 0)
    for extra in hit_ctx.get("bonus_damage", []):
        total_damage += _roll_damage(extra["dice"], crit and
                                     extra.get("crits", True))
    dealt = deal_damage(registry, combat, attacker, target,
                        max(0, total_damage), dtype,
                        tags=["attack", "melee" if melee else "ranged"])

    # statblock riders: e.g. the Wolf's Bite (#11.2 L1296-1297)
    if attacker["kind"] != "pc" and standing(target):
        rider = atk.get("rider")
        if rider:
            result = saving_throw(registry, combat, target,
                                  rider["save"]["ability"],
                                  rider["save"]["dc"])
            if not result["success"]:
                apply_condition(registry, combat, target,
                                rider["condition"], source=attacker,
                                data={"until": "source_next_turn"})
    return {"ok": True, "hit": True, "crit": crit, "roll": kept,
            "total": total, "damage": dealt}


def _roll_damage(dice_str, crit, min_die=1):
    """min_die = 3 is Great Weapon Fighting's 1s-and-2s-become-3s
    (#8.2 L947-948)."""
    if "d" not in dice_str:
        return int(dice_str)
    count, sides, flat = dice.parse(dice_str)
    if crit:
        count *= 2     # roll all of the attack's damage dice twice (#2.4)
    return sum(max(dice.d(sides), min_die) for _ in range(count)) + flat


def _ac_of(registry, combat, c):
    if c["kind"] == "pc":
        ac = ch.ac(registry, c["char"])
    else:
        ac = c["stats"]["ac"]
    ac += c["flags"].get("ac_bonus", 0)
    # ongoing spell effects, consulted on read (never stored, #16.4):
    # Warding Aegis +2 (#9.5 L1042), Haste of the Quick +2 (#9.6 L1062),
    # Corrode lane -2 (#9.6 L1064), Rend Bolt -1 (#9.6 L1054)
    for eff in combat.get("effects", ()):
        if eff["kind"] != "ac_mod":
            continue
        if eff.get("target") is not None:
            if eff["target"] == c["cid"]:
                ac += eff["data"]["amount"]
        elif eff.get("lane") and c["side"] == eff["side"] and \
                c["lane"] == eff["lane"]:
            ac += eff["data"]["amount"]
    return ac


# ---------------------------------------------------------------------------
# movement & opportunity attacks

def move_lane(registry, combat, mover, dest, forced=False, free=False):
    """Lane change. Voluntary retreat (front -> back) provokes one
    opportunity attack from EVERY standing melee-capable opposing
    Frontline combatant with its Reaction; the attacks resolve BEFORE the
    move; Downing the mover cancels it. Advancing and forced movement
    never provoke (#5.4 L273-281)."""
    if dest not in LANES or mover["lane"] == dest:
        return {"ok": False, "reason": "Already there."}
    if not forced:
        for cond in ("pinned", "tripped"):
            if cond in mover["conditions"]:
                return {"ok": False,
                        "reason": "%s cannot change lanes."
                        % cond.capitalize()}
    fire(registry, combat, "line_change_declared",
         {"mover": mover["cid"], "from": mover["lane"], "to": dest,
          "forced": forced})
    retreat = (mover["lane"] == "front" and dest == "back")
    if retreat and not forced and not free:
        _provoke_opportunity_attacks(registry, combat, mover)
        if not standing(mover):
            return {"ok": False, "reason": "Downed while retreating."}
    mover["lane"] = dest
    fire(registry, combat, "line_changed",
         {"mover": mover["cid"], "from": "front" if dest == "back" else "back",
          "to": dest, "forced": forced})
    log(combat, "%s moves to the %sline." % (mover["name"], dest))
    return {"ok": True}


def _provoke_opportunity_attacks(registry, combat, mover):
    """#5.4 L277-281 / #5.7 L333-335."""
    other = "enemy" if mover["side"] == "party" else "party"
    for c in combatants_on(combat, other, "front"):
        if combat["over"] or not standing(mover):
            break
        if c["acted"]["reaction"] or not _can_react(c):
            continue
        if not melee_capable(registry, c):
            continue
        if not _prompt_allows(registry, combat,
                              {"prompt": "always",
                               "ability_id": "opportunity_attack",
                               "title": "Opportunity attack"},
                              c, {"event": "line_change_declared",
                                  "mover": mover["cid"]}):
            continue
        c["acted"]["reaction"] = True
        log(combat, "%s takes an opportunity attack on %s!"
            % (c["name"], mover["name"]))
        attack(registry, combat, c, mover, opportunity=True)


def push(registry, combat, source, target, dest):
    """Forced movement never provokes (#5.4 L280-281)."""
    return move_lane(registry, combat, target, dest, forced=True)


# ---------------------------------------------------------------------------
# enemy turns: the intent-script interpreter (#16.3)

def enemy_take_turn(registry, combat, actor):
    if not can_act(actor):
        return advance_turn(registry, combat)
    tick_source_turn_start(registry, combat, actor)
    script = actor["stats"]["intent"]
    for rule in script:
        if _intent_predicate(registry, combat, actor, rule["if"]):
            # A rule whose action is a no-op (a move to the lane the actor
            # already holds) must NOT consume the turn -- fall through to the
            # next rule so a frontline wolf bites instead of wasting round 1.
            if _intent_action(registry, combat, actor, rule):
                break
    return advance_turn(registry, combat)


def _intent_predicate(registry, combat, actor, pred):
    other = "party" if actor["side"] == "enemy" else "enemy"
    if pred == "always":
        return True
    if pred.startswith("round"):
        return combat["round"] == int(pred.split("==")[1].strip())
    if pred == "party_frontline_empty":
        return frontline_empty(combat, other)
    if pred.startswith("hp_below"):
        frac = float(pred.split("(")[1].rstrip(")"))
        return actor["hp"] < actor["hp_max"] * frac
    if pred.startswith("ally_count_below"):
        n = int(pred.split("(")[1].rstrip(")"))
        return len(combatants_on(combat, actor["side"])) < n
    if pred.startswith("has_condition"):
        cond = pred.split("(")[1].rstrip(")")
        return cond in actor["conditions"]
    if pred.startswith("cooldown_ready"):
        ability = pred.split("(")[1].rstrip(")")
        return actor["intent_state"]["cooldowns"].get(ability, 0) <= 0
    if pred.startswith("target_exists"):
        sel = pred.split("(")[1].rstrip(")")
        return _intent_select(registry, combat, actor, sel) is not None
    raise ValueError("unknown intent predicate: %r" % pred)


def _intent_select(registry, combat, actor, selector):
    other = "party" if actor["side"] == "enemy" else "enemy"
    pool = combatants_on(combat, other)
    pool = [c for c in pool if "hidden" not in c["conditions"]]
    # Charmed cannot target the charmer (#5.6 L310): drop them; if the charmer
    # is the only option there is no legal target this turn.
    _charm = actor["conditions"].get("charmed")
    if _charm and _charm.get("source"):
        pool = [c for c in pool if c["cid"] != _charm["source"]]
    if not pool:
        return None
    if selector == "nearest_frontline":
        front = [c for c in pool if c["lane"] == "front"]
        chosen = front or pool
        return chosen[dice.d(len(chosen)) - 1]
    if selector == "random_backline":
        back = [c for c in pool if c["lane"] == "back"]
        chosen = back or pool
        return chosen[dice.d(len(chosen)) - 1]
    if selector == "lowest_hp":
        return min(pool, key=lambda c: c["hp"])
    if selector == "marked":
        marked = [c for c in pool if "quarry_mark" in c["flags"]]
        return marked[0] if marked else None
    if selector == "last_attacker":
        cid = actor["flags"].get("last_attacker")
        c = combat["combatants"].get(cid)
        return c if c and standing(c) else None
    if selector == "healer_first":
        # "kill their cleric" (#16.3, owner adjudication P2 / G-025): a
        # party member who cast a Heal/True Heal spell OR used a healing
        # feature this combat; ties and the no-healer case fall back to
        # lowest current HP.
        healers = [c for c in pool if "healed_this_combat" in c["flags"]]
        candidates = healers or pool
        return min(candidates, key=lambda c: c["hp"])
    raise ValueError("unknown intent selector: %r" % selector)


def _intent_action(registry, combat, actor, rule):
    """Execute one intent rule. Returns True when the action consumed the
    turn, False on a no-op (a move to the lane the actor already holds, or
    an attack with no legal target) so enemy_take_turn falls through to the
    next rule instead of wasting the turn (#16.3)."""
    do = rule["do"]
    if do.startswith("attack"):
        target = _intent_select(registry, combat, actor,
                                rule.get("target", "nearest_frontline"))
        if target is None:
            return False
        # honor the named attack -- attack(<id>) -- defaulting to the first
        # entry; melee gate: if the pick is unreachable, the engine lets the
        # attack call refuse (intent scripts are authored to avoid this)
        atk_id = do.split("(")[1].rstrip(")") if "(" in do else None
        attack(registry, combat, actor, target, attack_id=atk_id)
        return True
    elif do.startswith("move"):
        dest = do.split("(")[1].rstrip(")")
        dest = "front" if dest == "frontline" else "back"
        if actor["lane"] != dest:
            move_lane(registry, combat, actor, dest)
            return True
        return False                                       # already there
    elif do.startswith("telegraph"):
        ability = do.split("(")[1].rstrip(")")
        actor["telegraph"] = ability                       # #5.8 L357-359
        return True
    elif do == "flee":
        actor["dead"] = True
        actor["fled"] = True            # not defeated: grants no XP (#5.9)
        log(combat, "%s flees!" % actor["name"])
        if not combatants_on(combat, "enemy"):
            _victory(registry, combat)
        return True
    elif do.startswith("cast"):
        # enemy casters arrive with the region-1 roster (owner content);
        # the vocabulary is supported, the statblocks aren't here yet
        log(combat, "%s casts." % actor["name"])
        return True
    else:
        raise ValueError("unknown intent action: %r" % do)


# ---------------------------------------------------------------------------
# player-facing action wrappers: the turn economy (#5.2 L224-232)

def attacks_per_attack_action(actor):
    """Number of attacks made when this combatant takes the Attack action."""
    if actor["kind"] != "pc":
        return 1
    char = actor["char"]
    if ch.has_feature(char, "fighter_two_extra_attacks"):
        return 3
    if ch.has_feature(char, "extra_attack"):
        return 2
    return 1


def attack_action_available(actor):
    """True when the Attack button can start or continue an Attack action."""
    return (not actor["acted"]["action"] or
            actor["flags"].get("attack_action_remaining", 0) > 0)


def player_attack(registry, combat, actor, target, reckless=False):
    """The Attack action. Reckless (#7.5 L567-569) is declared with the
    attack: advantage now, attacks against you have advantage until your
    next turn."""
    remaining = actor["flags"].get("attack_action_remaining", 0)
    if actor["acted"]["action"] and remaining <= 0:
        return {"ok": False, "reason": "Action spent."}
    if reckless:
        if not (actor["kind"] == "pc" and
                ch.has_feature(actor["char"], "barbarian_reckless_attack")):
            return {"ok": False,
                    "reason": "Reckless Attack is not available."}
        actor["flags"]["reckless_open"] = True
    result = attack(registry, combat, actor, target)
    if not result["ok"]:
        actor["flags"].pop("reckless_open", None) if reckless else None
        return result
    if reckless and actor["kind"] == "pc":
        pass  # reckless advantage rides via the open flag + adv below
    actor["acted"]["action"] = True
    if remaining > 0:
        actor["flags"]["attack_action_remaining"] = remaining - 1
    else:
        actor["flags"]["attack_action_remaining"] = \
            attacks_per_attack_action(actor) - 1
    if actor["flags"]["attack_action_remaining"] <= 0:
        actor["flags"].pop("attack_action_remaining", None)
    # gates the Martial Arts Bonus-Action unarmed strike ("after taking
    # the Attack action", #7.11 L819); cleared at the next turn start
    actor["flags"]["attack_action_taken"] = True
    result["attacks_remaining"] = actor["flags"].get(
        "attack_action_remaining", 0)
    return result


def player_move(registry, combat, actor, dest):
    """Moving costs the Action by default (#5.2 L225-228); features that
    grant free lane changes set 'free_move_available' for the turn (the
    hooks layer owns granting it)."""
    if actor["flags"].get("no_move_this_turn"):
        return {"ok": False, "reason": "No lane change this turn."}  # Steady Aim, #7.2 L448-449
    free = actor["flags"].get("free_move_available", False)
    no_provoke = bool(actor["flags"].get("free_move_no_provoke", False)) \
        and free
    if not free and actor["acted"]["action"]:
        return {"ok": False, "reason": "Action spent."}
    # only features that SAY "without provoking" waive the retreat OA
    # (Stag #7.10 L778) -- the waiver is priced (#5.4 L282-284); a merely
    # free move (Haste #9.6 L1062) still provokes on retreat
    result = move_lane(registry, combat, actor, dest, free=no_provoke)
    # consume the cost only on a successful move: a refused move (same lane /
    # pinned / tripped / Downed-while-retreating) leaves BOTH the free-move
    # flag and the Action intact, instead of silently burning the free move
    if result["ok"]:
        if free:
            actor["flags"].pop("free_move_available", None)
            actor["flags"].pop("free_move_no_provoke", None)
        else:
            actor["acted"]["action"] = True
    return result


def player_use_item(registry, combat, actor, item_id, target, inventory):
    """The Use Item action (#14.4 L1448-1450): potions route through the
    same Healing/True-Healing gate as spells."""
    if actor["acted"]["action"]:
        return {"ok": False, "reason": "Action spent."}
    item = registry["consumables"].get(item_id)
    if not item or inventory.get(item_id, 0) < 1:
        return {"ok": False, "reason": "Not available."}
    heal_type = item["heal_type"]
    if target["dead"]:
        return {"ok": False, "reason": "Beyond help."}
    if target["downed"] and heal_type != "true_healing":
        return {"ok": False,
                "reason": "Healing cannot revive a Downed character — "
                          "only True Healing can."}
    amount = dice.roll(item["heal"]["dice"])
    healed = heal(registry, combat, actor, target, amount, heal_type)
    if healed is None:
        return {"ok": False, "reason": "It has no effect."}
    inventory[item_id] -= 1
    if inventory[item_id] <= 0:
        del inventory[item_id]
    actor["acted"]["action"] = True
    log(combat, "%s uses %s on %s." % (actor["name"], item["name"],
                                       target["name"]))
    return {"ok": True, "healed": healed}


# ---------------------------------------------------------------------------
# fleeing & wrap-up

def flee(registry, combat):
    """Always succeeds, instant end, no XP or loot (#5.9 L362-365)."""
    if not combat["flee_allowed"]:
        return {"ok": False, "reason": "No escape from this fight."}
    combat["over"] = {"result": "fled"}
    log(combat, "The party flees.")
    return {"ok": True}


def finish_combat(registry, combat, party):
    """Flush results back to the characters: HP, Downed rise at 1 HP
    (#5.5 L298-299), XP to the protagonist only (#6 L378-379), combat
    conditions clear (GAPS G-026 reading)."""
    for c in combat["combatants"].values():
        if c["kind"] != "pc":
            continue
        char = c["char"]
        if c["downed"]:
            char["hp"] = 1
        else:
            # clamp: in-fight maximum-HP buffs last "for the fight" only
            # (Vital Surge, #9.6 L1060)
            char["hp"] = min(c["hp"], char["hp_max"])
        char["temp_hp"] = 0
        char["conditions"] = []
    result = combat["over"] or {}
    if result.get("result") == "victory" and party:
        party[0]["xp"] += result.get("xp", 0)
    return result
