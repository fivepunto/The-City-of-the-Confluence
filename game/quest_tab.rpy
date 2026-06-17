# The quest tab (GDD #15.5 L1555-1563): a TAB in the menu, NOT a journal.
# Two panes side by side -- LEFT the active quests grouped Main / Side /
# Companion as LISTS (NOT a tab_bar; #15.5 groups are lists, L1556-1557);
# RIGHT the selected quest's render: current objective bolded ABOVE the
# crossed-out past objectives, with a Reward line ONLY when the quest
# authored one as a promise (#15.5 L1561). No map markers (#15.5 L1562).
#
# All quest strings (titles, givers, locations, objectives) are owner
# content -- already bracketed "[...]" placeholders in data (data/quests.py,
# GAPS G-039); this screen surfaces them as-is, never inventing content.
# The left/right data comes from core.quests (bquests): active_quests groups
# the lists (concluded quests already excluded, #15.5 L1559) and quest_view
# renders one quest. This screen only reads; no state mutation, so no
# rollback call is needed here.

init python:

    # The three quest groups, in the order #15.5 lists them (L1556-1557).
    BREACH_QUEST_GROUPS = [("main", "Main"),
                           ("side", "Side"),
                           ("companion", "Companion")]

    def breach_quest_reward_parts(rewards):
        """The reward promise as a LIST of short player-facing parts (gold,
        then each item by display name) from a quest_view rewards dict
        {gold, items:[item_id,...]} -- shown only when the quest promised a
        reward (#15.5 L1561). Uses the shared breach_item_name helper so
        reward items read by their display name. Presentation (chips vs a
        joined line) is the caller's; this is the single data source."""
        parts = []
        gold = rewards.get("gold") or 0
        if gold:
            parts.append("%d gold" % gold)
        for iid in rewards.get("items") or ():
            parts.append(breach_item_name(iid))
        return parts

    def breach_quest_reward_line(rewards):
        """One short player-facing Reward line (the comma-joined parts);
        the em-dash fallback when nothing is promised."""
        parts = breach_quest_reward_parts(rewards)
        return ", ".join(parts) if parts else "—"


screen quest_tab():
    modal True
    add Solid(gui.bg_color)

    default sel_quest = None

    ## active quest ids grouped Main / Side / Companion (#15.5 L1556-1557);
    ## active_quests already drops concluded quests (#15.5 L1559).
    $ breach_quest_groups = bquests.active_quests(REG, gs) if gs is not None else {"main": [], "side": [], "companion": []}
    $ breach_quest_any = any(breach_quest_groups[g] for g, _ in BREACH_QUEST_GROUPS)

    frame:
        background None
        xfill True
        yfill True
        padding (gui.pad_l, gui.pad_l)

        vbox:
            spacing gui.pad_m
            xfill True

            ## Header band: the screen's chrome -- title + Close -- raised over
            ## the content with a lamplit lip beneath (the eye's anchor).
            ## Header band: title + Close.
            use breach_quest_header()
            use breach_lip(gui.breach_accent_color)

            hbox:
                spacing gui.pad_m
                xfill True
                ## LEFT: the active quests, grouped (#15.5 L1556-1557).
                use breach_quest_list(breach_quest_groups, breach_quest_any, sel_quest)
                ## RIGHT: the selected quest's render (#15.5 L1557-1562).
                use breach_quest_detail(sel_quest)


## --- quest-tab regions (composed by quest_tab via `use`) -------------------
## sel_quest lives on quest_tab; the list's SetScreenVariable resolves against
## the shown screen.

## Header band: the screen's chrome -- title + Close.
screen breach_quest_header():
    frame:
        style "breach_band"
        xfill True
        padding (gui.pad_m, gui.pad_m)
        hbox:
            xfill True
            use breach_title("Quests")
            textbutton "Close":
                style "breach_button"
                xalign 1.0
                yalign 0.5
                action Return(None)


## LEFT region: the active quests, grouped as lists -- a recessed well with
## the list drawer sunk below the chrome; the selected quest is the lit focal
## row (#15.5 L1556-1557).
screen breach_quest_list(breach_quest_groups, breach_quest_any, sel_quest):
    frame:
        background None
        xsize gui.split_list_w
        use breach_panel():
            frame:
                style "breach_well"
                xfill True
                if breach_quest_any:
                    viewport:
                        scrollbars "vertical"
                        mousewheel True
                        ysize gui.pane_h
                        xfill True
                        vbox:
                            spacing gui.pad_s
                            xfill True
                            for grp_idx, (grp_key, grp_label) in enumerate(BREACH_QUEST_GROUPS):
                                if breach_quest_groups[grp_key]:
                                    ## Articulate the three groups: each new
                                    ## band gets a wider leading gap so Main /
                                    ## Side / Companion read as distinct.
                                    if grp_idx > 0:
                                        null height gui.pad_m
                                    use section_header(grp_label)
                                    for qid in breach_quest_groups[grp_key]:
                                        $ q_title = REG["quests"][qid]["title"]
                                        $ q_selected = (sel_quest == qid)
                                        ## THE shared framed list row: idle
                                        ## frame quiet, amber-edge + glow when
                                        ## selected/hovered. The selected row is
                                        ## the one lit focal surface of the list.
                                        ## Leading swatch keys off the quest id;
                                        ## the group label rides the right-meta
                                        ## column. action/selected wiring is
                                        ## unchanged (resolves on quest_tab).
                                        use breach_list_row(
                                            title=q_title,
                                            meta=grp_label,
                                            icon_key=qid,
                                            selected=q_selected,
                                            action=SetScreenVariable("sel_quest", qid),
                                            title_color=(gui.breach_accent_color if q_selected else None))
                else:
                    use breach_empty_state("No active quests.", "Quests you take on will appear here.")


## RIGHT region: the selected quest's render -- title, giver/location, the
## current objective above the struck-through past log, and a reward line when
## one is promised (#15.5 L1557-1562).
screen breach_quest_detail(sel_quest):
    frame:
        background None
        xfill True
        use breach_panel():
            if sel_quest is not None:
                $ q_view = bquests.quest_view(REG, gs, sel_quest)
                viewport:
                    scrollbars "vertical"
                    mousewheel True
                    ysize gui.pane_h
                    xfill True
                    vbox:
                        spacing gui.pad_l
                        xfill True

                        ## Title leads on the serif display tier; the giver /
                        ## location ride small metadata chips beneath it so the
                        ## quest's "where it came from" reads distinctly from
                        ## the struck past log below.
                        vbox:
                            spacing gui.pad_s
                            xfill True
                            $ q_title = q_view["title"]
                            text breach_lit(q_title):
                                style "breach_header_text"
                                size gui.size_heading
                                color gui.breach_text_color
                            ## "Given by [giver] · [location]" (#15.5 L1557;
                            ## both are owner placeholders).
                            $ q_giver = q_view["giver"]
                            $ q_location = q_view["location"]
                            hbox:
                                spacing gui.pad_s
                                use breach_tag(q_giver, gui.muted_text_color)
                                use breach_tag(q_location, gui.muted_text_color)

                        ## OBJECTIVE region: the player's "what do I do now".
                        ## The current objective is promoted to the ONE lit
                        ## focal surface of this pane (breach_panel_lit), bolded
                        ## and accent-coloured (#15.5 L1558); the past log sinks
                        ## struck-through and muted beneath it. Concluded quests
                        ## never reach this pane (#15.5 L1559).
                        vbox:
                            spacing gui.pad_m
                            xfill True
                            use section_header("Objective")
                            if q_view["current_objective"]:
                                $ q_current = q_view["current_objective"]
                                use breach_panel_lit():
                                    text ("{b}" + breach_lit(q_current) + "{/b}"):
                                        size gui.size_base
                                        color gui.breach_accent_color
                                        xfill True
                            ## Past objectives, each struck through with {s}
                            ## (#15.5 L1558) -- spent work sunk to muted micro.
                            for q_past in q_view["past_objectives"]:
                                text ("{s}" + breach_lit(q_past) + "{/s}"):
                                    size gui.size_micro
                                    color gui.muted_text_color

                        ## REWARD region ONLY when the quest promised one
                        ## (#15.5 L1561) -- each part rides a tag chip so the
                        ## promise carries visual weight.
                        if q_view["rewards"] is not None:
                            vbox:
                                spacing gui.pad_m
                                xfill True
                                use section_header("Reward")
                                $ q_reward_parts = breach_quest_reward_parts(q_view["rewards"])
                                if q_reward_parts:
                                    hbox:
                                        spacing gui.pad_s
                                        box_wrap True
                                        for q_reward_part in q_reward_parts:
                                            use breach_tag(q_reward_part, gui.breach_accent_color)
                                else:
                                    text "—":
                                        size gui.size_base
                                        color gui.muted_text_color
            else:
                use breach_empty_state("Select a quest.", "Pick a quest on the left to see its objective.")
