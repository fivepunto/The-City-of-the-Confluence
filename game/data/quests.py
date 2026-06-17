# -*- coding: utf-8 -*-
"""Quest registry for the quest tab (GDD #15.5 L1555-1563). DATA only -- the
runtime status/progress lives in state["quests"] (see core/state.py and
core/quests.py); this table is the static definition.

OWNER CONTENT (GAPS G-039): every title, giver, location, objective line
(including the authored "where to go" -- there are no map markers, #15.5
L1562), branch, and reward value is "[TO BE WRITTEN BY THE PROJECT OWNER]".
The SYSTEM ships against bracketed-placeholder quests so the state machine and
the mandatory conclusion toast are exercisable; no quest content is invented.
Placeholder titles are deliberately NOT added to the doc-integrity name check.

Record shape:
  {id, category: 'main'|'side'|'companion', title, giver, location,
   objectives: [{id, text}, ...]  (ordered; index 0 is the first objective),
   rewards: {gold, items:[item_id,...]} | None  (shown only when promised),
   src}
"""

QUESTS = {
    "quest_main_hook": {
        "id": "quest_main_hook",
        "category": "main",
        "title": "[Main Quest A]",            # owner-authored (G-039)
        "giver": "[Quest Giver]",
        "location": "[District B]",
        "objectives": [
            {"id": "obj1", "text": "[TO BE WRITTEN BY THE PROJECT OWNER]"},
            {"id": "obj2", "text": "[TO BE WRITTEN BY THE PROJECT OWNER]"},
        ],
        "rewards": None,                       # shown only when authored
        "src": "§15.5 L1555-1563",
    },
    "quest_side_a": {
        "id": "quest_side_a",
        "category": "side",
        "title": "[Side Quest A]",
        "giver": "[Merchant]",
        "location": "[District A]",
        "objectives": [
            {"id": "obj1", "text": "[TO BE WRITTEN BY THE PROJECT OWNER]"},
            {"id": "obj2", "text": "[TO BE WRITTEN BY THE PROJECT OWNER]"},
            {"id": "obj3", "text": "[TO BE WRITTEN BY THE PROJECT OWNER]"},
        ],
        # None = promises nothing yet; a reward line shows ONLY when the
        # owner authors a real promise (#15.5 L1561, G-039). No invented gold.
        "rewards": None,
        "src": "§15.5 L1555-1563",
    },
}
