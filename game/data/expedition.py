# -*- coding: utf-8 -*-
"""Expedition regions and the node-based expedition map (GDD #13.2 L1395-1402;
hunting #12.2 L1346-1347). DATA only -- core/rest.py reads a region's literal
hunt_dc; the expedition map screen renders these nodes the same way the city
location screen renders hotspots.

OWNER CONTENT (GAPS G-043/G-044): region names, the per-region hunt difficulty,
and the node layout/encounters are owner-authored. DATA vs GUIDANCE (#16.5):
§12.2's "about 10 in outer regions, scaling to 20 in the deep Ruin" is writer
calibration -- only a single LITERAL hunt_dc int per region is stored, never
the 10..20 range or the 3-5-fights-per-Supply ratio. Placeholder names use the
single-bracket marker and render through breach_lit() (D-031); they are NOT
added to the doc-integrity name check.

REGIONS: {id, name, hunt_dc(literal int), src}
EXPEDITION_NODES: {id, kind, name, pos(x,y on 1920x1080), connections[node ids],
region, encounter[enemy ids], loot{items,gold}|None, flee(bool)
(encounter nodes only), src}
  loot and flee are owner-authored (G-044) and ship empty/False; loot reuses
  the quest-reward shape {items:[id...], gold:int}.
  kind "entry"    -> where the party arrives (start node)
  kind "encounter"-> a fight; entering runs combat with `encounter`
  kind "campsite" -> a place to make Camp (#12.4)
  kind "exit"     -> leave the Breach, back to the city
"""

REGIONS = {
    "region_breach_1": {
        "id": "region_breach_1",
        "name": "[Breach Region 1]",      # owner-authored (G-043)
        "hunt_dc": 10,                    # literal, outer-region floor (§12.2)
        "src": "§12.2 L1346-1347",
    },
}

EXPEDITION_NODES = {
    "node_entry": {
        "id": "node_entry",
        "kind": "entry",
        "name": "[Breach Entrance]",      # owner-authored (G-044)
        "pos": (320, 520),
        "connections": ["node_fight"],
        "region": "region_breach_1",
        "encounter": [],
        "src": "§13.2 L1399-1402",
    },
    "node_fight": {
        "id": "node_fight",
        "kind": "encounter",
        "name": "[Wolf Den]",
        "pos": (760, 380),
        "connections": ["node_entry", "node_camp"],
        "region": "region_breach_1",
        "encounter": ["standard_wolf"],   # reuses an existing enemy (#11.2)
        "loot": None,                     # owner-authored {items,gold} (G-044)
        "flee": False,                    # GDD 18: the optional fight w/ Flee
        "src": "§13.2 L1399-1402",
    },
    "node_camp": {
        "id": "node_camp",
        "kind": "campsite",
        "name": "[Campsite]",
        "pos": (1180, 520),
        "connections": ["node_fight", "node_exit"],
        "region": "region_breach_1",
        "encounter": [],
        "src": "§13.2 L1401-1402",
    },
    "node_exit": {
        "id": "node_exit",
        "kind": "exit",
        "name": "[Back to the Surface]",
        "pos": (1600, 380),
        "connections": ["node_camp"],
        "region": "region_breach_1",
        "encounter": [],
        "src": "§13.2 L1396",
    },
}
