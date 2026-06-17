# -*- coding: utf-8 -*-
"""Turns choice records into pickable option lists for the generic stepper
screens (creation #3 step 4; the level-up wizard #15.2). All card text
reads from the registry -- rules text exists exactly once (#15.2 L1500-1501).

apply_choice in core.character stays the gate: this module only presents.
"""

from core import character as ch


def player_text(registry, category, rec_id, fallback):
    """The player-voiced display string (GDD #15.0): prefer the re-voiced
    blurb in registry['display'][category][rec_id], else the record's own
    mechanic text. Keeps rules text in the registry, shows warm text."""
    blurb = registry.get("display", {}).get(category, {}).get(rec_id)
    return blurb if blurb else fallback


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


_ABILITY_WORDS = {"str": "Strength", "dex": "Dexterity", "con": "Constitution",
                  "int": "Intelligence", "wis": "Wisdom", "cha": "Charisma"}


def creation_ability_word(aid):
    return _ABILITY_WORDS.get(aid, aid.upper())


def choice_title(choice):
    titles = {
        "skills": "Choose skills",
        "expertise": "Choose Expertise",
        "versatile_talent": "Versatile: choose a Talent",
        "asi_or_talent": "Ability Score Increase or Talent",
        "fighting_style": "Choose a Fighting Style",
        "weapon_mastery": "Choose weapon masteries",
        "cantrips": "Choose cantrips",
        "spellbook_init": "Fill your spellbook",
        "spellbook_add": "Add spells to your spellbook",
        "invocations": "Choose Eldritch Invocations",
        "metamagic": "Choose Metamagic",
        "aspects": "Choose Aspects",
        "circle": "Choose your Circle",
        "mystic_arcanum": "Choose your Mystic Arcanum",
        "spells_always_prepared": "Magical Discoveries",
        "feature_option": "Choose an option",
        "prepare_spells": "Prepare your spells",
        "magic_initiate": "Magic Initiate",
        "resilient_ability": "Resilient: choose an ability",
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
        options = [_opt(s, rec["name"],
                        player_text(registry, "fighting_styles", s, rec["effect"]))
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
        options = []
        for o in feat["options"]:
            locked = o.get("min_level", 1) > char["level"]
            note = ""
            if o.get("min_level"):
                note = "level %d+" % o["min_level"]
            if o.get("requires"):
                note = (note + ", " if note else "") + "needs %s" % o["requires"]
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
