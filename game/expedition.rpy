# Expedition (the Breach) flow glue (GDD #13.2 L1401-1402 node map; #12.1
# Breather). Mirrors city.rpy: the expedition map is the exploration screen
# with the HUD (expedition state) live; selecting a connected node moves there
# and fires its kind (encounter -> combat, campsite -> camp, exit -> leave).
# The Breather button lives on this exploration screen (#12.1 L1321).
#
# Owner content (GAPS G-044/G-046): node names + the Breather ambient beat are
# bracketed placeholders; every data-driven name renders through breach_lit.

init python:

    # The node-plate footprint -- the authored node positions in
    # REG["expedition_map"] are laid out for this exact size, so it is kept
    # verbatim from the original screen (the only raw geometry the map needs).
    # Defined ONCE here, not per-button, so the card and the travel-edge maths
    # read the same dimensions.
    # Geometry lives once in gui.rpy (CLAUDE.md one-style-source); referenced
    # here so the card and the travel-edge maths read the same dimensions.
    BREACH_NODE_W = gui.expedition_node_w
    BREACH_NODE_H = gui.expedition_node_h

    def breach_node_label(node):
        """A node plate's title: its placeholder name (literal-escaped). The
        kind hint is no longer inlined here -- it renders as a typed, colour-
        coded tag (breach_node_kind) so the name keeps its own type tier."""
        return breach_lit(node["name"])

    def breach_node_kind(node):
        """The node's kind as a player-voiced label + its category colour for
        a tag chip (Danger=red, Camp=green, Exit/Entrance=lamplight). Reads
        only node['kind']; returns (label, color) or (None, None) for unknown."""
        label = {"entry": "Entrance", "encounter": "Danger",
                 "campsite": "Camp", "exit": "Exit"}.get(node["kind"], "")
        if not label:
            return (None, None)
        color = {"encounter": gui.danger_color,
                 "campsite": gui.success_color}.get(node["kind"],
                                                    gui.breach_accent_color)
        return (label, color)

    def breach_node_edge(a_pos, b_pos, color):
        """A thin travel link between two node plates: a hairline Solid laid
        from the centre of plate `a_pos` to the centre of plate `b_pos`,
        rotated to the bearing between them. Pure presentation derived from the
        authored node positions -- no data is read or written. Returns a
        positioned Transform to `add` beneath the node cards."""
        import math
        ax = a_pos[0] + BREACH_NODE_W / 2.0
        ay = a_pos[1] + BREACH_NODE_H / 2.0
        bx = b_pos[0] + BREACH_NODE_W / 2.0
        by = b_pos[1] + BREACH_NODE_H / 2.0
        length = max(1.0, math.hypot(bx - ax, by - ay))
        angle = math.degrees(math.atan2(by - ay, bx - ax))
        # transform_anchor re-projects the placement anchor THROUGH the
        # rotation, so anchoring the line's left-centre (0.0, 0.5) and placing
        # it at node A's centre keeps the segment starting at A and running
        # toward B at the right bearing, for any direction.
        line = Transform(Solid(color, xsize=int(length), ysize=gui.hairline),
                         rotate=angle, rotate_pad=False, subpixel=True,
                         transform_anchor=True,
                         anchor=(0.0, 0.5), pos=(int(ax), int(ay)))
        return line

    def breach_breather_spend(char_id):
        """Spend one Recovery Die for a member during a Breather (#12.1)."""
        m = bstate.party_member(gs, char_id)
        try:
            healed = brest.spend_recovery_die(REG, m, bdice.roll)
            renpy.block_rollback()                 # a committed heal (#16.1)
            breach_toast("%s recovered %d health." % (m["name"], healed))
        except ValueError:
            breach_toast("No Recovery Dice left.")


## The node-based expedition map (#13.2). Plates at authored positions; only
## nodes connected to the current node are travellable, the current one is
## marked, the rest are dimmed. Breather + Leave buttons sit at the bottom so
## the top-right HUD (Supply + Breathers) never collides.

screen expedition_map(node_id):
    modal True

    $ exp_cur = REG["expedition_map"][node_id]
    $ exp_region = REG["regions"].get(exp_cur["region"])

    ## The room backdrop (base rung), then the map field sunk one rung below the
    ## chrome on breach_well -- depth from value, not art. The field is INSET
    ## (gui.screen_pad) so it never bleeds to the screen edge or under the HUD,
    ## and reads as a contained map. Placeholder map art stays placeholder: a
    ## colored region wash floats on the recessed ground, with an amber hairline
    ## edge framing the field as a deliberate boundary.
    add Solid(gui.bg_color)
    frame:
        style "breach_well"
        xfill True
        yfill True
        margin (gui.screen_pad, gui.screen_pad)
        ## a hairline border frames the wash so the field reads as a contained
        ## map, not a full-bleed colour wall; the region wash sits inside it.
        frame:
            xfill True
            yfill True
            background Solid(gui.panel_border_color)
            padding (gui.hairline, gui.hairline)
            add Solid(breach_placeholder_color(exp_cur["region"]))

    ## The travel-edge layer: thin links from the current node to every node it
    ## connects to, drawn BENEATH the node cards so reachability reads as a
    ## graph. Lamplit (accent_dim) for travellable links. Drawn in the SAME
    ## absolute coordinate space the authored node positions assume (origin at
    ## the screen, exactly as before) -- no data is read or shifted.
    for exp_eid in exp_cur["connections"]:
        $ exp_edge_n = REG["expedition_map"].get(exp_eid)
        if exp_edge_n:
            add breach_node_edge(exp_cur["pos"], exp_edge_n["pos"], gui.breach_accent_dim_color)

    ## The nodes -- framed selectable cards at their authored positions. The
    ## footprint (240x120) is small for the heavy panel ornament, so the card
    ## keeps the proven accent-border idiom (the portrait_chip / lane idiom: a
    ## bordered fill that lights amber on hover/selected) and carries REAL card
    ## structure: a kind swatch, the node name on the display tier, and a
    ## colour-coded kind tag. The current location is the ONE focal -- lit fill
    ## + a clean amber edge ('you are here'); travellable nodes carry a quiet
    ## accent border and brighten on hover; unreachable nodes desaturate into
    ## the dark. Cards keep their AUTHORED absolute positions (origin at the
    ## screen, exactly as before) so the registry coordinates land unshifted --
    ## the field inset is purely visual chrome behind them.
    for exp_nid in REG["expedition_map"]:
        $ exp_n = REG["expedition_map"][exp_nid]
        $ exp_here = (exp_nid == node_id)
        $ exp_reach = (exp_nid in exp_cur["connections"])
        $ exp_kind_label, exp_kind_color = breach_node_kind(exp_n)
        python:
            exp_border = (gui.breach_accent_color if (exp_here or exp_reach)
                          else gui.panel_border_color)
            exp_fill = (gui.breach_lit_panel_color if exp_here else gui.panel_color)
            ## unreachable, non-current nodes sink into the dark: the same
            ## saturation-0 + dim-alpha 'burning low' read the combat tiles use
            ## for downed/invalid units, so the whole game desaturates inactive
            ## elements identically. Live nodes keep full colour.
            if exp_here or exp_reach:
                exp_xform = Transform()
            else:
                exp_xform = Transform(matrixcolor=SaturationMatrix(0.0), alpha=0.45)
        button:
            pos (exp_n["pos"][0], exp_n["pos"][1])
            xsize BREACH_NODE_W
            ysize BREACH_NODE_H
            padding (gui.hairline, gui.hairline)
            background Solid(exp_border)
            hover_background Solid(gui.accent_bright_color if exp_reach else exp_border)
            sensitive exp_reach
            action (Return(("node", exp_nid)) if exp_reach else NullAction())
            at exp_xform
            fixed:
                xfill True
                yfill True
                add Solid(exp_fill)
                frame:
                    background None
                    xfill True
                    yfill True
                    padding (gui.pad_s, gui.pad_s)
                    hbox:
                        spacing gui.pad_s
                        yalign 0.5
                        add Solid(exp_kind_color or gui.panel_border_color):
                            xsize gui.card_thumb_size
                            ysize gui.card_thumb_size
                            yalign 0.5
                        vbox:
                            spacing gui.pad_xs
                            yalign 0.5
                            text breach_node_label(exp_n):
                                style "breach_display_text"
                                size gui.size_base
                                color (gui.breach_accent_color if exp_here else gui.breach_text_color)
                            if exp_kind_label:
                                text exp_kind_label.upper():
                                    style "breach_label_text"
                                    color (exp_kind_color or gui.muted_text_color)
                ## the current node is the one lit focal -- a clean amber
                ## outline marks 'you are here' without a muddy wash.
                if exp_here:
                    use breach_accent_edge()

    ## Title (top-left, clear of the HUD top-right cluster): a raised chrome
    ## panel with a quiet "The Breach" caption over the lit region name on the
    ## section-header treatment (display tier + hairline rule), so it grounds
    ## like every other screen's header instead of a bare lit line.
    frame:
        xpos gui.screen_pad
        ypos gui.screen_pad
        background None
        use breach_panel():
            vbox:
                spacing gui.pad_xs
                text "The Breach" style "breach_label_text"
                if exp_region:
                    ## breach_title (no full-width rule) keeps the header a small
                    ## top-left card that clears the top-centre / top-right HUD.
                    use breach_title(exp_region["name"])

    ## Breather + Leave: a docked action band at the bottom-centre, grounded by
    ## a lamplit lip above it so it reads as chrome, not a stray pill. The
    ## Breather count is surfaced as a segmented pip gauge (not jammed into the
    ## verb); when no Breathers remain the whole control desaturates -- the
    ## same 'lamplight burning low' language as camp.
    $ exp_breathers = brest.breathers_remaining(REG, gs, gs["party"])
    $ exp_breather_max = brest.breather_max(REG, gs["party"])
    frame:
        align (0.5, 0.98)
        background None
        use breach_panel():
            vbox:
                spacing gui.pad_s
                if exp_breather_max > 0:
                    ## NO breach_lip here -- a full-width rule would stretch this
                    ## content-sized (fit_first) panel across the whole screen.
                    use breach_resource("Breathers", exp_breathers, exp_breather_max)
                hbox:
                    spacing gui.pad_l
                    if exp_breathers > 0:
                        textbutton "Breather":
                            style "breach_frame_button"
                            action Return(("breather",))
                    else:
                        textbutton "Breather":
                            style "breach_frame_button"
                            sensitive False
                            at breach_desaturate
                            action Return(("breather",))
                    textbutton "Leave the Breach":
                        style "breach_frame_button"
                        action Return(("leave",))


## Recovery-die spend during a Breather (#12.1 L1325-1327): each member may
## spend a die to heal. Optional -- Close when done.

screen breather_recovery():
    modal True
    ## Modal: the dark scrim sinks everything behind it so the panel is the
    ## only lit object (DESIGN pattern 6).
    add Solid(gui.breach_scrim_color)
    frame:
        align (0.5, 0.5)
        background None
        use breach_panel():
            vbox:
                spacing gui.pad_m
                xsize gui.modal_w
                use section_header("Breather — spend Recovery Dice")
                ## the member list sits in a recessed well; each row is a framed
                ## list-row so the list reads with depth and a clear hover.
                frame:
                    style "breach_well"
                    xfill True
                    vbox:
                        spacing gui.pad_s
                        xfill True
                        for exp_m in gs["party"]:
                            $ exp_dice = exp_m["resources"].get("recovery_dice", exp_m["level"])
                            $ exp_can_spend = (exp_dice > 0 and exp_m["hp"] < exp_m["hp_max"])
                            ## a member with no dice or already at full health
                            ## sinks into the dark (the shared 'burning low' cue),
                            ## matching the spend-button sensitivity gate.
                            $ exp_row_xform = (Transform() if exp_can_spend else Transform(matrixcolor=SaturationMatrix(0.0)))
                            button:
                                style "breach_frame_row"
                                sensitive exp_can_spend
                                action Function(breach_breather_spend, exp_m["id"])
                                at exp_row_xform
                                hbox:
                                    spacing gui.pad_m
                                    xfill True
                                    yalign 0.5
                                    use portrait_chip(exp_m, size=96, show_hp=True)
                                    vbox:
                                        spacing gui.pad_s
                                        yalign 0.5
                                        text breach_lit(exp_m["name"]) size gui.size_base color gui.breach_text_color
                                        ## Recovery Dice as a small discrete pool:
                                        ## a segmented pip gauge, not plain text.
                                        use breach_resource("Recovery Dice", exp_dice, max(exp_dice, exp_m["level"]))
                                    null:
                                        xfill True
                                    ## the verb rides the right-meta column; the
                                    ## whole row is the spend affordance.
                                    text "Spend a die":
                                        size gui.size_base
                                        yalign 0.5
                                        xalign 1.0
                                        color (gui.breach_accent_color if exp_can_spend else gui.muted_text_color)
                textbutton "Done":
                    style "breach_frame_button"
                    xalign 1.0
                    action Return(None)


## ---------------------------------------------------------------------------
## Expedition flow (#13.1: a separate mode while in the Breach).
## ---------------------------------------------------------------------------

label expedition_mode:
    $ gs["in_expedition"] = True
    $ store.hud_mode = "expedition"
    if not gs.get("expedition_node"):
        $ bstate.set_breach_region(gs, "region_breach_1")
        $ gs["expedition_node"] = "node_entry"
    jump expedition_loop


label expedition_loop:
    $ store.hud_visible = (gs is not None)
    call screen expedition_map(gs["expedition_node"])
    $ _exp = _return
    $ store.hud_visible = False

    if _exp is None or (isinstance(_exp, (tuple, list)) and _exp and _exp[0] == "leave"):
        $ gs["in_expedition"] = False
        $ store.hud_mode = "city"
        return

    if isinstance(_exp, (tuple, list)) and _exp:
        $ _tag = _exp[0]
        if _tag == "node":
            $ gs["expedition_node"] = _exp[1]
            $ _node = REG["expedition_map"][_exp[1]]
            if _node["kind"] == "encounter":
                call combat_encounter(_node["encounter"], _node.get("flee", False), _node.get("loot"))
            elif _node["kind"] == "campsite":
                call camp_mode               # wilds Camp (burns Supply)
            elif _node["kind"] == "exit":
                $ gs["in_expedition"] = False
                $ store.hud_mode = "city"
                return
        elif _tag == "breather":
            call expedition_breather
        elif _tag == "hud":
            call breach_expedition_hud(_exp)
            if store.breach_free_leave:
                $ store.breach_free_leave = False
                $ gs["in_expedition"] = False
                $ store.hud_mode = "city"
                return
    jump expedition_loop


## HUD dispatch while in the Breach. Unlike the city, the map icon is a no-op
## (the expedition map IS the current screen); the gear opens the same Free
## Mode menu; a portrait opens that member's sheet (#15.1 L1502-1504).
label breach_expedition_hud(intent):
    if intent[1] == "menu":
        call screen free_mode_menu
        $ _em = _return
        if _em == "quests":
            call screen quest_tab
        elif _em == "inventory":
            call screen inventory_screen
        elif _em == "sheet":
            call screen character_sheet
            if isinstance(_return, (tuple, list)) and len(_return) >= 2 and _return[0] == "levelup":
                call levelup_wizard(_return[1])
        elif _em == "outfitter":
            call screen camp_upgrade_shop
        elif _em == "leave":
            $ store.breach_free_leave = True
    elif intent[1] == "sheet":
        $ _ecid = intent[2] if len(intent) > 2 else None
        $ _eidx = next((i for i, m in enumerate(gs["party"]) if m["id"] == _ecid), 0)
        call screen character_sheet(_eidx)
        if isinstance(_return, (tuple, list)) and len(_return) >= 2 and _return[0] == "levelup":
            call levelup_wizard(_return[1])
    # intent[1] == "map": no-op -- the expedition map is already showing.
    return


## A Breather (#12.1): recharge the party's short-rest features, advance the
## day clock, play the ambient beat, then offer Recovery Dice.
label expedition_breather:
    if brest.breathers_remaining(REG, gs, gs["party"]) <= 0:
        $ breach_toast("No Breathers left until you Camp.")
    else:
        $ brest.take_breather(REG, gs, gs["party"])
        $ renpy.block_rollback()             # the Breather is committed (#16.1)
        # The ten-second ambient beat (#12.1 L1331-1332) is owner content.
        "[[Breather — TO BE WRITTEN BY THE PROJECT OWNER]"
        call screen breather_recovery
    return
