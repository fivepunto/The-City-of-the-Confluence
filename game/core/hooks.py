# -*- coding: utf-8 -*-
"""The event-pipeline hook library (GDD #16.2) and the combat-facing
ability/spell dispatch.

A feature IS its hook record: HOOK_LIBRARY maps registry feature/trait ids
to hook records {event, priority, condition, effect, prompt, cost} whose
condition/effect entries name functions in this module. The combat loop
never mentions a class (CLAUDE.md iron rule); it only fires events.

Coverage targets the vertical slice (character levels 1-3, #18): deeper
features keep their data records and gain hooks in later passes.
"""

from core import dice, rules
from core import registry as reg
from core import character as ch


# ---------------------------------------------------------------------------
# hook collection

def _owner_feature_ids(registry, c):
    if c["kind"] == "pc":
        char = c["char"]
        ids = list(char["features"])
        ids += ["style_" + s for s in char["class_picks"].get("fighting_styles", [])]
        ids += ["inv_" + i for i in char["class_picks"].get("invocations", [])]
        ids += ["talent_" + t for t in char["talents"]]
        return ids
    return ["trait_" + t["id"] for t in c["stats"].get("traits", [])]




def check_condition(registry, combat, hook, owner, ctx):
    fn = CONDITIONS[hook["condition"]] if hook.get("condition") else None
    if fn is None:
        return True
    return fn(registry, combat, owner, ctx)


def run_effect(registry, combat, hook, owner, ctx):
    EFFECTS[hook["effect"]](registry, combat, owner, ctx)


# ---------------------------------------------------------------------------
# condition functions

def _c(combat, cid):
    return combat["combatants"][cid] if cid else None


def _turn_key(combat):
    """Identity of the current turn, for once-per-turn flags."""
    return combat["round"] * 1000 + combat["turn"]


def cond_own_attack(registry, combat, owner, ctx):
    return ctx.get("attacker") == owner["cid"]


def cond_pack_ally_same_lane(registry, combat, owner, ctx):
    """Pack Tactics: another wolf in the same lane (#11.2 L1298-1300) --
    deliberately inert when alone."""
    if ctx.get("attacker") != owner["cid"]:
        return False
    from core import combat as cb
    for c in cb.combatants_on(combat, owner["side"], owner["lane"]):
        if c["cid"] == owner["cid"]:
            continue
        # key off the statblock creature tag, never the cid string; PCs and
        # summons carry stats=None and simply don't match
        if "wolf" in ((c.get("stats") or {}).get("tags") or []):
            return True
    return False


def cond_sneak_attack(registry, combat, owner, ctx):
    """#7.2 L439-443: once per turn; Finesse or ranged weapon; advantage
    on the attack, OR a conscious ally in melee reach of the target and
    no disadvantage."""
    from core import combat as cb
    if ctx.get("attacker") != owner["cid"]:
        return False
    if owner["flags"].get("sneak_attack_used_turn") == combat["round"] * 1000 + combat["turn"]:
        return False
    weapon = ctx.get("weapon")
    if not weapon or not ({"finesse", "ranged"} & set(weapon["properties"])):
        return False
    if ctx.get("advantage_used"):
        return True
    if ctx.get("disadvantage_used"):
        return False
    target = _c(combat, ctx["target"])
    for ally in cb.combatants_on(combat, owner["side"]):
        if ally["cid"] != owner["cid"] and \
                cb.melee_reach(combat, ally, target):
            return True
    return False


def cond_raging_str_attack(registry, combat, owner, ctx):
    return ctx.get("attacker") == owner["cid"] and \
        "raging" in owner["flags"] and ctx.get("ability") == "str"


def cond_reckless_attacker(registry, combat, owner, ctx):
    """Reckless Attack: advantage on your Strength-based attacks this turn
    (#7.5 L567-568); the open-target half lives on the flag read by
    _advantage_state. The acting ability rides the attack_declared ctx."""
    return ctx.get("attacker") == owner["cid"] and \
        "reckless_open" in owner["flags"] and ctx.get("ability") == "str"


def cond_own_str_save(registry, combat, owner, ctx):
    return ctx.get("target") == owner["cid"] and \
        "raging" in owner["flags"] and ctx.get("ability") == "str"


def cond_own_dex_save(registry, combat, owner, ctx):
    return ctx.get("target") == owner["cid"] and ctx.get("ability") == "dex"


def cond_own_ranged_attack(registry, combat, owner, ctx):
    return ctx.get("attacker") == owner["cid"] and not ctx.get("melee")


def cond_dueling(registry, combat, owner, ctx):
    """+2 damage with a one-handed weapon when the other hand holds no
    weapon -- a shield is fine (#8.2 L944-946)."""
    if ctx.get("attacker") != owner["cid"]:
        return False
    weapon = ctx.get("weapon")
    if not weapon or "two_handed" in weapon["properties"]:
        return False
    off = owner["char"]["equipment"]["offhand"]
    return off is None or off == "shield"


def cond_gwf(registry, combat, owner, ctx):
    """Two-handed melee damage dice (#8.2 L947-948)."""
    weapon = ctx.get("weapon")
    return ctx.get("attacker") == owner["cid"] and ctx.get("melee") and \
        weapon is not None and "two_handed" in weapon["properties"]


def cond_mastery(name):
    def check(registry, combat, owner, ctx):
        if ctx.get("attacker") != owner["cid"] or owner["kind"] != "pc":
            return False
        weapon = ctx.get("weapon")
        if weapon is None or weapon["mastery"] != name:
            return False
        char = owner["char"]
        if not ch.has_feature(char, "weapon_mastery"):
            return False
        return weapon["id"] in char["class_picks"].get("weapon_masteries", [])
    return check


def cond_steady_aim_pending(registry, combat, owner, ctx):
    """Steady Aim: advantage on your next attack this turn (#7.2
    L448-449)."""
    return ctx.get("attacker") == owner["cid"] and \
        "steady_aim_adv" in owner["flags"]


def cond_frenzy(registry, combat, owner, ctx):
    """Frenzy (#7.5 L570-573): raging AND reckless this turn; fires on the
    first Strength-based hit each turn only."""
    return ctx.get("attacker") == owner["cid"] and \
        "raging" in owner["flags"] and \
        "reckless_open" in owner["flags"] and \
        ctx.get("ability") == "str" and \
        owner["flags"].get("frenzy_used_turn") != _turn_key(combat)


def cond_colossus_slayer(registry, combat, owner, ctx):
    """Hunter's Prey -- Colossus Slayer (#7.6 L608-610): once per turn,
    against a target that is missing HP."""
    if ctx.get("attacker") != owner["cid"] or owner["kind"] != "pc":
        return False
    if owner["char"]["class_picks"].get("ranger_hunters_prey") != \
            "colossus_slayer":
        return False
    if owner["flags"].get("colossus_used_turn") == _turn_key(combat):
        return False
    target = _c(combat, ctx.get("target"))
    return target is not None and target["hp"] < target["hp_max"]


def cond_own_melee_hit(registry, combat, owner, ctx):
    return ctx.get("attacker") == owner["cid"] and bool(ctx.get("melee"))


def cond_own_turn_start(registry, combat, owner, ctx):
    return ctx.get("actor") == owner["cid"]


def cond_stag_turn_start(registry, combat, owner, ctx):
    """Aspect of the Stag active at the owner's turn start (#7.10 L778)."""
    return ctx.get("actor") == owner["cid"] and \
        owner["flags"].get("aspect") == "stag"


def cond_own_hp_zero_aspect(registry, combat, owner, ctx):
    return ctx.get("target") == owner["cid"] and "aspect" in owner["flags"]


# ---------------------------------------------------------------------------
# effect functions

def eff_advantage(registry, combat, owner, ctx):
    ctx.setdefault("adv", []).append(ctx["event"])


def eff_sneak_damage(registry, combat, owner, ctx):
    feat = registry["features"]["rogue_sneak_attack"]
    count = reg.by_level(feat["by_level"], owner["char"]["level"])
    ctx.setdefault("bonus_damage", []).append(
        {"dice": "%dd6" % count, "crits": True, "label": "Sneak Attack"})
    owner["flags"]["sneak_attack_used_turn"] = \
        combat["round"] * 1000 + combat["turn"]


def eff_rage_damage(registry, combat, owner, ctx):
    feat = registry["features"]["barbarian_rage"]
    bonus = reg.by_level(feat["by_level"], owner["char"]["level"]) \
        if feat.get("by_level") else 2
    ctx["damage_mod_bonus"] = ctx.get("damage_mod_bonus", 0) + bonus


def eff_save_advantage(registry, combat, owner, ctx):
    ctx["advantage"] = 1


def eff_archery(registry, combat, owner, ctx):
    ctx["to_hit_bonus"] = ctx.get("to_hit_bonus", 0) + 2


def eff_dueling(registry, combat, owner, ctx):
    ctx["damage_mod_bonus"] = ctx.get("damage_mod_bonus", 0) + 2


def eff_gwf(registry, combat, owner, ctx):
    ctx["min_die"] = 3


def eff_improved_crit(registry, combat, owner, ctx):
    ctx["crit_range"] = min(ctx.get("crit_range", 20), 19)


def eff_vex(registry, combat, owner, ctx):
    """Vex: advantage on your next attack against that target (#10.3)."""
    owner["flags"]["vex_target"] = ctx["target"]


def eff_consume_vex(registry, combat, owner, ctx):
    if owner["flags"].get("vex_target") == ctx.get("target"):
        ctx.setdefault("adv", []).append("vex")
        owner["flags"].pop("vex_target", None)


def eff_sap(registry, combat, owner, ctx):
    """Sap: the target has disadvantage on its next attack (#10.3)."""
    _c(combat, ctx["target"])["flags"]["sapped"] = True


def eff_consume_sap(registry, combat, owner, ctx):
    if owner["flags"].pop("sapped", None):
        ctx.setdefault("dis", []).append("sapped")


def eff_graze(registry, combat, owner, ctx):
    """Graze: on a miss, damage equal to the ability modifier (#10.3
    L1200). The missing weapon rides the attack_miss ctx."""
    from core import combat as cb
    weapon = ctx.get("weapon")
    if weapon is None:
        return
    _bonus, ability = cb._attack_bonus(registry, owner, weapon)
    mod = ch.ability_mod(owner["char"], ability)
    if mod > 0:
        target = _c(combat, ctx["target"])
        cb.deal_damage(registry, combat, owner, target, mod,
                       weapon["damage_type"], tags=["graze"])


def eff_push(registry, combat, owner, ctx):
    from core import combat as cb
    target = _c(combat, ctx["target"])
    if target["lane"] == "front":
        cb.push(registry, combat, owner, target, "back")


def eff_slow(registry, combat, owner, ctx):
    from core import combat as cb
    target = _c(combat, ctx["target"])
    cb.apply_condition(registry, combat, target, "pinned", source=owner,
                       data={"until": "target_turn_end"})


def eff_topple(registry, combat, owner, ctx):
    """Topple: Con save DC 8 + ability modifier + proficiency or
    Staggered (#10.3 L1206-1207)."""
    from core import combat as cb
    char = owner["char"]
    bonus, ability = cb._attack_bonus(registry, owner,
                                      cb.weapon_of(registry, owner))
    dc = 8 + ch.ability_mod(char, ability) + ch.proficiency(char)
    target = _c(combat, ctx["target"])
    result = cb.saving_throw(registry, combat, target, "con", dc)
    if not result["success"]:
        cb.apply_condition(registry, combat, target, "staggered",
                           source=owner, data={"until": "source_next_turn"})


def eff_cleave(registry, combat, owner, ctx):
    """Cleave: on a melee hit, attack a second enemy in the same lane (no
    ability modifier to that damage); once per turn (#10.3 L1201-1203)."""
    from core import combat as cb
    key = combat["round"] * 1000 + combat["turn"]
    if owner["flags"].get("cleave_used_turn") == key:
        return
    target = _c(combat, ctx["target"])
    others = [c for c in cb.combatants_on(combat, target["side"],
                                          target["lane"])
              if c["cid"] != target["cid"]]
    if not others:
        return
    owner["flags"]["cleave_used_turn"] = key
    second = others[dice.d(len(others)) - 1]
    owner["flags"]["no_damage_mod_once"] = True
    cb.attack(registry, combat, owner, second)


def eff_consume_steady_aim(registry, combat, owner, ctx):
    """Spend the banked Steady Aim advantage on this attack (#7.2
    L448-449)."""
    ctx.setdefault("adv", []).append("steady aim")
    owner["flags"].pop("steady_aim_adv", None)


def eff_frenzy_damage(registry, combat, owner, ctx):
    """Frenzy: extra damage equal to the Rage damage bonus in d6s -- 2d6
    at slice levels, 3d6 from level 9 (#7.5 L570-573). Rides the attack's
    damage type via the bonus_damage channel."""
    feat = registry["features"]["barbarian_frenzy"]
    count = reg.by_level(feat["by_level"], owner["char"]["level"]) or 2
    ctx.setdefault("bonus_damage", []).append(
        {"dice": "%dd6" % count, "crits": True, "label": "Frenzy"})
    owner["flags"]["frenzy_used_turn"] = _turn_key(combat)


def eff_colossus_damage(registry, combat, owner, ctx):
    """Colossus Slayer: +1d8 once per turn vs a wounded target (#7.6
    L608-610)."""
    ctx.setdefault("bonus_damage", []).append(
        {"dice": "1d8", "crits": True, "label": "Colossus Slayer"})
    owner["flags"]["colossus_used_turn"] = _turn_key(combat)


def eff_record_melee_hit(registry, combat, owner, ctx):
    """Paladin's Smite: remember the melee hit that legalizes casting
    Radiant Smite as a Bonus Action this turn (#7.9 L737-738, #9.5
    L1043)."""
    owner["flags"]["last_melee_hit"] = ctx["target"]
    owner["flags"]["last_melee_hit_key"] = _turn_key(combat)


def eff_clear_turn_flags(registry, combat, owner, ctx):
    """Turn-scoped flags granted by the hooks layer expire at the owner's
    next turn start: Steady Aim's pair (#7.2 L448-449) and the Open Hand
    Addle ('until its next turn', #7.11 L834-835)."""
    for flag in ("steady_aim_adv", "no_move_this_turn", "addled"):
        owner["flags"].pop(flag, None)


def eff_stag_turn_grants(registry, combat, owner, ctx):
    """Aspect of the Stag: one free lane change each turn and +2 AC while
    active (#7.10 L778); re-granted at each of the owner's turn starts."""
    owner["flags"]["ac_bonus"] = 2
    owner["flags"]["free_move_available"] = True
    owner["flags"]["free_move_no_provoke"] = True   # "without provoking"


def eff_end_aspect(registry, combat, owner, ctx):
    """An Aspect lasts until dismissed or until you are Downed (#7.10
    L770-771) -- hp_zero clears the stance and its AC rider."""
    owner["flags"].pop("aspect", None)
    owner["flags"].pop("ac_bonus", None)


CONDITIONS = {
    "own_attack": cond_own_attack,
    "pack_ally_same_lane": cond_pack_ally_same_lane,
    "sneak_attack": cond_sneak_attack,
    "raging_str_attack": cond_raging_str_attack,
    "reckless_attacker": cond_reckless_attacker,
    "own_str_save_raging": cond_own_str_save,
    "own_dex_save": cond_own_dex_save,
    "own_ranged_attack": cond_own_ranged_attack,
    "dueling": cond_dueling,
    "gwf": cond_gwf,
    "mastery_vex": cond_mastery("vex"),
    "mastery_sap": cond_mastery("sap"),
    "mastery_graze": cond_mastery("graze"),
    "mastery_push": cond_mastery("push"),
    "mastery_slow": cond_mastery("slow"),
    "mastery_topple": cond_mastery("topple"),
    "mastery_cleave": cond_mastery("cleave"),
    "own_attack_any": cond_own_attack,
    "target_is_self": lambda r, cb_, o, ctx: ctx.get("target") == o["cid"],
    "steady_aim_pending": cond_steady_aim_pending,
    "frenzy": cond_frenzy,
    "colossus_slayer": cond_colossus_slayer,
    "own_melee_hit": cond_own_melee_hit,
    "own_turn_start": cond_own_turn_start,
    "stag_turn_start": cond_stag_turn_start,
    "own_hp_zero_aspect": cond_own_hp_zero_aspect,
}

EFFECTS = {
    "advantage": eff_advantage,
    "sneak_damage": eff_sneak_damage,
    "rage_damage": eff_rage_damage,
    "save_advantage": eff_save_advantage,
    "archery": eff_archery,
    "dueling": eff_dueling,
    "gwf": eff_gwf,
    "improved_crit": eff_improved_crit,
    "vex": eff_vex,
    "consume_vex": eff_consume_vex,
    "sap": eff_sap,
    "consume_sap": eff_consume_sap,
    "graze": eff_graze,
    "push": eff_push,
    "slow": eff_slow,
    "topple": eff_topple,
    "cleave": eff_cleave,
    "consume_steady_aim": eff_consume_steady_aim,
    "frenzy_damage": eff_frenzy_damage,
    "colossus_damage": eff_colossus_damage,
    "record_melee_hit": eff_record_melee_hit,
    "clear_turn_flags": eff_clear_turn_flags,
    "stag_turn_grants": eff_stag_turn_grants,
    "end_aspect": eff_end_aspect,
}


def _h(fid, event, condition, effect, **kw):
    hook = {"event": event, "condition": condition, "effect": effect,
            "ability_id": fid}
    hook.update(kw)
    return hook


# Feature id -> hook records. Each cites the rule it implements.
HOOK_LIBRARY = {
    # Pack Tactics: advantage while another wolf shares the lane (#11.2)
    "trait_pack_tactics": (
        _h("pack_tactics", "attack_declared", "pack_ally_same_lane",
           "advantage"),),
    # Sneak Attack (#7.2 L439-443)
    "rogue_sneak_attack": (
        _h("sneak_attack", "attack_hit", "sneak_attack", "sneak_damage"),),
    # Rage damage bonus on Strength attacks (#7.5 L561-562)
    "barbarian_rage": (
        _h("rage", "attack_hit", "raging_str_attack", "rage_damage"),
        _h("rage", "save_prompted", "own_str_save_raging",
           "save_advantage"),),
    # Danger Sense: advantage on Dexterity saves (#7.5 L566)
    "barbarian_danger_sense": (
        _h("danger_sense", "save_prompted", "own_dex_save",
           "save_advantage"),),
    # Reckless Attack: advantage on your Strength attacks this turn
    # (#7.5 L567-569)
    "barbarian_reckless_attack": (
        _h("reckless_attack", "attack_declared", "reckless_attacker",
           "advantage"),),
    # Improved Critical: crit on 19-20 (#7.1 L413)
    "fighter_improved_critical": (
        _h("improved_critical", "attack_declared", "own_attack",
           "improved_crit"),),
    # Fighting Styles (#8.2)
    "style_archery": (
        _h("archery", "attack_declared", "own_ranged_attack", "archery"),),
    "style_dueling": (
        _h("dueling", "attack_hit", "dueling", "dueling"),),
    "style_great_weapon_fighting": (
        _h("great_weapon_fighting", "attack_hit", "gwf", "gwf"),),
    # Weapon masteries (#10.3) -- active only for mastery-feature classes
    # with the weapon picked (gated in cond_mastery)
    "weapon_mastery": (
        _h("mastery_vex", "attack_hit", "mastery_vex", "vex"),
        _h("mastery_vex_use", "attack_declared", "own_attack",
           "consume_vex", priority=5),
        _h("mastery_sap", "attack_hit", "mastery_sap", "sap"),
        _h("mastery_graze", "attack_miss", "mastery_graze", "graze"),
        _h("mastery_push", "attack_hit", "mastery_push", "push"),
        _h("mastery_slow", "attack_hit", "mastery_slow", "slow"),
        _h("mastery_topple", "attack_hit", "mastery_topple", "topple"),
        _h("mastery_cleave", "attack_hit", "mastery_cleave", "cleave"),),
    # Steady Aim: the banked advantage is consumed by the next attack this
    # turn (#7.2 L448-449); the move lock lives in combat.player_move
    "rogue_steady_aim": (
        _h("steady_aim", "attack_declared", "steady_aim_pending",
           "consume_steady_aim", priority=5),),
    # Frenzy: rage bonus in d6s on the first reckless Strength hit each
    # turn while raging (#7.5 L570-573)
    "barbarian_frenzy": (
        _h("frenzy", "attack_hit", "frenzy", "frenzy_damage"),),
    # Hunter's Prey -- Colossus Slayer (#7.6 L608-610). Horde Breaker is
    # DEFERRED (see the block at the end of this module).
    "ranger_hunters_prey": (
        _h("colossus_slayer", "attack_hit", "colossus_slayer",
           "colossus_damage"),),
    # Paladin's Smite: record the qualifying melee hit; the Radiant Smite
    # cast gate reads it (#7.9 L737-738, #9.5 L1043)
    "paladin_paladins_smite": (
        _h("paladins_smite", "attack_hit", "own_melee_hit",
           "record_melee_hit"),),
    # Aspects (#7.10 L766-778): Stag's per-turn grants; any Aspect ends
    # when the druid is Downed
    "druid_aspects": (
        _h("aspect_stag", "turn_start", "stag_turn_start",
           "stag_turn_grants"),
        _h("aspect_end", "hp_zero", "own_hp_zero_aspect", "end_aspect"),),
}

# Every attacker consumes incoming Sap (#10.3) -- universal listener
HOOK_LIBRARY["_universal_sap"] = (
    _h("sapped", "attack_declared", "own_attack_any", "consume_sap"),)

# Turn-scoped hook flags expire at the owner's next turn start (Steady
# Aim #7.2 L448-449; Addle #7.11 L834-835) -- universal listener
HOOK_LIBRARY["_universal_turn_flags"] = (
    _h("turn_flags", "turn_start", "own_turn_start", "clear_turn_flags"),)


def universal_ids():
    return ("_universal_sap", "_universal_turn_flags")


def hooks_for(registry, combat, event):
    """All (hook, owner) pairs listening to one event, priority-sorted."""
    out = []
    for cid in combat["order"]:
        c = combat["combatants"][cid]
        if c["dead"]:
            continue
        ids = _owner_feature_ids(registry, c) + list(universal_ids())
        for fid in ids:
            for hook in HOOK_LIBRARY.get(fid, ()):
                if hook["event"] == event:
                    out.append((hook, c))
    out.sort(key=lambda pair: pair[0].get("priority", 0), reverse=True)
    return out


# ---------------------------------------------------------------------------
# player abilities (the Abilities button) -- slice-level coverage

def _uses_left(registry, char, fid):
    feat = registry["features"][fid]
    if not feat.get("uses"):
        return None
    uses = char["resources"].setdefault("uses", {})
    if fid not in uses:
        uses[fid] = ch.resolve_amount(char, feat["uses"]["amount"])
    return uses[fid]


def _spend_use(char, fid):
    char["resources"]["uses"][fid] -= 1


def _ability_options(registry, combat, actor, impl):
    """The legal option ids for an option-taking ability (e.g. the Druid's
    known Aspects, the Open Hand techniques). Static tuple or callable."""
    opts = impl.get("options")
    if opts is None:
        return []
    if callable(opts):
        return list(opts(registry, combat, actor))
    return list(opts)


def available_abilities(registry, combat, actor):
    """Activated abilities for the active panel. Returns
    [{id, name, action, uses_left, usable, reason, needs_target,
    options}]."""
    if actor["kind"] != "pc":
        return []
    char = actor["char"]
    out = []
    for aid, impl in ABILITY_IMPL.items():
        fid = impl["feature"]
        if fid not in char["features"]:
            continue
        feat = registry["features"][fid]
        if impl.get("resource"):
            left = char["resources"].get(impl["resource"], 0)
        elif impl.get("free_use"):
            left = None      # costs no feature use (Aspect attacks)
        else:
            left = _uses_left(registry, char, fid)
        action_kind = impl.get("action", feat.get("action", "action"))
        usable, reason = True, None
        if left is not None and left <= 0:
            usable, reason = False, "Nothing left to spend."
        if action_kind == "bonus" and actor["acted"]["bonus"]:
            usable, reason = False, "Bonus Action spent."
        if action_kind == "action" and actor["acted"]["action"]:
            usable, reason = False, "Action spent."
        if impl.get("check"):
            ok, why = impl["check"](registry, combat, actor)
            if not ok:
                usable, reason = False, why
        out.append({"id": aid, "name": impl.get("name", feat["name"]),
                    "action": action_kind, "uses_left": left,
                    "usable": usable, "reason": reason,
                    "needs_target": impl.get("needs_target", False),
                    "options": _ability_options(registry, combat, actor,
                                                impl)})
    return out


def use_ability(registry, combat, actor, aid, target=None, option=None):
    impl = ABILITY_IMPL[aid]
    fid = impl["feature"]
    char = actor["char"]
    feat = registry["features"][fid]
    action_kind = impl.get("action", feat.get("action", "action"))
    if impl.get("check"):
        ok, why = impl["check"](registry, combat, actor)
        if not ok:
            return {"ok": False, "reason": why}
    legal_options = _ability_options(registry, combat, actor, impl)
    if impl.get("option_required") and option is None:
        return {"ok": False, "reason": "Choose an option."}
    if option is not None and option not in legal_options:
        return {"ok": False, "reason": "Not an available option."}
    # the feature use is CHECKED here but not spent until the ability
    # actually resolves: a refused resolution (empty pool, no target, ...)
    # must NOT eat the use or the Action/Bonus Action (#16.1 -- never
    # pre-commit before resolution)
    use_based = not impl.get("resource") and not impl.get("free_use")
    if use_based:
        left = _uses_left(registry, char, fid)
        if left is not None and left <= 0:
            return {"ok": False, "reason": "No uses left."}
    result = impl["run"](registry, combat, actor, target, option) \
        or {"ok": True}
    if not result.get("ok", True):
        return result
    # committed and resolved: spend the use and the Action / Bonus Action
    if use_based and _uses_left(registry, char, fid) is not None:
        _spend_use(char, fid)
    if action_kind == "action":
        actor["acted"]["action"] = True
    elif action_kind == "bonus":
        actor["acted"]["bonus"] = True
    return result


def _run_second_wind(registry, combat, actor, target, option=None):
    """Bonus Action, heal 1d10 + Fighter level (#7.1 L405-407)."""
    from core import combat as cb
    amount = dice.d(10) + actor["char"]["level"]
    cb.heal(registry, combat, actor, actor, amount)
    cb.log(combat, "%s uses Second Wind." % actor["name"])


def _check_action_spent(registry, combat, actor):
    if not actor["acted"]["action"]:
        return False, "Use your Action first - the Surge refreshes it."
    return True, None


def _run_action_surge(registry, combat, actor, target, option=None):
    """One extra Action this turn; it cannot be used to cast a spell
    (#7.1 L409-410). The button enables only after the Action is spent,
    so the surged action is always the marked one."""
    actor["acted"]["action"] = False
    actor["flags"]["surge_extra"] = True
    from core import combat as cb
    cb.log(combat, "%s surges with action!" % actor["name"])


def _run_rage(registry, combat, actor, target, option=None):
    """#7.5 L560-564."""
    actor["flags"]["raging"] = True
    from core import combat as cb
    cb.log(combat, "%s rages!" % actor["name"])


def _run_lay_on_hands(registry, combat, actor, target, option=None):
    """Spend 5 from the pool (UI granularity for P2; #7.9 L736-740).
    Ordinary Healing -- cannot revive."""
    from core import combat as cb
    char = actor["char"]
    pool = char["resources"].get("lay_on_hands_pool", 0)
    spend = min(5, pool)
    if spend <= 0:
        return {"ok": False, "reason": "The pool is empty."}
    healed = cb.heal(registry, combat, actor, target or actor, spend,
                     heal_type="healing")
    if healed is None:
        return {"ok": False,
                "reason": "Healing cannot revive a Downed character."}
    char["resources"]["lay_on_hands_pool"] = pool - spend
    return {"ok": True}


def _open_hand_options(registry, combat, actor):
    """Flurry rider menu, present once the technique is known (#7.11
    L834-837)."""
    if not ch.has_feature(actor["char"], "monk_open_hand_technique"):
        return []
    feat = registry["features"]["monk_open_hand_technique"]
    return [o["id"] for o in feat["options"]]


def _open_hand_apply(registry, combat, actor, target, option):
    """Open Hand Technique, applied per Flurry hit (#7.11 L834-837).
    The doc names no save DC for Push/Stagger (the Stunning Strike
    presentation at #7.11 L839-841 names none either): per GAPS G-027 the
    feature uses 8 + proficiency + Wisdom modifier until the owner
    answers."""
    from core import combat as cb
    if not cb.standing(target):
        return
    char = actor["char"]
    dc = 8 + ch.proficiency(char) + ch.ability_mod(char, "wis")
    if option == "addle":
        # no save: no Reactions or opportunity attacks until its next turn
        # (combat._can_react reads the flag; the universal turn-start hook
        # clears it)
        target["flags"]["addled"] = True
        cb.log(combat, "%s is addled." % target["name"])
    elif option == "push":
        if target["lane"] != "front":
            return
        result = cb.saving_throw(registry, combat, target, "str", dc)
        if not result["success"]:
            cb.move_lane(registry, combat, target, "back", forced=True)
    elif option == "stagger":
        result = cb.saving_throw(registry, combat, target, "dex", dc)
        if not result["success"]:
            # Staggered lasts until the start of the source's next turn
            # (#5.6 L313)
            cb.apply_condition(registry, combat, target, "staggered",
                               source=actor,
                               data={"until": "source_next_turn"})


def _run_flurry(registry, combat, actor, target, option=None):
    """Flurry of Blows: 1 Focus Point, Bonus Action, two UNARMED strikes
    (#7.11 L822-823) -- the Martial Arts die, never the held weapon.
    option: an Open Hand technique imposed per hit (#7.11 L834-837)."""
    from core import combat as cb
    char = actor["char"]
    if char["resources"].get("focus_points", 0) < 1:
        return {"ok": False, "reason": "No Focus Points."}
    char["resources"]["focus_points"] -= 1
    for _ in range(2):
        if target and cb.standing(target):
            result = cb.attack(registry, combat, actor, target,
                               unarmed=True)
            if option and result.get("hit"):
                _open_hand_apply(registry, combat, actor, target, option)
    return {"ok": True}


def _check_attack_taken(registry, combat, actor):
    """Martial Arts gate: 'after taking the Attack action' (#7.11 L819);
    player_attack sets the flag, the next turn start clears it."""
    if not actor["flags"].get("attack_action_taken"):
        return False, "Take the Attack action first."
    return True, None


def _run_bonus_unarmed(registry, combat, actor, target, option=None):
    """Martial Arts: one unarmed strike as a Bonus Action after the
    Attack action (#7.11 L817-819)."""
    from core import combat as cb
    if target is None or not cb.standing(target):
        return {"ok": False, "reason": "No target."}
    return cb.attack(registry, combat, actor, target, unarmed=True)


def _run_patient_defense(registry, combat, actor, target, option=None):
    char = actor["char"]
    if char["resources"].get("focus_points", 0) < 1:
        return {"ok": False, "reason": "No Focus Points."}
    char["resources"]["focus_points"] -= 1
    actor["flags"]["patient_defense"] = True
    return {"ok": True}


def _run_step_of_wind(registry, combat, actor, target, option=None):
    from core import combat as cb
    char = actor["char"]
    if char["resources"].get("focus_points", 0) < 1:
        return {"ok": False, "reason": "No Focus Points."}
    char["resources"]["focus_points"] -= 1
    dest = "back" if actor["lane"] == "front" else "front"
    return cb.move_lane(registry, combat, actor, dest, free=True)


def _run_slip(registry, combat, actor, target, option=None):
    """Cunning Action -- Slip: change lanes without provoking (#7.2
    L445-446)."""
    from core import combat as cb
    dest = "back" if actor["lane"] == "front" else "front"
    return cb.move_lane(registry, combat, actor, dest, free=True)


def _check_backline(registry, combat, actor):
    if actor["lane"] != "back":
        return False, "Backline only."
    return True, None


def _run_hide(registry, combat, actor, target, option=None):
    """Cunning Action -- Hide: if you are in your Backline, gain Hidden
    (#7.2 L446-447; the condition per #5.6 L317)."""
    from core import combat as cb
    if not cb.apply_condition(registry, combat, actor, "hidden",
                              source=actor):
        return {"ok": False, "reason": "Backline only."}
    return {"ok": True}


def _run_steady_aim(registry, combat, actor, target, option=None):
    """Steady Aim (#7.2 L448-449): advantage on your next attack this
    turn (consumed by the attack_declared hook); no lane change this turn
    (the guard in combat.player_move). Both flags clear at the owner's
    next turn start."""
    actor["flags"]["steady_aim_adv"] = True
    actor["flags"]["no_move_this_turn"] = True
    return {"ok": True}


# --- Cleric Channel Divinity (#7.3 L483-490) -------------------------------

def _divine_spark_amount(registry, actor):
    """1d8 + Wisdom modifier; 2d8 at level 7 (#7.3 L485-487)."""
    feat = registry["features"]["cleric_channel_divinity"]
    opt = [o for o in feat["options"] if o["id"] == "divine_spark"][0]
    dice_str = reg.by_level(opt["by_level"], actor["char"]["level"])
    return dice.roll(dice_str) + ch.ability_mod(actor["char"], "wis")


def _channel_left(actor):
    return actor["char"]["resources"].get("channel_divinity", 0)


def _run_divine_spark_heal(registry, combat, actor, target, option=None):
    """Divine Spark, healing mode (#7.3 L485-487): one target at range,
    1d8 + Wis; ordinary Healing -- it cannot revive."""
    from core import combat as cb
    if _channel_left(actor) < 1:
        return {"ok": False, "reason": "No Channel Divinity left."}
    tgt = target or actor
    if tgt["dead"] or tgt["downed"]:
        return {"ok": False,
                "reason": "Healing cannot revive a Downed character."}
    actor["char"]["resources"]["channel_divinity"] -= 1
    amount = _divine_spark_amount(registry, actor)
    cb.heal(registry, combat, actor, tgt, amount, heal_type="healing")
    cb.log(combat, "%s channels a Divine Spark." % actor["name"])
    return {"ok": True}


def _run_divine_spark_damage(registry, combat, actor, target, option=None):
    """Divine Spark, damage mode (#7.3 L485-487): the same amount as
    necrotic or radiant damage, Constitution save for half. The doc names
    no DC for Channel Divinity saves: per GAPS G-028 it uses the spell
    save DC formula (#2.7 L74) until the owner answers."""
    from core import combat as cb
    char = actor["char"]
    if _channel_left(actor) < 1:
        return {"ok": False, "reason": "No Channel Divinity left."}
    char["resources"]["channel_divinity"] -= 1
    amount = _divine_spark_amount(registry, actor)
    dc = rules.spell_save_dc(ch.proficiency(char),
                             ch.ability_mod(char, "wis"))
    result = cb.saving_throw(registry, combat, target, "con", dc)
    if result["success"]:
        amount //= 2
    if amount > 0:
        cb.deal_damage(registry, combat, actor, target, amount,
                       option or "radiant", tags=["channel_divinity"])
    cb.log(combat, "%s channels a searing Divine Spark." % actor["name"])
    return {"ok": True}


def _run_turn_undead(registry, combat, actor, target, option=None):
    """Turn Undead (#7.3 L488-490): every Undead in both enemy lanes makes
    a Wisdom save or is Turned; Turned frontline undead flee backward.
    Undead check via statblock tags (combat._is_undead) -- a harmless
    no-op against the wolf roster. Save DC per GAPS G-028; Turned lasts
    until it takes damage (#5.6 L318; duration GAPS G-029)."""
    from core import combat as cb
    char = actor["char"]
    if _channel_left(actor) < 1:
        return {"ok": False, "reason": "No Channel Divinity left."}
    char["resources"]["channel_divinity"] -= 1
    dc = rules.spell_save_dc(ch.proficiency(char),
                             ch.ability_mod(char, "wis"))
    side = "enemy" if actor["side"] == "party" else "party"
    cb.log(combat, "%s presents their holy symbol!" % actor["name"])
    for c in cb.combatants_on(combat, side):
        if not cb._is_undead(c):
            continue
        result = cb.saving_throw(registry, combat, c, "wis", dc)
        if not result["success"]:
            applied = cb.apply_condition(registry, combat, c, "turned",
                                         source=actor)
            if applied and c["lane"] == "front":
                cb.move_lane(registry, combat, c, "back", forced=True)
    return {"ok": True}


# --- Druid Aspects (#7.10 L766-778) ----------------------------------------

def _known_aspects(registry, combat, actor):
    return list(actor["char"]["class_picks"].get("aspects", []))


def _run_aspect(registry, combat, actor, target, option=None):
    """Assume an Aspect (#7.10 L766-778): Bonus Action, spends an Aspect
    use (the druid_aspects feature pool), sets flags aspect=<name>.
    Bear grants temp HP = 2 x level; Stag sets +2 AC and a free lane
    change (re-granted each turn by the turn_start hook). Leveled casting
    is blocked while active (gates in castable_spells/cast_spell); the
    hp_zero hook ends the Aspect when Downed."""
    from core import combat as cb
    char = actor["char"]
    actor["flags"].pop("ac_bonus", None)
    actor["flags"]["aspect"] = option
    if option == "bear":
        cb.grant_temp_hp(combat, actor, 2 * char["level"])  # L772
    elif option == "stag":
        actor["flags"]["ac_bonus"] = 2                      # L778
        actor["flags"]["free_move_available"] = True
        actor["flags"]["free_move_no_provoke"] = True       # L778
    cb.log(combat, "%s assumes the Aspect of the %s."
           % (actor["name"], option.capitalize()))
    return {"ok": True}


def _check_aspect(name):
    def check(registry, combat, actor):
        if actor["flags"].get("aspect") != name:
            return False, "Requires the %s Aspect." % name.capitalize()
        return True, None
    return check


def _aspect_attack(registry, combat, actor, target, dice_str, dtype, melee,
                   fang_poison=False):
    """A natural Aspect attack (#7.10 L772-777): the doc states the damage
    (die + Wisdom modifier); to-hit follows the standard attack formula
    (#2.4 L70-72) with the Aspect's Wisdom -- damage types per GAPS
    G-030. Runs the full event pipeline like a weapon attack."""
    from core import combat as cb
    if target is None:
        return {"ok": False, "reason": "No target."}
    ok, reason = cb.targetable(combat, actor, target, melee)
    if not ok:
        return {"ok": False, "reason": reason}
    char = actor["char"]
    wis = ch.ability_mod(char, "wis")
    ctx = cb.fire(registry, combat, "attack_declared",
                  {"attacker": actor["cid"], "target": target["cid"],
                   "melee": melee, "opportunity": False, "weapon": None,
                   "ability": "wis", "adv": [], "dis": [],
                   "bonus_damage": [], "crit_range": 20,
                   "to_hit_bonus": 0})
    advantage, adv_src, dis_src = cb._advantage_state(
        registry, combat, actor, target, melee, ctx)
    # reveal AFTER reading the advantage state, or attacking out of Hidden
    # loses its promised advantage (#5.6 L317)
    if "hidden" in actor["conditions"]:
        cb.remove_condition(registry, combat, actor, "hidden")
    kept, _rolls = dice.d20(advantage)
    total = kept + wis + ch.proficiency(char) + ctx.get("to_hit_bonus", 0)
    ac = cb._ac_of(registry, combat, target)
    crit = kept >= ctx.get("crit_range", 20)
    hit = kept != 1 and (kept == 20 or total >= ac)
    if not hit:
        cb.fire(registry, combat, "attack_miss",
                {"attacker": actor["cid"], "target": target["cid"],
                 "weapon": None, "ctx": ctx})
        cb.float_text(combat, target["cid"], "Miss", "miss")
        cb.log(combat, "%s misses %s." % (actor["name"], target["name"]))
        return {"ok": True, "hit": False, "crit": False}
    if crit:
        cb.fire(registry, combat, "crit",
                {"attacker": actor["cid"], "target": target["cid"]})
        cb.float_text(combat, target["cid"], "CRIT!", "crit")
    hit_ctx = cb.fire(registry, combat, "attack_hit",
                      {"attacker": actor["cid"], "target": target["cid"],
                       "melee": melee, "crit": crit, "weapon": None,
                       "ability": "wis",
                       "bonus_damage": list(ctx.get("bonus_damage", [])),
                       "damage_mod_bonus": 0, "min_die": 1,
                       "advantage_used": bool(adv_src) and not dis_src,
                       "disadvantage_used": bool(dis_src) and not adv_src})
    amount = cb._roll_damage(dice_str, crit,
                             min_die=hit_ctx.get("min_die", 1))
    amount += wis + hit_ctx.get("damage_mod_bonus", 0)
    for extra in hit_ctx.get("bonus_damage", []):
        amount += cb._roll_damage(extra["dice"],
                                  crit and extra.get("crits", True))
    cb.deal_damage(registry, combat, actor, target, max(0, amount), dtype,
                   tags=["attack", "melee" if melee else "ranged", "aspect"])
    if fang_poison and cb.standing(target):
        # Serpent: Constitution save or Poisoned (#7.10 L776-777); the
        # condition repeats its save at the end of its turns (#5.6 L316).
        # DC per GAPS G-028.
        dc = rules.spell_save_dc(ch.proficiency(char), wis)
        result = cb.saving_throw(registry, combat, target, "con", dc)
        if not result["success"]:
            cb.apply_condition(registry, combat, target, "poisoned",
                               source=actor,
                               data={"repeat_save": {"ability": "con",
                                                     "dc": dc}})
    return {"ok": True, "hit": True, "crit": crit}


def _run_claw(registry, combat, actor, target, option=None):
    """Bear claw: d8 + Wis, melee (#7.10 L772-773)."""
    return _aspect_attack(registry, combat, actor, target, "1d8",
                          "slashing", True)


def _run_talon(registry, combat, actor, target, option=None):
    """Hawk talon dive: d6 + Wis, ranged (#7.10 L774-775)."""
    return _aspect_attack(registry, combat, actor, target, "1d6",
                          "piercing", False)


def _run_fang(registry, combat, actor, target, option=None):
    """Serpent fang: d6 + Wis, melee; Con save or Poisoned (#7.10
    L776-777)."""
    return _aspect_attack(registry, combat, actor, target, "1d6",
                          "piercing", True, fang_poison=True)


def _run_innate_sorcery(registry, combat, actor, target, option=None):
    """Innate Sorcery (#7.12 L863-864): Bonus Action, 2 uses per Camp,
    lasts the fight -- +1 spell save DC and advantage on spell attack
    rolls (both consulted in _resolve_spell_on)."""
    from core import combat as cb
    actor["flags"]["innate_sorcery"] = True
    cb.log(combat, "%s unleashes their innate sorcery." % actor["name"])
    return {"ok": True}


# ability id -> impl; "feature" names the owning registry feature (the
# ability shows when the character has it). "name" overrides the label for
# option-spends like the Monk's Focus menu. "options" lists/derives the
# legal option parameter values; "free_use" marks abilities that ride a
# feature without spending its uses (Aspect attacks).
ABILITY_IMPL = {
    "fighter_second_wind": {"feature": "fighter_second_wind",
                            "action": "bonus", "run": _run_second_wind},
    "fighter_action_surge": {"feature": "fighter_action_surge",
                             "action": "free", "run": _run_action_surge,
                             "check": _check_action_spent},
    "barbarian_rage": {"feature": "barbarian_rage", "action": "bonus",
                       "run": _run_rage},
    "paladin_lay_on_hands": {"feature": "paladin_lay_on_hands",
                             "action": "bonus", "run": _run_lay_on_hands,
                             "needs_target": True},
    # Martial Arts Bonus-Action unarmed strike (#7.11 L817-819)
    "monk_unarmed_strike": {"feature": "monk_martial_arts",
                            "name": "Unarmed Strike", "action": "bonus",
                            "run": _run_bonus_unarmed, "needs_target": True,
                            "free_use": True,
                            "check": _check_attack_taken},
    "monk_flurry_of_blows": {"feature": "monk_monks_focus",
                             "name": "Flurry of Blows", "action": "bonus",
                             "run": _run_flurry, "needs_target": True,
                             "resource": "focus_points",
                             "options": _open_hand_options},
    "monk_patient_defense": {"feature": "monk_monks_focus",
                             "name": "Patient Defense", "action": "bonus",
                             "run": _run_patient_defense,
                             "resource": "focus_points"},
    "monk_step_of_the_wind": {"feature": "monk_monks_focus",
                              "name": "Step of the Wind", "action": "bonus",
                              "run": _run_step_of_wind,
                              "resource": "focus_points"},
    # Cunning Action (#7.2 L445-447) + Steady Aim (#7.2 L448-449)
    "rogue_slip": {"feature": "rogue_cunning_action", "name": "Slip",
                   "action": "bonus", "run": _run_slip},
    "rogue_hide": {"feature": "rogue_cunning_action", "name": "Hide",
                   "action": "bonus", "run": _run_hide,
                   "check": _check_backline},
    "rogue_steady_aim": {"feature": "rogue_steady_aim", "action": "bonus",
                         "run": _run_steady_aim},
    # Channel Divinity options share the channel_divinity resource pool
    # (#7.3 L483-490)
    "cleric_divine_spark_heal": {"feature": "cleric_channel_divinity",
                                 "name": "Divine Spark (heal)",
                                 "action": "action", "needs_target": True,
                                 "resource": "channel_divinity",
                                 "run": _run_divine_spark_heal},
    "cleric_divine_spark_damage": {"feature": "cleric_channel_divinity",
                                   "name": "Divine Spark (smite)",
                                   "action": "action", "needs_target": True,
                                   "resource": "channel_divinity",
                                   "options": ("radiant", "necrotic"),
                                   "option_required": True,
                                   "run": _run_divine_spark_damage},
    "cleric_turn_undead": {"feature": "cleric_channel_divinity",
                           "name": "Turn Undead", "action": "action",
                           "resource": "channel_divinity",
                           "run": _run_turn_undead},
    # Aspects (#7.10 L766-778): activation spends a druid_aspects use;
    # the attacks are free while the matching Aspect is active
    "druid_aspect": {"feature": "druid_aspects", "name": "Assume Aspect",
                     "action": "bonus", "options": _known_aspects,
                     "option_required": True, "run": _run_aspect},
    "druid_claw": {"feature": "druid_aspects", "name": "Claw (Bear)",
                   "action": "action", "needs_target": True,
                   "free_use": True, "check": _check_aspect("bear"),
                   "run": _run_claw},
    "druid_talon": {"feature": "druid_aspects", "name": "Talon (Hawk)",
                    "action": "action", "needs_target": True,
                    "free_use": True, "check": _check_aspect("hawk"),
                    "run": _run_talon},
    "druid_fang": {"feature": "druid_aspects", "name": "Fang (Serpent)",
                   "action": "action", "needs_target": True,
                   "free_use": True, "check": _check_aspect("serpent"),
                   "run": _run_fang},
    # Innate Sorcery (#7.12 L863-864)
    "sorcerer_innate_sorcery": {"feature": "sorcerer_innate_sorcery",
                                "action": "bonus",
                                "run": _run_innate_sorcery},
}


# ---------------------------------------------------------------------------
# spellcasting (structured tiers 0-2; riders per spell id)

def castable_spells(registry, combat, actor):
    """[{id, name, tier, castable, reason}] for the Spells button: cantrips
    + prepared + always-prepared, gated by slots and concentration rules."""
    if actor["kind"] != "pc":
        return []
    char = actor["char"]
    caster = ch.caster_info(registry, char)
    out = []
    seen = []
    pool = list(char["spells"]["cantrips"]) + \
        list(char["spells"]["prepared"]) + ch.always_prepared(registry, char)
    for sid in pool:
        if sid in seen:
            continue
        seen.append(sid)
        sp = registry["spells"][sid]
        usable, reason = True, None
        if sp.get("action", "action") == "action":
            if actor["acted"]["action"]:
                usable, reason = False, "Action spent."
            elif actor["flags"].get("surge_extra"):
                # the surged Action cannot cast a spell (#7.1 L409-410)
                usable, reason = False, "The surged Action can't cast."
        if sp["tier"] > 0:
            if not _slot_available(registry, char, sp["tier"]):
                usable, reason = False, "No slot."
            if actor["flags"].get("aspect"):
                # no leveled spells while an Aspect is active; cantrips
                # are fine (#7.10 L768-770)
                usable, reason = False, "Aspect active — leveled spells locked."
        if sp.get("action") == "camp":
            usable, reason = False, "Camp only."
        if usable and sid in SPELL_GATES:
            gate_ok, why = SPELL_GATES[sid](registry, combat, actor)
            if not gate_ok:
                usable, reason = False, why
        out.append({"id": sid, "name": sp["name"], "tier": sp["tier"],
                    "castable": usable, "reason": reason})
    return out


def _slot_available(registry, char, tier):
    caster = ch.caster_info(registry, char)
    if not caster:
        return False
    res = char["resources"]
    if caster["kind"] == "pact":
        return res.get("pact_slots", 0) > 0 and \
            ch.pact_tier(registry, char) >= tier
    slots = res.get("slots", {})
    return any(count > 0 for t, count in slots.items() if t >= tier)


def _spend_slot(registry, char, tier):
    """Lowest available slot of at least the spell's tier. Returns the
    tier actually spent (upcasting feeds on the difference, #9.3)."""
    caster = ch.caster_info(registry, char)
    res = char["resources"]
    if caster["kind"] == "pact":
        res["pact_slots"] -= 1
        return ch.pact_tier(registry, char)
    slots = res["slots"]
    for t in sorted(slots):
        if t >= tier and slots[t] > 0:
            slots[t] -= 1
            return t
    raise ValueError("no slot")


def cantrip_dice_count(registry, char):
    """1 die at level 1, 2 at 5, 3 at 11 (#9.3 L992-993)."""
    table = registry["upcast_rules"]["cantrip_dice_by_level"]
    return reg.by_level(table, char["level"])


def cast_spell(registry, combat, actor, spell_id, target=None, lane=None,
               option=None):
    """Resolve a structured spell (tiers 0-2 engine coverage). target: a
    combatant for single-target spells; lane: 'front'/'back' for
    Small-area spells (side from the spell record); option: a per-spell
    choice the UI supplies (Ironhide's resisted damage type, #9.6
    L1061)."""
    from core import combat as cb
    char = actor["char"]
    sp = registry["spells"][spell_id]
    if sp["tier"] > 0 and actor["flags"].get("aspect"):
        # Aspects block leveled casting; cantrips are fine (#7.10 L768-770)
        return {"ok": False, "reason": "Aspect active — leveled spells locked."}
    if spell_id in SPELL_GATES:
        gate_ok, why = SPELL_GATES[spell_id](registry, combat, actor)
        if not gate_ok:
            return {"ok": False, "reason": why}
    # the action economy is CHECKED here, but nothing is spent until the
    # cast is known to be legal: an illegal/empty target must NOT eat the
    # Action or the slot (#16.1 -- never pre-commit before resolution)
    action_kind = sp.get("action", "action")
    if action_kind == "action":
        if actor["acted"]["action"]:
            return {"ok": False, "reason": "Action spent."}
        if actor["flags"].get("surge_extra"):
            # #7.1 L409-410: the extra Action cannot be used to cast
            return {"ok": False, "reason": "The surged Action can't cast."}
    elif action_kind == "bonus":
        if actor["acted"]["bonus"]:
            return {"ok": False, "reason": "Bonus Action spent."}

    # validate targets BEFORE committing anything (_spell_targets is pure)
    targets = _spell_targets(registry, combat, actor, sp, target, lane)
    if not targets:
        return {"ok": False, "reason": "No valid target."}

    # committed and legal: now spend the Action / Bonus Action and the slot
    if action_kind == "action":
        actor["acted"]["action"] = True
    elif action_kind == "bonus":
        actor["acted"]["bonus"] = True

    tier_cast = sp["tier"]
    if sp["tier"] > 0:
        tier_cast = _spend_slot(registry, char, sp["tier"])
    cb.fire(registry, combat, "cast_declared",
            {"caster": actor["cid"], "spell": spell_id, "tier": tier_cast})

    if sp.get("concentration"):
        cb.break_concentration(registry, combat, actor)
        # riders/effects/summons register here so break_concentration can
        # clean up everything the spell put in play (#5.6 L321)
        actor["concentration"] = {"spell": spell_id, "name": sp["name"],
                                  "targets": [], "condition": None,
                                  "effects": [], "summon": None}

    caster_info = ch.caster_info(registry, char)
    cast_mod = ch.ability_mod(char, caster_info["ability"]) if caster_info \
        else 0
    prof = ch.proficiency(char)
    dc = rules.spell_save_dc(prof, cast_mod)
    atk_bonus = rules.spell_attack_bonus(prof, cast_mod)

    if sp.get("area"):
        # lane-wide effects still hit a Hidden combatant and REVEAL it
        # (#5.6 L317)
        for tgt in targets:
            if "hidden" in tgt["conditions"]:
                cb.remove_condition(registry, combat, tgt, "hidden")

    upcast_steps = max(0, tier_cast - sp["tier"]) if sp["tier"] else 0
    resolver = SPELL_RESOLVERS.get(spell_id)
    if resolver is not None:
        results = resolver(registry, combat, actor, sp, targets, lane,
                           dc, upcast_steps)
    else:
        results = []
        for tgt in targets:
            results.append(_resolve_spell_on(registry, combat, actor, sp,
                                             tgt, dc, atk_bonus, cast_mod,
                                             upcast_steps, option))
    cb.fire(registry, combat, "cast_resolved",
            {"caster": actor["cid"], "spell": spell_id, "tier": tier_cast})
    cb.log(combat, "%s casts %s." % (actor["name"], sp["name"]))
    return {"ok": True, "results": results, "tier": tier_cast}


def _is_humanoid(c):
    """PCs are humanoid; enemies declare it with a 'humanoid' statblock
    tag (the wolf roster carries none -- correctly immune)."""
    if c["kind"] == "pc":
        return True
    return "humanoid" in (c["stats"].get("tags") or [])


# "One humanoid" target restriction: Hold Person (#9.6 L1065) and
# Beguile (#9.5 L1046).
HUMANOID_ONLY_SPELLS = ("hold_person", "beguile")


def _spell_targets(registry, combat, actor, sp, target, lane):
    from core import combat as cb
    override = SPELL_TARGET_OVERRIDES.get(sp["id"])
    if override is not None:
        return override(registry, combat, actor)
    area = sp.get("area")
    if area:
        side = ("enemy" if actor["side"] == "party" else "party") \
            if area["side"] == "enemies" else actor["side"]
        if area["size"] == "large":
            return cb.combatants_on(combat, side)
        return cb.combatants_on(combat, side, lane or "front")
    if target is None:
        return [actor] if sp["range"] == "self" else []
    if target["dead"] or (target["downed"] and
                          "true_heal" not in sp["roles"]):
        return []
    if "hidden" in target["conditions"]:
        return []
    if sp["id"] in HUMANOID_ONLY_SPELLS and not _is_humanoid(target):
        return []
    if sp["range"] == "touch":
        # Touch: melee reach against enemies; an ally in your own lane
        # (#9.1 L965)
        if target["side"] == actor["side"]:
            if target["lane"] != actor["lane"] and target is not actor:
                return []
        elif not cb.melee_reach(combat, actor, target):
            return []
    return [target]


def _resolve_spell_on(registry, combat, actor, sp, tgt, dc, atk_bonus,
                      cast_mod, upcast_steps, option=None):
    from core import combat as cb
    char = actor["char"]
    hit, save_ok = True, None

    if actor["flags"].get("innate_sorcery"):
        dc += 1   # Innate Sorcery: +1 to your spell save DCs (#7.12 L863-864)

    if sp.get("attack"):
        # Innate Sorcery: advantage on your spell attack rolls (#7.12
        # L863-864)
        adv = 1 if actor["flags"].get("innate_sorcery") else 0
        kept, _rolls = dice.d20(adv)
        total = kept + atk_bonus
        ac = cb._ac_of(registry, combat, tgt)
        hit = kept != 1 and (kept == 20 or total >= ac)
        if not hit:
            cb.float_text(combat, tgt["cid"], "Miss", "miss")

    if sp.get("save"):
        result = cb.saving_throw(registry, combat, tgt,
                                 sp["save"]["ability"], dc)
        save_ok = result["success"]

    if sp.get("damage") and hit:
        dmg = sp["damage"]
        entries = dmg if isinstance(dmg, list) else [dmg]
        for entry in entries:
            count, sides, flat = dice.parse(entry["dice"]) \
                if "d" in entry["dice"] else (0, 0, int(entry["dice"]))
            if sp["tier"] == 0:
                count *= cantrip_dice_count(registry, char)
            else:
                count += upcast_steps      # +1 die per tier (#9.3 L986)
            total = sum(dice.d(sides) for _ in range(count)) + flat
            total += _spell_damage_bonus(registry, actor, sp)
            if save_ok and sp["save"] and \
                    sp["save"].get("on_success") == "half":
                total //= 2
            if save_ok and sp["save"] and \
                    sp["save"].get("on_success") == "negates":
                total = 0
            if total > 0:
                cb.deal_damage(registry, combat, actor, tgt, total,
                               entry["type"], tags=["spell"])

    if sp.get("heal") and hit:
        amount = 0
        if "dice" in sp["heal"]:
            count, sides, flat = dice.parse(sp["heal"]["dice"])
            count += upcast_steps          # +1 die per tier (#9.3 L987)
            amount = sum(dice.d(sides) for _ in range(count)) + flat
        elif "flat" in sp["heal"]:
            amount = sp["heal"]["flat"]
        if sp["heal"].get("plus_casting_mod"):
            amount += cast_mod
        heal_type = "true_healing" if "true_heal" in sp["roles"] \
            else "healing"
        # combat.heal marks the source as a healer this combat (G-025);
        # no need to set the flag here too
        cb.heal(registry, combat, actor, tgt, amount, heal_type)

    rider = SPELL_RIDERS.get(sp["id"])
    if rider and hit and (save_ok is None or not save_ok or
                          rider.get("on_save_too")):
        rider["apply"](registry, combat, actor, tgt,
                       {"spell": sp, "dc": dc, "option": option,
                        "upcast_steps": upcast_steps})
    return {"target": tgt["cid"], "hit": hit, "save_ok": save_ok}


def _rider_condition(cond_id, until="source_next_turn"):
    """Apply a condition rider. Reads the spell record's save.repeating
    into the condition's repeat_save data ('repeating', #9.6 L1063/L1065,
    #9.5 L1048; Paralyzed/Poisoned repeat per #5.6 L309/L316) and
    registers concentration spells' targets on the caster's concentration
    entry so break_concentration cleans them up (#5.6 L321)."""
    def apply(registry, combat, actor, tgt, cast):
        from core import combat as cb
        sp = cast["spell"]
        data = {"until": until}
        save = sp.get("save") or {}
        if save.get("repeating"):
            data["repeat_save"] = {"ability": save["ability"],
                                   "dc": cast["dc"]}
        applied = cb.apply_condition(registry, combat, tgt, cond_id,
                                     source=actor, data=data)
        if applied and sp.get("concentration") and actor["concentration"] \
                and actor["concentration"].get("spell") == sp["id"]:
            conc = actor["concentration"]
            conc["condition"] = cond_id
            if tgt["cid"] not in conc["targets"]:
                conc["targets"].append(tgt["cid"])
    return {"apply": apply}


def _rider_no_heal():
    """Gravewhisper: no HP regained until the start of the caster's next
    turn (#9.4 L1020) -- combat.heal reads no_heal_src and
    tick_source_turn_start expires it by source cid."""
    def apply(registry, combat, actor, tgt, cast):
        tgt["flags"]["no_heal_src"] = actor["cid"]
    return {"apply": apply}


def _rider_flag(flag):
    """Set a consumable flag on the target: Cutting Quip's disadvantage on
    its next attack rides the universal Sap consumer (#9.4 L1025); Spark
    Arc's no-Reactions rides 'addled', cleared at the target's next turn
    start (#9.4 L1019)."""
    def apply(registry, combat, actor, tgt, cast):
        tgt["flags"][flag] = True
    return {"apply": apply}


def _rider_pull():
    def apply(registry, combat, actor, tgt, cast):
        from core import combat as cb
        if tgt["lane"] == "back":
            cb.move_lane(registry, combat, tgt, "front", forced=True)
    return {"apply": apply}


def _rider_push_back():
    def apply(registry, combat, actor, tgt, cast):
        from core import combat as cb
        if tgt["lane"] == "front":
            cb.move_lane(registry, combat, tgt, "back", forced=True)
    return {"apply": apply}


def _rider_lash():
    """Repelling Lash / Grasping Lash (#7.7 L650-652): once per turn each,
    an Eldritch Lash hit pushes the target to its Backline / pulls it to
    its Frontline. With both invocations known the target's current lane
    decides which applies (GAPS G-031)."""
    def apply(registry, combat, actor, tgt, cast):
        from core import combat as cb
        if actor["kind"] != "pc" or not cb.standing(tgt):
            return
        invs = actor["char"]["class_picks"].get("invocations", [])
        key = _turn_key(combat)
        if tgt["lane"] == "front" and "repelling_lash" in invs and \
                actor["flags"].get("repelling_used_turn") != key:
            actor["flags"]["repelling_used_turn"] = key
            cb.move_lane(registry, combat, tgt, "back", forced=True)
        elif tgt["lane"] == "back" and "grasping_lash" in invs and \
                actor["flags"].get("grasping_used_turn") != key:
            actor["flags"]["grasping_used_turn"] = key
            cb.move_lane(registry, combat, tgt, "front", forced=True)
    return {"apply": apply}


def _rider_ac_mod(amount, expires=None):
    """A target-scoped AC delta consulted by combat._ac_of: Warding Aegis
    +2 (#9.5 L1042), Rend Bolt -1 until the end of its next turn (#9.6
    L1054)."""
    def apply(registry, combat, actor, tgt, cast):
        data = {"amount": amount}
        if expires:
            data["expires"] = expires
        add_effect(registry, combat, actor, cast["spell"], "ac_mod",
                   target=tgt["cid"], data=data)
    return {"apply": apply}


def _rider_ironhide():
    """Ironhide: 2d8 temporary HP and resistance to one damage type
    (#9.6 L1061); the resisted type is the cast's option (UI choice)."""
    def apply(registry, combat, actor, tgt, cast):
        from core import combat as cb
        cb.grant_temp_hp(combat, tgt, dice.roll("2d8"))
        rtype = cast.get("option") or "slashing"
        add_effect(registry, combat, actor, cast["spell"], "resist",
                   target=tgt["cid"], data={"type": rtype})
    return {"apply": apply}


def _rider_haste():
    """Haste of the Quick: one free lane change each turn (granted at the
    target's turn starts) and +2 AC (#9.6 L1062)."""
    def apply(registry, combat, actor, tgt, cast):
        add_effect(registry, combat, actor, cast["spell"], "ac_mod",
                   target=tgt["cid"], data={"amount": 2})
        add_effect(registry, combat, actor, cast["spell"], "haste",
                   target=tgt["cid"], data={})
        tgt["flags"]["free_move_available"] = True
    return {"apply": apply}


def _rider_enfeeble():
    """Enfeeble: the target deals half damage with its attacks
    (Constitution save, repeating) (#9.6 L1063). Halving rides the
    damage_dealt ctx; the repeat save ticks at the target's turn ends."""
    def apply(registry, combat, actor, tgt, cast):
        save = cast["spell"].get("save") or {}
        data = {}
        if save.get("repeating"):
            data["repeat_save"] = {"ability": save["ability"],
                                   "dc": cast["dc"]}
        add_effect(registry, combat, actor, cast["spell"], "half_damage",
                   target=tgt["cid"], data=data)
    return {"apply": apply}


def _rider_mark():
    """Quarry's Mark: flag the target (the 'marked' intent selector reads
    it) and add +1d6 to the caster's weapon attacks against it
    (#9.5 L1044)."""
    def apply(registry, combat, actor, tgt, cast):
        tgt["flags"]["quarry_mark"] = True
        add_effect(registry, combat, actor, cast["spell"], "mark",
                   target=tgt["cid"], data={})
    return {"apply": apply}


def _rider_vital_surge():
    """Vital Surge: +5 maximum and current HP for the fight, no
    concentration (#9.6 L1060); finish_combat clamps back to the stored
    maximum."""
    def apply(registry, combat, actor, tgt, cast):
        tgt["hp_max"] += 5
        tgt["hp"] += 5
    return {"apply": apply}


# ---------------------------------------------------------------------------
# ongoing-effects layer (#9.5/#9.6 buff/debuff/control rows): a minimal
# combat["effects"] list whose entries are consulted at the existing
# pipeline ctx points. Concentration effects register on the caster's
# concentration entry; break_concentration removes them (#5.6 L321).

def add_effect(registry, combat, actor, sp, kind, lane=None, side=None,
               target=None, data=None):
    combat.setdefault("effects", [])
    seq = combat.get("effect_seq", 0) + 1
    combat["effect_seq"] = seq
    eff = {"id": seq, "spell": sp["id"], "source": actor["cid"],
           "kind": kind, "lane": lane, "side": side, "target": target,
           "data": data or {}}
    combat["effects"].append(eff)
    if sp.get("concentration") and actor.get("concentration") and \
            actor["concentration"].get("spell") == sp["id"]:
        actor["concentration"].setdefault("effects", []).append(seq)
    return eff


def remove_effect(registry, combat, effect_id):
    for eff in list(combat.get("effects", ())):
        if eff["id"] != effect_id:
            continue
        combat["effects"].remove(eff)
        tgt = combat["combatants"].get(eff.get("target"))
        if tgt is not None:
            if eff["kind"] == "mark":
                tgt["flags"].pop("quarry_mark", None)
            elif eff["kind"] == "haste":
                tgt["flags"].pop("free_move_available", None)
        return True
    return False


def effects_on_event(registry, combat, event, ctx):
    """Consult/advance every ongoing effect at one pipeline ctx point;
    called by combat.fire before the feature hooks run."""
    effects = combat.get("effects")
    if not effects:
        return
    from core import combat as cb
    for eff in list(effects):
        kind = eff["kind"]
        if event == "attack_declared" and kind == "lane_roll_mod":
            # Benediction +1d4 / Malediction -1d4 to attack rolls
            # (#9.5 L1041 / L1045)
            attacker = combat["combatants"].get(ctx.get("attacker"))
            if attacker and attacker["side"] == eff["side"] and \
                    attacker["lane"] == eff["lane"]:
                roll = dice.roll(eff["data"]["dice"])
                ctx["to_hit_bonus"] = ctx.get("to_hit_bonus", 0) + \
                    eff["data"]["sign"] * roll
        elif event == "save_prompted" and kind == "lane_roll_mod":
            # ... and to saves (#9.5 L1041 / L1045)
            target = combat["combatants"].get(ctx.get("target"))
            if target and target["side"] == eff["side"] and \
                    target["lane"] == eff["lane"]:
                roll = dice.roll(eff["data"]["dice"])
                ctx["save_bonus"] = ctx.get("save_bonus", 0) + \
                    eff["data"]["sign"] * roll
        elif event == "attack_hit" and kind == "mark":
            # Quarry's Mark: the caster's weapon attacks against the
            # marked target deal +1d6 (#9.5 L1044)
            if ctx.get("attacker") == eff["source"] and \
                    ctx.get("target") == eff["target"]:
                ctx.setdefault("bonus_damage", []).append(
                    {"dice": "1d6", "crits": True, "label": "Quarry's Mark"})
        elif event == "damage_dealt" and kind == "half_damage":
            # Enfeeble: half damage with its attacks (#9.6 L1063)
            if ctx.get("source") == eff["target"] and \
                    "attack" in (ctx.get("tags") or []):
                ctx["amount"] = ctx["amount"] // 2
        elif event == "turn_start":
            actor = combat["combatants"].get(ctx.get("actor"))
            if actor is None:
                continue
            if kind == "haste" and eff["target"] == actor["cid"]:
                # one free lane change each turn (#9.6 L1062)
                actor["flags"]["free_move_available"] = True
            elif kind == "lane_tick" and actor["side"] == eff["side"] and \
                    actor["lane"] == eff["lane"] and cb.standing(actor):
                # Moonfire Column: 2d10 radiant, Con save for half, at the
                # start of each enemy turn in the lane (#9.6 L1055)
                data = eff["data"]
                amount = sum(dice.d(data["sides"])
                             for _ in range(data["count"]))
                result = cb.saving_throw(registry, combat, actor,
                                         data["save"], data["dc"])
                if result["success"]:
                    amount //= 2
                source = combat["combatants"].get(eff["source"])
                if amount > 0:
                    cb.deal_damage(registry, combat, source, actor, amount,
                                   data["type"], tags=["spell", "effect"])
        elif event == "turn_end" and eff.get("target") == ctx.get("actor"):
            if eff["data"].get("expires") == "target_turn_end":
                # Rend Bolt's -1 AC: until the end of its next turn
                # (#9.6 L1054)
                remove_effect(registry, combat, eff["id"])
            elif eff["data"].get("repeat_save"):
                # repeating saves tick at the end of the target's turns
                # (Enfeeble #9.6 L1063)
                spec = eff["data"]["repeat_save"]
                tgt = combat["combatants"].get(ctx["actor"])
                if tgt is None or not cb.standing(tgt):
                    continue
                result = cb.saving_throw(registry, combat, tgt,
                                         spec["ability"], spec["dc"])
                if result["success"]:
                    remove_effect(registry, combat, eff["id"])
        elif event == "line_changed" and kind == "lane_trap":
            # Spike Field: any enemy that changes lanes into or out of the
            # lane takes 4d4 piercing (#9.6 L1067)
            mover = combat["combatants"].get(ctx.get("mover"))
            if mover and mover["side"] == eff["side"] and \
                    (ctx.get("from") == eff["lane"] or
                     ctx.get("to") == eff["lane"]):
                source = combat["combatants"].get(eff["source"])
                amount = sum(dice.d(4) for _ in range(eff["data"]["count"]))
                cb.deal_damage(registry, combat, source, mover, amount,
                               "piercing", tags=["spell", "effect"])


# --- whole-cast resolvers (lane effects, Slumber's budget, summons) --------

def _lane_for(actor, sp, lane):
    """(side, lane) a Small-area spell lands on, mirroring _spell_targets."""
    side = ("enemy" if actor["side"] == "party" else "party") \
        if sp["area"]["side"] == "enemies" else actor["side"]
    return side, lane or "front"


def _results_for(targets):
    return [{"target": t["cid"], "hit": True, "save_ok": None}
            for t in targets]


def _resolver_lane_roll_mod(sign, src):
    """Benediction +1d4 / Malediction -1d4 to attack rolls and saves for
    one lane (#9.5 L1041 / L1045). Concentration."""
    def resolve(registry, combat, actor, sp, targets, lane, dc,
                upcast_steps):
        side, eff_lane = _lane_for(actor, sp, lane)
        add_effect(registry, combat, actor, sp, "lane_roll_mod",
                   lane=eff_lane, side=side,
                   data={"dice": "1d4", "sign": sign, "src": src})
        return _results_for(targets)
    return resolve


def _resolver_corrode(registry, combat, actor, sp, targets, lane, dc,
                      upcast_steps):
    """Corrode: one enemy lane, -2 AC for the duration (#9.6 L1064);
    consulted live by combat._ac_of, so lane membership tracks moves."""
    side, eff_lane = _lane_for(actor, sp, lane)
    add_effect(registry, combat, actor, sp, "ac_mod", lane=eff_lane,
               side=side, data={"amount": -2})
    return _results_for(targets)


def _resolver_moonfire(registry, combat, actor, sp, targets, lane, dc,
                       upcast_steps):
    """Moonfire Column: no damage on the cast -- 2d10 radiant (Con save
    for half) at the start of each enemy turn in the lane (#9.6 L1055);
    +1 die per upcast tier (#9.3 L986)."""
    side, eff_lane = _lane_for(actor, sp, lane)
    count, sides, _flat = dice.parse(sp["damage"]["dice"])
    add_effect(registry, combat, actor, sp, "lane_tick", lane=eff_lane,
               side=side,
               data={"count": count + upcast_steps, "sides": sides,
                     "type": sp["damage"]["type"],
                     "save": sp["save"]["ability"], "dc": dc})
    return _results_for(targets)


def _resolver_spike_field(registry, combat, actor, sp, targets, lane, dc,
                          upcast_steps):
    """Spike Field: the lane sprouts thorns; lane changes into or out of
    it cost 4d4 piercing (#9.6 L1067); +1 die per upcast tier (#9.3
    L986)."""
    side, eff_lane = _lane_for(actor, sp, lane)
    count, _sides, _flat = dice.parse(sp["damage"]["dice"])
    add_effect(registry, combat, actor, sp, "lane_trap", lane=eff_lane,
               side=side, data={"count": count + upcast_steps})
    return _results_for(targets)


def _resolver_slumber(registry, combat, actor, sp, targets, lane, dc,
                      upcast_steps):
    """Slumber: the lowest-HP enemies in the lane fall Asleep, no save,
    up to a rolled 5d8 HP budget (#9.5 L1047), +2d8 per upcast tier
    (#9.3 L1002). Targets whose HP exceeds the remaining budget are
    skipped."""
    from core import combat as cb
    budget = dice.roll(sp["upcast"]["base_hp_budget"])
    for _ in range(upcast_steps):
        budget += dice.roll(sp["upcast"]["add_per_tier"])
    results = []
    for tgt in sorted(targets, key=lambda c: c["hp"]):
        if tgt["hp"] <= budget:
            budget -= tgt["hp"]
            cb.apply_condition(registry, combat, tgt, "asleep",
                               source=actor)
            results.append({"target": tgt["cid"], "hit": True,
                            "save_ok": None})
        else:
            results.append({"target": tgt["cid"], "hit": False,
                            "save_ok": None})
    return results


def _resolver_arc_bolt(registry, combat, actor, sp, targets, lane, dc,
                       upcast_steps):
    """Arc Bolt (#9.5 L1033): auto-hit force darts -- base 3 x (1d4+1),
    +1 dart per upcast tier (#9.3 L1001); no attack roll, no save. The
    generic resolver would roll the damage entry only ONCE (one dart), so
    Arc Bolt needs its own resolver. The darts may be freely split among
    targets; until the combat UI grows a multi-target picker (cf.
    _vital_surge_targets) every dart strikes the single chosen target."""
    from core import combat as cb
    up = sp["upcast"]
    darts = up["darts"] + up["add_dart_per_tier"] * upcast_steps
    dtype = sp["damage"]["type"]
    results = []
    for tgt in targets:
        total = sum(dice.roll(up["dart"]) for _ in range(darts))
        if total > 0:
            cb.deal_damage(registry, combat, actor, tgt, total, dtype,
                           tags=["spell"])
        results.append({"target": tgt["cid"], "hit": True, "save_ok": None})
    return results


def _resolver_conjure_beast(registry, combat, actor, sp, targets, lane, dc,
                            upcast_steps):
    """Conjure Beast: summon the Spirit Beast (#9.6 L1068; statblock #9.12
    L1155-1162) to a lane of your choice -- a full combatant under player
    control, inserted into the order immediately after the summoner (no
    initiative roll, #9.12 L1164-1166), concentration-bound. Slice casts
    cannot upcast a tier-2 spell, so the #9.3 summon scaling waits."""
    import copy
    from core import combat as cb
    stats = copy.deepcopy(registry["summons"][sp["summon"]]["statblock"])
    seq = combat.get("effect_seq", 0) + 1
    combat["effect_seq"] = seq
    cid = "sm_%s_%d" % (sp["summon"], seq)
    summon = {
        "cid": cid,
        "side": actor["side"],
        "kind": "summon",
        "name": registry["summons"][sp["summon"]]["name"],
        "char": None,
        "stats": stats,
        "lane": lane or actor["lane"],
        "hp": stats["hp"],
        "hp_max": stats["hp"],
        "temp_hp": 0,
        "conditions": {},
        "acted": {"action": False, "bonus": False, "reaction": False},
        "downed": False,
        "dead": False,
        "concentration": None,
        "revived_round": None,
        "flags": {"summoner": actor["cid"]},
    }
    combat["combatants"][cid] = summon
    idx = combat["order"].index(actor["cid"])
    combat["order"].insert(idx + 1, cid)
    actor["concentration"]["summon"] = cid
    cb.log(combat, "%s conjures a %s." % (actor["name"], summon["name"]))
    return [{"target": cid, "hit": True, "save_ok": None, "summon": cid}]


def _spell_damage_bonus(registry, actor, sp):
    """Per-spell flat damage bonus consult: Agonizing Blast adds the
    Charisma modifier to Eldritch Lash damage (#7.7 L649)."""
    if sp["id"] == "eldritch_lash" and actor["kind"] == "pc" and \
            "agonizing_blast" in actor["char"]["class_picks"].get(
                "invocations", []):
        return ch.ability_mod(actor["char"], "cha")
    return 0


def _gate_radiant_smite(registry, combat, actor):
    """Radiant Smite is castable as a Bonus Action only after your melee
    hit this turn (#9.5 L1043); the paladin_paladins_smite attack_hit hook
    records the hit."""
    from core import combat as cb
    if actor["flags"].get("last_melee_hit_key") != _turn_key(combat):
        return False, "Needs a melee hit this turn."
    tgt = combat["combatants"].get(actor["flags"].get("last_melee_hit"))
    if tgt is None or not cb.standing(tgt):
        return False, "The struck target is already down."
    return True, None


def _radiant_smite_targets(registry, combat, actor):
    """The smite strikes the creature your melee attack hit this turn
    (#9.5 L1043) -- the spell's Self range never targets the caster."""
    from core import combat as cb
    tgt = combat["combatants"].get(actor["flags"].get("last_melee_hit"))
    return [tgt] if tgt is not None and cb.standing(tgt) else []


def _vital_surge_targets(registry, combat, actor):
    """Vital Surge reaches up to 3 allies (#9.6 L1060); until the combat
    UI grows a multi-target picker the first three standing allies in
    initiative order receive it."""
    from core import combat as cb
    return cb.combatants_on(combat, actor["side"])[:3]


# Per-spell cast legality gates, consulted by castable_spells/cast_spell.
SPELL_GATES = {
    "radiant_smite": _gate_radiant_smite,            # 9.5 L1043
}

# Per-spell target redirection inside _spell_targets.
SPELL_TARGET_OVERRIDES = {
    "radiant_smite": _radiant_smite_targets,         # 9.5 L1043
    "vital_surge": _vital_surge_targets,             # 9.6 L1060
}

# Slice-relevant rider wiring (tiers 0-2). Each cites its table row.
SPELL_RIDERS = {
    "rimefinger": _rider_condition("pinned", "target_turn_end"),  # 9.4 L1018
    "spark_arc": _rider_flag("addled"),                            # 9.4 L1019
    "thorn_dart": _rider_pull(),                                   # 9.4 L1023
    "gravewhisper": _rider_no_heal(),                              # 9.4 L1020
    "cutting_quip": _rider_flag("sapped"),                         # 9.4 L1025
    "sickening_ray": _rider_condition("poisoned", "target_turn_end"),  # 9.5 L1037
    "frost_lance": _rider_condition("pinned", "target_turn_end"),  # 9.5 L1035
    "whispered_dread": _rider_push_back(),                         # 9.5 L1038
    "grasping_vines": _rider_condition("pinned", None),            # 9.5 L1048
    "warding_aegis": _rider_ac_mod(2),                             # 9.5 L1042
    "quarrys_mark": _rider_mark(),                                 # 9.5 L1044
    "thunderclap_wave": _rider_push_back(),                        # 9.6 L1056
    "ice_shackles": _rider_condition("pinned", "target_turn_end"),  # 9.6 L1057
    "rend_bolt": _rider_ac_mod(-1, expires="target_turn_end"),     # 9.6 L1054
    "vital_surge": _rider_vital_surge(),                           # 9.6 L1060
    "ironhide": _rider_ironhide(),                                 # 9.6 L1061
    "haste_of_the_quick": _rider_haste(),                          # 9.6 L1062
    "enfeeble": _rider_enfeeble(),                                 # 9.6 L1063
    "hold_person": _rider_condition("paralyzed", None),            # 9.6 L1065
    "frightful_visage": _rider_condition("frightened", None),      # 9.6 L1066
    "beguile": _rider_condition("charmed", None),                  # 9.5 L1046
    "eldritch_lash": _rider_lash(),                                # 7.7 L650-652
}

# Whole-cast resolvers: lane-scoped effects, Slumber's HP budget, and the
# summon. Each cites its table row.
SPELL_RESOLVERS = {
    "arc_bolt": _resolver_arc_bolt,                             # 9.5 L1033
    "benediction": _resolver_lane_roll_mod(+1, "benediction"),  # 9.5 L1041
    "malediction": _resolver_lane_roll_mod(-1, "malediction"),  # 9.5 L1045
    "corrode": _resolver_corrode,                               # 9.6 L1064
    "moonfire_column": _resolver_moonfire,                      # 9.6 L1055
    "spike_field": _resolver_spike_field,                       # 9.6 L1067
    "slumber": _resolver_slumber,                # 9.5 L1047 + 9.3 L1002
    "conjure_beast": _resolver_conjure_beast,    # 9.6 L1068 + 9.12
}


# ---------------------------------------------------------------------------
# DEFERRED slice features -- intentionally not wired (do not half-build):
# - Bardic Inspiration (#7.8 L694-703), Cutting Words (#7.8 L710-712) and
#   Tactical Mind (#7.1 L411-412): all three need the post-roll interrupt
#   flow (see a failed/failing d20 result, then choose to spend a die),
#   which the pipeline does not expose yet.
# - Fast Hands (#7.2 L450): Use Item as a Bonus Action -- needs an
#   action-economy override on combat.player_use_item.
# - Metamagic spends (#7.12 L869-877): a per-cast modifier picker over
#   Sorcery Points.
# - Deflect Attacks (#7.11 L830-833): an automatic damage-reduction
#   reaction with a conditional Focus-Point counterstrike.
# - Horde Breaker (#7.6 L610-611): the second Hunter's Prey option (one
#   extra attack against a different enemy in the target's lane).
# - Sacred Weapon (#7.9 L739-741): Channel Divinity, +Charisma modifier
#   to the weapon's attack rolls for the rest of the fight -- needs a
#   fight-long attack-bonus channel distinct from the per-attack ctx.
# - Disciple of Life (#7.3 L496-497): healing spells cast with a slot
#   restore an extra 2 + the slot's tier -- needs the spent-slot tier
#   plumbed into the heal resolution.
# - Per-Camp free-cast resources: Paladin's Smite's one free Radiant
#   Smite per Camp (#7.9 L737-738) and Favored Enemy's slot-free
#   Quarry's Mark casts (#7.6 L599-600) -- both need the P4 Camp
#   resource cycle to be meaningful and a free-cast path through
#   cast_spell's slot spend.
# - Lay on Hands, spend-5-to-cure-Poisoned (#7.9 L730-732): needs a
#   second spend mode on the pool ability (the P2 button heals only).
# - Guidance / Resistance (#9.4 L1026-1027): +1d4 to one ability check /
#   saving throw -- ability checks live outside combat, and the save die
#   needs the same post-roll interrupt flow as Bardic Inspiration.
# - Other L1-3 features awaiting their systems: Wild Companion + the
#   three Circles (#7.10 L779-797), Uncanny Metabolism (#7.11 L828-829),
#   Remarkable Athlete (#7.1 L414-415), Preserve Life (#7.3 L498-500),
#   Dark One's Blessing (#7.7) and the non-Lash invocations, Potent
#   Cantrip (#7.4), Font of Magic conversions (#7.12), the Two-Weapon
#   Fighting / Protection / Interception styles (#8.2) and the Nick
#   mastery (#10.3 L1198-1199) -- the offhand/dual-wield attack path,
#   reaction interposes, and companion actions arrive with later P2/P3
#   passes.
