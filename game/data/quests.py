# -*- coding: utf-8 -*-
"""Quest registry for the quest tab (GDD #15.5 L1555-1563). DATA only -- the
runtime status/progress lives in state["quests"] (see core/state.py and
core/quests.py); this table is the static definition.

OWNER CONTENT (GAPS G-039): quest OBJECTIVE steps (the authored "where to go"
-- there are no map markers, #15.5 L1562), branches, and reward values are
"[TO BE WRITTEN BY THE PROJECT OWNER]". The two prologue quests below carry
real titles, giver, and location (owner canon, #17.2); only their objective
steps stay placeholders so the state machine and the mandatory conclusion toast
are exercisable. No quest content is invented; bracketed placeholders are
deliberately NOT added to the doc-integrity name check.

Record shape:
  {id, category: 'main'|'side'|'companion', title, giver, location,
   objectives: [{id, text}, ...]  (ordered; index 0 is the first objective),
   rewards: {gold, items:[item_id,...]} | None  (shown only when promised),
   src}
"""

QUESTS = {
    # The two goals Imara hands the player at the close of the prologue
    # (#17.2); both are MAIN-category and are started automatically as Free
    # Mode begins (see prologue.rpy). Title, giver, and location are owner
    # canon from the prologue; only the OBJECTIVE steps are still bracketed
    # placeholders (G-039) for the owner to author. No invented prose; no
    # invented rewards (rewards stay None until the owner promises one).
    "quest_enter_breach": {
        "id": "quest_enter_breach",
        "category": "main",
        "title": "Enter the Ruined World",
        "giver": "Imara",
        "location": "The Breach",
        "objectives": [
            {"id": "obj1", "text": "[TO BE WRITTEN BY THE PROJECT OWNER]"},
            {"id": "obj2", "text": "[TO BE WRITTEN BY THE PROJECT OWNER]"},
        ],
        "rewards": None,
        "src": "§17.2 L1741",
    },
    "quest_find_companion": {
        "id": "quest_find_companion",
        "category": "main",
        "title": "Find a Companion",
        "giver": "Imara",
        "location": "Veycross",
        "objectives": [
            {"id": "obj1", "text": "[TO BE WRITTEN BY THE PROJECT OWNER]"},
            {"id": "obj2", "text": "[TO BE WRITTEN BY THE PROJECT OWNER]"},
        ],
        "rewards": None,
        "src": "§17.2 L1741",
    },
}
