# The ONE generic, data-driven location / hotspot screen (GDD #13 L1399-1400,
# #13.2 L1395-1402). Never a per-district hand-built screen: every district's
# sub-location renders from REG["locations"] + REG["hotspots"], and the screen
# RETURNS an intent for the city_free_mode glue to dispatch -- it never
# navigates itself (so doors, vendors, people, and the way out are all data).
#
# Background art is the placeholder-art pipeline (colored rect + the location's
# name label); real backgrounds drop in by changing the data, not this screen.

init python:

    # A hotspot is shown only when it has no gate flag, or that flag is set in
    # the live game state (#13.2 L1399-1400). gs may be None before a game
    # starts -- guard, then treat a missing flag bag as "nothing set yet".
    def breach_hotspot_visible(h):
        flag = h.get("visible_flag")
        if not flag:
            return True
        if gs is None:
            return False
        return bool(gs.get("flags", {}).get(flag))

    # One hotspot's resolved intent, BY KIND (the city_free_mode glue
    # dispatches the tuple; this screen decides nothing else). Faithful to the
    # data contract in data/locations.py:
    #   shop      -> ("shop", shop_id)        open a vendor
    #   character -> ("dialogue", label_name) talk to a person
    #   location  -> ("goto", location_id)    a door to another sub-location
    #   exit      -> ("exit", None)           leave back to the city map
    def breach_hotspot_intent(h):
        kind = h["kind"]
        if kind == "shop":
            return ("shop", h["target"])
        if kind == "character":
            return ("dialogue", h["target"])
        if kind == "location":
            return ("goto", h["target"])
        if kind == "exit":
            return ("exit", None)
        if kind == "questboard":
            return ("questboard", None)
        # An unknown kind is a data error; refuse rather than guess (#13.2).
        return None


## One hotspot plate: a structured node the eye can find on the location's
## scene. It rides the shared bronze button frame (style "breach_frame_button")
## so it carries the kit's framed states for free -- idle bronze frame at rest,
## the amber-edge + soft-glow lit frame on hover/focus (the one reliable "this
## is the spot under your hand" signal, the same focal language as the lane
## plates and the map nodes). Inside, the plate reads as a card with hierarchy:
## the label (title) over a kind tag (SHOP / PERSON / DOOR / OUT) in the
## small-caps caption tier, so the four hotspot kinds are distinguishable
## rather than identical coloured blocks. An unknown-kind plate is
## non-clickable and sinks (desaturated, dimmed). Clicking RETURNS the intent.
##
## The authored 240x120 footprint + absolute pos() are the load-bearing canvas
## contract (data/locations.py coordinates) -- kept exactly; only the interior
## is restyled. (The button frame's own paddings clear its border art, so
## labels never touch the bronze edge.)

init python:
    # The player-facing kind tag for a hotspot card's caption -- a short, warm,
    # jargon-free word per kind (GDD 15.0 voice). Presentation only; derived
    # from the same h["kind"] the intent reads, never altering the intent.
    BREACH_HOTSPOT_KIND_TAGS = {
        "shop": "Shop",
        "character": "Person",
        "location": "Door",
        "questboard": "Board",
        "exit": "Out",
    }

screen location_hotspot(hid, h):
    # An unknown hotspot kind yields None; make that plate non-clickable
    # rather than returning None (the glue reads a None return as "leave").
    $ lh_intent = breach_hotspot_intent(h)
    $ lh_ok = (lh_intent is not None)
    $ lh_tag = BREACH_HOTSPOT_KIND_TAGS.get(h["kind"], "")
    button:
        style "breach_frame_button"
        pos (h["pos"][0], h["pos"][1])
        xsize gui.expedition_node_w
        ysize gui.expedition_node_h
        sensitive lh_ok
        action (Return(lh_intent) if lh_ok else NullAction())
        if not lh_ok:
            at breach_desaturate
        vbox:
            spacing gui.pad_xs
            yalign 0.5
            text breach_lit(h["label"]):
                size gui.size_base
                color (gui.breach_text_color if lh_ok else gui.muted_text_color)
            if lh_tag:
                text lh_tag.upper():
                    size gui.size_micro
                    color gui.muted_text_color
                    kerning gui.kerning_label


## The location screen proper. Modal: it owns the screen while up, but the
## top-right HUD overlay may still fire and Return ("hud", ...) over it -- the
## city_free_mode glue handles either return, so this screen just surfaces the
## location's hotspots and gets out of the way.

screen location_screen(loc_id):
    modal True

    $ loc = REG["locations"][loc_id]
    $ loc_district = REG["districts"].get(loc["district"])
    $ loc_district_name = loc_district["name"] if loc_district else ""

    ## Background: placeholder art -- a colored rect keyed by the location
    ## (real backgrounds replace this by editing bg_placeholder_key -> art,
    ## never this screen, #13 L1399). The name lives in the top-left panel
    ## below; no centred watermark (it collided with the hotspot plates).
    add Solid(breach_placeholder_color(loc["bg_placeholder_key"]))

    ## Title area: top-left, clear of the top-right HUD (the location is reached
    ## FROM a district on the city map, so the district reads as a breadcrumb
    ## caption above the sub-location name). Same header family as the city map:
    ## a quiet breadcrumb caption, an accent hairline rule, then the location
    ## name on the display (serif) tier as the focal -- the breach_panel border
    ## is its chrome. The rule + content vbox bound to the text width (the panel
    ## is content-sized), so this stays a small top-left card and never stretches
    ## across the screen into the HUD.
    frame:
        xpos gui.screen_pad
        ypos gui.screen_pad
        background None
        use breach_panel():
            vbox:
                spacing gui.pad_s
                if loc_district_name:
                    text breach_lit(loc_district_name).upper():
                        style "breach_label_text"
                text breach_lit(loc["name"]):
                    style "breach_header_text"
                    size gui.size_title

    ## The hotspots: one placeholder button each, at its authored canvas
    ## position. A flag-gated hotspot is skipped until its flag is set.
    for hid in loc["hotspots"]:
        $ loc_h = REG["hotspots"][hid]
        if breach_hotspot_visible(loc_h):
            use location_hotspot(hid, loc_h)
