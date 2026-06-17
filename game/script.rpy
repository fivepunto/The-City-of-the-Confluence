# P1 boot: character creation & sheet phase. The canonical module aliases
# every screen file uses are defined here, once.

init 1 python:
    import data
    from core import character as bch
    from core import inventory as binv
    from core import state as bstate
    from core import ui_options as bui
    from core import dice as bdice
    from core import checks as bchecks
    from core import quests as bquests
    from core import shop as bshop
    from core import rest as brest

    REG = data.REGISTRY

    # dev-mode boot guard: the assembled registry must be structurally valid.
    # config.developer is auto-True in an unpacked project (dev / MCP runs) and
    # False in a packaged build, so players never hit this. Scoped to the
    # structural validate(); the fuller content validator (slice matrix + voice
    # scan) runs on demand from the debug hub's "Validate content" button.
    if config.developer:
        from core import registry as _reg_check
        _structural = _reg_check.validate(REG)
        assert _structural == [], \
            "registry.validate found problems: %r" % (_structural,)

    def breach_player_text(registry, category, rec_id, fallback):
        """Player-voiced display string (GDD #15.0); see
        core.ui_options.player_text."""
        return bui.player_text(registry, category, rec_id, fallback)

default gs = None


label after_load:
    # Save-migration seam (Ren'Py jumps here after every load): backfill keys
    # added since the save was made and re-stamp SAVE_VERSION. gs may be None
    # for a save made before the protagonist exists, so guard it.
    $ if gs is not None: bstate.migrate_state(gs)
    return


label start:
    $ gs = bstate.new_game_state(REG)
    "Breach prototype — P1 (character creation & sheet)."
    jump p1_hub


label p1_hub:
    while True:
        if not gs["party"]:
            menu:
                "P2 — what do you want to do?"
                "Play the prologue (P5)":
                    call prologue
                "Create the protagonist":
                    call character_creation
                "Open the debug hub":
                    call screen debug_hub
                "Quit to main menu":
                    return
        else:
            menu:
                "P2 — what do you want to do?"
                "Enter the city (Free Mode)":
                    call city_free_mode
                "Enter the Breach (expedition)":
                    call expedition_mode
                "Fight: Young Wolf (the tutorial fight)":
                    call combat_encounter(["young_wolf"])
                "Fight: wolf pack 4v4":
                    call combat_encounter(["standard_wolf", "standard_wolf", "standard_wolf", "standard_wolf"])
                "Character sheet":
                    call screen character_sheet
                    # the sheet is a level-up entry point (15.2). Guard the
                    # subscript: a screen can return a bare value (root
                    # cause B) -- only act on a well-shaped intent tuple.
                    if isinstance(_return, (tuple, list)) and len(_return) >= 2 and _return[0] == "levelup":
                        call levelup_wizard(_return[1])
                "Inventory & equipment":
                    call screen inventory_screen
                "Level up" if bch.can_level_up(REG, gs["party"][0]):
                    call levelup_wizard(gs["party"][0]["id"])
                "Open the debug hub":
                    call screen debug_hub
                    # the hub can launch any debug encounter
                    if isinstance(_return, (tuple, list)) and len(_return) >= 3 and _return[0] == "combat":
                        call combat_encounter(_return[1], _return[2])
                    # ...or jump straight into Free Mode (P3)
                    elif isinstance(_return, (tuple, list)) and _return and _return[0] == "city":
                        call city_free_mode
                    # ...or into the Breach / a camp (P4)
                    elif isinstance(_return, (tuple, list)) and _return and _return[0] == "expedition":
                        call expedition_mode
                    elif isinstance(_return, (tuple, list)) and _return and _return[0] == "camp":
                        call camp_mode
                    elif isinstance(_return, (tuple, list)) and _return and _return[0] == "inn":
                        call inn_sleep
                "Start over (new character)":
                    $ gs = bstate.new_game_state(REG)
                "Quit to main menu":
                    return
