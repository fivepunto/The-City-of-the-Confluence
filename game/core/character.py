# -*- coding: utf-8 -*-
"""Character model: creation (GDD #3), the stored schema (#16.4), derived
stats (recomputed on read, never stored -- #16.4 L1649-1651), and the
choice engine shared by creation and the level-up wizard (#15.2).

Pure Python: no renpy imports. All randomness goes through core.dice.
"""

from core import rules
from core import registry as reg

ABILITIES = ("str", "dex", "con", "int", "wis", "cha")

# The eight slots, GDD #10.2 L1180-1181
EQUIPMENT_SLOTS = ("head", "armor", "feet", "gloves", "ring",
                   "mainhand", "offhand", "cloak")


# ---------------------------------------------------------------------------
# construction (GDD #3, #16.4)

def new_character(registry, char_id, name, class_id, scores):
    """A fresh level-1 character, pre-choices. scores: {ability: 8..15},
    validated against Point Buy elsewhere (#3 L127-130).
    Schema: #16.4 L1642-1648."""
    cls = registry["classes"][class_id]
    char = {
        "id": char_id,
        "name": name,
        "class": class_id,
        "level": 1,
        "xp": 0,
        "abilities": dict(scores),
        "hp": 0,
        "hp_max": 0,
        "temp_hp": 0,
        "skills": {"proficiencies": [], "expertise": []},
        "save_proficiencies": list(cls["saves"]),
        "features": [],
        "talents": [],
        "class_picks": {},
        "conditions": [],
        "resources": {},
        "spells": {"cantrips": [], "prepared": [], "known": []},
        "equipment": {slot: None for slot in EQUIPMENT_SLOTS},
        "reaction_preferences": {},
        "flags": {},
    }
    if cls["skills"].get("fixed"):
        char["skills"]["proficiencies"] = list(cls["skills"]["fixed"])
    grant_level_features(registry, char, 1)
    return char


def grant_level_features(registry, char, level):
    """Append the manifest's feature ids for one level (#15.2 L1498)."""
    cls = registry["classes"][char["class"]]
    for fid in cls["levelup"][level]["features"]:
        if fid not in char["features"]:
            char["features"].append(fid)


def point_buy_ok(registry, scores):
    pb = registry["core"]["point_buy"]
    values = [scores[a] for a in ABILITIES if a in scores]
    if len(values) != 6:
        return False
    if any(not pb["min"] <= v <= pb["max"] for v in values):
        return False
    return rules.point_buy_valid(values, pb["costs"], pb["points"])


# ---------------------------------------------------------------------------
# derived stats -- never stored (#16.4 L1649-1651)

def ability_mod(char, ability):
    return rules.ability_modifier(char["abilities"][ability])


def proficiency(char):
    return rules.proficiency_bonus(char["level"])


def has_feature(char, fid):
    return fid in char["features"]


def fighting_styles(char):
    return char["class_picks"].get("fighting_styles", [])


def invocations(char):
    return char["class_picks"].get("invocations", [])


def chosen_feature_options(registry, char):
    """The option records the character selected through feature_option
    choices (Divine Order / Primal Order at L1, Blessed Strikes / Elemental
    Fury at L7...). class_picks stores each as {feature_id: option_id}; this
    resolves them back to their registry option records so consumers can
    read the option's `grants` block. (The Circle is a separate choice type
    keyed under 'circle', handled by its own callers.)"""
    out = []
    for key, val in char["class_picks"].items():
        if not isinstance(val, str):
            continue
        feat = registry["features"].get(key)
        if not feat or "options" not in feat:
            continue
        for opt in feat["options"]:
            if opt["id"] == val:
                out.append(opt)
    return out


def granted_weapon_tier(registry, char):
    """'martial' when a chosen feature option grants martial weapons --
    Divine Order Protector (#7.3 L480) / Primal Order Warden (#7.10 L765)."""
    for opt in chosen_feature_options(registry, char):
        if opt.get("grants", {}).get("weapons") == "martial":
            return "martial"
    return None


def granted_armor_categories(registry, char):
    """Armor categories granted by chosen feature options (heavy armor from
    Protector / Warden)."""
    cats = set()
    for opt in chosen_feature_options(registry, char):
        cats.update(opt.get("grants", {}).get("armor", []))
    return cats


def armor_record(registry, char):
    aid = char["equipment"]["armor"]
    return registry["armor"][aid] if aid else None


def has_shield(char):
    return char["equipment"]["offhand"] == "shield"


def ac(registry, char):
    """AC per #10.1 L1176-1177 with the unarmored-defense family
    (#7.5 L558-559, #7.11 L820, #7.12 L878-880, invocation Armor of
    Shadows #7.7 L653) and the Defense fighting style (#8.2 L927)."""
    armor = armor_record(registry, char)
    shield = has_shield(char)
    dex = ability_mod(char, "dex")
    if armor:
        total = rules.armor_ac(armor["base_ac"], dex,
                               dex_cap=armor["dex_cap"], shield=shield)
        if "defense" in fighting_styles(char):
            total += 1
        return total
    cls = registry["classes"][char["class"]]
    unarmored = cls.get("unarmored_defense")
    if unarmored:
        second = sum(ability_mod(char, a) for a in unarmored["add"]
                     if a != "dex")
        return rules.unarmored_ac(dex, second, base=unarmored["base"],
                                  shield=shield)
    if has_feature(char, "sorcerer_draconic_resilience"):
        return rules.unarmored_ac(dex, ability_mod(char, "cha"))
    if "armor_of_shadows" in invocations(char):
        return rules.unarmored_ac(dex, 0, base=13, shield=shield)
    return rules.unarmored_ac(dex, 0, shield=shield)


def save_mod(char, ability):
    return rules.save_modifier(ability_mod(char, ability), proficiency(char),
                               ability in char["save_proficiencies"])


def skill_mod(registry, char, skill_id):
    skill = registry["skills"][skill_id]
    total = rules.skill_total(
        ability_mod(char, skill["ability"]), proficiency(char),
        proficient=skill_id in char["skills"]["proficiencies"],
        expertise=skill_id in char["skills"]["expertise"],
        half_prof_untrained=has_feature(char, "bard_jack_of_all_trades"))
    # feature-option skill bonuses: Divine Order Thaumaturge / Primal Order
    # Magician add the Wisdom modifier to Lore checks (#7.3 L480-482,
    # #7.10 L763-765)
    for opt in chosen_feature_options(registry, char):
        sb = opt.get("grants", {}).get("skill_bonus")
        if sb and skill_id in sb["skills"]:
            total += ability_mod(char, sb["ability"])
    return total


def initiative_mod(char):
    alert = (proficiency(char) if "alert" in char["talents"] else 0)
    return rules.initiative_modifier(ability_mod(char, "dex"),
                                     alert_prof_bonus=alert)


def hp_bonus_per_level(char):
    """Flat per-level HP riders: Tough (#8.1 L915), Draconic Resilience
    (+3 then +1 per later level == +1/level +2 flat from level 3 on;
    #7.12 L878-879)."""
    return 2 if "tough" in char["talents"] else 0


def recompute_hp_max(registry, char, keep_damage=True):
    """#2.6 L90-93, from the current Constitution (ASIs apply to every
    level's contribution). Stored per the #16.4 schema; everything else
    derived."""
    cls = registry["classes"][char["class"]]
    new_max = rules.hp_max(cls["hit_die"], char["level"],
                           ability_mod(char, "con"),
                           flat_bonus_per_level=hp_bonus_per_level(char))
    if has_feature(char, "sorcerer_draconic_resilience"):
        # +3 at level 3, +1 per sorcerer level gained afterward
        new_max += 3 + max(0, char["level"] - 3)
    damage = max(0, char["hp_max"] - char["hp"]) if keep_damage else 0
    char["hp_max"] = new_max
    char["hp"] = max(1, new_max - damage) if keep_damage else new_max
    return new_max


def spell_slice(registry, char, tier=None):
    return reg.spell_slice(registry["spells"], char["class"], tier)


def caster_info(registry, char):
    return registry["classes"][char["class"]]["caster"]


def slots_max(registry, char):
    """{tier: count} for the character's level. Full/half tables and Pact
    Magic (#7 L394-395, #7.7 L634-639)."""
    caster = caster_info(registry, char)
    if not caster:
        return {}
    if caster["kind"] == "pact":
        pact = registry["core"]["pact_slots"]
        count = reg.by_level(pact["slots_by_level"], char["level"])
        return {"pact": count}
    table = (registry["core"]["slot_table_full"] if caster["kind"] == "full"
             else registry["core"]["slot_table_half"])
    return dict(table["by_level"][char["level"]])


def pact_tier(registry, char):
    pact = registry["core"]["pact_slots"]
    return reg.by_level(pact["tier_by_level"], char["level"])


def prepared_count(registry, char):
    caster = caster_info(registry, char)
    if not caster or not caster.get("prepared"):
        return 0
    return registry["core"]["prepared_spells"]["by_class"][char["class"]][char["level"] - 1]


def always_prepared(registry, char):
    """Spell ids granted by features (domain lists etc.), filtered to the
    tiers the character can currently cast -- 'each pair unlocks with its
    tier' (#7.3 L493-495); at_level grants unlock by character level."""
    out = []
    caster = caster_info(registry, char)
    max_tier = 0
    if caster:
        if caster["kind"] == "pact":
            max_tier = pact_tier(registry, char)
        else:
            tiers = [t for t in slots_max(registry, char) if isinstance(t, int)]
            max_tier = max(tiers) if tiers else 0
    for fid in char["features"]:
        feat = registry["features"][fid]
        for grant in feat.get("grants_spells", []):
            if "tier" in grant and grant["tier"] <= max_tier:
                out.append(grant["spell"])
            elif "at_level" in grant and grant["at_level"] <= char["level"]:
                out.append(grant["spell"])
    # option-granted always-prepared spells: the chosen Druid Circle's Ruin
    # Spells (#7.10 L783-785) and any feature-option grants. grants_spells
    # on the OPTION record is invisible to the feature loop above, so the
    # chosen option must be resolved explicitly.
    option_records = list(chosen_feature_options(registry, char))
    circle_id = char["class_picks"].get("circle")
    if circle_id:
        circle_feat = registry["features"]["druid_circle"]
        option_records += [o for o in circle_feat["options"]
                           if o["id"] == circle_id]
    for opt in option_records:
        for grant in opt.get("grants_spells", []):
            if "tier" in grant and grant["tier"] <= max_tier:
                out.append(grant["spell"])
            elif "at_level" in grant and grant["at_level"] <= char["level"]:
                out.append(grant["spell"])
    for sid in char["class_picks"].get("magical_discoveries", []):
        out.append(sid)
    # dedup at the single chokepoint, order preserved: two always-prepared
    # sources can grant the same spell, and the sheet must not list it twice
    seen = []
    for sid in out:
        if sid not in seen:
            seen.append(sid)
    return seen


def resolve_amount(char, amount):
    """Resolve a feature-uses amount token (data convention from P0)."""
    if isinstance(amount, int):
        return amount
    if isinstance(amount, dict) and "by_level" in amount:
        return reg.by_level(amount["by_level"], char["level"]) or 0
    if amount == "prof":
        return proficiency(char)
    if amount == "level":
        return char["level"]
    if amount == "level_div_3":
        return char["level"] // 3
    if isinstance(amount, str) and amount.endswith("_mod"):
        return max(0, ability_mod(char, amount[:-4]))
    raise ValueError("unknown uses amount: %r" % (amount,))


def resource_row(registry, char):
    """The per-class resource row of the sheet (#15.3 L1512-1514):
    {key: {'current', 'max', 'label'}}. Maxes derived on read."""
    row = {}
    res = char["resources"]
    caster = caster_info(registry, char)
    if caster and caster["kind"] != "pact":
        for tier, count in sorted(slots_max(registry, char).items()):
            key = "slot_%d" % tier
            row[key] = {"current": res.get("slots", {}).get(tier, count),
                        "max": count, "label": "Tier %d slots" % tier}
    if caster and caster["kind"] == "pact":
        count = slots_max(registry, char)["pact"]
        row["pact_slots"] = {
            "current": res.get("pact_slots", count), "max": count,
            "label": "Pact slots (tier %d)" % pact_tier(registry, char)}
    def feature_pool(fid, key, label, registry=registry):
        if has_feature(char, fid):
            feat = registry["features"][fid]
            amount = resolve_amount(char, feat["uses"]["amount"])
            row[key] = {"current": res.get(key, amount), "max": amount,
                        "label": label}
    if has_feature(char, "sorcerer_font_of_magic"):
        row["sorcery_points"] = {
            "current": res.get("sorcery_points", char["level"]),
            "max": char["level"], "label": "Sorcery Points"}
    feature_pool("fighter_second_wind", "second_wind", "Second Wind")
    feature_pool("fighter_action_surge", "action_surge", "Action Surge")
    feature_pool("monk_monks_focus", "focus_points", "Focus Points")
    feature_pool("barbarian_rage", "rage", "Rage uses")
    feature_pool("bard_bardic_inspiration", "bardic", "Bardic Inspiration")
    feature_pool("cleric_channel_divinity", "channel_divinity",
                 "Channel Divinity")
    feature_pool("paladin_channel_divinity", "channel_divinity",
                 "Channel Divinity")
    if has_feature(char, "paladin_lay_on_hands"):
        pool = 5 * char["level"]
        row["lay_on_hands_pool"] = {
            "current": res.get("lay_on_hands_pool", pool), "max": pool,
            "label": "Lay on Hands pool"}
    row["recovery_dice"] = {
        "current": res.get("recovery_dice", char["level"]),
        "max": char["level"], "label": "Recovery Dice"}
    row["heroic_inspiration"] = {
        "current": res.get("heroic_inspiration", 1), "max": 1,
        "label": "Heroic Inspiration"}
    return row


def refill_resources(registry, char):
    """Set every tracked pool to its maximum (creation; Camp uses this in
    P4 -- #12.1 L1333-1336 'restores everything')."""
    char["resources"] = {}
    row = resource_row(registry, char)
    slots = {}
    for key, entry in row.items():
        if key.startswith("slot_"):
            slots[int(key.split("_")[1])] = entry["max"]
        else:
            char["resources"][key] = entry["max"]
    if slots:
        char["resources"]["slots"] = slots
    char["temp_hp"] = 0


def gain_new_capacity(registry, char, old_resource_row):
    """Level-up resource handling (GDD #6: a level-up grants NO rest; only
    Camp restores everything, #12.1 L1334-1336). Add ONLY the newly-gained
    max capacity for each pool and leave already-spent resources spent; a pool
    that is brand-new at this level starts full. The level-up counterpart to
    refill_resources (which fully restores, for Camp / fresh synthesis). HP is
    handled by recompute_hp_max; temp_hp is left untouched (not a rest)."""
    new_row = resource_row(registry, char)
    char["resources"] = {}
    slots = {}
    for key, entry in new_row.items():
        old_max = old_resource_row.get(key, {}).get("max", 0)
        growth = max(0, entry["max"] - old_max)
        # entry["current"] reads the stored (spent-down) value, or the new max
        # for an unspent / brand-new pool; add only the new capacity on top
        current = min(entry["current"] + growth, entry["max"])
        if key.startswith("slot_"):
            slots[int(key.split("_")[1])] = current
        else:
            char["resources"][key] = current
    if slots:
        char["resources"]["slots"] = slots


def hp_gain_for_level(registry, char):
    """The fixed HP gained at the character's current level (#2.6): the chassis
    HP from reg.levelup (the single source of per-level chassis HP) plus the
    Constitution modifier. Screens read this instead of re-deriving the
    formula."""
    return reg.levelup(registry, char["class"], char["level"])["hp"] + \
        ability_mod(char, "con")


# ---------------------------------------------------------------------------
# the choice engine (creation #3 step 4; level-up wizard #15.2)

def manifest_choices(registry, char, level):
    """The pending choice records for one level, plus creation-only steps
    at level 1 (#3 L131-142: class skills, Human Skillful + Versatile)."""
    cls = registry["classes"][char["class"]]
    pending = []
    if level == 1:
        if cls["skills"].get("choose"):
            pending.append({"type": "skills", "choose": cls["skills"]["choose"],
                            "from": cls["skills"]["from"], "src": cls["src"]})
        # Human Skillful: proficiency in one skill (#3 L140)
        pending.append({"type": "skills", "choose": 1, "from": "any",
                        "human": "skillful", "src": "§3 L140"})
        # Human Versatile: one starter Talent (#3 L141-142)
        pending.append({"type": "versatile_talent",
                        "from": registry["core"]["human"]["traits"]["versatile"]["choices"],
                        "src": "§3 L141-142"})
    pending.extend(dict(c) for c in cls["levelup"][level]["choices"])
    if level == 1 and caster_info(registry, char) and \
            caster_info(registry, char).get("prepared"):
        # initial preparation -- "re-choose ... at Camp" implies a first
        # choice at creation (#7 L395; GAPS G-020)
        pending.append({"type": "prepare_spells", "src": "§7 L395"})
    return pending


def legal_skill_choices(registry, char, choice):
    pool = (list(registry["skills"]) if choice["from"] == "any"
            else list(choice["from"]))
    return [s for s in pool if s not in char["skills"]["proficiencies"]]


def cantrip_pool(registry, char, choice):
    classes = choice["from"]
    if isinstance(classes, str):
        classes = [classes]
    pool = []
    for cls_id in classes:
        for sp in reg.spell_slice(registry["spells"], cls_id, 0):
            if sp["id"] not in pool:
                pool.append(sp["id"])
    return [s for s in pool if s not in char["spells"]["cantrips"]]


def castable_tier_max(registry, char):
    """Highest spell tier the character can currently cast."""
    caster = caster_info(registry, char)
    if not caster:
        return 0
    if caster["kind"] == "pact":
        return pact_tier(registry, char)
    tiers = [t for t in slots_max(registry, char) if isinstance(t, int)]
    return max(tiers) if tiers else 0


def spellbook_add_pool(registry, char):
    """Unknown wizard-slice spells of castable tiers (#7.4 L529)."""
    max_tier = max(castable_tier_max(registry, char), 1)
    return [s["id"] for t in range(1, max_tier + 1)
            for s in spell_slice(registry, char, t)
            if s["id"] not in char["spells"]["known"]]


def prepared_pool(registry, char):
    """Spells the character may prepare: the wizard prepares from the book,
    everyone else from their slice; Magical Secrets widens the Bard's pool
    (#7.8 L733-734)."""
    max_tier = castable_tier_max(registry, char)
    if char["class"] == "wizard":
        pool = [s for s in char["spells"]["known"]
                if registry["spells"][s]["tier"] <= max_tier]
    else:
        pool = [s["id"] for t in range(1, max_tier + 1)
                for s in spell_slice(registry, char, t)]
    if has_feature(char, "bard_magical_secrets"):
        for cls_id in ("cleric", "druid", "wizard"):
            for t in range(1, max_tier + 1):
                for sp in reg.spell_slice(registry["spells"], cls_id, t):
                    if sp["id"] not in pool:
                        pool.append(sp["id"])
    return pool


def discoveries_pool(registry, char, classes):
    """Pool for spells_always_prepared choices (#7.8 L729-730)."""
    max_tier = max(castable_tier_max(registry, char), 1)
    pool = []
    for cls_id in classes:
        for t in range(1, max_tier + 1):
            for sp in reg.spell_slice(registry["spells"], cls_id, t):
                if sp["id"] not in pool:
                    pool.append(sp["id"])
    return pool


def apply_choice(registry, char, choice, selection):
    """Apply one resolved choice. Selections are validated; raises
    ValueError on an illegal pick. Choices are FINAL once committed --
    there is no respec (#6 L377, #15.2 L1495)."""
    ctype = choice["type"]

    if ctype == "skills":
        legal = legal_skill_choices(registry, char, choice)
        if len(selection) != choice["choose"] or \
                any(s not in legal for s in selection):
            raise ValueError("illegal skill picks: %r" % (selection,))
        char["skills"]["proficiencies"].extend(selection)

    elif ctype == "expertise":
        pool = choice.get("from") or char["skills"]["proficiencies"]
        legal = [s for s in pool if s in char["skills"]["proficiencies"]
                 and s not in char["skills"]["expertise"]]
        if len(selection) != choice["choose"] or \
                any(s not in legal for s in selection):
            raise ValueError("illegal expertise picks: %r" % (selection,))
        char["skills"]["expertise"].extend(selection)

    elif ctype == "versatile_talent":
        if selection not in choice["from"]:
            raise ValueError("not a Versatile starter talent: %r" % selection)
        return add_talent(registry, char, selection)

    elif ctype == "asi_or_talent":
        return apply_asi_or_talent(registry, char, selection)

    elif ctype == "fighting_style":
        styles = char["class_picks"].setdefault("fighting_styles", [])
        if selection == choice.get("or_feature"):
            char["features"].append(selection)
            feat = registry["features"][selection]
            # Druidic/Blessed Warrior grant 2 cantrips from another set
            if "druidic" in selection:
                return [{"type": "cantrips", "known_total":
                         len(char["spells"]["cantrips"]) + 2, "from": "druid"}]
            if "blessed" in selection:
                return [{"type": "cantrips", "known_total":
                         len(char["spells"]["cantrips"]) + 2, "from": "cleric"}]
            return []
        if selection not in registry["fighting_styles"] or \
                selection in styles:
            raise ValueError("illegal fighting style: %r" % selection)
        styles.append(selection)

    elif ctype == "weapon_mastery":
        legal = [w["id"] for w in registry["weapons"].values()]
        owned = char["class_picks"].get("weapon_masteries", [])
        if len(selection) != choice["known_total"] or \
                len(set(selection)) != len(selection) or \
                any(w not in legal for w in selection):
            raise ValueError("illegal mastery picks: %r" % (selection,))
        # weapon masteries are permanent: every prior pick must remain
        # (owner adjudication, P1 review)
        if any(o not in selection for o in owned):
            raise ValueError("weapon masteries are permanent; a prior pick "
                             "cannot be dropped: %r" % (selection,))
        char["class_picks"]["weapon_masteries"] = list(selection)

    elif ctype == "cantrips":
        pool = cantrip_pool(registry, char, choice)
        need = choice["known_total"] - len(char["spells"]["cantrips"])
        if len(selection) != need or any(s not in pool for s in selection):
            raise ValueError("illegal cantrip picks: %r" % (selection,))
        char["spells"]["cantrips"].extend(selection)

    elif ctype == "spellbook_init":
        pool = [s["id"] for s in spell_slice(registry, char, choice["tier"])]
        if len(selection) != choice["choose"] or \
                any(s not in pool for s in selection):
            raise ValueError("illegal spellbook picks: %r" % (selection,))
        char["spells"]["known"].extend(selection)

    elif ctype == "spellbook_add":
        pool = spellbook_add_pool(registry, char)
        # G-021 (owner adjudication, P1): when the castable slice is
        # exhausted, unspent free picks BANK and may be spent at any later
        # level-up where options exist (#7.4 L527-528).
        owed = choice["count"] + char["flags"].get("spellbook_banked", 0)
        take = min(owed, len(pool))
        if len(selection) != take or any(s not in pool for s in selection):
            raise ValueError("illegal spellbook additions: %r" % (selection,))
        char["spells"]["known"].extend(selection)
        banked = owed - take
        if banked:
            char["flags"]["spellbook_banked"] = banked
        else:
            char["flags"].pop("spellbook_banked", None)

    elif ctype == "invocations":
        feat = registry["features"]["warlock_eldritch_invocations"]
        owned = char["class_picks"].setdefault("invocations", [])
        options = {o["id"]: o for o in feat["options"]}
        if len(selection) != choice["known_total"] or \
                len(set(selection)) != len(selection):
            raise ValueError("invocation count mismatch")
        for inv in selection:
            opt = options.get(inv)
            if opt is None:
                raise ValueError("unknown invocation: %r" % inv)
            if opt.get("min_level", 1) > char["level"]:
                raise ValueError("%s needs level %d" % (inv, opt["min_level"]))
            if opt.get("requires") and opt["requires"] not in selection:
                raise ValueError("%s requires %s" % (inv, opt["requires"]))
        char["class_picks"]["invocations"] = list(selection)

    elif ctype == "metamagic":
        feat = registry["features"]["sorcerer_metamagic"]
        legal = {o["id"] for o in feat["options"]}
        owned = char["class_picks"].get("metamagic", [])
        if len(selection) != choice["known_total"] or \
                len(set(selection)) != len(selection) or \
                any(s not in legal for s in selection):
            raise ValueError("illegal metamagic: %r" % (selection,))
        # cumulative permanent: prior picks must remain
        if any(o not in selection for o in owned):
            raise ValueError("metamagic is permanent; a prior pick cannot "
                             "be dropped: %r" % (selection,))
        char["class_picks"]["metamagic"] = list(selection)

    elif ctype == "aspects":
        feat = registry["features"]["druid_aspects"]
        legal = {o["id"] for o in feat["options"]}
        owned = char["class_picks"].get("aspects", [])
        if len(selection) != choice["known_total"] or \
                len(set(selection)) != len(selection) or \
                any(s not in legal for s in selection):
            raise ValueError("illegal aspects: %r" % (selection,))
        # cumulative permanent: prior picks must remain
        if any(o not in selection for o in owned):
            raise ValueError("aspects are permanent; a prior pick cannot "
                             "be dropped: %r" % (selection,))
        char["class_picks"]["aspects"] = list(selection)

    elif ctype == "circle":
        feat = registry["features"]["druid_circle"]
        legal = {o["id"] for o in feat["options"]}
        if selection not in legal:
            raise ValueError("illegal circle: %r" % selection)
        char["class_picks"]["circle"] = selection

    elif ctype == "mystic_arcanum":
        pool = [s["id"] for s in spell_slice(registry, char, 6)]
        if selection not in pool:
            raise ValueError("illegal arcanum: %r" % selection)
        char["class_picks"]["mystic_arcanum"] = selection

    elif ctype == "spells_always_prepared":
        pool = discoveries_pool(registry, char, choice["from"])
        if len(selection) != choice["choose"] or \
                any(s not in pool for s in selection):
            raise ValueError("illegal discoveries: %r" % (selection,))
        char["class_picks"]["magical_discoveries"] = list(selection)

    elif ctype == "feature_option":
        feat = registry["features"][choice["feature"]]
        options = {o["id"]: o for o in feat["options"]}
        if selection not in options:
            raise ValueError("illegal option for %s: %r"
                             % (choice["feature"], selection))
        char["class_picks"][choice["feature"]] = selection
        # an option may grant extra cantrips: Divine Order Thaumaturge
        # (#7.3 L480-482) / Primal Order Magician (#7.10 L763-765). Queue
        # the follow-up cantrips choice, mirroring the Druidic/Blessed
        # Warrior path in the fighting_style branch above.
        extra = options[selection].get("grants", {}).get("cantrips", 0)
        if extra:
            return [{"type": "cantrips",
                     "known_total": len(char["spells"]["cantrips"]) + extra,
                     "from": feat["class"]}]

    elif ctype == "prepare_spells":
        return prepare_spells(registry, char, selection)

    elif ctype == "magic_initiate":
        return apply_magic_initiate(registry, char, selection)

    elif ctype == "resilient_ability":
        return apply_resilient(registry, char, selection)

    else:
        raise ValueError("unknown choice type: %r" % ctype)
    return []


def add_talent(registry, char, talent_id):
    """#8.1 L904-906: talents cannot be taken twice. Returns follow-up
    choices the talent itself demands."""
    if talent_id in char["talents"]:
        raise ValueError("talent already taken: %r" % talent_id)
    if talent_id not in registry["talents"]:
        raise ValueError("unknown talent: %r" % talent_id)
    char["talents"].append(talent_id)
    follow = []
    if talent_id == "skilled":          # 2 skill proficiencies (#8.1 L914)
        follow.append({"type": "skills", "choose": 2, "from": "any"})
    elif talent_id == "tough":          # recompute (#8.1 L915)
        recompute_hp_max(registry, char)
    elif talent_id == "resilient":      # +1 score + save prof (#8.1 L916)
        follow.append({"type": "resilient_ability"})
    elif talent_id == "magic_initiate":  # (#8.1 L912)
        follow.append({"type": "magic_initiate"})
    return follow


def apply_asi_or_talent(registry, char, selection):
    """#6 L373-374: +2 ability points (or +1 to two) OR one Talent."""
    if selection.get("mode") == "talent":
        return add_talent(registry, char, selection["talent"])
    increases = selection["scores"]
    if sum(increases.values()) != 2 or \
            any(v not in (1, 2) for v in increases.values()) or \
            any(a not in ABILITIES for a in increases):
        raise ValueError("illegal ASI: %r" % (increases,))
    for ability, inc in increases.items():
        if char["abilities"][ability] + inc > 20:   # cap 20, #2.1 L48
            raise ValueError("%s would exceed 20" % ability)
        char["abilities"][ability] += inc
    if "con" in increases:
        recompute_hp_max(registry, char)
    return []


def apply_magic_initiate(registry, char, selection):
    """#8.1 L912: choose one class slice; learn 2 of its cantrips and one
    tier 1 spell. selection: {'class', 'cantrips': [2], 'spell'}."""
    cls_id = selection["class"]
    if cls_id not in reg.CASTER_CLASS_IDS:
        raise ValueError("not a caster slice: %r" % cls_id)
    cantrips = [s["id"] for s in reg.spell_slice(registry["spells"], cls_id, 0)
                if s["id"] not in char["spells"]["cantrips"]]
    tier1 = [s["id"] for s in reg.spell_slice(registry["spells"], cls_id, 1)]
    picks = selection["cantrips"]
    if len(picks) != 2 or any(p not in cantrips for p in picks):
        raise ValueError("illegal magic initiate cantrips: %r" % (picks,))
    if selection["spell"] not in tier1:
        raise ValueError("illegal magic initiate spell: %r" % selection["spell"])
    char["spells"]["cantrips"].extend(picks)
    char["class_picks"]["magic_initiate"] = {
        "class": cls_id, "spell": selection["spell"]}
    return []


def apply_resilient(registry, char, ability):
    """#8.1 L916: +1 to one ability and proficiency in its saves."""
    if ability not in ABILITIES:
        raise ValueError("bad ability: %r" % ability)
    if char["abilities"][ability] >= 20:
        raise ValueError("%s already 20" % ability)
    char["abilities"][ability] += 1
    if ability not in char["save_proficiencies"]:
        char["save_proficiencies"].append(ability)
    if ability == "con":
        recompute_hp_max(registry, char)
    return []


def prepare_spells(registry, char, selection):
    """Choose the prepared list (count per the standard table; #7 L395,
    GAPS G-020 for the creation-time first pick). Always-prepared grants
    don't count against the number."""
    count = prepared_count(registry, char)
    pool = prepared_pool(registry, char)
    if len(selection) > count or any(s not in pool for s in selection):
        raise ValueError("illegal prepared list: %r" % (selection,))
    char["spells"]["prepared"] = list(selection)
    return []


# ---------------------------------------------------------------------------
# creation finalization and level-up

def finalize_creation(registry, char):
    """After all choices: HP (#2.6), resources, starting kit (#10.6)."""
    recompute_hp_max(registry, char, keep_damage=False)
    refill_resources(registry, char)
    return char


def xp_threshold(registry, level):
    return registry["core"]["xp_thresholds"]["by_level"][level - 1]


def can_level_up(registry, char):
    """#6 L370-372; the + badge condition (#15.1 L1478-1479). Called by the
    HUD for every party member, so it must tolerate a member without an xp
    key: only the protagonist accrues XP (#6 L378-379), so a follower (or a
    legacy/partial record) may legitimately carry no xp -- such a member
    simply can never level."""
    level = char.get("level", 1)
    xp = char.get("xp")
    if level >= 12 or xp is None:
        return False
    return xp >= xp_threshold(registry, level + 1)


def level_up(registry, char):
    """Raise one level, grant features, return the pending choices for the
    wizard (#15.2). Caller collects selections, applies them via
    apply_choice, then calls finalize_level_up. One level at a time --
    multi-level gains run the wizard repeatedly (#15.2 L1494)."""
    if not can_level_up(registry, char):
        raise ValueError("not enough XP to level")
    char["level"] += 1
    grant_level_features(registry, char, char["level"])
    return manifest_choices(registry, char, char["level"])


def finalize_level_up(registry, char, old_resource_row=None):
    """Flush a level-up onto the working character: grow HP max (keeping
    accumulated damage) and add this level's newly-gained resource capacity.
    GDD #6 grants NO rest at level-up; only Camp restores everything (#12.1
    L1334-1336). An in-game level-up passes old_resource_row (the pre-level-up
    row) so only new capacity is added and spent resources stay spent; a None
    call (fresh debug synthesis) fully refills."""
    recompute_hp_max(registry, char)
    if old_resource_row is not None:
        gain_new_capacity(registry, char, old_resource_row)
    else:
        refill_resources(registry, char)
    return char
