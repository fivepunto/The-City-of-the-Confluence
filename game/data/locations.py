# -*- coding: utf-8 -*-
"""City districts, locations, and hotspots (GDD #13.2 L1395-1402 navigation;
#13 L1399-1400 hotspots). DATA only -- the city map (screen city_map) and the
ONE generic location screen (screen location_screen) read these tables; no
per-district screen is ever hand-built.

OWNER CONTENT (GAPS G-038): the city's districts and sub-locations are owner
content, authored here as data as the owner names them. The only district that
exists so far is the owner-canon Lamplighter Guildhall (#17.2); the earlier
bracketed-placeholder districts (A/B/C) and their locations/hotspots were
removed. Add new districts/locations/hotspots to the three tables below.

Hotspot contract (the location screen dispatches on `kind`, faithful to
#13.2's "sub-locations, characters, doors"):
  kind "location"   -> target = a location id (a door to another sub-location)
  kind "character"  -> target = a dialogue label name (a person to talk to)
  kind "shop"       -> target = a shop id (a vendor door)
  kind "questboard" -> target = None (opens the Guild notice board screen)
  kind "exit"       -> target = None (leave the district back to the city map)
`pos` is an (x, y) placement on the 1920x1080 canvas; `visible_flag`, when
set, names a state flag that must be truthy for the hotspot to show.
"""

DISTRICTS = {
    # The first NON-placeholder district (owner content, confirmed by the owner
    # and already canon in the prologue, #17.2). Free Mode opens here -- its one
    # location is the Guild Hall -- and the player can return any time via the
    # HUD map button. (src: prologue registration beat; confirm the citation.)
    "district_guildhall": {
        "id": "district_guildhall",
        "name": "Lamplighter Guildhall",
        "available": True,               # shown on the city map
        "entry": "loc_guildhall",
        "locations": ["loc_guildhall"],
        "src": "§17.2 L1741",
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
        "hotspots": ["hs_guildhall_imara", "hs_guildhall_vekshara",
                     "hs_guildhall_reinecke", "hs_guildhall_questboard"],
        "src": "§17.2 L1741",
    },
}

HOTSPOTS = {
    # Imara, the guild receptionist (owner canon, #17.2). Clicking her runs the
    # conversational dialogue hub (dialogue.rpy). The hall has no exit plate --
    # the player leaves via the HUD map button.
    "hs_guildhall_imara": {
        "id": "hs_guildhall_imara",
        "label": "Imara",
        "kind": "character",
        "target": "dlg_imara",          # -> dialogue label in dialogue.rpy
        "pos": (900, 520),
        "visible_flag": None,
        "src": "§17.2 L1727-1736",
    },
    # Two more Guild Hall NPCs (owner canon). Same character-hotspot shape as
    # Imara; each opens its own conversational dialogue hub (dialogue.rpy).
    "hs_guildhall_vekshara": {
        "id": "hs_guildhall_vekshara",
        "label": "Vekshara",
        "kind": "character",
        "target": "dlg_vekshara",       # -> dialogue label in dialogue.rpy
        "pos": (350, 450),
        "visible_flag": None,
        "src": "§17.2 L1727-1736",
    },
    "hs_guildhall_reinecke": {
        "id": "hs_guildhall_reinecke",
        "label": "Reinecke",
        "kind": "character",
        "target": "dlg_reinecke",       # -> dialogue label in dialogue.rpy
        "pos": (1350, 820),
        "visible_flag": None,
        "src": "§17.2 L1727-1736",
    },
    # The Guild notice board (owner canon, #17.2 -- Imara points the player at
    # it). kind "questboard" -> opens the quest_board screen (city_free_loop).
    # Empty until a quest is flagged board:True (core.quests.board_quests).
    "hs_guildhall_questboard": {
        "id": "hs_guildhall_questboard",
        "label": "Notice Board",
        "kind": "questboard",
        "target": None,                 # one board; the screen is fixed
        "pos": (1350, 500),
        "visible_flag": None,
        "src": "§17.2 L1727-1736",
    },
}
