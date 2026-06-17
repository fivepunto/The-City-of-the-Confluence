# Camp scene + the rest economy flow (GDD #12.4 six verbs; #12.2 economy).
# camp_mode is the wilds campsite (Talk / Breather / Hunt / Manage / Sleep /
# Leave); Sleep resolves the hunt, burns a Supply Cache (unless the hunt
# spared it), and commits the long rest. inn_sleep is the trivial city case
# (10 gold, no expedition machinery, #12.4 L1381).
#
# Owner content (GAPS G-046): the Talk banter, the sleep/Breather beats, and
# region/campsite names are bracketed placeholders rendered through breach_lit.

default camp_hunter = None
default camp_slept = False


init python:

    BREACH_DAY_LABEL = {"morning": "Morning", "afternoon": "Afternoon",
                        "evening": "Evening"}

    def breach_buy_supply():
        """Buy one Supply Cache (#14.2/#14.3, ~50 gold), hard-capped at the
        derived carry capacity (3, or 4 with the Pack-Frame)."""
        price = REG["economy"]["supply_cache_price"]["value"]
        cap = brest.supply_capacity(REG, gs)
        if gs["gold"] < price:
            breach_toast("Not enough gold.")
            return
        try:
            bstate.add_supplies(gs, 1, cap=cap)
        except ValueError:
            breach_toast("Supply Cache capacity is full.")
            return
        bstate.spend_gold(gs, price)
        renpy.block_rollback()                     # committed purchase (#16.1)
        breach_toast("Bought 1 Supply Cache.")

    def breach_buy_upgrade(upgrade_id):
        """One-time camp-upgrade purchase (#14.3): spend gold, flag it owned."""
        up = REG["camp_upgrades"][upgrade_id]
        if upgrade_id in gs.get("camp_upgrades", []):
            breach_toast("Upgrade already owned.")
            return
        try:
            bstate.spend_gold(gs, up["price"])
            gs["camp_upgrades"].append(upgrade_id)
            renpy.block_rollback()                 # committed purchase (#16.1)
            breach_toast("Purchased %s." % up["name"])
        except ValueError:
            breach_toast("Not enough gold.")


## The camp scene (#12.4): the party round the fire, the day/Supply/Breather
## readout, and the six verbs.

screen camp_scene():
    modal True
    add Solid(breach_placeholder_color("campsite"))

    $ camp_phase = BREACH_DAY_LABEL.get(gs.get("day_phase", "morning"), "Morning")
    $ camp_breathers = brest.breathers_remaining(REG, gs, gs["party"])
    $ camp_breather_max = brest.breather_max(REG, gs["party"])
    $ camp_cap = brest.supply_capacity(REG, gs)

    $ camp_supplies = gs["supplies"]

    vbox:
        xfill True
        yfill True

        ## Header band: the camp's chrome -- title left, the burning-resource
        ## readout (#15.1: day phase, Supply, Breathers) right. Supply and
        ## Breathers are small discrete pools, so they ride the shared
        ## breach_resource pip gauge; the day phase is an instrument cell.
        ## Raised over the campsite ground with a lamplit lip beneath.
        frame:
            style "breach_band"
            xfill True
            padding (gui.pad_l, gui.pad_m)
            hbox:
                xfill True
                yalign 0.5
                use breach_title("Camp")
                hbox:
                    xalign 1.0
                    yalign 0.5
                    spacing gui.pad_l
                    use breach_stat_cell("Time of day", camp_phase, gui.breach_accent_color)
                    use breach_resource("Supply", camp_supplies, camp_cap)
                    use breach_resource("Breathers", camp_breathers, camp_breather_max)
        use breach_lip(gui.breach_accent_color)

        frame:
            background None
            xfill True
            yfill True
            padding (gui.screen_pad, gui.screen_pad)
            vbox:
                spacing gui.pad_l
                xfill True

                ## The party gathered round the fire -- sunk onto a recessed
                ## ground so they read as gathered rather than floating.
                use section_header("Your party")
                frame:
                    style "breach_well"
                    xfill True
                    hbox:
                        spacing gui.pad_m
                        for camp_m in gs["party"]:
                            use portrait_chip(camp_m, size=128, show_hp=True)

                ## The six verbs, framed on a deliberate grid: restorative and
                ## management verbs grouped, Sleep promoted as the single lit
                ## focal action (it ends the Camp), and Leave camp held apart as
                ## the exit. The Breather goes insensitive ("lamplight burning
                ## low") when none remain. Every Return() payload is unchanged.
                use section_header("Camp")
                $ camp_breather_spent = (camp_breathers <= 0)
                vbox:
                    spacing gui.pad_m
                    xfill True
                    hbox:
                        spacing gui.pad_m
                        textbutton "Talk" style "breach_frame_button" tooltip "Speak with party members at camp." action Return("talk")
                        textbutton "Breather  (%d/%d)" % (camp_breathers, camp_breather_max):
                            style "breach_frame_button"
                            sensitive (not camp_breather_spent)
                            tooltip ("Spend a Breather to recover short-rest resources and optionally spend Recovery Dice."
                                     if not camp_breather_spent
                                     else "No Breathers remain until the party sleeps at Camp.")
                            action Return("breather")
                        textbutton "Hunt" style "breach_frame_button" tooltip "Assign a hunter. On success, this Camp does not spend a Supply Cache." action Return("hunt")
                        textbutton "Manage" style "breach_frame_button" tooltip "Open camp management, supplies, upgrades, inventory, and character sheets." action Return("manage")
                    hbox:
                        spacing gui.pad_l
                        ## Sleep is the focal verb -- the selected/lit frame.
                        textbutton "Sleep" style "breach_frame_button" selected True tooltip "End the Camp, restore long-rest resources, and advance the day." action Return("sleep")
                        null:
                            xfill True
                        textbutton "Leave Camp" style "breach_frame_button" tooltip "Return without sleeping." action Return("leave")

                ## The assigned-hunter state reads at a glance as an amber tag,
                ## not a stray sentence at the foot of the screen.
                if camp_hunter:
                    $ camp_h = bstate.party_member(gs, camp_hunter)
                    use breach_tag("Sending " + camp_h["name"] + " to hunt")


## Hunt picker (#12.4 L1371-1372): each member's Awareness modifier, the
## Ranger's advantage marked. Returns the chosen char id (or None).

screen camp_hunt_picker():
    modal True
    add Solid(gui.breach_scrim_color)
    frame:
        align (0.5, 0.5)
        background None
        use breach_panel():
            vbox:
                spacing gui.pad_l
                xsize gui.modal_w
                use section_header("Who hunts?")
                text "The hunter misses the fireside this Camp.":
                    size gui.size_micro
                    color gui.muted_text_color
                ## The candidate roster sits on the recessed well as framed list
                ## rows; choosing a member sends them. The Ranger's advantage is
                ## the single lit focal row (selected = amber-edge frame).
                frame:
                    style "breach_well"
                    xfill True
                    vbox:
                        spacing gui.pad_s
                        xfill True
                        for hp_m in gs["party"]:
                            $ hp_mod = bch.skill_mod(REG, hp_m, "awareness")
                            $ hp_ranger = (hp_m["class"] == "ranger" and REG["economy"]["hunting_ranger_advantage"]["value"])
                            use camp_hunt_row(hp_m, hp_mod, hp_ranger)
                hbox:
                    xalign 1.0
                    spacing gui.pad_m
                    textbutton "No one" style "breach_frame_button" action Return(None)
                    textbutton "Cancel" style "breach_frame_button" action Return("__cancel__")


## One candidate row inside the hunt picker: the framed list row carries the
## name (title), the Awareness modifier (right-meta, accent-tinted on the
## Ranger's advantage), and the whole row is the Send action. The Ranger's
## advantage row reads as the lit focal (selected frame).

screen camp_hunt_row(hp_m, hp_mod, hp_ranger):
    $ hp_meta = "Awareness %+d%s" % (hp_mod, "  (advantage)" if hp_ranger else "")
    use breach_list_row(
        hp_m["name"],
        meta=hp_meta,
        icon_key=hp_m["class"],
        action=Return(hp_m["id"]),
        selected=hp_ranger,
        meta_color=(gui.breach_accent_color if hp_ranger else None),
    )


## Camp-upgrade purchases (#14.3): the three one-time sinks.

screen camp_upgrade_shop():
    modal True
    add Solid(gui.bg_color)

    $ camp_gold = gs["gold"]

    vbox:
        xfill True
        yfill True

        ## Header band: title left, the gold readout right on the SAME figure
        ## scale as camp_scene (the shared instrument cell), then Close. Raised
        ## over the ground with a lamplit lip beneath.
        frame:
            style "breach_band"
            xfill True
            padding (gui.pad_l, gui.pad_m)
            hbox:
                xfill True
                yalign 0.5
                use breach_title("Camp Outfitter")
                hbox:
                    xalign 1.0
                    yalign 0.5
                    spacing gui.pad_l
                    use breach_stat_cell("Gold", camp_gold, gui.breach_accent_color)
                    textbutton "Close" style "breach_frame_button" yalign 0.5 action Return(None)
        use breach_lip(gui.breach_accent_color)

        frame:
            background None
            xfill True
            yfill True
            padding (gui.screen_pad, gui.screen_pad)

            ## The sinks sit on the recessed well as framed list rows.
            frame:
                style "breach_well"
                xfill True
                yfill True

                ## Live purchasability, computed each render.
                $ sup_price = REG["economy"]["supply_cache_price"]["value"]
                $ sup_cap = brest.supply_capacity(REG, gs)
                $ sup_have = gs["supplies"]
                $ sup_buyable = (gs["gold"] >= sup_price and sup_have < sup_cap)
                $ camp_all_owned = all(uid in gs.get("camp_upgrades", []) for uid in REG["camp_upgrades"])

                ## Nothing left to buy -- a designed empty state rather than a
                ## stack of dimmed rows alone.
                if camp_all_owned and not sup_buyable:
                    use breach_empty_state(
                        "The outfitter has nothing more for you.",
                        "Every camp upgrade is owned and your Supply Caches are full.")
                else:
                    vbox:
                        spacing gui.pad_s
                        xfill True

                        ## The recurring Supply Cache buy (#14.2/#14.3), capped
                        ## at the derived carry capacity -- the single lit focal
                        ## row while you can still buy one.
                        use camp_supply_row(sup_price, sup_have, sup_cap, sup_buyable)

                        for up_id in REG["camp_upgrades"]:
                            $ up = REG["camp_upgrades"][up_id]
                            $ up_owned = (up_id in gs.get("camp_upgrades", []))
                            use camp_upgrade_row(up_id, up, up_owned)


## One Supply Cache row: a framed list row -- name + provisions/carry subtitle,
## the price as right-meta, the whole row the capped Buy action. Lit (selected
## frame) while buyable -- the shop's single focal row.

screen camp_supply_row(sup_price, sup_have, sup_cap, sup_buyable):
    button:
        style "breach_frame_row"
        sensitive sup_buyable
        selected sup_buyable
        action Function(breach_buy_supply)
        hbox:
            spacing gui.pad_m
            xfill True
            yalign 0.5
            add Solid(breach_placeholder_color("supply_cache")) xsize gui.card_thumb_size ysize gui.card_thumb_size yalign 0.5
            vbox:
                spacing gui.pad_xs
                yalign 0.5
                text "Supply Cache" size gui.size_base color gui.breach_text_color
                text "Provisions for one wilderness Camp.  ([sup_have]/[sup_cap] carried)":
                    size gui.size_micro
                    color gui.muted_text_color
            null:
                xfill True
            text ("%s gold" % sup_price):
                size gui.size_small
                color gui.breach_accent_color
                yalign 0.5
                xmaximum gui.row_meta_w
                text_align 1.0
                xalign 1.0


## One camp-upgrade row: a framed list row -- name + effect subtitle, the price
## as right-meta. Buyable rows are the whole-row Buy action; owned rows are a
## designed sunk/locked state (desaturated, insensitive, an Owned tag chip).

screen camp_upgrade_row(up_id, up, up_owned):
    $ up_price = up["price"]
    if up_owned:
        ## Owned: a deliberately dimmed, locked row -- a non-button framed
        ## displayable (per the contract: the owned branch is never a button),
        ## with a quiet success-tinted Owned tag in the meta column.
        frame:
            style "breach_frame_row"
            at breach_desaturate
            hbox:
                spacing gui.pad_m
                xfill True
                yalign 0.5
                add Solid(breach_placeholder_color(up_id)) xsize gui.card_thumb_size ysize gui.card_thumb_size yalign 0.5
                vbox:
                    spacing gui.pad_xs
                    yalign 0.5
                    text breach_lit(up["name"]) size gui.size_base color gui.breach_text_color
                    text breach_lit(up["effect"]) size gui.size_micro color gui.muted_text_color
                null:
                    xfill True
                use breach_tag("Owned", gui.success_color)
    else:
        button:
            style "breach_frame_row"
            sensitive (gs["gold"] >= up["price"])
            action Function(breach_buy_upgrade, up_id)
            hbox:
                spacing gui.pad_m
                xfill True
                yalign 0.5
                add Solid(breach_placeholder_color(up_id)) xsize gui.card_thumb_size ysize gui.card_thumb_size yalign 0.5
                vbox:
                    spacing gui.pad_xs
                    yalign 0.5
                    text breach_lit(up["name"]) size gui.size_base color gui.breach_text_color
                    text breach_lit(up["effect"]) size gui.size_micro color gui.muted_text_color
                null:
                    xfill True
                text ("%s gold" % up_price):
                    size gui.size_small
                    color gui.breach_accent_color
                    yalign 0.5
                    xmaximum gui.row_meta_w
                    text_align 1.0
                    xalign 1.0


## A small Manage hub (#12.4: equipment + the sheet; spell preparation and
## the follower lineup extend this later -- followers are P5).

screen camp_manage_menu():
    modal True
    add Solid(gui.breach_scrim_color)
    frame:
        align (0.5, 0.5)
        background None
        use breach_panel():
            vbox:
                spacing gui.pad_l
                xsize gui.panel_w_narrow
                use section_header("Manage")
                ## The three navigation items, framed to match the camp verbs.
                vbox:
                    spacing gui.pad_s
                    xfill True
                    textbutton "Inventory & Equipment" style "breach_frame_button" xfill True action Return("inventory")
                    textbutton "Character Sheet" style "breach_frame_button" xfill True action Return("sheet")
                    textbutton "Camp Outfitter" style "breach_frame_button" xfill True action Return("upgrades")
                ## A hairline rule sets the exit apart from the navigation.
                use breach_lip(gui.panel_border_color)
                textbutton "Back" style "breach_frame_button" xfill True action Return(None)


## ---------------------------------------------------------------------------
## Camp flow.
## ---------------------------------------------------------------------------

label camp_mode:
    $ store.camp_hunter = None
    $ store.camp_slept = False
    jump camp_scene_loop


label camp_scene_loop:
    call screen camp_scene
    $ _cv = _return
    if _cv == "leave":
        return
    elif _cv == "talk":
        call camp_talk
    elif _cv == "breather":
        call expedition_breather          # the Breather works at camp too
    elif _cv == "hunt":
        call screen camp_hunt_picker
        if _return != "__cancel__":
            $ store.camp_hunter = _return
    elif _cv == "manage":
        call camp_manage
    elif _cv == "sleep":
        call camp_sleep
        if store.camp_slept:
            return
    jump camp_scene_loop


label camp_talk:
    # Deep follower scenes / pair banter are owner content (#12.4 L1365-1368).
    "[[Camp banter — TO BE WRITTEN BY THE PROJECT OWNER]"
    return


label camp_manage:
    call screen camp_manage_menu
    $ _mm = _return
    if _mm == "inventory":
        call screen inventory_screen
    elif _mm == "sheet":
        call screen character_sheet
        if isinstance(_return, (tuple, list)) and len(_return) >= 2 and _return[0] == "levelup":
            call levelup_wizard(_return[1])
    elif _mm == "upgrades":
        call screen camp_upgrade_shop
    return


## Sleep commits the rest (#12.4 L1377-1378): the hunt resolves, the Supply
## burns unless the hunt spared it, and morning comes. A wilds Camp needs a
## Supply Cache (or a successful hunt) -- without one you cannot Camp here.
label camp_sleep:
    $ store.camp_slept = False
    $ _camp_saved = False

    # Resolve the hunt first -- success spares the Supply (#12.2 L1346-1349).
    if store.camp_hunter:
        $ _hunter = bstate.party_member(gs, store.camp_hunter)
        $ _region = REG["regions"].get(gs.get("breach_region"))
        if _region:
            $ _ranger_adv = (_hunter["class"] == "ranger" and REG["economy"]["hunting_ranger_advantage"]["value"])
            $ _hunt = brest.resolve_hunt(REG, _hunter, _region, _ranger_adv)
            $ renpy.block_rollback()      # the hunt roll is committed (#16.1)
            if _hunt["success"]:
                $ _camp_saved = True
                # Cook's Kit (#14.3): each member heals their own level on a
                # successful hunt. (Redundant with the long rest's full HP
                # restore below -- see GAPS G-049 -- but applied per the text.)
                if "cooks_kit" in gs.get("camp_upgrades", []):
                    python:
                        for _pm in gs["party"]:
                            _pm["hp"] = min(_pm["hp"] + _pm["level"], _pm["hp_max"])
                $ breach_toast("Hunt succeeded. No Supply Cache spent.")
            else:
                $ breach_toast("Hunt failed. A Supply Cache will be spent.")

    # Burn a Supply Cache unless the hunt spared it (#12.2 L1342).
    if not _camp_saved:
        if gs.get("supplies", 0) < 1:
            $ breach_toast("No Supply Cache available. You cannot Camp here.")
            return
        $ bstate.spend_supplies(gs, 1)

    $ brest.do_sleep(REG, gs, gs["party"])
    $ renpy.block_rollback()              # the long rest is committed (#16.1)
    $ store.camp_slept = True
    # The fireside / sleep beat is owner content (#12.4).
    "[[You make camp and rest until morning. — TO BE WRITTEN BY THE PROJECT OWNER]"
    return


## The city inn (#12.2 L1340-1341, #12.4 L1381): 10 gold, full rest, no Supply
## and none of the expedition machinery.
label inn_sleep:
    $ _inn_cost = REG["economy"]["inn_rest_cost"]["value"]
    if gs["gold"] < _inn_cost:
        $ breach_toast("Not enough gold for the inn.")
    else:
        $ bstate.spend_gold(gs, _inn_cost)
        $ brest.do_sleep(REG, gs, gs["party"])
        $ renpy.block_rollback()          # committed rest + spend (#16.1)
        "[[You take a room at the inn and rest. — TO BE WRITTEN BY THE PROJECT OWNER]"
    return
