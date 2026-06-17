"""Registry access and validation helpers. Pure functions over the data
assembled by game/data/__init__.py -- this module never imports game.data,
so there is no import cycle and tests can feed it fixtures.
"""

import re

ABILITY_IDS = ("str", "dex", "con", "int", "wis", "cha")

CASTER_CLASS_IDS = ("wizard", "sorcerer", "cleric", "druid", "bard",
                    "warlock", "paladin", "ranger")

SPELL_ROLES = ("damage", "heal", "true_heal", "buff", "debuff", "control",
               "utility", "summon")


def by_level(table, level):
    """Resolve a {level: value} scaling map: value at the highest key <= level
    (DECISIONS.md D-004)."""
    best = None
    for lvl in sorted(table):
        if lvl <= level:
            best = table[lvl]
    return best


def levelup(registry, class_id, level):
    """LEVELUP[class][level] -> {hp, features, choices} (GDD #15.2, L1482).
    hp is computed from the chassis at read time (DECISIONS.md D-003);
    the Constitution modifier is added by the caller, per #2.6."""
    cls = registry["classes"][class_id]
    manifest = cls["levelup"][level]
    die = cls["hit_die"]
    hp = die if level == 1 else die // 2 + 1
    return {"hp": hp, "features": manifest["features"],
            "choices": manifest["choices"]}


def derive_slice_matrix(spells):
    """Re-derive the #9.2 access matrix from spell class tags. The tags in
    the spell tables are the source of truth; the printed matrix is derived
    (GDD #9.2, L978-980). Returns {class_id: {tier: count}} with tier 0 =
    cantrips."""
    matrix = {}
    for spell in spells.values():
        for cls in spell["classes"]:
            matrix.setdefault(cls, {t: 0 for t in range(7)})
            matrix[cls][spell["tier"]] += 1
    return matrix


def spell_slice(spells, class_id, tier=None):
    """A class's spell list: the pool filtered to its tag (GDD #9.2, L962)."""
    out = []
    for spell in spells.values():
        if class_id in spell["classes"] and (tier is None or spell["tier"] == tier):
            out.append(spell)
    return sorted(out, key=lambda s: (s["tier"], s["id"]))


def validate(registry):
    """Structural validation of the assembled registry. Returns a list of
    problem strings; empty list = valid. The doc-integrity test suite asserts
    counts; this asserts shape and referential integrity."""
    problems = []

    def check_src(record, where):
        src = record.get("src")
        if not src or not isinstance(src, str) or not src.startswith("\xa7"):
            problems.append("%s: bad or missing src %r" % (where, src))

    # unique ids within each kind
    for kind, records in registry.items():
        if not isinstance(records, dict):
            continue
        for rid, rec in records.items():
            if isinstance(rec, dict) and "id" in rec and rec["id"] != rid:
                problems.append("%s[%s]: id mismatch %r" % (kind, rid, rec["id"]))

    spells = registry["spells"]
    classes = registry["classes"]
    features = registry["features"]
    weapons = registry["weapons"]
    armor = registry["armor"]
    masteries = registry["masteries"]
    conditions = registry["conditions"]

    for sid, sp in spells.items():
        where = "spells[%s]" % sid
        check_src(sp, where)
        if sp["tier"] not in range(7):
            problems.append("%s: bad tier %r" % (where, sp["tier"]))
        for role in sp["roles"]:
            if role not in SPELL_ROLES:
                problems.append("%s: bad role %r" % (where, role))
        for cls in sp["classes"]:
            if cls not in CASTER_CLASS_IDS:
                problems.append("%s: bad class tag %r" % (where, cls))
        if sp.get("save") and sp["save"]["ability"] not in ABILITY_IDS:
            problems.append("%s: bad save ability" % where)

    for cid, cls in classes.items():
        where = "classes[%s]" % cid
        check_src(cls, where)
        if set(cls["levelup"].keys()) != set(range(1, 13)):
            problems.append("%s: levelup must cover levels 1-12" % where)
            continue
        for lvl, entry in cls["levelup"].items():
            for fid in entry["features"]:
                if fid not in features:
                    problems.append("%s L%d: unknown feature %r" % (where, lvl, fid))
            for choice in entry["choices"]:
                if "type" not in choice:
                    problems.append("%s L%d: choice missing type" % (where, lvl))

    for fid, feat in features.items():
        check_src(feat, "features[%s]" % fid)

    for wid, w in weapons.items():
        where = "weapons[%s]" % wid
        check_src(w, where)
        if w["mastery"] not in masteries:
            problems.append("%s: unknown mastery %r" % (where, w["mastery"]))

    for aid, a in armor.items():
        check_src(a, "armor[%s]" % aid)

    for cid, c in conditions.items():
        check_src(c, "conditions[%s]" % cid)

    for eid, enemy in registry["enemies"].items():
        where = "enemies[%s]" % eid
        check_src(enemy, where)
        for rule in enemy["intent"]:
            if "if" not in rule or "do" not in rule:
                problems.append("%s: malformed intent rule %r" % (where, rule))

    for kit_class, kit in registry["starting_equipment"].items():
        if kit_class not in classes:
            problems.append("starting_equipment: unknown class %r" % kit_class)
        for item in kit["items"]:
            if item not in weapons and item not in armor and \
                    item not in registry["consumables"] and \
                    item not in ("spellbook",):
                problems.append("starting_equipment[%s]: unknown item %r"
                                % (kit_class, item))

    return problems


def content_problems(registry):
    """On-demand content validation for the debug-hub "Validate content"
    button (CLAUDE.md). Returns a list[str] of problems (empty = clean),
    composing three checks over the assembled registry:
      (a) validate() structural / referential integrity,
      (b) the spell-slice matrix re-derived from spell tags vs the GDD #9.2
          literal counts (a literal-number check per GDD 16.5, never a data
          block), and
      (c) a player-voice jargon scan of the DISPLAY strings (GDD 15.0)."""
    problems = ["structure: " + p for p in validate(registry)]

    # (b) the GDD #9.2 access matrix (docs/gdd.md L965-974); index 0 = cantrips,
    # a dash in the doc = 0. These literal counts are writer calibration
    # (GDD 16.5), copied from the doc and kept here -- never a data block.
    expected_9_2 = {
        "wizard":   [6, 7, 10, 10, 9, 7, 7],
        "sorcerer": [6, 6, 7, 6, 6, 4, 4],
        "cleric":   [4, 5, 7, 8, 5, 4, 5],
        "druid":    [5, 5, 7, 7, 6, 5, 4],
        "bard":     [3, 7, 5, 7, 4, 3, 2],
        "warlock":  [4, 3, 4, 3, 4, 3, 2],
        "paladin":  [0, 4, 3, 2, 0, 0, 0],
        "ranger":   [0, 3, 3, 3, 0, 0, 0],
    }
    matrix = derive_slice_matrix(registry["spells"])
    for cls, expected in expected_9_2.items():
        got = matrix.get(cls, {})
        for tier in range(7):
            if got.get(tier, 0) != expected[tier]:
                problems.append("slice 9.2 %s tier%d: expected %d got %d"
                                % (cls, tier, expected[tier], got.get(tier, 0)))

    # (c) the player-voice jargon scan (GDD 15.0). Dice/label tokens match as
    # plain substrings; ability abbreviations and the saving-throw noun match
    # on word boundaries (a bare "Cha"/"Dex"/... substring hits ordinary words
    # like Charisma/Dexterity). The banned plural "saves" is scanned rather
    # than the verb "save" so legitimate prose ("save up") does not trip it.
    substr_tokens = ("d4", "d6", "d8", "d10", "d12", "d20", "DC ", "AC ")
    word_tokens = ("Cha", "Dex", "Str", "Con", "Int", "Wis", "saves")
    for category, records in registry.get("display", {}).items():
        if not isinstance(records, dict):
            continue
        for rid, blurb in records.items():
            if not isinstance(blurb, str):
                continue
            for tok in substr_tokens:
                if tok in blurb:
                    problems.append("jargon: display[%s][%s] contains %r"
                                    % (category, rid, tok))
            for tok in word_tokens:
                if re.search(r"\b" + tok + r"\b", blurb):
                    problems.append("jargon: display[%s][%s] contains %r"
                                    % (category, rid, tok))
    return problems
