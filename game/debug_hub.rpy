# P0 debug hub: registry browser + RNG seeding (CLAUDE.md P0).
# Later-phase debug actions appear as disabled stubs (DECISIONS.md D-009).
# Dev tool: plain default styling (the GUI discipline applies to game
# screens from P1).

init python:
    import pprint
    import store
    import data as _gd
    from core import dice as _dice

    # Curated browse order; falls back to sorted for anything new.
    _DEBUG_KIND_ORDER = [
        "classes", "features", "spells", "upcast_rules", "talents",
        "fighting_styles", "conditions", "skills", "weapons",
        "weapon_properties", "armor", "masteries", "equipment_slots",
        "rarities", "starting_equipment", "starting_common", "consumables",
        "camp_upgrades", "enemies", "intent_vocab", "summons", "economy",
        "core",
    ]

    def debug_kinds():
        known = [k for k in _DEBUG_KIND_ORDER if k in _gd.REGISTRY]
        extra = sorted(k for k in _gd.REGISTRY if k not in _DEBUG_KIND_ORDER)
        return known + extra

    def debug_kind_items(kind):
        value = _gd.REGISTRY.get(kind)
        if isinstance(value, dict):
            return sorted(value.keys(), key=str)
        return ["(value)"]

    def debug_detail(kind, item):
        value = _gd.REGISTRY.get(kind)
        if item is None:
            return "(select a record)"
        if isinstance(value, dict):
            if item not in value:
                return "(select a record)"
            obj = value[item]
        else:
            obj = value
        text = pprint.pformat(obj, width=72, sort_dicts=False)
        return text.replace("{", "{{").replace("[", "[[")

    def debug_apply_seed():
        raw = store.debug_seed_text.strip()
        try:
            seed_value = int(raw)
        except ValueError:
            seed_value = raw or None
        _dice.seed(seed_value)
        store.debug_roll_log = "seeded with %r" % (seed_value,)

    def debug_roll_test():
        rolls = [_dice.d(20) for _i in range(5)]
        store.debug_roll_log = "5d20: " + ", ".join(str(r) for r in rolls)

    def debug_validate_content():
        """Run the content validator (registry.validate + the spell-slice
        matrix vs GDD 9.2 + a hard scan for unresolved authoring placeholder
        tokens in DISPLAY strings) and report to the status line. A flagged
        placeholder is counted as a problem, not advisory."""
        from core import registry as _reg
        problems = _reg.content_problems(store.REG)
        if problems:
            store.debug_roll_log = "%d issue(s): %s" % (
                len(problems), " | ".join(problems[:3]))
        else:
            store.debug_roll_log = "content OK"

    def debug_give_xp(amount):
        """Debug menu from P0 grows with the phases (CLAUDE.md): XP to
        every party member's sheet -- only the protagonist earns XP by
        design (GDD 6 L369-370), so this targets the MC."""
        if store.gs and store.gs["party"]:
            store.gs["party"][0]["xp"] += amount
            store.debug_roll_log = "+%d XP (MC at %d)" % (
                amount, store.gs["party"][0]["xp"])
            renpy.block_rollback()             # committed gs mutation (#16.1)

    def debug_give_gold(amount):
        if store.gs is not None:
            store.gs["gold"] += amount
            store.debug_roll_log = "+%d gold (%d total)" % (
                amount, store.gs["gold"])
            renpy.block_rollback()             # committed gs mutation (#16.1)

    def debug_give_item(item_id):
        if store.gs is not None:
            store.gs["inventory"][item_id] = \
                store.gs["inventory"].get(item_id, 0) + 1
            store.debug_roll_log = "gave 1 %s" % item_id
            renpy.block_rollback()             # committed gs mutation (#16.1)

    DEBUG_GIVEABLE_KINDS = ("weapons", "armor", "consumables",
                            "relics", "magic_items", "key_items")

    # --- P3 (city & free mode) debug controls -----------------------------

    def debug_cycle_day_phase():
        """Cycle morning -> afternoon -> evening (GDD 12.3); the HUD sun
        indicator reads gs['day_phase']."""
        if store.gs is None:
            return
        phases = store.REG["core"]["rest_rules"]["day_phases"]
        cur = store.gs.get("day_phase", phases[0])
        nxt = phases[(phases.index(cur) + 1) % len(phases)] \
            if cur in phases else phases[0]
        store.bstate.set_day_phase(store.gs, nxt)
        store.debug_roll_log = "day phase: %s" % nxt
        renpy.block_rollback()                 # committed gs mutation (#16.1)

    def debug_set_supplies(n):
        if store.gs is not None:
            store.gs["supplies"] = n
            store.debug_roll_log = "supplies = %d" % n
            renpy.block_rollback()             # committed gs mutation (#16.1)

    def debug_set_breathers(n):
        if store.gs is not None:
            store.gs["breathers"] = n
            store.debug_roll_log = "breathers used = %d" % n
            renpy.block_rollback()             # committed gs mutation (#16.1)

    def debug_give_upgrade(uid):
        if store.gs is not None and uid not in store.gs["camp_upgrades"]:
            store.gs["camp_upgrades"].append(uid)
            store.debug_roll_log = "gave camp upgrade %s" % uid
            renpy.block_rollback()             # committed gs mutation (#16.1)

    def debug_prep_camp():
        """Set the Breach region + ensure a Supply so a debug wilds-Camp can
        resolve the Hunt and burn a cache."""
        if store.gs is not None:
            store.bstate.set_breach_region(store.gs, "region_breach_1")
            if store.gs["supplies"] < 1:
                store.gs["supplies"] = 1

    def debug_quest(action, qid="quest_main_hook"):
        """Drive a placeholder quest through its states so the quest tab and
        the mandatory conclusion toast (GDD 15.5) are testable."""
        if store.gs is None:
            return
        try:
            if action == "start":
                store.bquests.start_quest(store.REG, store.gs, qid)
                renpy.block_rollback()
                store.breach_toast("Quest updated")
                store.debug_roll_log = "started %s" % qid
            elif action == "advance":
                store.bquests.advance_objective(store.REG, store.gs, qid)
                renpy.block_rollback()
                store.breach_toast("Quest updated")
                store.debug_roll_log = "advanced %s" % qid
            elif action == "complete":
                store.bquests.conclude_quest(store.REG, store.gs, qid,
                                             "completed")
                renpy.block_rollback()
                store.breach_toast("Quest completed")
                store.debug_roll_log = "completed %s" % qid
            elif action == "fail":
                store.bquests.conclude_quest(store.REG, store.gs, qid,
                                             "failed")
                renpy.block_rollback()
                store.breach_toast("Quest failed")
                store.debug_roll_log = "failed %s" % qid
        except ValueError as e:
            store.debug_roll_log = "quest: %s" % e

    # Debug encounters: jump to combat with any encounter (CLAUDE.md debug
    # menu). Tooling, not authored content.
    DEBUG_ENCOUNTERS = [
        ("Young Wolf (tutorial)", ["young_wolf"], False),
        ("Standard Wolf", ["standard_wolf"], False),
        ("Wolf pack 4v4", ["standard_wolf"] * 4, False),
        ("2 wolves, Flee allowed", ["standard_wolf"] * 2, True),
    ]

    def debug_first_legal(char, choice, opts):
        """First-legal auto-chooser for debug follower creation (mirrors
        the test suite's deterministic chooser)."""
        from core import registry as _reg
        if opts["mode"] == "asi_or_talent":
            for ability in store.bch.ABILITIES:
                if char["abilities"][ability] <= 18:
                    return {"mode": "asi", "scores": {ability: 2}}
            return {"mode": "talent", "talent": "savage_attacker"}
        if opts["mode"] == "magic_initiate":
            cans = [s["id"] for s in
                    _reg.spell_slice(store.REG["spells"], "wizard", 0)
                    if s["id"] not in char["spells"]["cantrips"]][:2]
            spell = [s["id"] for s in
                     _reg.spell_slice(store.REG["spells"], "wizard", 1)][0]
            return {"class": "wizard", "cantrips": cans, "spell": spell}
        enabled = [o["id"] for o in opts["options"] if not o["disabled"]]
        picks = list(opts.get("preselected", []))
        picks += [o for o in enabled if o not in picks]
        if opts.get("shape") == "single":
            return picks[0]
        return picks[:opts["pick"]]

    def debug_add_follower(cls_id):
        """A throwaway debug follower at the protagonist's level (followers
        are always at the MC's level, GDD 6 L369-371)."""
        if store.gs is None or not store.gs["party"] or \
                len(store.gs["party"]) >= 4:
            return
        n = len(store.gs["party"])
        char = store.bch.new_character(
            store.REG, "dbg%d" % n, "Test %s" % cls_id.capitalize(), cls_id,
            {"str": 15, "dex": 14, "con": 13, "int": 12, "wis": 10, "cha": 8})
        queue = list(store.bch.manifest_choices(store.REG, char, 1))
        while queue:
            choice = queue.pop(0)
            opts = store.bui.options_for(store.REG, char, choice)
            if opts["mode"] == "list" and opts["pick"] == 0:
                follow = store.bch.apply_choice(store.REG, char, choice, [])
            else:
                follow = store.bch.apply_choice(
                    store.REG, char, choice,
                    debug_first_legal(char, choice, opts))
            queue = list(follow or []) + queue
        store.bch.finalize_creation(store.REG, char)
        mc = store.gs["party"][0]
        char["xp"] = mc["xp"]
        while store.bch.can_level_up(store.REG, char):
            queue = list(store.bch.level_up(store.REG, char))
            while queue:
                choice = queue.pop(0)
                opts = store.bui.options_for(store.REG, char, choice)
                if opts["mode"] == "list" and opts["pick"] == 0:
                    follow = store.bch.apply_choice(store.REG, char,
                                                    choice, [])
                else:
                    follow = store.bch.apply_choice(
                        store.REG, char, choice,
                        debug_first_legal(char, choice, opts))
                queue = list(follow or []) + queue
            store.bch.finalize_level_up(store.REG, char)
        store.binv.auto_equip_starting_kit(store.REG, char,
                                           store.gs["inventory"])
        store.bstate.add_to_party(store.gs, char)
        store.debug_roll_log = "added %s" % char["name"]
        renpy.block_rollback()                 # committed party mutation (#16.1)


default debug_kind = "classes"
default debug_item = None
default debug_seed_text = "42"
default debug_roll_log = ""


screen debug_hub():
    modal True

    frame:
        xfill True
        yfill True
        padding (20, 20)

        vbox:
            spacing 10

            hbox:
                spacing 20
                text "Debug Hub — P0" size 30
                null width 30
                text "RNG seed:" yalign 0.5
                frame:
                    xminimum 140
                    input value VariableInputValue("debug_seed_text") length 16
                textbutton "Apply seed" action Function(debug_apply_seed) yalign 0.5
                textbutton "Roll 5d20" action Function(debug_roll_test) yalign 0.5
                textbutton "Validate content" action Function(debug_validate_content) yalign 0.5
                text debug_roll_log yalign 0.5

            hbox:
                spacing 10
                $ debug_has_party = (gs is not None and bool(gs["party"]))
                textbutton "Give 300 XP" action Function(debug_give_xp, 300) sensitive debug_has_party
                textbutton "Give 5,000 XP" action Function(debug_give_xp, 5000) sensitive debug_has_party
                textbutton "Give 100 gold" action Function(debug_give_gold, 100) sensitive (gs is not None)
                textbutton "Give 500 gold" action Function(debug_give_gold, 500) sensitive (gs is not None)
                textbutton "Cycle day phase" action Function(debug_cycle_day_phase) sensitive (gs is not None)
                textbutton "Enter city (Free Mode)" action Return(("city",)) sensitive debug_has_party
                textbutton "Exit" action Return()

            hbox:
                spacing 10
                text "Combat:" yalign 0.5
                for enc_name, enc_ids, enc_flee in DEBUG_ENCOUNTERS:
                    textbutton enc_name:
                        action Return(("combat", enc_ids, enc_flee))
                        sensitive debug_has_party
                text "Follower:" yalign 0.5
                for cls_id in ("fighter", "barbarian", "rogue", "cleric"):
                    textbutton cls_id.capitalize():
                        action Function(debug_add_follower, cls_id)
                        sensitive (debug_has_party and len(gs["party"]) < 4)

            ## P3 (city & free mode) controls.
            hbox:
                spacing 10
                text "Supplies:" yalign 0.5
                for _n in (0, 1, 2, 3, 4):
                    textbutton str(_n):
                        action Function(debug_set_supplies, _n)
                        sensitive (gs is not None)
                null width 20
                text "Main quest:" yalign 0.5
                textbutton "Start" action Function(debug_quest, "start") sensitive debug_has_party
                textbutton "Advance" action Function(debug_quest, "advance") sensitive debug_has_party
                textbutton "Complete" action Function(debug_quest, "complete") sensitive debug_has_party
                textbutton "Fail" action Function(debug_quest, "fail") sensitive debug_has_party
                null width 20
                text "HUD mode:" yalign 0.5
                textbutton "City" action SetVariable("hud_mode", "city") selected (hud_mode == "city")
                textbutton "Expedition" action SetVariable("hud_mode", "expedition") selected (hud_mode == "expedition")

            ## P4 (camp & expedition) controls.
            hbox:
                spacing 10
                textbutton "Enter the Breach" action Return(("expedition",)) sensitive debug_has_party
                textbutton "Camp (wilds)" action [Function(debug_prep_camp), Return(("camp",))] sensitive debug_has_party
                textbutton "Inn (10 gold)" action Return(("inn",)) sensitive debug_has_party
                null width 16
                text "Breathers used:" yalign 0.5
                for _b in (0, 1, 2, 3):
                    textbutton str(_b) action Function(debug_set_breathers, _b) sensitive (gs is not None)
                null width 16
                text "Camp upgrade:" yalign 0.5
                for _u, _ul in (("provisioners_pack_frame", "Pack-Frame"), ("fieldwrights_tent", "Tent"), ("cooks_kit", "Cook's Kit")):
                    textbutton _ul action Function(debug_give_upgrade, _u) sensitive (gs is not None)

            hbox:
                spacing 10

                frame:
                    xsize 0.16
                    ysize 0.78
                    viewport:
                        scrollbars "vertical"
                        mousewheel True
                        vbox:
                            for kind in debug_kinds():
                                textbutton kind:
                                    action [SetVariable("debug_kind", kind),
                                            SetVariable("debug_item", None)]
                                    selected (debug_kind == kind)
                                    xfill True
                                    text_size 18

                frame:
                    xsize 0.22
                    ysize 0.78
                    viewport:
                        scrollbars "vertical"
                        mousewheel True
                        vbox:
                            for item in debug_kind_items(debug_kind):
                                textbutton "[item]":
                                    action SetVariable("debug_item", item)
                                    selected (debug_item == item)
                                    xfill True
                                    text_size 18

                frame:
                    xfill True
                    ysize 0.78
                    vbox:
                        spacing 8
                        if debug_kind in DEBUG_GIVEABLE_KINDS and debug_item \
                                and gs is not None:
                            textbutton "Give 1 [debug_item] to the party":
                                action Function(debug_give_item, debug_item)
                        viewport:
                            scrollbars "vertical"
                            mousewheel True
                            text debug_detail(debug_kind, debug_item) size 16
