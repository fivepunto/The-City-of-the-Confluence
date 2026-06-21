# City map + Free Mode flow glue (GDD #13.2 L1395-1402, #15.1). This is the
# orchestration that ties the leaf screens together: it shows the city map
# and the generic location screen with the HUD overlay live, and dispatches
# the intents they (and the HUD) return -- districts, hotspots (shop /
# dialogue / door / exit), and the HUD's map/menu/sheet buttons.
#
# Owner content (GAPS G-038): district/location/hotspot NAMES are bracketed
# placeholders in data/locations.py; this glue is content-free.

default breach_free_leave = False


## The city map (#13.2 L1396-1398): district-to-district travel. Only
## available districts are shown -- locked ones are simply absent (never
## greyed, no map markers, #13.2 / #15.5 L1562).
##
## Presentation (DESIGN.md City anchor): the map is the room itself, so it
## sits on the bg ground. A small raised chrome band carries the title, a
## quiet day-phase sun indicator, and the Leave exit, with a lamplit lip
## along its bottom edge. The districts live on a recessed breach_well map
## field; each open district is a swatch marker that lights on hover/focus.
screen city_map():
    modal True
    add Solid(gui.bg_color)

    frame:
        background None
        xfill True
        yfill True
        padding (gui.pad_l, gui.pad_l)
        vbox:
            spacing gui.pad_m
            xfill True

            ## Top chrome band: title + day-phase sun indicator + Leave.
            ## Small at the edge, lamplit lip beneath -- the HUD hides here,
            ## so the map carries its own quiet day/menu chrome.
            frame:
                style "breach_band"
                xfill True
                padding (gui.pad_m, gui.pad_s)
                hbox:
                    spacing gui.pad_m
                    xfill True
                    yalign 0.5
                    ## the band's one clear focal text: the title on the display
                    ## (serif) tier, left-dominant, matching the location header.
                    text "City Map":
                        style "breach_header_text"
                        size gui.size_title
                        yalign 0.5
                    ## right cluster: the day-phase sun indicator + the exit,
                    ## pushed to the far edge (nested hbox xalign, like the
                    ## sheet's tab-row exits).
                    hbox:
                        spacing gui.pad_m
                        yalign 0.5
                        xalign 1.0
                        ## the day-phase "sun position" indicator: three slots,
                        ## the active one lit (same language as the HUD), named
                        ## in the micro caption tier. Reads gs["day_phase"].
                        $ city_phase = gs.get("day_phase", "morning")
                        $ city_phase_label = dict(BREACH_DAY_PHASES).get(city_phase, city_phase.capitalize())
                        hbox:
                            spacing gui.pad_s
                            yalign 0.5
                            hbox:
                                spacing gui.pad_xs
                                yalign 0.5
                                for city_p_key, city_p_label in BREACH_DAY_PHASES:
                                    ## Solid marker (the "●" glyph is missing
                                    ## from the UI font and rendered as a box);
                                    ## matches the HUD day-phase dot size.
                                    add Solid(gui.breach_accent_color if city_p_key == city_phase
                                              else gui.muted_text_color):
                                        xysize (gui.size_micro, gui.size_micro)
                                        yalign 0.5
                            text city_phase_label:
                                size gui.size_micro
                                yalign 0.5
                                color gui.muted_text_color
                        textbutton "Leave Free Mode":
                            style "breach_button"
                            yalign 0.5
                            action Return(("leave",))
            use breach_lip(gui.breach_accent_color)

            ## The map field: a recessed dark ground the district markers rise
            ## on (depth from value, not art). The districts read as a MAP of
            ## framed nodes laid on a two-column grid, not a settings list.
            frame:
                style "breach_well"
                xfill True
                yfill True
                vbox:
                    spacing gui.pad_l
                    xfill True
                    use section_header("Districts of Veycross")
                    $ breach_open_districts = [d for d in REG["districts"].values() if d["available"]]
                    if breach_open_districts:
                        ## one framed node per open district: the shared bronze
                        ## list row (swatch + name + "Travel here" caption), lit
                        ## by the amber-edge frame on hover/focus -- the hovered
                        ## destination is the focal. No node is resting-lit:
                        ## none of these IS "where you are", they are all travel
                        ## choices. Two columns so the wide field is used.
                        vpgrid:
                            cols 2
                            spacing gui.pad_l
                            xfill True
                            for d in breach_open_districts:
                                fixed:
                                    xsize gui.split_list_w
                                    yfit True
                                    use breach_list_row(
                                        d["name"],
                                        subtitle="Travel here",
                                        icon_key=d["id"],
                                        action=Return(("district", d["id"])))
                    else:
                        ## a structured, centred empty state -- never a bare
                        ## line; it fills the field so the mark sits centred on
                        ## the recessed ground.
                        fixed:
                            xfill True
                            yfill True
                            use breach_empty_state("No districts are open yet.")


## The Free Mode menu (the HUD gear button, #15.1). The quest tab lives in
## the menu (#15.5), alongside inventory and the character sheet.
screen free_mode_menu():
    modal True
    ## a modal floating over the live game: lay the scrim first, then the
    ## panel is the only lit object (DESIGN.md pattern 6).
    add Solid(gui.breach_scrim_color)
    frame:
        background None
        align (0.5, 0.5)
        use breach_panel():
            vbox:
                spacing gui.pad_s
                xsize gui.panel_w_narrow
                use section_header("Menu")
                ## full-width framed menu items: the shared bronze button frame
                ## (amber edge on hover/focus), so the menu reads as the same
                ## framed family as the rest of the game.
                textbutton "Quests" style "breach_frame_button" xfill True action Return("quests")
                textbutton "Inventory & Equipment" style "breach_frame_button" xfill True action Return("inventory")
                textbutton "Character Sheet" style "breach_frame_button" xfill True action Return("sheet")
                textbutton "Camp Outfitter: Supplies & Upgrades" style "breach_frame_button" xfill True action Return("outfitter")
                textbutton "Save Game" style "breach_frame_button" xfill True action ShowMenu("save")
                textbutton "Preferences" style "breach_frame_button" xfill True action ShowMenu("preferences")
                ## a quiet lamplit ledge separates the session controls below
                ## from the navigation group above.
                null height gui.pad_xs
                use breach_lip(gui.breach_accent_dim_color)
                null height gui.pad_xs
                textbutton "Resume" style "breach_frame_button" xfill True action Return(None)
                textbutton "Return to Main Menu" style "breach_frame_button" xfill True action Return("leave")


## Free Mode (#13.1 L1388-1393): the interface enables and the player owns
## the game. The HUD overlay is live ONLY while the exploration screens (the
## city map / a location) are showing; it auto-hides during dialogue and any
## full-screen sub-menu (#15.1 L1496-1499).
label city_free_mode:
    $ store.breach_free_leave = False
    # The FIRST-ever Free Mode entry (including straight out of the prologue,
    # #17.2, where Imara has just registered the MC) opens INSIDE the Lamplighter
    # Guildhall; every later entry opens on the city map as before. The player
    # can return to the hall any time via the HUD map button. Marking the
    # one-shot is a committed state change, so block rollback right after it
    # (CLAUDE.md rollback discipline).
    if not gs["flags"].get("entered_free_mode"):
        $ gs["flags"]["entered_free_mode"] = True
        $ renpy.block_rollback()
        $ bstate.set_region(gs, "district_guildhall")
        $ bstate.set_location(gs, "loc_guildhall")
    else:
        $ bstate.set_location(gs, None)     # start at the city map
    $ store.hud_mode = "city"
    jump city_free_loop


label city_free_loop:
    if gs.get("location") is None:
        # The city map is a navigation screen and owns the top-right corner,
        # so the HUD (also top-right) hides here to avoid overlapping it.
        $ store.hud_visible = False
        call screen city_map
    else:
        # HUD visible while exploring a location; hidden again during dispatch.
        $ store.hud_visible = (gs is not None)
        call screen location_screen(gs.get("location"))
    $ _intent = _return
    $ store.hud_visible = False

    if _intent is None or (isinstance(_intent, (tuple, list)) and _intent and _intent[0] == "leave"):
        $ store.hud_visible = False
        return

    if isinstance(_intent, (tuple, list)) and _intent:
        $ _tag = _intent[0]
        if _tag == "district":
            $ _d = REG["districts"][_intent[1]]
            $ bstate.set_region(gs, _intent[1])
            $ bstate.set_location(gs, _d["entry"])
        elif _tag == "goto":
            $ bstate.set_location(gs, _intent[1])
        elif _tag == "exit":
            $ bstate.set_location(gs, None)          # back to the city map
        elif _tag == "shop":
            call screen shop_screen(_intent[1])
        elif _tag == "dialogue":
            # HUD auto-hides during dialogue (#15.1 L1496-1497)
            call expression _intent[1]
        elif _tag == "hud":
            call breach_hud_action(_intent)

    if store.breach_free_leave:
        $ store.hud_visible = False
        return
    jump city_free_loop


## Dispatch a HUD button (#15.1): map icon -> back to the city map; gear ->
## the Free Mode menu (quests / inventory / sheet); portrait -> that
## member's sheet, which is also the level-up entry point (#15.2 L1512).
label breach_hud_action(intent):
    if intent[1] == "map":
        $ bstate.set_location(gs, None)
    elif intent[1] == "sheet":
        # open the CLICKED member's sheet (#15.1 L1502-1504), not party[0]
        $ _cid = intent[2] if len(intent) > 2 else None
        $ _idx = next((i for i, m in enumerate(gs["party"]) if m["id"] == _cid), 0)
        call screen character_sheet(_idx)
        if isinstance(_return, (tuple, list)) and len(_return) >= 2 and _return[0] == "levelup":
            call levelup_wizard(_return[1])
    elif intent[1] == "menu":
        call screen free_mode_menu
        $ _m = _return
        if _m == "quests":
            call screen quest_tab
        elif _m == "inventory":
            call screen inventory_screen
        elif _m == "sheet":
            call screen character_sheet
            if isinstance(_return, (tuple, list)) and len(_return) >= 2 and _return[0] == "levelup":
                call levelup_wizard(_return[1])
        elif _m == "outfitter":
            call screen camp_upgrade_shop
        elif _m == "leave":
            $ store.breach_free_leave = True
    return
