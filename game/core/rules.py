"""Derived math. Every function recomputes from inputs/registry on read --
derived stats are never stored (GDD #16.4, L1630-1632).

Each function cites the GDD line it implements.
"""


def ability_modifier(score):
    """Modifier = (score - 10) // 2, rounded down (GDD #2.1, L49)."""
    return (score - 10) // 2


def proficiency_bonus(level):
    """+2 at 1-4, +3 at 5-8, +4 at 9-12 (GDD #2.5, L85-86)."""
    if not 1 <= level <= 12:
        raise ValueError("level out of range 1-12: %r" % (level,))
    if level <= 4:
        return 2
    if level <= 8:
        return 3
    return 4


def hp_max(hit_die, level, con_mod, flat_bonus_per_level=0, flat_bonus=0):
    """Level 1: max die + Con mod; later levels: die//2 + 1 + Con mod each.
    HP is never rolled (GDD #2.6, L90-93).

    flat_bonus_per_level / flat_bonus exist for features that say exactly
    that (e.g. Tough, GDD #8.1 L915; Draconic Resilience, #7.12 L878).
    """
    total = hit_die + con_mod
    total += (level - 1) * (hit_die // 2 + 1 + con_mod)
    total += level * flat_bonus_per_level + flat_bonus
    return total


def spell_save_dc(prof, casting_mod):
    """8 + proficiency bonus + casting-ability modifier (GDD #2.4, L74)."""
    return 8 + prof + casting_mod


def spell_attack_bonus(prof, casting_mod):
    """Proficiency bonus + casting-ability modifier (GDD #2.4, L75)."""
    return prof + casting_mod


def feature_save_dc(prof, governing_mod):
    """8 + proficiency bonus + the feature's governing ability modifier --
    the general DC for any feature-imposed save (Channel Divinity, Aspect,
    Monk Open Hand/Stunning Strike...). Same formula as the spell save DC;
    owner adjudication, P2 (GDD #2.4). An alias so call sites read by intent.
    """
    return 8 + prof + governing_mod


def skill_total(ability_mod, prof, proficient=False, expertise=False,
                half_prof_untrained=False):
    """Skill check modifier. Proficiency is never added twice; Expertise
    doubles it, once (GDD #2.5, L86-88). half_prof_untrained is the Bard's
    Jack of All Trades (GDD #7.8, L707-708), rounded down, non-proficient
    skills only.
    """
    if proficient:
        return ability_mod + prof * (2 if expertise else 1)
    if half_prof_untrained:
        return ability_mod + prof // 2
    return ability_mod


def save_modifier(ability_mod, prof, proficient=False):
    """Saving-throw modifier (GDD #2.7)."""
    return ability_mod + (prof if proficient else 0)


def initiative_modifier(dex_mod, alert_prof_bonus=0):
    """1d20 + Dexterity modifier (GDD #5.1, L206); the Alert talent adds the
    proficiency bonus (GDD #8.1, L910)."""
    return dex_mod + alert_prof_bonus


def armor_ac(base_ac, dex_mod, dex_cap=None, shield=False):
    """AC = armor base + Dex modifier (capped by armor type), +2 shield
    (GDD #10.1, L1160-1161). dex_cap None = uncapped; 0 = flat armor.
    """
    dex_part = dex_mod if dex_cap is None else min(dex_mod, dex_cap)
    return base_ac + dex_part + (2 if shield else 0)


def unarmored_ac(dex_mod, second_mod=0, base=10, shield=False):
    """Unarmored Defense family: base + Dex + a second modifier.
    Barbarian 10+Dex+Con (#7.5 L558-559, shield allowed); Monk 10+Dex+Wis
    (#7.11 L820, no shield -- caller enforces); Draconic Resilience
    10+Dex+Cha (#7.12 L879-880); Armor of Shadows 13+Dex (#7.7 L653).
    """
    return base + dex_mod + second_mod + (2 if shield else 0)


def concentration_save_dc(damage):
    """DC 10 or half the damage taken, whichever is higher (GDD #5.6, L321)."""
    return max(10, damage // 2)


def point_buy_cost(score, costs):
    """Cost of one score under Point Buy (GDD #3, L127-130). costs is the
    registry table {8:0 ... 15:9}."""
    if score not in costs:
        raise ValueError("score not buyable: %r" % (score,))
    return costs[score]


def point_buy_total(scores, costs):
    """Total cost of six scores."""
    return sum(point_buy_cost(s, costs) for s in scores)


def point_buy_valid(scores, costs, budget):
    """True if exactly six scores, all buyable, within the 27-point budget
    (GDD #3, L127-130). Spending less than the budget is legal."""
    if len(scores) != 6:
        return False
    try:
        return point_buy_total(scores, costs) <= budget
    except ValueError:
        return False


def level_for_xp(xp, thresholds):
    """Highest level whose threshold is <= xp. thresholds[0] is level 1's 0
    (GDD #6, L370-372; values flagged in GAPS.md G-001)."""
    level = 1
    for i, need in enumerate(thresholds):
        if xp >= need:
            level = i + 1
    return min(level, 12)


def recovery_die_heal(hit_die_roll, con_mod):
    """Each Recovery Die heals the class hit die + Con modifier
    (GDD #12.1, L1308-1310)."""
    return hit_die_roll + con_mod
