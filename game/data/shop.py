# -*- coding: utf-8 -*-
"""Vendor stock tables for the shop screen (GDD #15.8 L1608-1612, #14.3
L1424-1428). DATA only -- buy/sell pricing and rule enforcement live in
core/shop.py, which reads the economy rule flags (data/economy.py) and the
priced item records (consumables, magic_items). This table only lists WHAT a
shop offers and HOW MANY.

OWNER CONTENT (GAPS G-040): which shops exist, their names, and exactly what
each stocks is owner-authored. Relics are SELL-ONLY (#14.2 frames them as
income), so they are absent from buy stock. Very Rare and +3 magic items are
never vendor-sold (#14.3 L1426). Prices are NOT duplicated here -- the single
source of a buy price is the item record's `price` field, so a shop cannot
silently contradict the catalogue. The SYSTEM ships against a single
bracketed-placeholder vendor; placeholder names are NOT added to the
doc-integrity name check.

Record shape:
  {shop_id: {id, name, stock: [{item_id, count}], src}}
    count = int  -> stock-limited ("X in stock"; sold-out greys out, #15.8 L1611)
    count = None -> unlimited
The Phoenix Draught is stock-capped as insurance, not a Cleric replacement
(#14.4 L1451); the default cap of 2 lives on its stock entry (G-040).
"""

SHOPS = {
    "general_store": {
        "id": "general_store",
        "name": "[General Store]",        # owner-authored (G-040)
        "stock": [
            {"item_id": "healing_potion", "count": None},
            {"item_id": "greater_healing_potion", "count": None},
            {"item_id": "superior_healing_potion", "count": None},
            {"item_id": "phoenix_draught", "count": 2},   # stock-limited (§14.4)
            {"item_id": "magic_item_a", "count": 1},       # uncommon
            {"item_id": "magic_item_b", "count": 1},       # rare
        ],
        "src": "§14.3 L1424-1426, §15.8 L1608-1612",
    },
}
