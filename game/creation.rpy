# Character creation flow (GDD #3, #15.9). Order (owner adjudication, P1
# review, D4): Name -> Race display -> Class -> Point Buy -> level-1 choice
# steps (choice_steps.rpy) -> derived summary. Everything stays in working
# variables until the final Begin -- commit is atomic (#15.2), then
# rollback is blocked (#16.1). No say/textbox renders during creation (D13):
# every step is a modal full-screen screen, never a `say`.

init python:

    # ----- plain-language helpers for the newbie-friendly cards (D9) -----

    BREACH_ABILITY_NAMES = {
        "str": "Strength", "dex": "Dexterity", "con": "Constitution",
        "int": "Intelligence", "wis": "Wisdom", "cha": "Charisma",
    }

    def creation_ability_name(aid):
        return BREACH_ABILITY_NAMES.get(aid, aid.upper())

    def creation_primary_text(cls):
        return " or ".join(creation_ability_name(a) for a in cls["primary"])

    def creation_durability(hit_die):
        """A plain durability word derived from the hit die (D9)."""
        return {6: "Low", 8: "Medium", 10: "High", 12: "Very High"}.get(
            hit_die, "Medium")

    def creation_weapons_text(cls):
        w = cls["weapons"]
        if w["base"] == "all":
            base = "all weapons"
        else:
            base = "simple weapons"
        plus = w.get("plus_martial_with_any")
        if plus:
            base += (", plus martial weapons that are "
                     + " or ".join(p.capitalize() for p in plus))
        return base

    def creation_armor_text(cls):
        armor = cls["armor"]
        cats = [c for c in ("light", "medium", "heavy") if c in armor]
        shields = "shields" in armor
        if cats == ["light", "medium", "heavy"]:
            text = "all armor"
        elif cats:
            text = " and ".join(cats) + " armor"
        else:
            text = ""
        if shields:
            text = (text + " and shields") if text else "shields"
        return text or "no armor"

    def creation_caster_text(cls):
        caster = cls["caster"]
        if not caster:
            return ""
        kinds = {"full": "Full spellcaster", "half": "Half spellcaster",
                 "pact": "Pact spellcaster"}
        return "%s (%s)" % (kinds.get(caster["kind"], caster["kind"]),
                            creation_ability_name(caster["ability"]))

    def creation_class_desc(cls_id):
        return REG["class_ui"][cls_id]["desc"]

    def creation_item_record(item_id):
        """Registry record for an item id (weapons, armor incl. shield,
        consumables) -- for item_card display only."""
        for table in ("weapons", "armor", "consumables"):
            if item_id in REG[table]:
                return REG[table][item_id]
        return None

    # The five wizard steps, in order, for the header breadcrumb. Purely
    # presentational: each screen passes its OWN step key literally, so the
    # driver's step state machine and the return contracts are untouched.
    CREATION_STEPS = [
        ("name", "Name"),
        ("race", "Race"),
        ("class", "Class"),
        ("attributes", "Attributes"),
        ("review", "Review"),
    ]


## The shared wizard header: title (serif amber) on the left, the five-step
## breadcrumb on the right (current step lit accent, the rest muted), a lamplit
## rule beneath. This is the reference's "top HUD: title/breadcrumb left,
## resources right" applied to the creation flow. `current` is the step key.
screen creation_header(title, current):
    vbox:
        spacing gui.pad_s
        xfill True
        frame:
            style "breach_band"
            xfill True
            padding (gui.pad_m, gui.pad_s)
            hbox:
                xfill True
                yalign 0.5
                use breach_title(title)
                null:
                    xfill True
                hbox:
                    spacing gui.pad_s
                    yalign 0.5
                    for cs_i, (cs_key, cs_label) in enumerate(CREATION_STEPS):
                        if cs_i > 0:
                            text "›":
                                size gui.size_micro
                                color gui.panel_border_color
                                yalign 0.5
                        text cs_label.upper():
                            style "breach_label_text"
                            yalign 0.5
                            color (gui.breach_accent_color if cs_key == current else gui.muted_text_color)
        use breach_lip(gui.breach_accent_color)


## The shared wizard footer: a lamplit rule, then the right-aligned action row.
## `back_action` is optional (step 1 has no Back); `primary_label` /
## `primary_action` are the Continue / Begin button; `primary_sensitive` gates
## it. One component so the bottom bar reads identically on every step.
screen creation_footer(primary_label, primary_action, primary_sensitive=True, back_action=None, note=None):
    vbox:
        spacing gui.pad_s
        xfill True
        use breach_lip(gui.panel_border_color)
        hbox:
            spacing gui.pad_m
            xfill True
            yalign 0.5
            if note:
                text breach_lit(note):
                    size gui.size_micro
                    color gui.muted_text_color
                    yalign 0.5
            null:
                xfill True
            if back_action is not None:
                textbutton "Back":
                    style "breach_frame_button"
                    action back_action
            textbutton primary_label:
                style "breach_frame_button"
                sensitive primary_sensitive
                action primary_action


## Step 1 -- Name (D4: naming is the first creation step). A dedicated
## screen with a styled input field -- never renpy.input, so no say window
## appears over the creation flow (D13).

screen creation_name_step(initial=""):
    modal True
    add Solid(gui.bg_color)

    default cc_name_text = initial

    ## Full-bleed wizard layout (header band / content / footer), BOUNDED to the
    ## screen so the breadcrumb and content can never overflow. Identical shape
    ## on every step: header on top, content fills the middle, footer pinned
    ## bottom. (Replaces the centred fit_first panel, which sized to its content
    ## and ran off-screen.)
    frame:
        background None
        xfill True
        yfill True
        padding (gui.screen_pad, gui.screen_pad)
        ## side "t c b": header pinned top, footer pinned BOTTOM, content fills
        ## the middle -- so the Continue button is always on-screen (a yfill
        ## child in a plain vbox eats the footer's space and pushes it off).
        side "t c b":
            spacing gui.pad_l

            use creation_header("Character Creation", "name")

            ## the step question, then a centred, lit gold-framed input card
            ## (the question moved off the top bar, per the owner's direction).
            fixed:
                xfill True
                yfill True
                vbox:
                    align (0.5, 0.5)
                    spacing gui.pad_l
                    text "What is your Name?" style "breach_header_text" xalign 0.5
                    frame:
                        background gui.panel_frame_fill_lit
                        foreground gui.panel_frame
                        xsize gui.modal_w
                        xalign 0.5
                        padding (gui.panel_frame_pad, gui.panel_frame_pad)
                        frame:
                            style "breach_well"
                            xfill True
                            padding (gui.pad_l, gui.pad_m)
                            input:
                                value ScreenVariableInputValue("cc_name_text")
                                length 24
                                color gui.breach_text_color
                                size gui.size_heading
                                xalign 0.5

            use creation_footer("Continue", Return(cc_name_text.strip()), primary_sensitive=(cc_name_text.strip() != ""))


## Step 2 -- Race display (GDD #3: display only, "the lock reads as
## identity"). No Cancel button (D6) -- nothing to cancel on the identity
## step; Back returns to naming.

screen creation_race_step():
    modal True
    add Solid(gui.bg_color)

    frame:
        background None
        xfill True
        yfill True
        padding (gui.screen_pad, gui.screen_pad)
        side "t c b":
            spacing gui.pad_l

            use creation_header("Character Creation", "race")

            fixed:
                xfill True
                yfill True
                vbox:
                    align (0.5, 0.5)
                    xsize gui.modal_w_l
                    spacing gui.pad_m

                    text breach_lit(REG["core"]["human"]["name"]) style "breach_header_text" xalign 0.5

                    text "You are a Human. As a Human, you gain the following traits:":
                        size gui.size_base
                        color gui.breach_text_color
                        xalign 0.5

                    frame:
                        style "breach_well"
                        xfill True
                        vbox:
                            spacing gui.pad_s
                            xfill True
                            for trait in REG["core"]["human"]["traits"].values():
                                use breach_list_row(
                                    trait["name"],
                                    subtitle=breach_player_text(REG, "human", trait["id"], trait["effect"]),
                                    icon_key=trait["id"],
                                    title_color=gui.breach_accent_color)

            use creation_footer("Continue", Return(("ok",)), back_action=Return(("back",)))


## Step 3 -- Class choice (D5, D10): a selectable GRID of class cards;
## clicking highlights, Continue advances (no auto-advance). Cards are
## written for someone new to the genre (D9).

screen creation_class_step(initial=None):
    modal True
    add Solid(gui.bg_color)

    default cc_pick = initial

    frame:
        background None
        xfill True
        yfill True
        padding (gui.screen_pad, gui.screen_pad)
        side "t c b":
            spacing gui.pad_l

            use creation_header("Character Creation", "class")

            ## Two BOUNDED regions: the choice LIST on the left (recessed well,
            ## FIXED width so the detail always fits -- an xfill list pushed the
            ## detail off-screen), the SELECTED detail on the right.
            hbox:
                spacing gui.pane_gap
                xfill True
                yfill True

                frame:
                    style "breach_well"
                    xsize gui.list_pane_w
                    yfill True
                    vbox:
                        spacing gui.pad_s
                        xfill True
                        yfill True
                        ## the step question, above its list (per the owner).
                        use section_header("Choose a Class")
                        viewport:
                            scrollbars "vertical"
                            mousewheel True
                            yfill True
                            vbox:
                                spacing gui.pad_s
                                xfill True
                                for cls_id, cls in REG["classes"].items():
                                    $ cc_lit = (cc_pick == cls_id)
                                    use breach_list_row(
                                        cls["name"],
                                        subtitle=creation_class_desc(cls_id),
                                        meta="Durability " + creation_durability(cls["hit_die"]),
                                        icon_key=cls_id,
                                        selected=cc_lit,
                                        action=SetScreenVariable("cc_pick", cls_id),
                                        title_color=(gui.breach_accent_color if cc_lit else None))

                ## The SELECTED detail -- a lit gold-framed panel of fixed width
                ## (lit fill + the shared gold frame as foreground), so it bounds
                ## cleanly without fit_first. Long values stack label-over-value
                ## so they WRAP inside the column instead of overflowing.
                frame:
                    background gui.panel_frame_fill_lit
                    foreground gui.panel_frame
                    xsize gui.detail_pane_w
                    yfill True
                    padding (gui.panel_frame_pad, gui.panel_frame_pad)
                    if cc_pick is None:
                        use breach_empty_state("Select a class to see details")
                    else:
                        $ cc_sel = REG["classes"][cc_pick]
                        viewport:
                            scrollbars "vertical"
                            mousewheel True
                            yfill True
                            vbox:
                                spacing gui.pad_m
                                xfill True

                                use section_header(cc_sel["name"])

                                text breach_lit(creation_class_desc(cc_pick)):
                                    size gui.size_base
                                    color gui.breach_text_color

                                ## Role / identity at a glance, as wrapping chips.
                                hbox:
                                    spacing gui.pad_s
                                    box_wrap True
                                    use breach_tag(creation_durability(cc_sel["hit_die"]) + " durability", gui.muted_text_color)
                                    if cc_sel["caster"]:
                                        use breach_tag("Spellcaster")

                                use breach_lip(gui.panel_border_color)

                                python:
                                    cc_detail = [
                                        ("Primary Attribute", creation_primary_text(cc_sel), gui.breach_accent_color),
                                        ("Weapons", creation_weapons_text(cc_sel), None),
                                        ("Armor", creation_armor_text(cc_sel), None),
                                    ]
                                    if cc_sel["caster"]:
                                        cc_detail.append(("Spellcasting", creation_caster_text(cc_sel), gui.breach_accent_color))
                                for cc_dl, cc_dv, cc_dc in cc_detail:
                                    vbox:
                                        spacing gui.pad_xs
                                        xfill True
                                        text cc_dl.upper() style "breach_label_text"
                                        text breach_lit(cc_dv):
                                            size gui.size_small
                                            color (cc_dc or gui.breach_text_color)

            use creation_footer("Continue", Return(("ok", cc_pick)), primary_sensitive=(cc_pick is not None), back_action=Return(("back",)))


## Step 4 -- Point Buy (GDD #3 step 3; overhaul D11): clear header, full
## attribute names, one aligned grid (name / value / -/+ / modifier / cost
## all in shared columns), +/- read as interactive. Continue validity is
## recomputed every show from current scores (D14).

screen creation_point_buy(initial=None):
    modal True
    add Solid(gui.bg_color)

    default scores = dict(initial) if initial else {a: 8 for a in bch.ABILITIES}
    $ pb = REG["core"]["point_buy"]
    $ remaining = pb["points"] - sum(pb["costs"][v] for v in scores.values())

    frame:
        background None
        xfill True
        yfill True
        padding (gui.screen_pad, gui.screen_pad)
        side "t c b":
            spacing gui.pad_l

            use creation_header("Character Creation", "attributes")

            ## centred, bounded content so the allocator's fixed columns align.
            fixed:
                xfill True
                yfill True
                vbox:
                    align (0.5, 0.5)
                    xsize gui.modal_w_l
                    spacing gui.pad_l

                    text "Choose Your Attributes" style "breach_header_text" xalign 0.5

                    ## The live points figure -- the most-watched number on the
                    ## step -- in a recessed instrument cell.
                    frame:
                        style "breach_well"
                        xfill True
                        padding (gui.pad_m, gui.pad_s)
                        use breach_stat_cell("Points remaining", "%d / %d" % (remaining, pb["points"]), gui.breach_accent_color)

                    # The shared attribute_allocator component (game/style.rpy)
                    # renders the fixed-width aligned grid; this screen only
                    # builds the rows. Creation point-buy and the level-up ASI
                    # step use the SAME component so they cannot drift.
                    python:
                        cc_rows = []
                        for cc_a in bch.ABILITIES:
                            cc_v = scores[cc_a]
                            cc_up = (pb["costs"][cc_v + 1] - pb["costs"][cc_v]) if cc_v < pb["max"] else None
                            cc_rows.append({
                                "name": creation_ability_name(cc_a),
                                "value": cc_v,
                                "modifier": (cc_v - 10) // 2,
                                "can_dec": cc_v > pb["min"],
                                "dec_action": SetDict(scores, cc_a, cc_v - 1),
                                "can_inc": cc_up is not None and cc_up <= remaining,
                                "inc_action": SetDict(scores, cc_a, cc_v + 1),
                                "last": (("%d point%s" % (cc_up, "" if cc_up == 1 else "s"))
                                         if cc_up is not None else "max"),
                            })
                    use attribute_allocator(cc_rows)

            # P1: gate on full spend. point_buy_ok validates legality (its "<="
            # is correct); the screen also requires every point spent.
            use creation_footer(
                "Continue",
                Return(("ok", dict(scores))),
                primary_sensitive=(bch.point_buy_ok(REG, scores) and remaining == 0),
                back_action=Return(("back",)),
                note=("Unspent points are lost." if remaining > 0 else None))


## Step 6 -- Derived summary (GDD #3 step 4). All numbers recomputed from
## the registry; nothing here is stored. Shows ONLY equipped items (D8).
## Begin commits; Back steps to the choices and does NOT wipe the
## character (D8).

screen creation_summary(char, log):
    modal True
    add Solid(gui.bg_color)

    $ cc_ac = bch.ac(REG, char)
    $ cc_init = bch.initiative_mod(char)
    $ cc_prof = bch.proficiency(char)
    $ cc_cls = REG["classes"][char["class"]]

    frame:
        background None
        xfill True
        yfill True
        padding (gui.screen_pad, gui.screen_pad)

        frame:
            background None
            xfill True
            yfill True
            padding (0, 0)
            side "t c b":
                spacing gui.pad_m

                ## Header band: the finished character is the chrome -- portrait
                ## and identity raised on the left, the derived snapshot elevated
                ## on the right (the reference's "resources right" balance), a
                ## lamplit lip beneath (DESIGN.md: the charsheet header pattern).
                frame:
                    style "breach_band"
                    xfill True
                    padding (gui.pad_m, gui.pad_m)
                    hbox:
                        spacing gui.pad_m
                        xfill True
                        yalign 0.5
                        use portrait_chip(char, size=96)
                        vbox:
                            spacing gui.pad_xs
                            yalign 0.5
                            text breach_lit(char["name"]) size gui.size_heading color gui.breach_text_color
                            text breach_lit(cc_cls["name"]) + " — Level 1" size gui.size_small color gui.muted_text_color
                        null:
                            xfill True
                        hbox:
                            spacing gui.pad_l
                            yalign 0.5
                            vbox:
                                spacing gui.pad_xs
                                yalign 0.5
                                text "HEALTH" style "breach_label_text"
                                use hp_bar(char["hp"], char["hp_max"])
                            use breach_stat_cell("Armor", cc_ac)
                            use breach_stat_cell("Initiative", "%+d" % cc_init)
                            use breach_stat_cell("Proficiency", "%+d" % cc_prof)

                ## The derived sheet is a list of readouts -- it sinks into the
                ## recessed ground (DESIGN.md: lists on breach_well). Each
                ## key/value reads as a structured stat row (breach_stat_line)
                ## with a fixed label column, so values align down each list.
                frame:
                    style "breach_well"
                    xfill True
                    yfill True
                    hbox:
                        spacing gui.pad_l
                        yfill True

                        viewport:
                            xsize gui.summary_col_w
                            yfill True
                            scrollbars "vertical"
                            mousewheel True
                            vbox:
                                spacing gui.pad_s
                                xfill True

                                use section_header("Attributes")
                                for a in bch.ABILITIES:
                                    use breach_stat_line(creation_ability_name(a), "%d  (%+d)" % (char["abilities"][a], bch.ability_mod(char, a)))

                                use section_header("Derived")
                                hbox:
                                    spacing gui.pad_m
                                    text "Health" size gui.size_small color gui.muted_text_color yalign 0.5
                                    use hp_bar(char["hp"], char["hp_max"])
                                use breach_stat_line("Armor", cc_ac)
                                use breach_stat_line("Initiative", "%+d" % cc_init)
                                use breach_stat_line("Proficiency", "%+d" % cc_prof)

                                use section_header("Saving throws")
                                for a in bch.ABILITIES:
                                    $ cc_save_prof = a in char["save_proficiencies"]
                                    use breach_stat_line(
                                        creation_ability_name(a),
                                        "%+d" % bch.save_mod(char, a),
                                        (gui.breach_accent_color if cc_save_prof else gui.muted_text_color))

                        viewport:
                            xsize gui.summary_col_w
                            yfill True
                            scrollbars "vertical"
                            mousewheel True
                            vbox:
                                spacing gui.pad_s
                                xfill True

                                use section_header("Skills")
                                for sid, srec in REG["skills"].items():
                                    $ cc_skill_prof = sid in char["skills"]["proficiencies"]
                                    # Proficient skill names tint with the accent (GDD 15.7).
                                    use breach_stat_line(
                                        srec["name"],
                                        "%+d" % bch.skill_mod(REG, char, sid),
                                        (gui.breach_accent_color if cc_skill_prof else gui.muted_text_color))

                                use section_header("Level 1 choices")
                                for cc_title, cc_summary in log:
                                    use breach_list_row(cc_summary, subtitle=cc_title)

                        viewport:
                            xsize gui.summary_col_w_wide
                            yfill True
                            scrollbars "vertical"
                            mousewheel True
                            vbox:
                                spacing gui.pad_s
                                xfill True

                                use section_header("Equipped")
                                for cc_slot, cc_item in char["equipment"].items():
                                    if cc_item:
                                        use item_card(cc_item, creation_item_record(cc_item), info=cc_slot.capitalize())

                use creation_footer("Begin", Return("begin"), back_action=Return("back"))


## The flow. State lives in cc_* working variables; gs is untouched until
## the final Begin (atomic commit + block rollback, #16.1). The textbox is
## hidden and the quick menu suppressed for the whole flow (D13).

label character_creation:

    window hide
    $ quick_menu = False

    python:
        cc_step = "name"
        cc_name = ""
        cc_class_id = None
        cc_scores = None
        cc_working = None
        cc_kit = None
        cc_log = None
        cc_done = False

    while not cc_done:

        if cc_step == "name":
            $ cc_r = renpy.call_screen("creation_name_step", initial=cc_name)
            if isinstance(cc_r, str) and cc_r:
                $ cc_name = cc_r
                $ cc_step = "race"
            else:
                # no Back on step 1; a stray return just re-shows
                $ cc_step = "name"

        elif cc_step == "race":
            $ cc_r = renpy.call_screen("creation_race_step")
            if cc_r == ("ok",):
                $ cc_step = "class"
            else:
                $ cc_step = "name"

        elif cc_step == "class":
            $ cc_r = renpy.call_screen("creation_class_step", initial=cc_class_id)
            if isinstance(cc_r, (tuple, list)) and len(cc_r) == 2 and cc_r[0] == "ok":
                $ cc_class_id = cc_r[1]
                $ cc_step = "pointbuy"
            else:
                $ cc_step = "race"

        elif cc_step == "pointbuy":
            $ cc_r = renpy.call_screen("creation_point_buy", initial=cc_scores)
            if isinstance(cc_r, (tuple, list)) and len(cc_r) == 2 and cc_r[0] == "ok":
                $ cc_scores = cc_r[1]
                $ cc_step = "choices"
            else:
                $ cc_step = "class"

        elif cc_step == "choices":
            # Build the working character and run the level-1 choice steps
            # (GDD #3 step 4; stepper in choice_steps.rpy). The fresh dict
            # IS the working copy -- nothing is in gs yet.
            python:
                cc_working = bch.new_character(REG, "mc", cc_name, cc_class_id, cc_scores)
                cc_choice_result = breach_run_choices(cc_working, bch.manifest_choices(REG, cc_working, 1))
            if cc_choice_result["status"] != "done":
                # Back out of the first choice -> previous step (point buy).
                $ cc_step = "pointbuy"
            else:
                python:
                    cc_log = cc_choice_result["log"]
                    bch.finalize_creation(REG, cc_working)
                    cc_kit = {}
                    binv.auto_equip_starting_kit(REG, cc_working, cc_kit)
                $ cc_step = "summary"

        elif cc_step == "summary":
            $ cc_r = renpy.call_screen("creation_summary", char=cc_working, log=cc_log)
            if cc_r == "begin":
                # The atomic commit: kit into the shared inventory, the
                # character into the party, then block rollback (#16.1).
                python:
                    for cc_item_id, cc_item_count in cc_kit.items():
                        bstate.add_item(gs, cc_item_id, cc_item_count)
                    bstate.add_to_party(gs, cc_working)
                    renpy.block_rollback()
                $ cc_done = True
            else:
                # Back: re-run the level-1 choices (does NOT wipe; nothing
                # was ever written to gs).
                $ cc_step = "choices"

    $ quick_menu = True
    return
