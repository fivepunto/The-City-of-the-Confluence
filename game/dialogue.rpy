# The skill-tagged dialogue SYSTEM and placeholder dialogue labels
# (GDD 15.7 "Dialogue & skill checks" + 4.2 "Skill checks").
#
# The acting character for every check is the protagonist, gs["party"][0]
# (15.7 L1597). Skill-tagged choices show a coloured skill TAG before the
# line; the tag is the accent (lamplight) colour when the protagonist is
# proficient in that skill, plain otherwise (15.7 L1600). The hidden
# difficulty is NEVER shown before the roll (15.7 L1599) -- the result LINE
# after the roll MAY show the numbers (it is the post-roll outcome, not the
# pre-roll difficulty, 15.7 L1597-1602).
#
# Hard-gated class/feature lines are HIDDEN when unavailable, never greyed
# (15.7 L1604-1606).
#
# All dialogue spoken text is OWNER content; this file ships the literal
# placeholder "[[TO BE WRITTEN BY THE PROJECT OWNER]" for every line and a
# bracketed placeholder for every speaker. The labels only demonstrate the
# system wiring (CLAUDE.md P5: never write story content).
#
# Rollback discipline (GDD 16.1): the .rpy layer calls renpy.block_rollback()
# immediately after every check resolution and quest start -- core never does.
# (breach_do_check and the quest-start branch do this here.)


init python:

    def breach_skill_result_line(res):
        """Format the GDD 15.7 result line from a bchecks.skill_check result
        dict (keys: skill, success, total, dc). e.g. "Presence — Failed
        (9 vs 15)". The numbers are shown because this is the POST-roll
        outcome, not the hidden pre-roll difficulty (15.7 L1597-1602)."""
        skill_name = REG["skills"][res["skill"]]["name"]
        outcome = "Passed" if res["success"] else "Failed"
        return "%s — %s (%d vs %d)" % (
            skill_name, outcome, res["total"], res["dc"])

    def breach_do_check(skill, dc):
        """Resolve one skill check for the protagonist, commit it against
        rollback, and surface the result line as a non-blocking notice.

        The roll happens in core (bchecks.skill_check); we block rollback
        IMMEDIATELY after so the committed result cannot be rerolled by
        in-place rollback (GDD 16.1 L1624). The toast is the player-facing
        result line (15.7). Returns the result dict for branching."""
        actor = gs["party"][0]
        res = bchecks.skill_check(REG, actor, skill, dc)
        renpy.block_rollback()                       # commit the roll (16.1)
        breach_toast(breach_skill_result_line(res))  # non-blocking notice
        return res


## The skill-tagged choice menu (GDD 15.7 L1597-1606).
##
## `options` is a list of dicts: {id, label, skill (a skill id, or None for
## a plain line), dc (int, ignored for plain), hidden (bool)}.
##
## - opt["hidden"] -> the option is SKIPPED entirely (hard-gated class/feature
##   lines are HIDDEN when unavailable, never greyed, 15.7 L1604-1606).
## - A skill option shows a coloured skill TAG ("[SkillName]") before the
##   line: accent (lamplight) when `actor` is proficient, plain otherwise
##   (15.7 L1600). The DC is NEVER shown (15.7 L1599).
## - A plain option (skill None) shows just the label.
##
## Colours come only from gui.* constants (no hardcoded hex). The tag is a
## separate text displayable from the label so each gets its own colour
## without Ren'Py text tags carrying a literal colour.
##
## Returns opt["id"] of the chosen option.

screen skill_menu(actor, options):
    ## The prompt is a modal over the say flow: the scrim sinks the scene and
    ## textbox into the dark (DESIGN.md pattern 6), leaving the lit panel as the
    ## only object that owns the moment -- the textbox identity stays intact,
    ## just quiet behind the choice. (reaction_prompt / reaction_settings do the
    ## same.)
    modal True
    add Solid(gui.breach_scrim_color)
    frame:
        align (0.5, 0.5)
        xsize gui.modal_w_l
        background None
        use breach_panel():
            vbox:
                spacing gui.pad_m
                xfill True
                use section_header("What do you do?")
                ## the lamplit lip beneath the header (the eye anchors here),
                ## then the choices in a recessed well -- value layering, rows
                ## rising on panel over a darker ground.
                use breach_lip(gui.breach_accent_color)
                frame:
                    style "breach_well"
                    xfill True
                    vbox:
                        spacing gui.pad_m
                        xfill True
                        for sm_opt in options:
                            ## Hidden options are SKIPPED entirely, never greyed
                            ## (15.7 L1604-1606) -- the guard renders nothing.
                            if not sm_opt.get("hidden"):
                                $ sm_skill = sm_opt.get("skill")
                                ## A framed list row per choice: idle frame
                                ## normally, the amber-edge + lit fill on
                                ## hover/focus so exactly one row is lit at a
                                ## time. The Return id is the load-bearing
                                ## action; the DC is never shown.
                                button:
                                    style "breach_frame_row"
                                    xfill True
                                    action Return(sm_opt["id"])
                                    hbox:
                                        spacing gui.pad_m
                                        xfill True
                                        yalign 0.5
                                        ## the skill tag as a real leading chip:
                                        ## accent when the acting char is
                                        ## proficient (15.7 L1600), muted plain
                                        ## otherwise. A skill name is data-driven
                                        ## so breach_tag escapes it (breach_lit).
                                        if sm_skill:
                                            $ sm_tag_color = (gui.breach_accent_color
                                                              if sm_skill in actor["skills"]["proficiencies"]
                                                              else gui.muted_text_color)
                                            use breach_tag(REG["skills"][sm_skill]["name"], sm_tag_color)
                                        ## the line itself; breach_lit escapes
                                        ## owner placeholder brackets so they
                                        ## display literally instead of crashing.
                                        text breach_lit(sm_opt["label"]):
                                            size gui.size_base
                                            color gui.breach_text_color
                                            yalign 0.5
                                        ## left-pack the tag + line (the trailing
                                        ## filler keeps them flush-left, not drifting
                                        ## to the row centre).
                                        null:
                                            xfill True


## --------------------------------------------------------------------------
## Placeholder dialogue labels (GDD 15.7 + 4.2). Each is a Ren'Py label the
## integration glue (label city_free_mode) `call`s; each ends in `return`.
## Every spoken line is the owner placeholder; every speaker is a bracketed
## placeholder. The single authored DC literals (12) are conservative
## one-off numbers per GAPS G-041 -- NOT drawn from any difficulty ladder
## (the ladder is writer calibration, never data; CLAUDE.md iron rules).
## --------------------------------------------------------------------------

label dlg_townsperson:
    # A bracketed placeholder speaker; the line is owner content.
    "[[Townsperson]" "[[TO BE WRITTEN BY THE PROJECT OWNER]"

    # One plain line, one skill (Presence) line, one HIDDEN class line.
    # 12 is a single conservative authored literal (GAPS G-041); it is NOT
    # from a difficulty ladder.
    call screen skill_menu(gs["party"][0], [
        {"id": "leave", "label": "Say nothing and move on.", "skill": None},
        {"id": "persuade", "label": "Win them over.", "skill": "presence", "dc": 12},
        # Hard-gated class line (e.g. a [Subtle Spell]-style feature): HIDDEN
        # while unavailable, never greyed (15.7 L1604-1606).
        {"id": "subtle", "label": "Bend their mind, unseen.", "skill": "presence",
         "dc": 12, "hidden": True},
    ])

    if _return == "persuade":
        $ res = breach_do_check("presence", 12)   # 12: conservative authored literal (G-041)
        if res["success"]:
            "[[Townsperson]" "[[TO BE WRITTEN BY THE PROJECT OWNER]"
        else:
            "[[Townsperson]" "[[TO BE WRITTEN BY THE PROJECT OWNER]"
    return


label dlg_merchant:
    # A merchant both talks and trades.
    "[[Merchant]" "[[TO BE WRITTEN BY THE PROJECT OWNER]"

    call screen skill_menu(gs["party"][0], [
        {"id": "browse", "label": "Look over the wares.", "skill": None},
        {"id": "haggle", "label": "Talk the price down.", "skill": "guile", "dc": 12},
        {"id": "leave", "label": "Step away.", "skill": None},
    ])

    if _return == "browse":
        # Open the shop, then fall through to return (the shop screen is part
        # of the integration glue; this label only references it).
        call screen shop_screen("general_store")
    elif _return == "haggle":
        $ res = breach_do_check("guile", 12)      # 12: conservative authored literal (G-041)
        if res["success"]:
            "[[Merchant]" "[[TO BE WRITTEN BY THE PROJECT OWNER]"
        else:
            "[[Merchant]" "[[TO BE WRITTEN BY THE PROJECT OWNER]"
    return


label dlg_questgiver:
    "[[Quest Giver]" "[[TO BE WRITTEN BY THE PROJECT OWNER]"

    call screen skill_menu(gs["party"][0], [
        {"id": "accept", "label": "Take up the task.", "skill": None},
        {"id": "read", "label": "Size them up first.", "skill": "intuition", "dc": 12},
        {"id": "decline", "label": "Not now.", "skill": None},
    ])

    if _return == "accept":
        # Start the main quest only if it has never been started. Concluded
        # quests stay concluded (15.5); a double-start would raise, so guard
        # on is_active AND not-already-present, with a try/except backstop so
        # re-talking can never crash (GDD 15.5 / 16.1).
        if (not bquests.is_active(gs, "quest_main_hook")
                and "quest_main_hook" not in gs.get("quests", {})):
            python:
                try:
                    bquests.start_quest(REG, gs, "quest_main_hook")
                    renpy.block_rollback()        # commit the quest start (16.1)
                    breach_toast("Quest updated")
                except ValueError:
                    pass
        "[[Quest Giver]" "[[TO BE WRITTEN BY THE PROJECT OWNER]"
    elif _return == "read":
        $ res = breach_do_check("intuition", 12)  # 12: conservative authored literal (G-041)
        if res["success"]:
            "[[Quest Giver]" "[[TO BE WRITTEN BY THE PROJECT OWNER]"
        else:
            "[[Quest Giver]" "[[TO BE WRITTEN BY THE PROJECT OWNER]"
    return
