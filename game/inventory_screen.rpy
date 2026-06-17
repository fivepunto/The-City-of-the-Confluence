# The inventory & equipment screen (GDD #15.4 L1509-1519): party row on
# top, the selected member's paper-doll (the eight #10.2 slots around the
# portrait) on the left, the shared party inventory on the right.
# Validation is centralized in core.inventory and explains itself; this
# screen only displays what validate_equip / equip_delta return.

default breach_inv_error = None


init python:

    BREACH_INV_TABS = [
        ("gear", "Weapons & Armor"),
        ("magic", "Magic Items"),
        ("consumables", "Consumables"),
        ("relics", "Relics"),
        ("key", "Key Items"),
    ]

    # Paper-doll arrangement of the eight slots (#10.2 L1171-1172) around
    # the central portrait.
    BREACH_DOLL_LEFT = ("head", "armor", "mainhand", "gloves")
    BREACH_DOLL_RIGHT = ("cloak", "ring", "offhand", "feet")

    # P3 added the magic_items / relics / key_items categories.
    BREACH_ITEM_TABLES = ("weapons", "armor", "consumables",
                          "magic_items", "relics", "key_items")

    def breach_item_name(item_id):
        for table in BREACH_ITEM_TABLES:
            rec = REG.get(table, {}).get(item_id)
            if rec:
                return rec["name"]
        return str(item_id).replace("_", " ").title()

    def breach_item_record(item_id):
        """Registry record for the item card across every item category."""
        for table in BREACH_ITEM_TABLES:
            rec = REG.get(table, {}).get(item_id)
            if rec:
                return rec
        return {"name": breach_item_name(item_id)}

    def breach_item_info(item_id):
        """The item card's one-line info, from registry fields only."""
        kind = binv.item_kind(REG, item_id)
        if kind == "weapon":
            w = REG["weapons"][item_id]
            return "%s %s" % (w["dice"], w["damage_type"])
        if kind == "shield":
            return "AC +%d" % REG["armor"]["shield"]["ac_bonus"]
        if kind == "armor":
            a = REG["armor"][item_id]
            if a["dex_cap"] is None:
                return "AC %d + Dexterity" % a["base_ac"]
            if a["dex_cap"] == 0:
                return "AC %d" % a["base_ac"]
            return "AC %d + Dexterity (max %d)" % (a["base_ac"], a["dex_cap"])
        if kind == "consumable":
            return breach_player_text(REG, "consumables", item_id,
                                      REG["consumables"][item_id]["effect"])
        if kind == "magic_item":
            m = REG["magic_items"][item_id]
            return breach_player_text(REG, "magic_items", item_id, m["effect"])
        if kind == "relic":
            return breach_player_text(REG, "relics", item_id, "")
        return ""

    def breach_inv_tab_items(tab):
        """Item ids in the shared inventory matching a filter tab
        (#15.4 L1546-1547). Magic items and relics arrive via the shop (P3)."""
        rows = []
        for iid in gs["inventory"]:
            kind = binv.item_kind(REG, iid)
            if tab == "gear" and kind in ("weapon", "shield", "armor"):
                rows.append(iid)
            elif tab == "magic" and kind == "magic_item":
                rows.append(iid)
            elif tab == "consumables" and kind == "consumable":
                rows.append(iid)
            elif tab == "relics" and kind == "relic":
                rows.append(iid)
            elif tab == "key" and kind == "key_item":
                rows.append(iid)
        return sorted(rows, key=breach_item_name)

    def breach_equip_options(item_id):
        """(slot, button label) pairs an item can try to equip to."""
        kind = binv.item_kind(REG, item_id)
        if kind == "weapon":
            return [("mainhand", "Equip mainhand"),
                    ("offhand", "Equip offhand")]
        if kind == "shield":
            return [("offhand", "Equip offhand")]
        if kind == "armor":
            return [("armor", "Equip")]
        return []

    def breach_equip_item(char_id, slot, item_id):
        """Equip from the shared inventory; binv.equip returns displaced
        items (including a Two-Handed weapon's cleared offhand) to it."""
        member = bstate.party_member(gs, char_id)
        try:
            binv.equip(REG, member, slot, item_id, gs["inventory"])
            store.breach_inv_error = None
        except ValueError as e:
            store.breach_inv_error = str(e)

    def breach_unequip_slot(char_id, slot):
        member = bstate.party_member(gs, char_id)
        binv.unequip(REG, member, slot, gs["inventory"])

    def breach_use_item(item_id, target_id):
        """Use a consumable on a party member -- works outside combat
        (#15.4 L1518-1519). The Healing / True Healing gate lives in
        binv.use_consumable; its ValueError text is the player-facing
        reason (#5.5, #9.1)."""
        target = bstate.party_member(gs, target_id)
        try:
            result = binv.use_consumable(REG, item_id, target, bdice.roll)
        except ValueError as e:
            store.breach_inv_error = str(e)
            return
        bstate.remove_item(gs, item_id)
        renpy.block_rollback()   # a consumable was consumed (#16.1)
        store.breach_inv_error = None
        renpy.notify("Healed %d HP" % result["healed"])

    def breach_discard_item(item_id):
        bstate.remove_item(gs, item_id)
        renpy.block_rollback()   # a committed permanent change (#16.1)


## One paper-doll slot: slot name (small, muted) over the equipped item
## name; clicking a filled slot unequips it back to the shared inventory.
## The five magic-only slots (#10.2 L1179-1181) say so when empty.

screen breach_inv_slot(member, slot_id):
    $ breach_slot_item = member["equipment"][slot_id]
    ## A real beveled gear socket: the framed-button idiom carries idle / hover
    ## / disabled frame states, so a filled slot reads as a lit socket and an
    ## empty one as the recessed disabled frame. The slot name rides the
    ## small-caps caption tier over the equipped name (the reference's
    ## caption-over-value cell).
    button:
        style "breach_frame_socket"
        sensitive (breach_slot_item is not None)
        action (Function(breach_unequip_slot, member["id"], slot_id)
                if breach_slot_item else None)
        ## An empty slot sinks into the dark (desaturated); a filled slot reads
        ## at full value -- the equipped gear is what the eye wants.
        if breach_slot_item is None:
            at breach_desaturate
        vbox:
            spacing gui.pad_xs
            xfill True
            text slot_id.replace("_", " ").upper() style "breach_label_text"
            if breach_slot_item:
                text breach_lit(breach_item_name(breach_slot_item)):
                    size gui.size_small
                    color gui.breach_text_color
            elif slot_id in binv.MAGIC_ONLY_SLOTS:
                text "magic only" size gui.size_small color gui.muted_text_color
            else:
                text "—" size gui.size_small color gui.muted_text_color


screen inventory_screen():
    modal True
    add Solid(gui.bg_color)

    default sel_id = (gs["party"][0]["id"] if gs and gs["party"] else None)
    default sel_item = None
    default tab = "gear"
    default use_picker = False

    $ breach_inv_member = bstate.party_member(gs, sel_id)

    frame:
        background None
        xfill True
        yfill True
        padding (gui.pad_l, gui.pad_l)

        vbox:
            spacing gui.pad_m
            xfill True
            yfill True

            ## Header band: title, gold, Close, the party row.
            use breach_inv_header(sel_id)
            use breach_lip(gui.breach_accent_color)

            if breach_inv_member:
                hbox:
                    spacing gui.pad_m
                    xfill True
                    yfill True
                    ## LEFT: the paper-doll, eight slots around the portrait.
                    use breach_inv_doll(breach_inv_member)
                    ## RIGHT: the shared party inventory (#10.2 L1170).
                    use breach_inv_list(breach_inv_member, tab, sel_item)
            else:
                frame:
                    background None
                    xfill True
                    use breach_panel():
                        use breach_empty_state("No party members.",
                            sub="Recruit a follower to manage their gear.")

    ## Target picker for Use (#15.4 L1518): the party members as portrait
    ## chips; works outside combat. One dark scrim sinks the screen behind it.
    use breach_inv_use_picker(sel_item, use_picker)


## --- inventory regions (composed by inventory_screen via `use`) ------------
## State (sel_id / sel_item / tab / use_picker) lives on inventory_screen;
## each region receives what it reads and its SetScreenVariable actions
## resolve against the shown screen.

## Header band: the inventory's chrome -- title, gold (gold shows in
## inventory, #15.1), Close, and the party row (the selected member is the lit
## focal chip).
screen breach_inv_header(sel_id):
    frame:
        style "breach_band"
        xfill True
        padding (gui.pad_m, gui.pad_m)
        vbox:
            spacing gui.pad_m
            xfill True

            ## Top-HUD discipline: title/breadcrumb pinned left; the right edge
            ## carries the resource cluster (gold, set apart as its own framed
            ## instrument) THEN navigation (Close), so a resource never reads as
            ## a button and navigation never reads as a number.
            hbox:
                xfill True
                yalign 0.5
                use breach_title("Inventory & Equipment")
                hbox:
                    spacing gui.pad_l
                    xalign 1.0
                    yalign 0.5
                    frame:
                        background Solid(gui.breach_stage_color)
                        padding (gui.pad_m, gui.pad_s)
                        yalign 0.5
                        use breach_stat_cell("Gold", gs["gold"],
                            value_color=gui.breach_accent_color)
                    textbutton "Close":
                        style "breach_frame_button"
                        yalign 0.5
                        action Return(None)

            ## Party row: click to select a member.
            hbox:
                spacing gui.pad_m
                for m in gs["party"]:
                    use portrait_chip(m, size=128,
                        action=[SetVariable("breach_inv_error", None),
                                SetScreenVariable("sel_id", m["id"])],
                        selected=(m["id"] == sel_id),
                        show_hp=True)


## LEFT region: the paper-doll -- the eight #10.2 slots around the central
## portrait, with the member's AC and HP.
screen breach_inv_doll(breach_inv_member):
    ## A bounded, gold-framed panel (panel fill + the shared gold frame as the
    ## foreground) of fixed width -- NOT a fit_first panel, so the three-column
    ## doll lays out reliably (the fit_first wrapper collapsed it to one column).
    frame:
        background gui.panel_frame_fill
        foreground gui.panel_frame
        xsize gui.detail_pane_w
        yfill True
        padding (gui.panel_frame_pad, gui.panel_frame_pad)
        vbox:
            spacing gui.pad_m
            xfill True
            use section_header("Equipment — " + breach_inv_member["name"])
            ## The reference paper-doll: four sockets | centre portrait | four
            ## sockets, side by side. Stacking the portrait ON TOP of the slots
            ## ran taller than the panel and clipped the bottom sockets; the
            ## flanking layout is short enough to show all eight. FIXED column
            ## widths (two xfill columns don't split -- the first grabs the row).
            $ breach_doll_center = 200
            $ breach_doll_col = (gui.detail_pane_w - 2 * gui.panel_frame_pad - breach_doll_center - 2 * gui.pad_s) // 2
            hbox:
                spacing gui.pad_s
                xfill True
                yalign 0.0
                ## left sockets
                vbox:
                    xsize breach_doll_col
                    spacing gui.pad_s
                    for slot_id in BREACH_DOLL_LEFT:
                        use breach_inv_slot(breach_inv_member, slot_id)
                ## centre: the framed portrait (bevel + corner ticks) with AC
                ## and HP beneath it -- nothing squeezes the portrait.
                vbox:
                    xsize breach_doll_center
                    spacing gui.pad_s
                    frame:
                        background breach_frame_portrait
                        padding (gui.pad_m, gui.pad_m)
                        xalign 0.5
                        use portrait_chip(breach_inv_member, size=160)
                    use breach_stat_cell("AC", bch.ac(REG, breach_inv_member))
                    use hp_bar(breach_inv_member["hp"], breach_inv_member["hp_max"], width=110)
                ## right sockets
                vbox:
                    xsize breach_doll_col
                    spacing gui.pad_s
                    for slot_id in BREACH_DOLL_RIGHT:
                        use breach_inv_slot(breach_inv_member, slot_id)


## RIGHT region: the shared party inventory -- filter tabs, the item list in a
## recessed well, and the action panel for the selected item (#10.2 L1170).
screen breach_inv_list(breach_inv_member, tab, sel_item):
    $ breach_inv_rows = breach_inv_tab_items(tab)
    ## A bounded gold panel; side "t c b" pins the action panel to the BOTTOM
    ## (always visible) while the list well fills the space between.
    frame:
        background gui.panel_frame_fill
        foreground gui.panel_frame
        xsize gui.list_pane_w
        yfill True
        padding (gui.panel_frame_pad, gui.panel_frame_pad)
        side "t c b":
            spacing gui.pad_l

            ## TOP: title + the shared filter tabs.
            vbox:
                spacing gui.pad_l
                xfill True
                use section_header("Party Inventory")
                use tab_bar(BREACH_INV_TABS, tab,
                    lambda tab_key: [SetScreenVariable("tab", tab_key),
                                     SetScreenVariable("sel_item", None),
                                     SetVariable("breach_inv_error", None)])

            ## CENTRE: the recessed list well, filling the middle.
            frame:
                style "breach_well"
                xfill True
                yfill True
                viewport:
                    scrollbars "vertical"
                    mousewheel True
                    yfill True
                    xfill True
                    if breach_inv_rows:
                        vbox:
                            spacing gui.pad_s
                            xfill True
                            for iid in breach_inv_rows:
                                use item_card(iid, breach_item_record(iid),
                                    count=gs["inventory"][iid],
                                    action=[SetVariable("breach_inv_error", None),
                                            SetScreenVariable("sel_item", iid)],
                                    selected=(sel_item == iid),
                                    info=breach_item_info(iid))
                    else:
                        use breach_empty_state("Nothing in this category.",
                            sub="Loot and shop finds land here.")

            ## BOTTOM: the action panel for the selected item -- side keeps it
            ## pinned below the (filling) well, so the equip/use/discard buttons
            ## are always on-screen.
            vbox:
                xfill True
                if sel_item and gs["inventory"].get(sel_item, 0) > 0:
                    $ breach_sel_kind = binv.item_kind(REG, sel_item)
                    use breach_panel_lit():
                        vbox:
                            spacing gui.pad_m
                            xfill True
                            use section_header(breach_item_name(sel_item))
                            $ breach_sel_info = breach_item_info(sel_item)
                            if breach_sel_info:
                                text breach_lit(breach_sel_info):
                                    size gui.size_small
                                    color gui.muted_text_color

                            ## Equip options: one centralized validation, shown
                            ## verbatim (#15.4).
                            for eq_slot, eq_label in breach_equip_options(sel_item):
                                python:
                                    breach_eq_check = binv.validate_equip(
                                        REG, breach_inv_member, eq_slot, sel_item)
                                    if not breach_eq_check["ok"]:
                                        breach_eq_action = None
                                    elif breach_eq_check["confirm"]:
                                        # Two-Handed clears the offhand, with a
                                        # confirmation (#15.4 L1515)
                                        breach_eq_action = Confirm(
                                            "This weapon needs both hands — return %s to the inventory?"
                                            % breach_item_name(breach_inv_member["equipment"]["offhand"]),
                                            yes=Function(breach_equip_item,
                                                         breach_inv_member["id"],
                                                         eq_slot, sel_item))
                                    else:
                                        breach_eq_action = Function(
                                            breach_equip_item,
                                            breach_inv_member["id"],
                                            eq_slot, sel_item)
                                hbox:
                                    spacing gui.pad_m
                                    textbutton eq_label:
                                        style "breach_frame_button"
                                        xsize gui.split_list_w / 2
                                        sensitive breach_eq_check["ok"]
                                        action breach_eq_action
                                    if breach_eq_check["ok"]:
                                        $ breach_eq_delta = binv.equip_delta(REG, breach_inv_member, eq_slot, sel_item)
                                        if breach_eq_delta:
                                            ## the stat delta is secondary data -- micro caption tier.
                                            text breach_eq_delta:
                                                size gui.size_micro
                                                color gui.muted_text_color
                                                yalign 0.5
                                    else:
                                        text breach_eq_check["reason"]:
                                            size gui.size_small
                                            color gui.danger_color
                                            yalign 0.5

                            hbox:
                                spacing gui.pad_m
                                if breach_sel_kind == "consumable":
                                    textbutton "Use":
                                        style "breach_frame_button"
                                        action [SetVariable("breach_inv_error", None),
                                                SetScreenVariable("use_picker", True)]
                                if breach_sel_kind == "key_item":
                                    # quest items refuse discard (#15.4 L1519)
                                    text "Quest items cannot be discarded.":
                                        size gui.size_small
                                        color gui.muted_text_color
                                        yalign 0.5
                                else:
                                    textbutton "Discard":
                                        style "breach_frame_button"
                                        action Confirm(
                                            "Discard %s?" % breach_lit(breach_item_name(sel_item)),
                                            yes=Function(breach_discard_item, sel_item))

                            if breach_inv_error:
                                text breach_inv_error:
                                    size gui.size_small
                                    color gui.danger_color

                elif breach_inv_error:
                    text breach_inv_error:
                        size gui.size_small
                        color gui.danger_color


## Use-target picker (#15.4 L1518): the party members as portrait chips;
## works outside combat. One dark scrim sinks the screen behind it.
screen breach_inv_use_picker(sel_item, use_picker):
    if use_picker and sel_item and gs["inventory"].get(sel_item, 0) > 0:
        add Solid(gui.breach_scrim_color)
        dismiss action SetScreenVariable("use_picker", False)
        frame:
            background None
            align (0.5, 0.5)
            xsize gui.modal_w
            use breach_modal():
                vbox:
                    spacing gui.pad_l
                    xfill True
                    use section_header("Use " + breach_item_name(sel_item))
                    $ breach_use_info = breach_item_info(sel_item)
                    if breach_use_info:
                        text breach_lit(breach_use_info):
                            size gui.size_small
                            color gui.muted_text_color
                    text "CHOOSE A TARGET" style "breach_label_text"
                    hbox:
                        spacing gui.pad_m
                        for m in gs["party"]:
                            use portrait_chip(m, size=128,
                                action=[Function(breach_use_item, sel_item, m["id"]),
                                        SetScreenVariable("use_picker", False)],
                                show_hp=True)
                    textbutton "Cancel":
                        style "breach_frame_button"
                        xalign 1.0
                        action SetScreenVariable("use_picker", False)
