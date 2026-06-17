# -*- coding: utf-8 -*-
"""Turns choice records into pickable option lists for the generic stepper
screens (creation #3 step 4; the level-up wizard #15.2). All card text
reads from the registry -- rules text exists exactly once (#15.2 L1500-1501).

apply_choice in core.character stays the gate: this module only presents.
"""

from core import character as ch


_ABILITY_WORDS = {"str": "Strength", "dex": "Dexterity", "con": "Constitution",
                  "int": "Intelligence", "wis": "Wisdom", "cha": "Charisma"}

_ACTION_WORDS = {
    "action": "Action",
    "bonus": "Bonus Action",
    "reaction": "Reaction",
    "free": "Free Action",
    "passive": "Passive",
    "camp": "Camp Action",
}

_RANGE_WORDS = {
    "touch": "Touch",
    "distance": "Distance",
    "self": "Self",
    "special": "Special",
}

_PER_WORDS = {
    "camp": "Camp",
    "breather": "Breather",
    "turn": "turn",
    "round": "round",
    "fight": "fight",
    "combat": "combat",
}

_AMOUNT_WORDS = {
    "level": "your level",
    "prof": "your proficiency bonus",
    "cha_mod": "your Charisma modifier",
    "wis_mod": "your Wisdom modifier",
    "int_mod": "your Intelligence modifier",
    "str_mod": "your Strength modifier",
    "dex_mod": "your Dexterity modifier",
    "con_mod": "your Constitution modifier",
}


def _clean(text):
    return (text or "").strip()


def _ending(text):
    text = _clean(text)
    if not text:
        return ""
    return text if text[-1] in ".!?" else text + "."


def _amount_text(amount):
    if isinstance(amount, dict):
        by_level = amount.get("by_level")
        if isinstance(by_level, dict):
            parts = ["%s at level %s" % (by_level[level], level)
                     for level in sorted(by_level)]
            return "scales by level (%s)" % ", ".join(parts)
        return str(amount)
    try:
        return _AMOUNT_WORDS.get(amount, str(amount))
    except TypeError:
        return str(amount)


def _uses_text(uses):
    if not uses:
        return ""
    if not isinstance(uses, dict):
        return _amount_text(uses)
    amount = _amount_text(uses.get("amount", 1))
    per = _PER_WORDS.get(uses.get("per"), str(uses.get("per", "")).title())
    if per:
        return "%s per %s" % (amount, per)
    return amount


def _record_action_prefix(record, base):
    """Add action and use cadence without changing the underlying rules text."""
    base = _ending(base)
    if not record:
        return base
    prefixes = []
    action = record.get("action")
    action_label = _ACTION_WORDS.get(action)
    if action_label and not base.lower().startswith(action_label.lower()):
        prefixes.append(action_label + ".")
    uses = _uses_text(record.get("uses"))
    if uses and (" per " not in base[:80].lower()):
        prefixes.append("Uses: %s." % uses)
    return " ".join(prefixes + ([base] if base else []))


def _damage_text(damage):
    if not damage:
        return ""
    if isinstance(damage, list):
        return " + ".join(_damage_text(d) for d in damage if d)
    if damage.get("dice"):
        return "%s %s" % (damage["dice"], damage.get("type", "damage"))
    if damage.get("flat") is not None:
        return "%s %s" % (damage["flat"], damage.get("type", "damage"))
    return ""


def _heal_text(heal):
    if not heal:
        return ""
    if heal.get("dice"):
        text = heal["dice"]
        if heal.get("plus_casting_mod"):
            text += " + casting modifier"
        return text + " HP"
    if heal.get("flat") is not None:
        return "%s HP" % heal["flat"]
    return ""


def _save_text(save):
    if not save:
        return ""
    ability = creation_ability_word(save["ability"])
    result = {
        "half": "success halves the damage",
        "negates": "success avoids the effect",
    }.get(save.get("on_success"), "success changes the effect")
    repeat = "; repeats as specified" if save.get("repeating") else ""
    return "%s save: %s%s" % (ability, result, repeat)


def _target_text(spell):
    area = spell.get("area")
    roles = set(spell.get("roles") or ())
    if area:
        side = area.get("side")
        size = area.get("size")
        if size == "large":
            if side == "enemies":
                return "all enemies"
            if side == "allies":
                return "all allies"
        if size == "small":
            if side == "enemies":
                return "one enemy lane"
            if side == "allies":
                return "one ally lane"
        if area.get("special"):
            return area["special"].replace("_", " ")
        return "an area"
    if spell.get("range") == "self":
        return "self"
    if roles & {"heal", "true_heal", "buff"}:
        return "one ally"
    return "one target"


def _spell_upcast_text(spell):
    upcast = spell.get("upcast")
    if not upcast or upcast == "none":
        return ""
    if isinstance(upcast, dict):
        if upcast.get("add_dart_per_tier"):
            return "+%d dart per higher tier" % upcast["add_dart_per_tier"]
        if upcast.get("add_target_per_tier"):
            return "+%d target per higher tier" % upcast["add_target_per_tier"]
        if upcast.get("add_damage_die_per_tier"):
            return "+%s damage per higher tier" % upcast["add_damage_die_per_tier"]
    return "improves when cast with a higher tier slot"


def _spell_text(registry, rec_id, fallback):
    spell = registry.get("spells", {}).get(rec_id)
    if not spell:
        return _ending(fallback)

    tier = "Cantrip" if spell["tier"] == 0 else "Tier %d spell" % spell["tier"]
    details = [
        tier,
        _ACTION_WORDS.get(spell.get("action"), str(spell.get("action", "")).title()),
        "Range: %s" % _RANGE_WORDS.get(spell.get("range"), spell.get("range")),
        "Target: %s" % _target_text(spell),
    ]
    if spell.get("attack"):
        details.append("requires a spell attack roll")
    if spell.get("weapon_attack"):
        details.append("requires a ranged weapon attack")
    damage = _damage_text(spell.get("damage"))
    if damage:
        details.append("Damage: %s" % damage)
    heal = _heal_text(spell.get("heal"))
    if heal:
        details.append("Healing: %s" % heal)
    save = _save_text(spell.get("save"))
    if save:
        details.append(save)
    if spell.get("concentration"):
        details.append("requires Concentration")
    if "true_heal" in (spell.get("roles") or ()):
        details.append("True Healing can revive Downed allies")
    upcast = _spell_upcast_text(spell)
    if upcast:
        details.append("Upcast: %s" % upcast)

    rules = _ending(fallback or spell.get("effect", ""))
    return "%s Details: %s." % (rules, "; ".join(d for d in details if d))


def _condition_text(registry, rec_id, fallback):
    condition = registry.get("conditions", {}).get(rec_id)
    return _ending((condition or {}).get("effect") or fallback)


def _consumable_text(registry, rec_id, fallback):
    item = registry.get("consumables", {}).get(rec_id)
    if not item:
        return _ending(fallback)
    heal = _heal_text(item.get("heal"))
    parts = []
    if item.get("heal_type") == "true_healing":
        parts.append("True Healing: revives a Downed ally and restores %s" % heal)
    elif heal:
        parts.append("Restores %s to one living ally" % heal)
        parts.append("cannot revive a Downed character")
    if item.get("stock_limited"):
        parts.append("limited shop stock")
    if item.get("price") is not None:
        parts.append("shop price %d gold" % item["price"])
    return _ending("; ".join(parts) or fallback)


def _relic_text(registry, rec_id, fallback):
    relic = registry.get("relics", {}).get(rec_id)
    if not relic:
        return _ending(fallback)
    parts = [
        "%s relic" % relic.get("rarity", "unknown").replace("_", " ").title(),
        "sell-only treasure worth %d gold" % relic.get("sell_value", 0),
    ]
    if relic.get("alt_use"):
        parts.append("alternate use: %s" % relic["alt_use"].replace("_", " "))
    else:
        parts.append("no alternate use implemented")
    return _ending("; ".join(parts))


def _magic_item_text(registry, rec_id, fallback):
    item = registry.get("magic_items", {}).get(rec_id)
    if not item:
        return _ending(fallback)
    slot = item.get("slot", "slot").replace("_", " ")
    parts = [
        "%s magic item for the %s slot" %
        (item.get("rarity", "unknown").replace("_", " ").title(), slot),
    ]
    if item.get("plus_bonus"):
        parts.append("+%d item rating" % item["plus_bonus"])
    if item.get("effect") and "TO BE WRITTEN" not in item["effect"]:
        parts.append(item["effect"])
    else:
        parts.append("no combat effect is implemented yet")
    if item.get("price") is not None:
        parts.append("shop price %d gold" % item["price"])
    return _ending("; ".join(parts))


def _key_item_text(registry, rec_id, fallback):
    item = registry.get("key_items", {}).get(rec_id)
    if not item:
        return _ending(fallback)
    if rec_id == "spellbook":
        return ("Quest item. Holds a Wizard's known spells; it cannot be "
                "sold or discarded.")
    return "Quest item. Cannot be sold or discarded."


def player_text(registry, category, rec_id, fallback):
    """Player-facing rules text.

    Stored display blurbs are still used for soft categories like skills, but
    rules-heavy records prefer the registry mechanics so tooltips expose the
    real action cost, uses, dice, saves, range, duration, and restrictions.
    """
    if category == "spells":
        return _spell_text(registry, rec_id, fallback)
    if category == "conditions":
        return _condition_text(registry, rec_id, fallback)
    if category == "consumables":
        return _consumable_text(registry, rec_id, fallback)
    if category == "relics":
        return _relic_text(registry, rec_id, fallback)
    if category == "magic_items":
        return _magic_item_text(registry, rec_id, fallback)
    if category == "key_items":
        return _key_item_text(registry, rec_id, fallback)

    # These categories already store precise mechanical text in their records.
    if category in ("features", "talents", "fighting_styles", "masteries",
                    "invocations", "metamagic", "aspects", "circle",
                    "human"):
        if category == "features":
            return _record_action_prefix(
                registry.get("features", {}).get(rec_id), fallback)
        return _ending(fallback)

    blurb = registry.get("display", {}).get(category, {}).get(rec_id)
    return _ending(blurb if blurb else fallback)


def _opt(oid, label, desc="", disabled=False, note=""):
    return {"id": oid, "label": label, "desc": desc,
            "disabled": disabled, "note": note}


def _spell_opt(registry, sid):
    sp = registry["spells"][sid]
    tier = "Cantrip" if sp["tier"] == 0 else "Tier %d" % sp["tier"]
    return _opt(sid, sp["name"],
                player_text(registry, "spells", sid, sp["effect"]), note=tier)


def _skill_opt(registry, sid):
    sk = registry["skills"][sid]
    return _opt(sid, sk["name"],
                player_text(registry, "skills", sid, sk["desc"]),
                note=creation_ability_word(sk["ability"]))


def creation_ability_word(aid):
    return _ABILITY_WORDS.get(aid, aid.upper())


def choice_title(choice):
    titles = {
        "skills": "Choose Skill Proficiencies",
        "expertise": "Choose Expertise",
        "versatile_talent": "Human Versatility: Choose a Talent",
        "asi_or_talent": "Ability Score Increase or Talent",
        "fighting_style": "Choose a Fighting Style",
        "weapon_mastery": "Choose Weapon Masteries",
        "cantrips": "Choose Cantrips",
        "spellbook_init": "Choose Starting Spellbook Spells",
        "spellbook_add": "Add Spells to Your Spellbook",
        "invocations": "Choose Eldritch Invocations",
        "metamagic": "Choose Metamagic",
        "aspects": "Choose Primal Aspects",
        "circle": "Choose Your Druid Circle",
        "mystic_arcanum": "Choose Your Mystic Arcanum",
        "spells_always_prepared": "Magical Discoveries",
        "feature_option": "Choose an option",
        "prepare_spells": "Prepare Spells",
        "magic_initiate": "Magic Initiate",
        "resilient_ability": "Resilient: Choose an Ability",
    }
    return titles.get(choice["type"], choice["type"])


def options_for(registry, char, choice):
    """-> {'pick': N, 'options': [...], 'preselected': [...], 'mode': str,
    'shape': 'list'|'single'}.
    mode 'list' = pick N of options; pass apply_choice a LIST when shape is
    'list' (even if pick == 1) and the bare option id when 'single'.
    'asi_or_talent' and 'magic_initiate' need bespoke steps in the screen
    (they assemble their own selection objects)."""
    ctype = choice["type"]

    if ctype == "skills":
        legal = ch.legal_skill_choices(registry, char, choice)
        return {"pick": choice["choose"], "mode": "list", "shape": "list", "preselected": [],
                "options": [_skill_opt(registry, s) for s in legal]}

    if ctype == "expertise":
        pool = choice.get("from") or char["skills"]["proficiencies"]
        legal = [s for s in pool if s in char["skills"]["proficiencies"]
                 and s not in char["skills"]["expertise"]]
        return {"pick": choice["choose"], "mode": "list", "shape": "list", "preselected": [],
                "options": [_skill_opt(registry, s) for s in legal]}

    if ctype == "versatile_talent":
        return {"pick": 1, "mode": "list", "shape": "single", "preselected": [],
                "options": [_opt(t, registry["talents"][t]["name"],
                                 player_text(registry, "talents", t,
                                             registry["talents"][t]["effect"]))
                            for t in choice["from"]]}

    if ctype == "asi_or_talent":
        talents = [_opt(t, rec["name"],
                        player_text(registry, "talents", t, rec["effect"]),
                        disabled=t in char["talents"],
                        note="taken" if t in char["talents"] else "")
                   for t, rec in registry["talents"].items()]
        return {"pick": 1, "mode": "asi_or_talent", "preselected": [],
                "options": talents}

    if ctype == "fighting_style":
        owned = ch.fighting_styles(char)
        # Styles with engine support in the current slice: the three wired into
        # HOOK_LIBRARY (archery/dueling/great_weapon_fighting) plus 'defense'
        # (read by character.ac). The rest are authored but not yet wired
        # (#8.2 deferred) -- offer them disabled so a pick is never wasted.
        wired_styles = ("archery", "dueling", "great_weapon_fighting", "defense")
        options = [_opt(s, rec["name"],
                        player_text(registry, "fighting_styles", s, rec["effect"]),
                        disabled=s not in wired_styles,
                        note="" if s in wired_styles else "not yet implemented")
                   for s, rec in registry["fighting_styles"].items()
                   if s not in owned]
        if choice.get("or_feature"):
            feat = registry["features"][choice["or_feature"]]
            options.append(_opt(choice["or_feature"], feat["name"],
                                player_text(registry, "features",
                                            choice["or_feature"], feat["effect"]),
                                note="instead of a style"))
        return {"pick": 1, "mode": "list", "shape": "single", "preselected": [],
                "options": options}

    if ctype == "weapon_mastery":
        owned = char["class_picks"].get("weapon_masteries", [])
        options = []
        for wid, w in registry["weapons"].items():
            mastery = registry["masteries"][w["mastery"]]
            mtext = player_text(registry, "masteries", w["mastery"],
                                mastery["effect"])
            options.append(_opt(wid, w["name"],
                                "%s — %s" % (mastery["name"], mtext),
                                note=w["damage_type"]))
        # weapon masteries are PERMANENT: prior picks are locked, only the
        # newly granted slot(s) are interactive this level (owner P1 review).
        return {"pick": choice["known_total"], "mode": "list", "shape": "list",
                "preselected": list(owned), "locked": list(owned),
                "options": options}

    if ctype == "cantrips":
        pool = ch.cantrip_pool(registry, char, choice)
        need = choice["known_total"] - len(char["spells"]["cantrips"])
        return {"pick": need, "mode": "list", "shape": "list", "preselected": [],
                "options": [_spell_opt(registry, s) for s in pool]}

    if ctype == "spellbook_init":
        pool = [s["id"] for s in ch.spell_slice(registry, char, choice["tier"])]
        return {"pick": choice["choose"], "mode": "list", "shape": "list", "preselected": [],
                "options": [_spell_opt(registry, s) for s in pool]}

    if ctype == "spellbook_add":
        pool = ch.spellbook_add_pool(registry, char)
        banked = char["flags"].get("spellbook_banked", 0)
        result = {"pick": min(choice["count"] + banked, len(pool)),  # G-021
                  "mode": "list", "shape": "list", "preselected": [],
                  "options": [_spell_opt(registry, s) for s in pool]}
        if banked:
            result["note"] = "includes %d banked pick%s" % (
                banked, "" if banked == 1 else "s")
        return result

    if ctype == "invocations":
        feat = registry["features"]["warlock_eldritch_invocations"]
        owned = ch.invocations(char)
        # Invocations with engine support: the three combat hooks plus
        # armor_of_shadows (read by character.ac). The rest are authored but
        # not yet wired -- NOTE them (do NOT disable): known_total reaches 8
        # while only 4 are wired, so the pick must stay satisfiable. The note
        # warns the player so a swap-limited pick is spent knowingly.
        wired_invocations = ("agonizing_blast", "repelling_lash",
                             "grasping_lash", "armor_of_shadows")
        options = []
        for o in feat["options"]:
            locked = o.get("min_level", 1) > char["level"]
            wired = o["id"] in wired_invocations
            note = ""
            if o.get("min_level"):
                note = "level %d+" % o["min_level"]
            if o.get("requires"):
                note = (note + ", " if note else "") + "needs %s" % o["requires"]
            if not wired:
                note = (note + ", " if note else "") + "not yet implemented"
            options.append(_opt(o["id"], o["name"],
                                player_text(registry, "invocations", o["id"],
                                            o["effect"]),
                                disabled=locked, note=note))
        return {"pick": choice["known_total"], "mode": "list", "shape": "list",
                "preselected": list(owned), "options": options}

    if ctype in ("metamagic", "aspects"):
        fid = ("sorcerer_metamagic" if ctype == "metamagic"
               else "druid_aspects")
        feat = registry["features"][fid]
        owned = char["class_picks"].get(ctype, [])
        # metamagic and aspects are cumulative permanent picks (no swap in
        # the GDD): prior picks lock, only the new slots are interactive.
        return {"pick": choice["known_total"], "mode": "list", "shape": "list",
                "preselected": list(owned), "locked": list(owned),
                "options": [_opt(o["id"], o["name"],
                                 player_text(registry, ctype, o["id"], o["effect"]))
                            for o in feat["options"]]}

    if ctype == "circle":
        feat = registry["features"]["druid_circle"]
        return {"pick": 1, "mode": "list", "shape": "single", "preselected": [],
                "options": [_opt(o["id"], o["name"],
                                 player_text(registry, "circle", o["id"], o["effect"]))
                            for o in feat["options"]]}

    if ctype == "feature_option":
        feat = registry["features"][choice["feature"]]
        return {"pick": 1, "mode": "list", "shape": "single", "preselected": [],
                "options": [_opt(o["id"], o["name"],
                                 player_text(registry, "features", o["id"], o["effect"]))
                            for o in feat["options"]]}

    if ctype == "mystic_arcanum":
        pool = [s["id"] for s in ch.spell_slice(registry, char, 6)]
        return {"pick": 1, "mode": "list", "shape": "single", "preselected": [],
                "options": [_spell_opt(registry, s) for s in pool]}

    if ctype == "spells_always_prepared":
        pool = ch.discoveries_pool(registry, char, choice["from"])
        return {"pick": choice["choose"], "mode": "list", "shape": "list", "preselected": [],
                "options": [_spell_opt(registry, s) for s in pool]}

    if ctype == "prepare_spells":
        pool = ch.prepared_pool(registry, char)
        return {"pick": ch.prepared_count(registry, char), "mode": "list",
                "shape": "list", "allow_fewer": True,
                "preselected": list(char["spells"]["prepared"]),
                "options": [_spell_opt(registry, s) for s in pool]}

    if ctype == "magic_initiate":
        return {"pick": 1, "mode": "magic_initiate", "preselected": [],
                "options": []}

    if ctype == "resilient_ability":
        return {"pick": 1, "mode": "list", "shape": "single", "preselected": [],
                "options": [_opt(a, a.upper(),
                                 disabled=char["abilities"][a] >= 20)
                            for a in ch.ABILITIES]}

    raise ValueError("no options presenter for %r" % ctype)
