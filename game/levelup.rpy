# The level-up wizard (GDD 15.2): a data-driven flow over the class
# LEVELUP manifest. Entry: `call levelup_wizard(char_id)` from the badge
# or the character sheet. Flow per level: "what you gain" -> one stepper
# step per pending choice (choice_steps.rpy) -> confirmation summary.
# Everything happens on a deep copy; gs is replaced atomically on the
# final Confirm only, and Cancel anywhere discards the copy -- peeking
# is free, the badge stays (15.2). Multi-level gains run the wizard
# repeatedly, one committed level at a time. All rules text comes from
# the registry; nothing is duplicated here (15.2 L1491-1492).

init python:

    def breach_levelup_facts(char, working):
        """Display facts for the two wizard screens, derived on read
        (16.4 -- nothing stored): the fixed HP gain for the new level
        (hit die average, GDD 2.6), the new level's feature records,
        and proficiency before/after."""
        cls = REG["classes"][working["class"]]
        return {
            "hp_gain": bch.hp_gain_for_level(REG, working),
            "features": [REG["features"][fid]
                         for fid in cls["levelup"][working["level"]]["features"]],
            "prof_old": bch.proficiency(char),
            "prof_new": bch.proficiency(working),
        }


label levelup_wizard(char_id):

    while bch.can_level_up(REG, bstate.party_member(gs, char_id)):

        # 1. Work on a deep copy; gs stays untouched until the final
        #    Confirm (15.2: choices commit atomically).
        python:
            import copy
            lw_char = bstate.party_member(gs, char_id)
            lw_working = copy.deepcopy(lw_char)
            lw_pending = bch.level_up(REG, lw_working)

        # 2. "What you gain". Cancel -> discard, end the wizard.
        $ lw_go = renpy.call_screen("levelup_gains", char=lw_char,
                                    working=lw_working, pending=lw_pending)
        if not lw_go:
            return

        # 3. One stepper step per pending choice; mutates the working
        #    copy. Back out of the first choice -> discard, end the wizard
        #    (the level-up badge stays; 15.2).
        $ lw_result = breach_run_choices(lw_working, lw_pending)
        if lw_result["status"] != "done":
            return
        $ lw_log = lw_result["log"]

        # 4. Recompute HP max and add ONLY the capacity this level grants --
        #    spent resources stay spent; a level-up is not a rest (GDD #6 /
        #    #12.1). lw_char is the un-levelled snapshot, so its resource row
        #    is the pre-level-up baseline.
        $ lw_old_row = bch.resource_row(REG, lw_char)
        $ bch.finalize_level_up(REG, lw_working, old_resource_row=lw_old_row)

        # 5. Confirmation summary. Cancel -> discard, end the wizard.
        $ lw_ok = renpy.call_screen("levelup_confirm", char=lw_char,
                                    working=lw_working, log=lw_log)
        if not lw_ok:
            return

        # Atomic commit: replace the member, then block rollback (16.1).
        python:
            for lw_i, lw_member in enumerate(gs["party"]):
                if lw_member["id"] == char_id:
                    gs["party"][lw_i] = lw_working
                    break
            renpy.block_rollback()

        # 6. Loop: multi-level gains run the wizard repeatedly (15.2),
        #    each level committed separately.

    return


## The "what you gain" screen (15.2): fixed HP, new features,
## proficiency change, and how many choices are pending.

screen levelup_gains(char, working, pending):
    modal True
    add Solid(gui.bg_color)

    $ lw_facts = breach_levelup_facts(char, working)
    $ lw_name = breach_lit(working["name"])

    frame:
        background None
        align (0.5, 0.5)
        xsize gui.modal_w_l

        ## The active step is the ONE lit focal panel (DESIGN: focal = lit),
        ## matching the creation wizard. The nested blocks below stay quiet so
        ## there is exactly one lit surface per region.
        use breach_panel_lit():
            vbox:
                spacing gui.pad_m
                xfill True

                ## Top bar: title/breadcrumb left, the level context right.
                hbox:
                    xfill True
                    yalign 0.5
                    use breach_title("Level-Up Gains")
                    null:
                        xfill True
                    use breach_stat_cell("Level", working["level"], gui.breach_accent_color)
                text "[lw_name] reaches level [working['level']]." size gui.size_base color gui.breach_text_color

                ## The fixed gains read as a column-aligned ledger: each row is
                ## the shared label|value line (gain green, proficiency amber) so
                ## the eye lands on the numbers and the columns never drift.
                vbox:
                    spacing gui.pad_s
                    xfill True
                    use breach_stat_line("HP gain", "+%d HP" % lw_facts["hp_gain"], gui.success_color)
                    if lw_facts["prof_old"] != lw_facts["prof_new"]:
                        use breach_stat_line("Proficiency", "+%d -> +%d" % (lw_facts["prof_old"], lw_facts["prof_new"]), gui.breach_accent_color)

                ## New features + pending choices scroll within a bounded body so
                ## the action row below is ALWAYS on-screen -- the modal can never
                ## grow past the screen (matches the choice-stepper's fixed body).
                viewport:
                    scrollbars "vertical"
                    mousewheel True
                    ymaximum gui.modal_body_h_l
                    xfill True
                    vbox:
                        spacing gui.pad_l
                        xfill True

                        ## The new features are a scannable framed list sunk into
                        ## the recessed ground: one list row each, or a structured
                        ## empty state when the level grants none.
                        text "New Features" style "breach_label_text"
                        frame:
                            style "breach_well"
                            xfill True
                            if lw_facts["features"]:
                                vbox:
                                    spacing gui.pad_s
                                    xfill True
                                    for lw_feat in lw_facts["features"]:
                                        use breach_list_row(lw_feat["name"], subtitle=breach_player_text(REG, "features", lw_feat["id"], lw_feat.get("effect") or ""), icon_key="feature", title_color=gui.breach_accent_color)
                            else:
                                use breach_empty_state("None at this level.", sub="Your gains this level are HP and progress.")

                        ## Pending choices previewed as a numbered mini-list so the
                        ## player sees count-as-list before the stepper; a
                        ## structured empty state when there are none.
                        text "Choices Ahead" style "breach_label_text"
                        frame:
                            style "breach_well"
                            xfill True
                            if pending:
                                vbox:
                                    spacing gui.pad_s
                                    xfill True
                                    for lw_idx, lw_choice in enumerate(pending):
                                        use breach_list_row(bui.choice_title(lw_choice), meta="%d" % (lw_idx + 1), title_color=gui.breach_accent_color)
                            else:
                                use breach_empty_state("No choices at this level.", sub="Nothing to pick here.")

                ## A lamplit ledge anchors the action row; Continue is the
                ## primary forward action (the bevelled frame), Cancel stays
                ## quiet (DESIGN: one obvious next).
                use breach_lip(gui.breach_accent_dim_color)
                hbox:
                    spacing gui.pad_m
                    xalign 1.0
                    textbutton "Cancel":
                        style "breach_button"
                        action Return(False)
                    textbutton "Continue":
                        style "breach_frame_button"
                        action Return(True)


## The confirmation summary (15.2): old -> new level, HP max,
## proficiency change if any, the choice log, new feature names.
## Confirm commits; Cancel discards everything.

screen levelup_confirm(char, working, log):
    modal True
    add Solid(gui.bg_color)

    $ lw_facts = breach_levelup_facts(char, working)

    frame:
        background None
        align (0.5, 0.5)
        xsize gui.modal_w_l

        ## The commit step is the ONE lit focal panel (matching the gains
        ## screen and the creation wizard); nested blocks stay quiet.
        use breach_panel_lit():
            vbox:
                spacing gui.pad_m
                xfill True

                ## Top bar: title left, the committed level right.
                hbox:
                    xfill True
                    yalign 0.5
                    use breach_title("Confirm Level Up")
                    null:
                        xfill True
                    use breach_stat_cell("Level", working["level"], gui.breach_accent_color)

                ## The whole summary scrolls within a bounded body so Confirm
                ## below is ALWAYS on-screen -- the modal never grows past the
                ## screen (matches the gains screen and the choice stepper).
                viewport:
                    scrollbars "vertical"
                    mousewheel True
                    ymaximum gui.modal_body_h_l
                    xfill True
                    vbox:
                        spacing gui.pad_l
                        xfill True

                        ## Before -> after ledger: the OLD value sinks muted, the
                        ## arrow is a quiet glyph, the NEW value carries the
                        ## semantic color and weight (level plain, HP green, prof amber).
                        vbox:
                            spacing gui.pad_s
                            xfill True
                            use breach_stat_line("Level", "%d -> %d" % (char["level"], working["level"]), gui.breach_text_color)
                            use breach_stat_line("HP maximum", "%d -> %d" % (char["hp_max"], working["hp_max"]), gui.success_color)
                            if lw_facts["prof_old"] != lw_facts["prof_new"]:
                                use breach_stat_line("Proficiency", "+%d -> +%d" % (lw_facts["prof_old"], lw_facts["prof_new"]), gui.breach_accent_color)

                        ## The new features being committed -- the same scannable
                        ## rows as the gains preview, effect subline included so the
                        ## commit screen is not less informative than the preview.
                        text "New features" style "breach_label_text"
                        frame:
                            style "breach_well"
                            xfill True
                            if lw_facts["features"]:
                                vbox:
                                    spacing gui.pad_s
                                    xfill True
                                    for lw_feat in lw_facts["features"]:
                                        use breach_list_row(lw_feat["name"], subtitle=breach_player_text(REG, "features", lw_feat["id"], lw_feat.get("effect") or ""), icon_key="feature", title_color=gui.breach_accent_color)
                            else:
                                use breach_empty_state("None at this level.")

                        ## The choice log is committed history -- framed list rows
                        ## (category as title, the picked content on the readable
                        ## full-width subtitle line).
                        if log:
                            text "Choices" style "breach_label_text"
                            frame:
                                style "breach_well"
                                xfill True
                                vbox:
                                    spacing gui.pad_s
                                    xfill True
                                    for lw_title, lw_summary in log:
                                        use breach_list_row(lw_title, subtitle=lw_summary)

                ## A lamplit ledge anchors the action row; Confirm is the primary
                ## forward action (bevelled frame), Cancel stays quiet.
                use breach_lip(gui.breach_accent_dim_color)
                hbox:
                    spacing gui.pad_m
                    xalign 1.0
                    textbutton "Cancel":
                        style "breach_button"
                        action Return(False)
                    textbutton "Confirm":
                        style "breach_frame_button"
                        action Return(True)
