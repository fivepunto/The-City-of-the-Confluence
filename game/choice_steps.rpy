# The generic choice stepper: one step per pending choice, shared by
# character creation (GDD 3 step 4) and the level-up wizard (GDD 15.2).
# All option text comes from the registry via core.ui_options -- rules text
# exists exactly once (15.2).

init python:
    def breach_selection_summary(choice, selection):
        """One line for the confirmation screen."""
        if isinstance(selection, dict):
            if selection.get("mode") == "asi":
                parts = ["%s +%d" % (bui.creation_ability_word(a), n)
                         for a, n in selection["scores"].items()]
                return ", ".join(parts)
            if selection.get("mode") == "talent":
                return REG["talents"][selection["talent"]]["name"]
            if "cantrips" in selection:    # magic initiate
                return "%s: %s + %s" % (
                    selection["class"].capitalize(),
                    ", ".join(REG["spells"][c]["name"]
                              for c in selection["cantrips"]),
                    REG["spells"][selection["spell"]]["name"])
        if isinstance(selection, (list, set, tuple)):
            names = []
            for oid in selection:
                if oid in REG["spells"]:
                    names.append(REG["spells"][oid]["name"])
                elif oid in REG["skills"]:
                    names.append(REG["skills"][oid]["name"])
                elif oid in REG["weapons"]:
                    names.append(REG["weapons"][oid]["name"])
                else:
                    names.append(str(oid).replace("_", " ").title())
            return ", ".join(names) if names else "(none)"
        return str(selection).replace("_", " ").title()

    def breach_present_choice(char, choice, opts):
        """The Ren'Py present callback for core.stepper: show one modal
        step and return its ("ok", selection) / ("back",) result."""
        return renpy.call_screen("choice_step", char=char,
                                 choice=choice, opts=opts)

    def breach_run_choices(char, pending):
        """Run the stepper over a pending-choice list (15.2: choices commit
        atomically; char is the WORKING COPY). Delegates to the pure-Python
        core.stepper (unit-tested); see it for the Back-navigation contract.
        Returns {"status": "done", "log": [...]} or {"status": "back"}."""
        from core import stepper
        return stepper.run_choices(REG, char, pending, breach_present_choice,
                                   summarize=breach_selection_summary)

    def breach_permanence_tag(choice):
        """15.2: permanent picks carry a 'permanent' tag; swappable things
        say so. Fighting styles and weapon masteries are PERMANENT (owner
        adjudication, P1 review, D1/D2)."""
        swap = choice.get("swappable")
        if swap == "camp":
            return "swappable at Camp"
        if swap == "rest":
            return "swappable at each rest"
        if choice["type"] == "prepare_spells":
            return "re-chosen at Camp"     # 7 L386
        if choice["type"] == "invocations":
            return "one may be swapped at each level-up"   # 7.7 L640
        return "permanent"


screen choice_step(char, choice, opts):
    modal True
    # Modal pattern (DESIGN 6): lay the scrim first so the room sinks into the
    # dark, then float the lit panel -- this step is the only lit object.
    add Solid(gui.breach_scrim_color)

    default picks = set(opts.get("preselected", []))
    default asi_view = "asi"
    # live allocated scores for the ASI step -- a screen variable mutated by
    # SetDict so the displayed value re-renders on every +/- (the proven
    # creation point-buy pattern). Starts at the character's current scores.
    default asi_scores = dict(char["abilities"])
    default mi_class = None
    default mi_cantrips = set()
    default mi_spell = None

    frame:
        background None
        align (0.5, 0.5)
        xsize gui.modal_w_l
        ysize gui.modal_h_l

        ## The active step is the ONE lit focal panel in the room (DESIGN.md:
        ## focal = lit) -- the same lamplit surface the creation and level-up
        ## steps float on, so the stepper reads as the same moment.
        use breach_panel_lit():
            vbox:
                spacing gui.pad_m
                xfill True

                ## Top-bar discipline: the step title sits left as the
                ## breadcrumb; the permanence tag rides the right as a read-only
                ## chip (what this pick costs you forever).
                hbox:
                    spacing gui.pad_m
                    xfill True
                    use breach_title(bui.choice_title(choice))
                    null:
                        xfill True
                    # 15.2: every pick states what it costs you forever (or
                    # when it can be swapped) as a read-only chip on the right.
                    use breach_tag(breach_permanence_tag(choice), gui.muted_text_color)
                # D12: clarify the Versatile talent comes from the Human
                # racial trait.
                if choice["type"] == "versatile_talent":
                    text "Human Versatility lets you choose one starter Talent.":
                        size gui.size_small
                        color gui.muted_text_color
                if opts["mode"] == "list":
                    hbox:
                        spacing gui.pad_m
                        if opts.get("allow_fewer"):
                            text "Choose up to [opts['pick']]" size gui.size_micro color gui.muted_text_color yalign 0.5
                        else:
                            text "Choose [opts['pick']]" size gui.size_micro color gui.muted_text_color yalign 0.5
                        text "[len(picks)] selected" size gui.size_micro color gui.breach_accent_color yalign 0.5

                if opts["mode"] == "list":
                    use choice_step_list(opts, picks)

                elif opts["mode"] == "asi_or_talent":
                    use choice_step_asi(char, opts, asi_view, asi_scores, picks)

                elif opts["mode"] == "magic_initiate":
                    use choice_step_magic_initiate(char, mi_class, mi_cantrips, mi_spell)

                # A lamplit ledge separates the action row from the step
                # content (DESIGN 5: the lip catches lamplight).
                use breach_lip(gui.breach_accent_dim_color)
                hbox:
                    spacing gui.pad_m
                    xalign 1.0
                    # Back is a navigation signal, never a selection
                    # (root cause A): the loop maps ("back",) to the
                    # previous choice / creation step.
                    textbutton "Back":
                        style "breach_frame_button"
                        action Return(("back",))
                    if opts["mode"] == "list":
                        $ pick_ok = (len(picks) <= opts["pick"]
                                     if opts.get("allow_fewer")
                                     else len(picks) == opts["pick"])
                        textbutton "Confirm":
                            style "breach_frame_button"
                            sensitive pick_ok
                            action Return(("ok",
                                           [o["id"] for o in opts["options"]
                                            if o["id"] in picks]
                                           if opts.get("shape") != "single"
                                           else (list(picks)[0] if picks else None)))
                    elif opts["mode"] == "asi_or_talent":
                        if asi_view == "asi":
                            # full-spend gate (same rule as creation): all
                            # 2 points must be allocated. The selection is
                            # the per-ability delta from the base scores.
                            $ asi_delta = {a: asi_scores[a] - char["abilities"][a] for a in asi_scores if asi_scores[a] != char["abilities"][a]}
                            textbutton "Confirm":
                                style "breach_frame_button"
                                sensitive (sum(asi_delta.values()) == 2)
                                action Return(("ok", {"mode": "asi",
                                               "scores": dict(asi_delta)}))
                        else:
                            textbutton "Confirm":
                                style "breach_frame_button"
                                sensitive (len(picks) == 1)
                                action Return(("ok", {"mode": "talent",
                                               "talent": (list(picks)[0] if picks else None)}))
                    elif opts["mode"] == "magic_initiate":
                        textbutton "Confirm":
                            style "breach_frame_button"
                            sensitive (mi_class and len(mi_cantrips) == 2 and mi_spell)
                            action Return(("ok", {"class": mi_class,
                                           "cantrips": list(mi_cantrips),
                                           "spell": mi_spell}))


## --- choice_step mode bodies (composed by choice_step via `use`) -----------
## State (picks / asi_scores / mi_*) lives on choice_step; the set/dict picks
## mutate in place by reference (ToggleSetMembership / SetDict) and the
## SetScreenVariable actions resolve against the shown screen.

## List mode: the option picker -- a recessed well of selectable rows; the
## selected row is the lit focal surface, a LOCKED prior permanent pick
## desaturates (DESIGN 2-4).
screen choice_step_list(opts, picks):
    frame:
        style "breach_well"
        xfill True
        if not opts["options"]:
            ## Structured empty state -- a sunk well should never read as a
            ## bare void when a step happens to offer nothing.
            use breach_empty_state("No options available", "Nothing to choose at this step.")
        else:
            viewport:
                scrollbars "vertical"
                mousewheel True
                ysize 636
                xfill True
                vbox:
                    spacing gui.pad_s
                    xfill True
                    for opt in opts["options"]:
                        # multi-select with a cap (root cause C): an unselected
                        # option past the pick limit is disabled until something is
                        # deselected. LOCKED options are permanent prior picks
                        # (e.g. weapon masteries): shown chosen, never deselectable.
                        $ cc_locked = opt["id"] in opts.get("locked", ())
                        $ cc_at_cap = (len(picks) >= opts["pick"]
                                       and opt["id"] not in picks)
                        $ cc_sel = opt["id"] in picks
                        ## The selectable option rides the shared bronze
                        ## list-row frame (frames.rpy): idle frame normally, the
                        ## amber-edge + soft-glow lit frame when selected/hovered
                        ## (DESIGN 3: focal = lit) -- the same row inventory,
                        ## shop and talents use. A LOCKED prior permanent pick
                        ## reads chosen and desaturates -- burning low, never
                        ## clickable.
                        button:
                            style "breach_frame_row"
                            sensitive (not opt["disabled"] and not cc_at_cap and not cc_locked)
                            selected cc_sel
                            action ToggleSetMembership(picks, opt["id"])
                            if cc_locked:
                                vbox at breach_desaturate:
                                    spacing gui.pad_xs
                                    xfill True
                                    hbox:
                                        spacing gui.pad_s
                                        text breach_lit(opt["label"]) size gui.size_base color gui.breach_text_color
                                        use breach_tag("chosen", gui.muted_text_color)
                                    if opt["desc"]:
                                        text breach_lit(opt["desc"]) size gui.size_micro color gui.muted_text_color
                            else:
                                vbox:
                                    spacing gui.pad_xs
                                    xfill True
                                    hbox:
                                        spacing gui.pad_s
                                        text breach_lit(opt["label"]) size gui.size_base color (gui.breach_accent_color if cc_sel else gui.breach_text_color)
                                        if opt["note"]:
                                            text breach_lit(opt["note"]) size gui.size_micro color gui.muted_text_color yalign 0.5
                                    if opt["desc"]:
                                        text breach_lit(opt["desc"]) size gui.size_micro color gui.muted_text_color


## ASI-or-Talent mode: a toggle between spending +2 ability points (the shared
## point-buy allocator) and taking one Talent.
screen choice_step_asi(char, opts, asi_view, asi_scores, picks):
    ## The two ways to spend this step read as framed command tabs (the bronze
    ## frame-button); the active path lights amber.
    hbox:
        spacing gui.pad_s
        textbutton "+2 Ability Points":
            style "breach_frame_button"
            action SetScreenVariable("asi_view", "asi")
            selected (asi_view == "asi")
        textbutton "Choose a Talent":
            style "breach_frame_button"
            action SetScreenVariable("asi_view", "talent")
            selected (asi_view == "talent")
    if asi_view == "asi":
        $ asi_base = char["abilities"]
        $ asi_spent = sum(asi_scores[a] - asi_base[a] for a in asi_scores)
        hbox:
            spacing gui.pad_s
            text "Spend two points: +2 to one ability, or +1 to two abilities. Scores cannot exceed 20." size gui.size_micro color gui.muted_text_color yalign 0.5
            text ("Points remaining: %d" % (2 - asi_spent)) size gui.size_micro color gui.breach_accent_color yalign 0.5
        # The SAME shared allocator component creation uses; the displayed
        # value is the live asi_scores entry (mutated by SetDict), so it
        # refreshes on every +/-.
        python:
            asi_rows = []
            for asi_a in ("str", "dex", "con", "int", "wis", "cha"):
                asi_cur = asi_scores[asi_a]
                asi_b = asi_base[asi_a]
                asi_rows.append({
                    "name": bui.creation_ability_word(asi_a),
                    "value": asi_cur,
                    "modifier": (asi_cur - 10) // 2,
                    "can_dec": asi_cur > asi_b,
                    "dec_action": SetDict(asi_scores, asi_a, asi_cur - 1),
                    "can_inc": (asi_spent < 2 and (asi_cur - asi_b) < 2 and asi_cur < 20),
                    "inc_action": SetDict(asi_scores, asi_a, asi_cur + 1),
                    "last": ("+%d" % (asi_cur - asi_b)) if asi_cur > asi_b else "",
                })
        use attribute_allocator(asi_rows, last_header="Increase")
    else:
        frame:
            style "breach_well"
            xfill True
            if not opts["options"]:
                use breach_empty_state("No talents available", "Nothing to choose here.")
            else:
                viewport:
                    scrollbars "vertical"
                    mousewheel True
                    ysize 536
                    xfill True
                    vbox:
                        spacing gui.pad_s
                        xfill True
                        for opt in opts["options"]:
                            $ tal_sel = opt["id"] in picks
                            ## Focal = lit (DESIGN 3): the chosen talent rises
                            ## onto the amber-edge lit row; the rest sit on the
                            ## idle bronze list-row frame -- the same selectable
                            ## row the option list uses, so the step reads
                            ## consistently.
                            button:
                                style "breach_frame_row"
                                sensitive (not opt["disabled"])
                                selected tal_sel
                                action [SetScreenVariable("picks", set([opt["id"]]))]
                                vbox:
                                    spacing gui.pad_xs
                                    xfill True
                                    hbox:
                                        spacing gui.pad_s
                                        text breach_lit(opt["label"]) size gui.size_base color (gui.breach_accent_color if tal_sel else gui.breach_text_color)
                                        if opt["note"]:
                                            text breach_lit(opt["note"]) size gui.size_micro color gui.muted_text_color yalign 0.5
                                    if opt["desc"]:
                                        text breach_lit(opt["desc"]) size gui.size_micro color gui.muted_text_color


## Magic Initiate mode: choose a class slice, then 2 of its cantrips and one
## tier-1 spell.
screen choice_step_magic_initiate(char, mi_class, mi_cantrips, mi_spell):
    text "Choose one class spell list. Learn two cantrips and one tier 1 spell from it." size gui.size_micro color gui.muted_text_color
    hbox:
        spacing gui.pad_m
        ## The class slice picker -- framed command buttons in a column; the
        ## chosen class lights amber.
        vbox:
            spacing gui.pad_s
            text "Class" style "breach_label_text"
            for cls_id in ("wizard", "sorcerer", "cleric", "druid", "bard", "warlock"):
                textbutton cls_id.capitalize():
                    style "breach_frame_button"
                    selected (mi_class == cls_id)
                    action [SetScreenVariable("mi_class", cls_id),
                            SetScreenVariable("mi_cantrips", set()),
                            SetScreenVariable("mi_spell", None)]
        if mi_class:
            vbox:
                spacing gui.pad_s
                text "Cantrips: Choose 2" style "breach_label_text"
                frame:
                    style "breach_well"
                    xsize gui.panel_w_narrow
                    python:
                        mi_cantrip_opts = [sp for sp in breach_class_spells(mi_class, 0)
                                           if sp["id"] not in char["spells"]["cantrips"]]
                    if not mi_cantrip_opts:
                        use breach_empty_state("No cantrips available", "You already know them all.")
                    else:
                        viewport:
                            scrollbars "vertical"
                            mousewheel True
                            ysize 476
                            xfill True
                            vbox:
                                spacing gui.pad_s
                                xfill True
                                for sp in mi_cantrip_opts:
                                    button:
                                        style "breach_frame_row"
                                        selected (sp["id"] in mi_cantrips)
                                        sensitive (sp["id"] in mi_cantrips or len(mi_cantrips) < 2)
                                        action ToggleSetMembership(mi_cantrips, sp["id"])
                                        text breach_lit(sp["name"]) style "breach_frame_row_text" yalign 0.5
            vbox:
                spacing gui.pad_s
                text "Tier 1 Spell: Choose 1" style "breach_label_text"
                frame:
                    style "breach_well"
                    xsize gui.panel_w_narrow
                    python:
                        mi_spell_opts = breach_class_spells(mi_class, 1)
                    if not mi_spell_opts:
                        use breach_empty_state("No tier 1 spells available")
                    else:
                        viewport:
                            scrollbars "vertical"
                            mousewheel True
                            ysize 476
                            xfill True
                            vbox:
                                spacing gui.pad_s
                                xfill True
                                for sp in mi_spell_opts:
                                    button:
                                        style "breach_frame_row"
                                        selected (mi_spell == sp["id"])
                                        action SetScreenVariable("mi_spell", sp["id"])
                                        text breach_lit(sp["name"]) style "breach_frame_row_text" yalign 0.5


init python:
    def breach_class_spells(cls_id, tier):
        """Slice helper for the magic-initiate step."""
        from core import registry as _reg
        return _reg.spell_slice(REG["spells"], cls_id, tier)
