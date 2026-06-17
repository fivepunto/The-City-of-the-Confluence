# -*- coding: utf-8 -*-
"""The rest economy (GDD #12): the Breather (short rest), Camp (long rest),
the Hunt check, and the day clock. Pure Python -- no renpy import. The .rpy
layer calls renpy.block_rollback() immediately after every committed Breather,
recovery-die spend, Camp/Sleep, Hunt resolution, and Supply/upgrade purchase
(#16.1); this module never touches renpy.

Capacities are DERIVED on read, never stored: the Breather pool is 2, or 3 if
any party member is a pact caster (the Warlock's Magical Cunning; multiple
Warlocks do not stack -- #12.1 L1322-1323). Supply capacity is 3, or 4 with
the Provisioner's Pack-Frame upgrade (#12.2 L1343-1344, #14.3).
"""

from core import character as ch
from core import rules

# Resource pools a Breather can recharge, paired with the feature that drives
# them; the per-feature `uses` data decides full vs +1 (#12.1 L1328-1330).
# Bardic Inspiration and Warlock pact slots are special-cased below (their
# Breather timing is not on a `uses` dict). Channel Divinity shares one
# resource key across the Cleric and Paladin features; a `bumped` set makes
# the +1 fire at most once per key per Breather, so a (future) character with
# both features can never gain +2.
_BREATHER_FEATURE_POOLS = [
    ("second_wind", "fighter_second_wind"),
    ("action_surge", "fighter_action_surge"),
    ("focus_points", "monk_monks_focus"),
    ("channel_divinity", "cleric_channel_divinity"),
    ("channel_divinity", "paladin_channel_divinity"),
]


def breather_max(registry, party):
    """2 Breathers between Camps, 3 if any party member is a pact caster
    (#12.1 L1322-1323; Warlocks do not stack)."""
    rest = registry["core"]["rest_rules"]
    has_warlock = any((ch.caster_info(registry, m) or {}).get("kind") == "pact"
                      for m in party)
    return (rest["breathers_with_warlock"] if has_warlock
            else rest["breathers_per_camp"])


def breathers_remaining(registry, state, party):
    return max(0, breather_max(registry, party) - state.get("breathers", 0))


def supply_capacity(registry, state):
    """3 base, 4 with the Pack-Frame (#12.2 L1343-1344). Reads the literal
    capacities from the economy table; ownership is a flag in state."""
    eco = registry["economy"]
    if "provisioners_pack_frame" in state.get("camp_upgrades", []):
        return eco["supply_capacity_with_pack_frame"]["value"]
    return eco["supply_capacity_base"]["value"]


def recharge_breather(registry, char):
    """Recharge a single character's short-rest features on a Breather
    (#12.1 L1328-1330). Full for `uses.per == 'breather'`; +1 (capped) for
    `uses.regain_one_per_breather`; Bardic Inspiration to full only with Font
    of Inspiration (level 5+); ALL Warlock pact slots to full. Recovery Dice
    are the SPEND pool, not recharged here; Camp-only pools are untouched."""
    row = ch.resource_row(registry, char)
    res = char["resources"]
    bumped = set()
    for key, fid in _BREATHER_FEATURE_POOLS:
        if not ch.has_feature(char, fid) or key not in row:
            continue
        uses = registry["features"][fid].get("uses", {})
        mx = row[key]["max"]
        cur = res.get(key, mx)
        if uses.get("per") == "breather":
            res[key] = mx
        elif uses.get("regain_one_per_breather") and key not in bumped:
            res[key] = min(mx, cur + 1)
            bumped.add(key)
    # Bardic Inspiration: full on a Breather only once Font of Inspiration is
    # granted (level 5+, #12.1 L1329-1330; bard_font_of_inspiration).
    if ch.has_feature(char, "bard_font_of_inspiration") and "bardic" in row:
        res["bardic"] = row["bardic"]["max"]
    # Warlock pact slots: ALL recharge on a Breather (#12.1 L1330; the timing
    # lives in core PACT_SLOTS, not on the feature).
    caster = ch.caster_info(registry, char)
    if (caster and caster["kind"] == "pact"
            and registry["core"]["pact_slots"]["recharge"] == "breather"
            and "pact_slots" in row):
        res["pact_slots"] = row["pact_slots"]["max"]
    return char


def take_breather(registry, state, party):
    """A party Breather (#12.1): every member's short-rest features recharge,
    the Breather count ticks, and the day clock advances one step (clamped at
    evening). Recovery-die healing is a SEPARATE per-character choice offered
    during the Breather (spend_recovery_die). Raises if none remain."""
    if breathers_remaining(registry, state, party) <= 0:
        raise ValueError("no Breathers remaining until you Camp")
    for member in party:
        recharge_breather(registry, member)
    state["breathers"] = state.get("breathers", 0) + 1
    advance_day_phase(registry, state)


def spend_recovery_die(registry, char, dice_roller):
    """Spend one Recovery Die to heal (#12.1 L1325-1327): roll the class hit
    die, heal that + the Constitution modifier, clamp to max HP, decrement the
    pool. `dice_roller(notation) -> int` (core.dice.roll in production).
    Returns the HP healed; raises if the pool is empty."""
    have = char["resources"].get("recovery_dice", char["level"])
    if have <= 0:
        raise ValueError("no Recovery Dice left")
    hit_die = registry["classes"][char["class"]]["hit_die"]
    face = dice_roller("1d%d" % hit_die)
    healed = rules.recovery_die_heal(face, ch.ability_mod(char, "con"))
    char["hp"] = min(char["hp"] + healed, char["hp_max"])
    char["resources"]["recovery_dice"] = have - 1
    return healed


def do_camp(registry, party, recovery_bonus=0):
    """The long rest restore (#12.1 L1334-1336): every pool to max (reusing
    refill_resources), HP to full (refill_resources does NOT set HP), and
    lingering conditions cleared. `recovery_bonus` adds extra Recovery Dice
    this Camp (Fieldwright's Tent, #14.3 L1431). Used by both a wilds Camp and
    the city inn; the cost (1 Supply vs 10 gold) is the caller's concern."""
    for member in party:
        ch.refill_resources(registry, member)
        member["hp"] = member["hp_max"]
        member["conditions"] = []
        if recovery_bonus:
            member["resources"]["recovery_dice"] = member["level"] + recovery_bonus


def camp_recovery_bonus(registry, state):
    """Extra Recovery Dice granted at Camp by the Fieldwright's Tent upgrade
    (#14.3 L1431). The number is data on the upgrade record."""
    if "fieldwrights_tent" in state.get("camp_upgrades", []):
        return registry["camp_upgrades"]["fieldwrights_tent"].get(
            "recovery_dice_bonus", 0)
    return 0


def do_sleep(registry, state, party):
    """Commit a rest (#12.4 L1377-1378): restore the party (with any Tent
    bonus Recovery Dice), reset the Breather count, and the day clock to
    morning."""
    do_camp(registry, party, recovery_bonus=camp_recovery_bonus(registry, state))
    state["breathers"] = 0
    reset_day_phase(registry, state)


def resolve_hunt(registry, hunter, region, ranger_advantage=False):
    """The Hunt check (#12.2 L1345-1350): an Awareness check against the
    region's hunt difficulty; the Ranger has advantage. On success the Camp
    consumes no Supply Cache. Returns the skill-check result dict; the caller
    blocks rollback and spends (or spares) the Supply."""
    from core import checks
    skill = registry["economy"]["hunting_skill"]["value"]
    adv = 1 if ranger_advantage else 0
    return checks.skill_check(registry, hunter, skill, region["hunt_dc"], adv)


def advance_day_phase(registry, state):
    """morning -> afternoon -> evening, clamped at evening (no wrap until the
    party Camps; #12.3 L1356-1358)."""
    phases = registry["core"]["rest_rules"]["day_phases"]
    cur = state.get("day_phase", phases[0])
    idx = phases.index(cur) if cur in phases else 0
    state["day_phase"] = phases[min(idx + 1, len(phases) - 1)]


def reset_day_phase(registry, state):
    """Camp/sleeping resets to morning (#12.3 L1358)."""
    state["day_phase"] = registry["core"]["rest_rules"]["day_phases"][0]
