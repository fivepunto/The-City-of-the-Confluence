# -*- coding: utf-8 -*-
"""Economy values transcribed from GDD sections 12.2 (the rest economy)
and 14 (economy: sinks, vendor rules, sell rules, spell copying)."""

ECONOMY = {
    "inn_rest_cost": {
        "value": 10,
        "src": "§12.2 L1339-1340",
    },
    "supply_cache_price": {
        "value": 50,
        "note": "doc says ~50",
        "src": "§12.2 L1341-1342, §14.3 L1424",
    },
    "supply_capacity_base": {
        "value": 3,
        "src": "§12.2 L1343",
    },
    "supply_capacity_with_pack_frame": {
        "value": 4,
        "src": "§12.2 L1343",
    },
    "hunting_skill": {
        "value": "awareness",
        "src": "§12.2 L1344-1345",
    },
    "hunting_ranger_advantage": {
        "value": True,
        "src": "§12.2 L1348",
    },
    "relic_sell_ratio": {
        "value": 1.0,
        "src": "§14.5 L1453",
    },
    "gear_sell_ratio": {
        "value": 0.5,
        "src": "§14.5 L1453",
    },
    "sell_confirm_min_rarity": {
        "value": "rare",
        "src": "§14.5 L1453-1454",
    },
    "sell_all_button": {
        "value": False,
        "src": "§14.5 L1454-1455",
    },
    "buyback": {
        "value": False,
        "src": "§14.5 L1455",
    },
    "very_rare_sold_by_vendors": {
        "value": False,
        "src": "§14.3 L1426",
    },
    "plus_three_items_sold": {
        "value": False,
        "src": "§14.3 L1426",
    },
    "wizard_spell_copy_cost_per_tier": {
        "value": 50,
        "src": "§14.3 L1428",
    },
}
