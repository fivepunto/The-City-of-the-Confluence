# game/hud.rpy -- the persistent two-state HUD overlay (GDD 15.1).
#
# The scene art owns the centre of the screen; the HUD lives framed and small
# at the edges. Two states (15.1): "city" everywhere in the city, and
# "expedition" out on the map, which adds the burning-resource widgets (the
# Supply Cache and the Breathers/bedroll readout) that exist ONLY there.
#
# Explicit 15.1 prohibitions, honoured here: NO gold on the HUD (gold lives in
# the inventory screen), and NO persistent quest tracker.
#
# Like quick_menu, the HUD is registered as a config overlay screen so it rides
# on top of whatever screen/label is showing. It is NON-modal: it overlays the
# called screen without stealing input, so the underlying location/map buttons
# keep working while its own buttons (Map / Menu / a party portrait) still fire.
#
# Return() contract (the glue label routes each of these):
#   ("hud", "map")            -- open the city map / expedition map
#   ("hud", "menu")           -- open the in-game menu / gear page
#   ("hud", "sheet", char_id) -- open that member's character sheet
# All four lanes of routing are the calling label's job; this file only raises
# the intent. The HUD is shown only while a game is running and a screen has
# explicitly turned it on (see hud_visible below).


# Whether the HUD draws at all, and which of the two 15.1 states it shows.
# A screen/label turns it on (hud_visible = True) and picks its state
# (hud_mode = "city" | "expedition"); the expedition state is a P3 stub the
# debug hub toggles (the real expedition is P4).
default hud_visible = False
default hud_mode = "city"


init python:
    # Mirror quick_menu: register the HUD as a config overlay so it rides on
    # top of the current screen without being explicitly shown.
    config.overlay_screens.append("hud")

    # The three day-phase positions for the "sun position" indicator (15.1):
    # ordered list so the accent dot can sit at the correct slot, plus the
    # short jargon-free label for each. Read straight off gs["day_phase"]
    # (one of morning | afternoon | evening, core.state.set_day_phase).
    BREACH_DAY_PHASES = [
        ("morning", "Morning"),
        ("afternoon", "Afternoon"),
        ("evening", "Evening"),
    ]


## The day-phase "sun position" indicator: three slots in a row, the current
## one lit with the accent dot and named (no jargon). Small edge chrome -- a
## raised band carrying micro data, the active slot the one lit thing.
screen hud_day_phase():
    $ hud_phase = gs["day_phase"]
    $ hud_phase_label = dict(BREACH_DAY_PHASES).get(hud_phase, hud_phase.capitalize())
    frame:
        style "breach_band"
        padding (gui.pad_m, gui.pad_s)
        vbox:
            spacing gui.pad_xs
            ## NO breach_lip here: the lip is a full-width (xsize 1.0) rule, and
            ## this band is content-sized edge chrome -- a lip would stretch it
            ## across the screen. Lips belong on full-width bands only.
            hbox:
                spacing gui.pad_m
                yalign 0.5
                ## micro caption tier: a quiet data label for the readout.
                text "PHASE" style "breach_label_text" yalign 0.5
                ## three sun positions; the active slot is the accent dot,
                ## the others sink to muted (inactive = sink).
                hbox:
                    spacing gui.pad_xs
                    yalign 0.5
                    for hud_p_key, hud_p_label in BREACH_DAY_PHASES:
                        ## A filled marker drawn as a Solid: the bullet glyph
                        ## "●" is absent from the UI font and renders as a
                        ## missing-glyph box, so the lit slot was invisible.
                        add Solid(gui.breach_accent_color if hud_p_key == hud_phase
                                  else gui.muted_text_color):
                            xysize (gui.size_micro, gui.size_micro)
                            yalign 0.5
                ## the lit current slot, raised to the small-caps label tier in
                ## the accent so it reads as the single focal point.
                text hud_phase_label.upper():
                    style "breach_label_text"
                    yalign 0.5
                    color gui.breach_accent_color


## The top-right cluster: day-phase chip, the city-map icon button, the
## menu/gear button. Shared by both HUD states (15.1). Small edge chrome, so
## it stays content-sized and anchored top-right. The informational day-phase
## chip and the action buttons read as two groups: a wider gap (pad_m) divides
## the data readout from the controls, the controls themselves sit at pad_s.
screen hud_top_right():
    hbox:
        xalign 1.0
        yalign 0.0
        xoffset -gui.pad_m
        yoffset gui.pad_m
        spacing gui.pad_m
        use hud_day_phase()
        ## the action group -- framed bevelled chrome (idle / hover / selected /
        ## disabled), with a left icon slot for the map / menu glyphs when real
        ## art lands (label stays the text child; no code change needed).
        hbox:
            spacing gui.pad_s
            yalign 0.5
            textbutton "Map":
                style "breach_frame_button"
                yalign 0.5
                action Return(("hud", "map"))
            textbutton "Menu":
                style "breach_frame_button"
                yalign 0.5
                action Return(("hud", "menu"))


## The bottom-left party portrait strip: one small portrait chip per member,
## the level-up + badge when that member can level up, click opens the sheet
## (15.1; the glue routes ("hud","sheet",id)). Drawn only if there is a party.
## The strip rides a small raised band (content-sized edge chrome) -- no
## full-width lip (it would stretch the band across the whole screen bottom).
screen hud_party_strip():
    if gs["party"]:
        $ hud_leader_id = gs["party"][0]["id"]
        frame:
            style "breach_band"
            xalign 0.0
            yalign 1.0
            xoffset gui.pad_m
            yoffset -gui.pad_m
            padding (gui.pad_m, gui.pad_s)
            vbox:
                spacing gui.pad_xs
                ## a quiet caption so the strip reads as a labelled group.
                text "PARTY" style "breach_label_text"
                hbox:
                    spacing gui.pad_m
                    for m in gs["party"]:
                        ## the protagonist (the dialogue actor) carries the
                        ## focal accent ring; followers stay quiet. Visual only
                        ## -- the action, badge, and party order are untouched.
                        use portrait_chip(m, size=96, show_hp=True,
                            selected=(m["id"] == hud_leader_id),
                            badge=bch.can_level_up(REG, m),
                            action=Return(("hud", "sheet", m["id"])))


## The expedition-only burning-resource widgets (15.1): the Supply Cache
## counter and the bedroll / Breathers readout. These appear ONLY in the
## expedition state -- never in the city. Placed top-CENTRE so they clear the
## top-left expedition-map title, the top-right cluster, and the party strip.
## Small raised content-sized chrome (no full-width lip); the readouts are
## quiet micro data, the burning supply tinted with lamplight, bedroll muted.
screen hud_expedition_resources():
    frame:
        style "breach_band"
        xalign 0.5
        yalign 0.0
        yoffset gui.pad_m
        padding (gui.pad_m, gui.pad_s)
        vbox:
            spacing gui.pad_xs
            hbox:
                spacing gui.pad_l
                yalign 0.5
                ## the burning supply cache and the bedroll / Breathers count,
                ## rebuilt as the shared resource widget (small-caps label +
                ## lit-vs-dim pips + count) so they read as real readouts. Same
                ## computed current/max -- the core/data calls are untouched.
                $ hud_supplies = gs.get("supplies", 0)
                $ hud_supply_cap = brest.supply_capacity(REG, gs)
                use breach_resource("Supply", hud_supplies, hud_supply_cap)
                ## a thin vertical divider between the two readouts.
                add Solid(gui.panel_border_color) xsize gui.hairline ysize gui.size_base yalign 0.5
                $ hud_breathers = brest.breathers_remaining(REG, gs, gs["party"])
                $ hud_breather_max = brest.breather_max(REG, gs["party"])
                use breach_resource("Breathers", hud_breathers, hud_breather_max)


## The HUD proper. Renders NOTHING unless a game is running and a screen has
## turned it on. Non-modal so it overlays the called screen and leaves its
## input alone; its own buttons still fire. zorder ~80 (under quick_menu's
## 100, above ordinary screens).
screen hud():
    zorder 80

    if hud_visible and gs is not None:

        ## Shared in both states: the top-right cluster and the party strip.
        use hud_top_right()
        use hud_party_strip()

        ## Expedition state adds the burning-resource widgets (15.1). This
        ## state is a P3 stub toggled by the debug hub; the real expedition
        ## map and recharges are P4.
        if hud_mode == "expedition":
            use hud_expedition_resources()
