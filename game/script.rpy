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
    # structural validate(); the fuller content validator (slice matrix +
    # DISPLAY placeholder scan) runs on demand from the debug hub's
    # "Validate content" button.
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
    # New game enters the scripted prologue (GDD #17.2). The prologue builds the
    # game state, runs character creation, plays the beats + tutorial fight, and
    # flows straight into Free Mode -- which is the whole game loop. The prologue
    # does not return in normal play, so the trailing `return` is only a safety
    # net (it drops to the Ren'Py main menu if Free Mode ever exits).
    #
    # A long, dramatic fade carries the main menu into the first creation screen.
    # There is no built-in "game start" transition (see options.rpy), so we
    # transition the next interaction directly. game_start_fade is defined in
    # options.rpy (slower than the stock `fade`, for an epic open).
    $ renpy.transition(game_start_fade)
    call prologue
    return
