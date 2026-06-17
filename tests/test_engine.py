"""Engine suite (pure Python, no Ren'Py).

Two halves:
  * a first-legal deterministic chooser that walks the real creation + level-up
    choice flow for every class to the level cap -- this exercises
    ui_options.options_for and character.apply_choice across every choice type,
    and proves the not-yet-wired fighting-style / invocation pickers stay
    *satisfiable* (a regression guard for the "disable vs note" decision);
  * focused regressions for the bugs fixed in the audit pass.
"""
import data
from core import character as ch, ui_options as bui, combat as cb, rules, hooks, dice

REG = data.REGISTRY

_SCORES = {"str": 15, "dex": 14, "con": 13, "int": 12, "wis": 10, "cha": 8}


def _first_legal(char, choice, opts):
    """First-legal deterministic chooser (mirrors debug_hub.debug_first_legal):
    handle the special selection shapes, else keep preselected and fill with
    enabled (non-disabled) ids up to the required count."""
    from core import registry as reg
    if opts["mode"] == "asi_or_talent":
        for ability in ch.ABILITIES:
            if char["abilities"][ability] <= 18:
                return {"mode": "asi", "scores": {ability: 2}}
        return {"mode": "talent", "talent": "savage_attacker"}
    if opts["mode"] == "magic_initiate":
        cans = [s["id"] for s in reg.spell_slice(REG["spells"], "wizard", 0)
                if s["id"] not in char["spells"]["cantrips"]][:2]
        spell = reg.spell_slice(REG["spells"], "wizard", 1)[0]["id"]
        return {"class": "wizard", "cantrips": cans, "spell": spell}
    pre = list(opts.get("preselected", []))
    enabled = [o["id"] for o in opts["options"] if not o.get("disabled")]
    picks = pre + [o for o in enabled if o not in pre]
    if opts.get("shape") == "single":
        return picks[0]
    return picks[:opts["pick"]]


def _run_choices(char, pending):
    queue = list(pending)
    while queue:
        choice = queue.pop(0)
        opts = bui.options_for(REG, char, choice)
        if opts["mode"] == "list" and opts["pick"] == 0:
            follow = ch.apply_choice(REG, char, choice, [])
        else:
            follow = ch.apply_choice(REG, char, choice,
                                     _first_legal(char, choice, opts))
        queue = list(follow or []) + queue


def _build_to_12(cls_id):
    char = ch.new_character(REG, "t", "T", cls_id, dict(_SCORES))
    _run_choices(char, ch.manifest_choices(REG, char, 1))
    ch.finalize_creation(REG, char)
    char["xp"] = REG["core"]["xp_thresholds"]["by_level"][-1]
    while ch.can_level_up(REG, char):
        _run_choices(char, ch.level_up(REG, char))
        ch.finalize_level_up(REG, char)
    return char


def _mk(cls_id):
    c = ch.new_character(REG, "t", "T", cls_id, dict(_SCORES))
    ch.finalize_creation(REG, c)
    return c


def test_build_every_class_to_level_12():
    # also guards that the disabled/noted fighting-style & invocation pickers
    # never make a choice unsatisfiable (warlock needs 8 invocations).
    for cls_id in REG["classes"]:
        char = _build_to_12(cls_id)
        assert char["level"] == 12, cls_id


def test_monk_ignores_shield_barbarian_honors_it():
    monk, barb = _mk("monk"), _mk("barbarian")
    for c in (monk, barb):
        c["equipment"]["offhand"] = None
    m0, b0 = ch.ac(REG, monk), ch.ac(REG, barb)
    for c in (monk, barb):
        c["equipment"]["offhand"] = "shield"
    assert ch.ac(REG, monk) == m0          # Monk: no shield bonus (#7.11)
    assert ch.ac(REG, barb) == b0 + 2      # Barbarian: +2 (#7.5)


def test_recovery_die_heal_floored_at_zero():
    assert rules.recovery_die_heal(1, -5) == 0
    assert rules.recovery_die_heal(4, 2) == 6


def test_fled_enemy_excluded_from_victory_xp():
    barb = _mk("barbarian")
    combat = cb.build_combat(REG, [barb], ["standard_wolf", "standard_wolf"])
    ens = [c for c in combat["combatants"].values() if c["kind"] == "enemy"]
    ens[0]["dead"] = True
    ens[0]["fled"] = True
    ens[1]["dead"] = True
    cb._victory(REG, combat)
    assert combat["over"]["xp"] == ens[1]["stats"]["xp"]


def test_charmed_cannot_target_or_attack_charmer():
    barb = _mk("barbarian")
    combat = cb.build_combat(REG, [barb], ["standard_wolf"])
    pc = next(c for c in combat["combatants"].values() if c["kind"] == "pc")
    en = next(c for c in combat["combatants"].values() if c["kind"] == "enemy")
    cb.apply_condition(REG, combat, en, "charmed", source=pc)
    assert cb._intent_select(REG, combat, en, "nearest_frontline") is None
    assert cb.attack(REG, combat, en, pc)["ok"] is False


def test_magic_initiate_tier1_spell_castable_for_a_caster():
    from core import registry as reg
    cleric = _mk("cleric")
    spell = reg.spell_slice(REG["spells"], "wizard", 1)[0]["id"]
    cleric["class_picks"]["magic_initiate"] = {"class": "wizard", "spell": spell}
    assert spell in ch.always_prepared(REG, cleric)


def test_save_advantage_hook_contributes_to_adv_set():
    ctx = {"adv": [], "dis": []}
    hooks.eff_save_advantage(REG, None, None, ctx)
    assert ctx["adv"] == ["save_advantage"]
