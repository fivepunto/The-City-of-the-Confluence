# -*- coding: utf-8 -*-
"""City districts, locations, and hotspots (GDD #13.2 L1395-1402 navigation;
#13 L1399-1400 hotspots). DATA only -- the city map (screen city_map) and the
ONE generic location screen (screen location_screen) read these tables; no
per-district screen is ever hand-built.

OWNER CONTENT (GAPS G-038): which districts exist and which are reachable at
Free Mode start is "[TO BE SPECIFIED BY THE PROJECT OWNER]" (#13.2 L1398,
#17.2 L1741). The #17.1 flavour names (Gutter Market, Sunward House,
Guildhall) are setting prose, NOT a confirmed list, so nothing is transcribed.
Until the owner names them, the SYSTEM ships against bracketed-placeholder
districts ('[District A]'...) -- placeholder names are deliberately NOT added
to the doc-integrity name check (they cannot match a gdd line).

Hotspot contract (the location screen dispatches on `kind`, faithful to
#13.2's "sub-locations, characters, doors"):
  kind "location"  -> target = a location id (a door to another sub-location)
  kind "character" -> target = a dialogue label name (a person to talk to)
  kind "shop"      -> target = a shop id (a vendor door)
  kind "exit"      -> target = None (leave the district back to the city map)
`pos` is an (x, y) placement on the 1920x1080 canvas; `visible_flag`, when
set, names a state flag that must be truthy for the hotspot to show.
"""

DISTRICTS = {
    # The first NON-placeholder district (owner content, confirmed by the
    # owner + already canon in the prologue, #17.2). It leads the city map
    # ahead of the bracketed placeholders, and is where Free Mode opens the
    # first time (see label city_free_mode). Its one location is the Guild
    # Hall, reachable again from the map button at any time. (src: prologue
    # registration beat; confirm the canonical citation.)
    "district_guildhall": {
        "id": "district_guildhall",
        "name": "Lamplighter Guildhall",
        "available": True,               # on the map, alongside A and B
        "entry": "loc_guildhall",
        "locations": ["loc_guildhall"],
        "src": "§17.2 L1741",
    },
    "district_a": {
        "id": "district_a",
        "name": "[District A]",          # owner-authored (G-038)
        "available": True,               # reachable at Free Mode start
        "entry": "loc_a1",               # first location on entry
        "locations": ["loc_a1", "loc_a2"],
        "src": "§13.2 L1396-1398",
    },
    "district_b": {
        "id": "district_b",
        "name": "[District B]",          # owner-authored (G-038)
        "available": True,
        "entry": "loc_b1",
        "locations": ["loc_b1"],
        "src": "§13.2 L1396-1398",
    },
    "district_c": {
        "id": "district_c",
        "name": "[District C]",          # owner-authored (G-038)
        "available": False,              # locked: absent from the map, never greyed
        "entry": None,
        "locations": [],
        "src": "§13.2 L1396-1398",
    },
}

LOCATIONS = {
    # The Lamplighter Guild Hall interior -- the first real sub-location. Named
    # "Guild Hall" so the map breadcrumb reads "LAMPLIGHTER GUILDHALL / Guild
    # Hall" rather than doubling. Background is still the placeholder-art
    # pipeline (no guildhall art exists). Only Imara is here for now.
    "loc_guildhall": {
        "id": "loc_guildhall",
        "district": "district_guildhall",
        "name": "Guild Hall",
        "bg_placeholder_key": "loc_guildhall",
        "hotspots": ["hs_guildhall_imara"],
        "src": "§17.2 L1741",
    },
    "loc_a1": {
        "id": "loc_a1",
        "district": "district_a",
        "name": "[Location A1]",         # owner-authored (G-038)
        "bg_placeholder_key": "loc_a1",  # placeholder-art pipeline key
        "hotspots": ["hs_a1_shop", "hs_a1_npc", "hs_a1_door", "hs_a1_exit"],
        "src": "§13 L1399-1400",
    },
    "loc_a2": {
        "id": "loc_a2",
        "district": "district_a",
        "name": "[Location A2]",
        "bg_placeholder_key": "loc_a2",
        "hotspots": ["hs_a2_npc", "hs_a2_back"],
        "src": "§13 L1399-1400",
    },
    "loc_b1": {
        "id": "loc_b1",
        "district": "district_b",
        "name": "[Location B1]",
        "bg_placeholder_key": "loc_b1",
        "hotspots": ["hs_b1_npc", "hs_b1_exit"],
        "src": "§13 L1399-1400",
    },
}

HOTSPOTS = {
    # --- Lamplighter Guildhall, Guild Hall ---
    # Imara, the guild receptionist (owner canon, #17.2). The ONLY hotspot in
    # the hall for now -- the player leaves via the HUD map button, not an exit
    # plate. Clicking her runs the conversational dialogue hub (dialogue.rpy).
    "hs_guildhall_imara": {
        "id": "hs_guildhall_imara",
        "label": "Imara",
        "kind": "character",
        "target": "dlg_imara",          # -> dialogue label in dialogue.rpy
        "pos": (900, 520),
        "visible_flag": None,
        "src": "§17.2 L1727-1736",
    },
    # --- District A, Location 1 ---
    "hs_a1_shop": {
        "id": "hs_a1_shop",
        "label": "[Shop]",              # owner-authored (G-038)
        "kind": "shop",
        "target": "general_store",      # -> data/shop.py SHOPS
        "pos": (380, 420),
        "visible_flag": None,
        "src": "§13 L1399-1400",
    },
    "hs_a1_npc": {
        "id": "hs_a1_npc",
        "label": "[Townsperson]",
        "kind": "character",
        "target": "dlg_townsperson",    # -> dialogue label in dialogue.rpy
        "pos": (900, 520),
        "visible_flag": None,
        "src": "§13 L1399-1400",
    },
    "hs_a1_door": {
        "id": "hs_a1_door",
        "label": "[Back Alley]",
        "kind": "location",
        "target": "loc_a2",             # door to another sub-location
        "pos": (1420, 420),
        "visible_flag": None,
        "src": "§13 L1399-1400",
    },
    "hs_a1_exit": {
        "id": "hs_a1_exit",
        "label": "Leave",
        "kind": "exit",
        "target": None,
        "pos": (960, 880),
        "visible_flag": None,
        "src": "§13.2 L1396",
    },
    # --- District A, Location 2 ---
    "hs_a2_npc": {
        "id": "hs_a2_npc",
        "label": "[Merchant]",
        "kind": "character",
        "target": "dlg_merchant",
        "pos": (700, 480),
        "visible_flag": None,
        "src": "§13 L1399-1400",
    },
    "hs_a2_back": {
        "id": "hs_a2_back",
        "label": "[Main Street]",
        "kind": "location",
        "target": "loc_a1",
        "pos": (1200, 480),
        "visible_flag": None,
        "src": "§13 L1399-1400",
    },
    # --- District B, Location 1 ---
    "hs_b1_npc": {
        "id": "hs_b1_npc",
        "label": "[Quest Giver]",
        "kind": "character",
        "target": "dlg_questgiver",
        "pos": (760, 500),
        "visible_flag": None,
        "src": "§13 L1399-1400",
    },
    "hs_b1_exit": {
        "id": "hs_b1_exit",
        "label": "Leave",
        "kind": "exit",
        "target": None,
        "pos": (960, 880),
        "visible_flag": None,
        "src": "§13.2 L1396",
    },
}
