# The Guildhall notice board (GDD #15.5 L1555-1563 / #17.2): the surface where
# Guild jobs are POSTED for the player to accept (Imara points the player at it
# at the end of the prologue). DATA-driven -- the postings come from
# core.quests.board_quests (a quest flagged `board: True` that has not been
# started or concluded). Accepting a posting starts the quest and blocks
# rollback (#16.1), so it leaves the board. The board is EMPTY until a quest
# sets `board: True`.
#
# Reached from the guild-hall hotspot (data/locations.py hs_guildhall_questboard
# -> kind "questboard" -> ("questboard", None), dispatched by city_free_loop via
# `call screen quest_board`). This screen only READS the registry and starts a
# quest on click; the start mutation + rollback block live here (the .rpy
# layer), per the rollback discipline.

init python:

    def breach_accept_board_quest(qid):
        """Accept a posted job: start the quest, commit it past rollback
        (#16.1), and toast. Guarded with try/except so a double-accept (or a
        stale row) can never crash; the row then drops off the board because the
        quest is now active (board_quests excludes started quests)."""
        try:
            bquests.start_quest(REG, gs, qid)
            renpy.block_rollback()                   # commit the accept (16.1)
            breach_toast("Quest accepted")
        except ValueError:
            pass


screen quest_board():
    modal True
    add Solid(gui.bg_color)

    ## Postings available to accept (#15.5). board_quests already excludes any
    ## quest that has been started or concluded, so accepting one removes it.
    $ breach_board_ids = bquests.board_quests(REG, gs) if gs is not None else []

    frame:
        background None
        xfill True
        yfill True
        padding (gui.pad_l, gui.pad_l)

        vbox:
            spacing gui.pad_m
            xfill True

            ## Header band: title + Close, with the lamplit lip beneath (the
            ## same chrome family as the quest tab and city map).
            frame:
                style "breach_band"
                xfill True
                padding (gui.pad_m, gui.pad_m)
                hbox:
                    xfill True
                    use breach_title("Notice Board")
                    textbutton "Close Board":
                        style "breach_frame_button"
                        xalign 1.0
                        yalign 0.5
                        action Return(None)
            use breach_lip(gui.breach_accent_color)

            ## The postings well: a recessed ground the job rows rise on. Each
            ## posting is a framed list row -- title + "Posted by <giver>" --
            ## that ACCEPTS the quest on click (start it, then it leaves the
            ## board). Empty until a quest is flagged board:True.
            frame:
                background None
                xfill True
                yfill True
                use breach_panel():
                    frame:
                        style "breach_well"
                        xfill True
                        yfill True
                        if breach_board_ids:
                            viewport:
                                scrollbars "vertical"
                                mousewheel True
                                ysize gui.pane_h
                                xfill True
                                vbox:
                                    spacing gui.pad_s
                                    xfill True
                                    for qb_id in breach_board_ids:
                                        $ qb = REG["quests"][qb_id]
                                        ## title + giver ride the shared bronze
                                        ## row (it escapes the names itself);
                                        ## clicking accepts the job.
                                        use breach_list_row(
                                            title=qb["title"],
                                            subtitle="Posted by %s" % qb["giver"],
                                            icon_key=qb_id,
                                            action=Function(breach_accept_board_quest, qb_id))
                        else:
                            use breach_empty_state(
                                "The board is bare.",
                                "No jobs are posted right now.")
