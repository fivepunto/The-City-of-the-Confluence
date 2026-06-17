# The combat screen (GDD 15.6): "the screen IS the rules."
#
# label combat_encounter(enemy_ids, flee_allowed=False) builds the fight
# from gs["party"], runs the dedicated screen loop with rollback blocked
# (GDD 16.1), applies results via bcombat.finish_combat, and returns.
#
# All rules text shown here comes from the registry (condition/feature/
# spell/item "effect" fields) or from engine refusal reasons — this file
# contains only UI labels (CLAUDE.md: one registry).

init python:
    from core import combat as bcombat
    from core import hooks as bhooks
    from core import state as bstate


# ---------------------------------------------------------------------------
# helpers (UI-side only: targeting affordances mirror engine predicates,
# they never resolve anything themselves)

init python:

    # The engine's own Downed/healing refusal (core.combat.player_use_item),
    # reused verbatim so the gate reads the same everywhere (GDD 5.5 / 9.1).
    BREACH_DOWNED_HEAL_REASON = (
        "Healing cannot revive a Downed character — only True Healing can.")

    # Which side an activated ability targets (UI affordance; the engine
    # validates the actual use).
    BREACH_ABILITY_SIDE = {
        "paladin_lay_on_hands": "party",
        "cleric_divine_spark_heal": "party",   # heals an ally (GDD 7.3)
        "monk_flurry_of_blows": "enemy",
    }

    # Whether an enemy-targeted ability is melee (lane-gated) or ranged —
    # ranged ignores lanes entirely (GDD 5.4 L269). Mirrors each engine
    # run function; unlisted abilities stay melee, the conservative read.
    BREACH_ABILITY_MELEE = {
        "monk_flurry_of_blows": True,
        "druid_claw": True,
        "druid_fang": True,
        "druid_talon": False,                  # ranged dive (GDD 7.10 L765)
        "cleric_divine_spark_damage": False,   # "at range" (GDD 7.3 L476)
    }

    def breach_ability_click(ab):
        """Route one ability button press: the option menu first when the
        ability takes options (hooks.use_ability option=), then targeting,
        else straight to dispatch."""
        if ab["options"]:
            return [SetScreenVariable("pending", ab["id"]),
                    SetScreenVariable("pending_option", None),
                    SetScreenVariable("mode", "ability_option")]
        if ab["needs_target"]:
            return [SetScreenVariable("pending", ab["id"]),
                    SetScreenVariable("pending_option", None),
                    SetScreenVariable("mode", "ability_target")]
        return Return(("ability", ab["id"], None, None))

    def breach_ability_option_info(char, opt):
        """(label, rules text) for an ability option id, read from the
        owning feature's registry options (one registry — no rules text
        lives here). Plain ids (e.g. damage types) title-case themselves."""
        for fid in char["features"]:
            feat = REG["features"].get(fid)
            if not feat:
                continue
            for o in feat.get("options") or ():
                if o.get("id") == opt:
                    return o["name"], o.get("effect")
        return opt.replace("_", " ").title(), None

    def breach_ask_reaction(card):
        """The engine's ask_fn: one modal yes/no card (GDD 5.2 / 15.6)."""
        return renpy.call_screen("reaction_prompt", card=card)

    def breach_set_reaction_pref(card, mode):
        """The inline Always/Never links on the prompt (15.6)."""
        for char in gs["party"]:
            if "pc_" + char["id"] == card["owner"]:
                char["reaction_preferences"][card["ability_id"]] = mode

    def breach_reaction_abilities(char):
        """[(ability_id, label, default_mode)] for the settings overlay.
        The universal opportunity attack costs nothing -> defaults Always
        (GDD 5.2 L233-236); costed hooks carry their own prompt default."""
        out = [("opportunity_attack", "Opportunity Attack", "always")]
        ids = list(char["features"])
        ids += ["style_" + s
                for s in char["class_picks"].get("fighting_styles", [])]
        ids += ["inv_" + i
                for i in char["class_picks"].get("invocations", [])]
        ids += ["talent_" + t for t in char["talents"]]
        for fid in ids:
            for hook in bhooks.HOOK_LIBRARY.get(fid, ()):
                if hook.get("cost") != "reaction":
                    continue
                aid = hook.get("ability_id", fid)
                if aid not in [o[0] for o in out]:
                    out.append((aid,
                                hook.get("title",
                                         aid.replace("_", " ").title()),
                                hook.get("prompt", "ask")))
        return out

    def breach_drain_floats(combat):
        """Move engine float events into the on-screen feed (15.6)."""
        for f in combat["floats"]:
            c = combat["combatants"].get(f["cid"])
            store.breach_floats_view.append({
                "who": c["name"] if c else "",
                "text": f["text"], "kind": f["kind"]})
        del combat["floats"][:]
        del store.breach_floats_view[:-5]

    def breach_float_color(kind):
        if kind == "damage":
            return gui.danger_color
        if kind == "heal":
            return gui.success_color
        if kind == "condition":
            return gui.breach_accent_color
        if kind == "crit":
            return gui.accent_bright_color
        if kind == "miss":
            return gui.muted_text_color
        return gui.breach_text_color

    def breach_actor_melee(actor):
        """Does the actor's Attack action reach in melee? (lane rules,
        GDD 5.4)."""
        weapon = bcombat.weapon_of(REG, actor)
        return weapon is None or "ranged" not in weapon["properties"]

    def breach_spell_side(sp):
        """Single-target spells: allies for heal/buff roles, enemies
        otherwise (15.6)."""
        if set(sp["roles"]) & {"heal", "true_heal", "buff"}:
            return "party"
        return "enemy"

    def breach_spell_click(sp):
        """How the Spells list routes a pick: lane-area, self, or
        single-target mode."""
        area = sp.get("area")
        if area:
            if area.get("side") and area.get("size"):
                return "lane"
            return "unsupported"
        if sp.get("range") == "self":
            return "self"
        return "target"

    def breach_tile_target(combat, actor, c, mode, pending, pending_option,
                           reckless):
        """(candidate, ok, reason, intent) for one combatant tile in a
        single-target mode. Reasons feed the greyed-target tooltip
        (15.6 L1549-1551); validity mirrors the engine's own gates."""
        if mode == "attack":
            if c["side"] != "enemy":
                return (False, False, None, None)
            ok, reason = bcombat.targetable(combat, actor, c,
                                            breach_actor_melee(actor))
            return (True, ok, reason, ("attack", c["cid"], reckless))
        if mode == "spell_target" and pending:
            sp = REG["spells"][pending]
            intent = ("cast", pending, c["cid"], None)
            if c["side"] != breach_spell_side(sp):
                return (False, False, None, None)
            if c["side"] == "enemy":
                ok, reason = bcombat.targetable(combat, actor, c,
                                                sp["range"] == "touch")
                return (True, ok, reason, intent)
            # ally-side single target (mirrors hooks._spell_targets)
            if c["dead"]:
                return (True, False, "Beyond help.", None)
            if c["downed"]:
                if "true_heal" in sp["roles"]:
                    return (True, True, None, intent)
                return (True, False, BREACH_DOWNED_HEAL_REASON, None)
            if "hidden" in c["conditions"]:
                return (True, False, "Hidden — cannot be single-targeted.",
                        None)
            if sp["range"] == "touch" and c["lane"] != actor["lane"] and \
                    c["cid"] != actor["cid"]:
                return (True, False, "Touch — must share your lane.", None)
            return (True, True, None, intent)
        if mode == "ability_target" and pending:
            side = BREACH_ABILITY_SIDE.get(pending, "enemy")
            intent = ("ability", pending, c["cid"], pending_option)
            if c["side"] != side:
                return (False, False, None, None)
            if side == "enemy":
                ok, reason = bcombat.targetable(
                    combat, actor, c,
                    BREACH_ABILITY_MELEE.get(pending, True))
                return (True, ok, reason, intent)
            if c["dead"]:
                return (True, False, "Beyond help.", None)
            if c["downed"]:
                return (True, False, BREACH_DOWNED_HEAL_REASON, None)
            return (True, True, None, intent)
        if mode == "item_target" and pending:
            if c["side"] != "party":
                return (False, False, None, None)
            item = REG["consumables"][pending]
            if c["dead"]:
                return (True, False, "Beyond help.", None)
            if c["downed"] and item["heal_type"] != "true_healing":
                return (True, False, BREACH_DOWNED_HEAL_REASON, None)
            return (True, True, None, ("item", pending, c["cid"]))
        return (False, False, None, None)

    def breach_plate_target(combat, actor, side, lane, mode, pending):
        """(candidate, ok, reason, intent) for a lane plate: the Move
        command and lane-area spells (15.6 L1536-1537, L1551-1552)."""
        if mode == "move":
            if side != actor["side"] or lane == actor["lane"]:
                return (False, False, None, None)
            return (True, True, None, ("move", lane))
        if mode == "spell_lane" and pending:
            sp = REG["spells"][pending]
            area = sp.get("area") or {}
            want = "enemy" if area.get("side") == "enemies" else "party"
            if side != want:
                return (False, False, None, None)
            if area.get("size") == "large":
                there = bcombat.combatants_on(combat, side)
            else:
                there = bcombat.combatants_on(combat, side, lane)
            if not there:
                return (True, False, "No one there.", None)
            return (True, True, None, ("cast", pending, None, lane))
        return (False, False, None, None)

    def breach_move_check(actor):
        """Move button availability (mirrors core.combat.move_lane /
        player_move refusals; GDD 5.2: moving costs the Action)."""
        for cond in ("pinned", "tripped"):
            if cond in actor["conditions"]:
                return False, "%s — can't change lanes." % cond.capitalize()
        if actor["flags"].get("free_move_available"):
            return True, None
        if actor["acted"]["action"]:
            return False, "Action spent."
        return True, None

    def breach_telegraph_text(c):
        """Boss/elite telegraph hover text (GDD 5.8 / 15.6): the named
        attack from the statblock, or the raw ability id."""
        if c["kind"] != "enemy":
            return None
        tid = c.get("telegraph")
        if not tid:
            return None
        for atk in (c["stats"].get("attacks") or []):
            if atk.get("id") == tid:
                return "Preparing: %s" % atk.get("name", tid)
        return "Preparing: %s" % str(tid).replace("_", " ").title()

    def breach_mode_caption(mode, pending):
        name = None
        if mode in ("spell_target", "spell_lane") and pending:
            name = REG["spells"][pending]["name"]
        elif mode in ("ability_target", "ability_option") and pending:
            impl = bhooks.ABILITY_IMPL.get(pending, {})
            fid = impl.get("feature")
            name = impl.get("name") or (REG["features"][fid]["name"]
                                        if fid else pending)
        elif mode == "item_target" and pending:
            name = REG["consumables"][pending]["name"]
        if mode == "attack":
            return "Choose an enemy to attack."
        if mode == "move":
            return "Choose the lane to move to."
        if mode == "spell_lane":
            return "Choose a lane for %s." % name
        if mode == "ability_option" and name:
            return "Choose an option for %s." % name
        if name:
            return "Choose a target for %s." % name
        return ""

    def breach_combat_dispatch(combat, actor, intent):
        """Apply one intent tuple from the combat screen. Returns the
        engine result dict (or None); {ok: False, reason} surfaces via
        renpy.notify in the loop. Shape-guard the intent: a screen can
        return a bare value (root cause B), which must be a no-op, never
        a subscript crash."""
        if not (isinstance(intent, (tuple, list)) and len(intent) >= 1):
            return None
        kind = intent[0]
        if kind == "attack":
            target = combat["combatants"][intent[1]]
            reckless = bool(intent[2]) if len(intent) > 2 else False
            return bcombat.player_attack(REG, combat, actor, target,
                                         reckless=reckless)
        if kind == "move":
            return bcombat.player_move(REG, combat, actor, intent[1])
        if kind == "cast":
            target = combat["combatants"][intent[2]] if intent[2] else None
            return bhooks.cast_spell(REG, combat, actor, intent[1],
                                     target=target, lane=intent[3])
        if kind == "ability":
            target = combat["combatants"][intent[2]] if intent[2] else None
            option = intent[3] if len(intent) > 3 else None
            return bhooks.use_ability(REG, combat, actor, intent[1],
                                      target=target, option=option)
        if kind == "item":
            target = combat["combatants"][intent[2]]
            return bcombat.player_use_item(REG, combat, actor, intent[1],
                                           target, gs["inventory"])
        if kind == "end":
            bcombat.end_turn(REG, combat)
            return None
        if kind == "flee":
            return bcombat.flee(REG, combat)
        return None

    def breach_combat_trace(msg):
        # DEBUG TRACE for the "attack does nothing" repro (TEMPORARY -- remove
        # after diagnosis). Appends to combat_trace.log in the project root.
        try:
            import os, time
            with open(os.path.join(config.basedir, "combat_trace.log"), "a") as _f:
                _f.write("[%.3f] %s\n" % (time.time(), msg))
        except Exception:
            pass


# Float feed shown near the battlefield band; rebuilt every encounter.
default breach_floats_view = []

# Live combat state; non-None only inside combat_encounter (set at build,
# cleared after the results panel). The Save guard refuses saving while this
# is not None, so a mid-fight save can never pickle the transient combat dict.
default combat = None


# ---------------------------------------------------------------------------
# (the small chip button is now the shared breach_chip, defined in style.rpy)


# ---------------------------------------------------------------------------
# the encounter label: build -> dedicated loop -> results (GDD 16.1: block
# rollback after every engine step; reload rerolls are by design)

label combat_encounter(enemy_ids, flee_allowed=False, loot=None):
    $ renpy.block_rollback()
    $ breach_combat_trace("==== COMBAT START enemies=%r ====" % (enemy_ids,))
    $ breach_floats_view = []
    $ combat = bcombat.build_combat(REG, gs["party"], enemy_ids, flee_allowed)
    $ bcombat.begin(REG, combat, breach_ask_reaction)
    $ breach_drain_floats(combat)

    $ breach_wd_key = None
    $ breach_wd_count = 0
    while combat["over"] is None:
        $ renpy.block_rollback()
        $ bcombat.set_ask_fn(breach_ask_reaction)
        $ breach_actor = bcombat.current(combat)
        $ breach_combat_trace("ITER round=%d turn=%d actor=%s side=%s kind=%s can_act=%s" % (combat["round"], combat["turn"], breach_actor["name"], breach_actor["side"], breach_actor["kind"], bcombat.can_act(breach_actor)))
        python:
            # Forward-progress watchdog: if the loop sees the same
            # (actor, turn, round) for combat_watchdog_limit iterations
            # running, the fight is stuck -- raise loudly instead of hanging
            # silently. The counter resets on any real advance (turn, round,
            # or actor change), so a legitimate multi-action turn never trips.
            _wd_key = (breach_actor["cid"], combat["turn"], combat["round"])
            if _wd_key == breach_wd_key:
                breach_wd_count += 1
            else:
                breach_wd_key = _wd_key
                breach_wd_count = 0
            if breach_wd_count >= gui.combat_watchdog_limit:
                raise RuntimeError(
                    "Combat made no forward progress: stuck on %r for %d "
                    "iterations (actor=%s round=%s turn=%s)." % (
                        _wd_key, breach_wd_count, breach_actor["name"],
                        combat["round"], combat["turn"]))
        if breach_actor["side"] == "enemy" or not bcombat.can_act(breach_actor):
            # enemy turns and condition-blocked turns resolve in the
            # engine; the short pause lets the player read the floats
            $ breach_combat_trace("  ENEMY/BLOCKED show screen -> %s" % breach_actor["name"])
            show screen combat_screen(combat)
            python:
                if breach_actor["side"] == "enemy":
                    bcombat.enemy_take_turn(REG, combat, breach_actor)
                else:
                    bcombat.end_turn(REG, combat)
                renpy.block_rollback()
                breach_drain_floats(combat)
            $ renpy.pause(0.4)
            hide screen combat_screen
        else:
            $ breach_combat_trace("  PLAYER call_screen for %s (acted.action=%s)" % (breach_actor["name"], breach_actor["acted"].get("action")))
            $ breach_intent = renpy.call_screen("combat_screen", combat=combat)
            $ breach_combat_trace("  PLAYER intent=%r" % (breach_intent,))
            $ breach_result = breach_combat_dispatch(combat, breach_actor, breach_intent)
            $ breach_combat_trace("  PLAYER result=%r" % (breach_result,))
            $ renpy.block_rollback()
            $ breach_drain_floats(combat)
            if breach_result is not None and not breach_result.get("ok", True):
                $ renpy.notify(breach_result.get("reason") or "Can't do that.")

    hide screen combat_screen
    $ renpy.block_rollback()
    # flush HP/Downed/XP back to the party BEFORE any panel (15.6)
    $ breach_summary = bcombat.finish_combat(REG, combat, gs["party"])
    $ renpy.block_rollback()
    if breach_summary.get("result") == "victory":
        # grant authored loot into the shared inventory (15.6: "loot into the
        # shared inventory"); block_rollback commits it (16.1). Default-empty
        # loot grants nothing. The granted loot rides breach_summary so the
        # victory panel can show it. loot shape: {"items": [id...], "gold": int}.
        python:
            _loot = loot or {}
            for _iid in _loot.get("items", []):
                bstate.add_item(gs, _iid)
            if _loot.get("gold"):
                bstate.add_gold(gs, _loot["gold"])
            breach_summary["loot"] = _loot
            renpy.block_rollback()
        call screen combat_victory(combat, breach_summary)
    elif breach_summary.get("result") == "defeat":
        # all-Downed is defeat, no exceptions (GDD 5.5 / 11.2); the
        # screen's Continue goes to the main menu
        call screen combat_defeat(combat)
    else:
        $ renpy.notify("The party flees — no XP, no loot.")
    $ combat = None
    return


# ---------------------------------------------------------------------------
# the combat screen proper (GDD 15.6)

screen combat_screen(combat):
    modal True
    add Solid(gui.bg_color)

    default mode = "main"
    default pending = None
    default pending_option = None
    default reckless = False
    default overlay = None

    $ actor = bcombat.current(combat)
    $ p_pc = (actor["kind"] == "pc")
    $ achar = actor["char"] if p_pc else None
    $ p_playable = p_pc and bcombat.can_act(actor) and combat["over"] is None
    $ abilities = bhooks.available_abilities(REG, combat, actor) if p_playable else []
    $ bonus_abilities = [a for a in abilities if a["action"] == "bonus" and a["usable"]]
    $ spells = bhooks.castable_spells(REG, combat, actor) if p_playable else []
    $ p_items = [(iid, gs["inventory"][iid]) for iid in sorted(gs["inventory"]) if iid in REG["consumables"]]
    $ p_chips = (mode in ("main", "spell_list", "ability_list", "item_list"))
    $ p_round = combat["round"]
    $ p_cancel = [SetScreenVariable("mode", "main"), SetScreenVariable("pending", None), SetScreenVariable("pending_option", None)]
    $ breach_tt = GetTooltip()

    ## Layout geometry derived from the gui tokens + the canvas -- no magic
    ## y-positions. The initiative ribbon (turn order) runs across the top; below
    ## it the stage SPLITS into the battlefield (lanes, left) and the info
    ## sidebar (rolled initiative order + combat log, right); the action panel
    ## keeps the bottom band.
    $ c_gap = gui.pad_m
    $ c_ribbon_h = gui.combat_ribbon_h
    $ c_panel_h = gui.combat_panel_h
    $ c_stage_y = c_ribbon_h + c_gap
    $ c_stage_h = config.screen_height - c_stage_y - c_panel_h - c_gap
    $ c_panel_y = c_stage_y + c_stage_h + c_gap
    ## the sidebar is a fixed right column; the lanes well fills the rest. The
    ## plate width is DERIVED so four plates + the no-man's-land seam tile the
    ## well exactly (no magic plate width).
    $ c_sidebar_w = gui.combat_sidebar_w
    $ c_lanes_w = config.screen_width - 2 * gui.pad_m - gui.pad_m - c_sidebar_w
    $ c_plate_w = (c_lanes_w - 2 * gui.pad_m - 5 * gui.pad_s) // 4
    $ c_plate_h = c_stage_h - 2 * gui.pad_m
    ## the active actor's lane lights -- but only out of targeting mode, so in
    ## a target mode the only lit things are the valid targets (light = intent).
    $ c_active_lane = (actor["side"], actor["lane"])
    $ c_show_active = (mode == "main")

    ## Band 1 -- the initiative ribbon (turn order) across the top.
    use combat_ribbon(combat, p_round, c_ribbon_h)
    ## the ribbon's lamplit bottom lip
    add Solid(gui.breach_accent_dim_color) xsize 1.0 ysize gui.hairline ypos (c_ribbon_h - gui.hairline)

    ## Band 2 -- the battlefield (lanes, left) + the info sidebar (right).
    use combat_stage(combat, actor, mode, pending, pending_option, reckless, p_chips, c_stage_y, c_stage_h, c_lanes_w, c_sidebar_w, c_plate_w, c_plate_h, c_active_lane, c_show_active)

    ## Band 3 -- the action panel (shared gold frame).
    use combat_action_panel(combat, actor, achar, p_pc, p_playable, mode, pending, spells, abilities, bonus_abilities, p_items, reckless, p_cancel, breach_tt, c_panel_y, c_panel_h)

    ## Overlays: the full log and the reactions settings page (15.6).
    use combat_overlays(combat, overlay)


# ---------------------------------------------------------------------------
# Combat sub-screens (GDD 15.6): combat_screen is composed from these focused
# pieces -- one per region -- via `use`, in the same band positions. The
# interaction STATE (mode / pending / overlay / reckless) lives on
# combat_screen; each sub-screen receives the values it reads, and its
# SetScreenVariable / Return / ToggleScreenVariable actions resolve against the
# shown screen -- exactly as the existing list/button sub-screens already do.

## Band 1 -- the initiative ribbon (GDD 15.6): the turn-order strip across the
## top. One horizontal chip per combatant in interleaved order; the current
## actor is lit (accent border + accent, larger name), chips that have already
## acted burn low (desaturated + dim), and a round counter sits at the far
## right. This is who-acts-when; the rolled VALUES live in the sidebar.
screen combat_ribbon(combat, p_round, c_ribbon_h):
    frame:
        style "breach_band"
        xpos 0
        ypos 0
        xfill True
        ysize c_ribbon_h
        padding (gui.pad_m, gui.pad_s)
        hbox:
            spacing gui.pad_m
            xfill True
            yalign 0.5
            hbox:
                spacing gui.pad_l
                yalign 0.5
                for r_idx, r_cid in enumerate(combat["order"]):
                    $ rc = combat["combatants"][r_cid]
                    $ r_out = rc["dead"] or rc["downed"]
                    $ r_cur = (r_idx == combat["turn"])
                    $ r_acted = (r_idx < combat["turn"]) and not r_cur
                    $ r_key = (rc["char"]["class"] if rc["kind"] == "pc" else rc["cid"])
                    python:
                        if r_out:
                            r_xform = Transform(matrixcolor=SaturationMatrix(0.0), alpha=0.5)
                        elif r_acted:
                            r_xform = Transform(matrixcolor=SaturationMatrix(0.0))
                        else:
                            r_xform = Transform()
                        r_border = (gui.breach_accent_color if r_cur
                                    else (gui.breach_accent_dim_color if r_acted
                                          else gui.panel_border_color))
                        r_name_color = (gui.muted_text_color if r_out
                                        else (gui.breach_accent_color if r_cur
                                              else gui.breach_text_color))
                    ## one HORIZONTAL chip per combatant -- the colored letter
                    ## tile beside the name (the reference's turn-order strip).
                    hbox:
                        spacing gui.pad_s
                        at r_xform
                        yalign 0.5
                        ## the mini portrait swatch (nested-frame border)
                        frame:
                            background Solid(r_border)
                            padding (gui.hairline, gui.hairline)
                            yalign 0.5
                            frame:
                                background Solid(breach_placeholder_color(r_key))
                                xysize (gui.combat_chip_size, gui.combat_chip_size)
                                padding (0, 0)
                                text breach_initials(rc["name"]):
                                    align (0.5, 0.5)
                                    size gui.size_micro
                                    color gui.breach_text_color
                        text breach_lit(rc["name"]):
                            yalign 0.5
                            xmaximum gui.combat_chip_name_w
                            size (gui.size_small if r_cur else gui.size_micro)
                            color r_name_color
            vbox:
                xalign 1.0
                yalign 0.5
                text "ROUND" style "breach_label_text" xalign 1.0
                text "[p_round]" style "breach_display_text" size gui.size_base xalign 1.0


## Band 2's right column -- the info sidebar (GDD 15.6): the rolled INITIATIVE
## ORDER (each combatant's name + their 1d20 initiative value, in initiative
## order, current actor in accent and the out-of-fight muted), over the
## scrolling combat log -- a tall, many-line feed. The ribbon tracks turn
## state; this panel is the rolled reference (the reference image).
screen combat_sidebar(combat, actor, sidebar_w):
    frame:
        background gui.panel_frame_fill
        foreground gui.panel_frame
        xsize sidebar_w
        yfill True
        padding (gui.panel_frame_pad, gui.panel_frame_pad)
        side "t c b":
            spacing gui.pad_s
            ## TOP -- the rolled initiative order (name + value), then the log's
            ## own section header.
            vbox:
                spacing gui.pad_xs
                xfill True
                use section_header("Initiative Order")
                for r_idx, r_cid in enumerate(combat["order"]):
                    $ rc = combat["combatants"][r_cid]
                    $ r_out = rc["dead"] or rc["downed"]
                    $ r_cur = (r_idx == combat["turn"])
                    python:
                        r_color = (gui.muted_text_color if r_out
                                   else (gui.breach_accent_color if r_cur
                                         else gui.breach_text_color))
                        r_name_max = (sidebar_w - 2 * gui.panel_frame_pad
                                      - gui.pad_s - gui.combat_init_val_w)
                    hbox:
                        xfill True
                        spacing gui.pad_s
                        text breach_lit(rc["name"]):
                            size gui.size_small
                            color r_color
                            yalign 0.5
                            xmaximum r_name_max
                        null:
                            xfill True
                        text ("%d" % rc["initiative"]):
                            size gui.size_small
                            color r_color
                            yalign 0.5
                use section_header("Combat Log")
            ## CENTRE -- the scrolling combat log, newest pinned to the bottom,
            ## many lines instead of one (15.6).
            viewport:
                scrollbars "vertical"
                mousewheel True
                yinitial 1.0
                yfill True
                xfill True
                vbox:
                    spacing gui.pad_xs
                    xfill True
                    for log_line in combat["log"]:
                        text breach_lit(log_line) size gui.size_micro color gui.muted_text_color
            ## BOTTOM -- the full-log opener (the big reading overlay).
            textbutton "Full log":
                style "breach_chip"
                xalign 1.0
                action SetScreenVariable("overlay", "log")


## Band 2 -- the stage (GDD 5.4 / 15.6): the battlefield on the LEFT (the four
## lane plates on a recessed dark well) and the info sidebar on the RIGHT
## (initiative order + the combat log). Depth is value, not art.
screen combat_stage(combat, actor, mode, pending, pending_option, reckless, p_chips, stage_y, stage_h, lanes_w, sidebar_w, plate_w, plate_h, active_lane, show_active):
    fixed:
        xpos 0
        ypos stage_y
        xsize config.screen_width
        ysize stage_h
        hbox:
            xpos gui.pad_m
            yalign 0.0
            xsize (config.screen_width - 2 * gui.pad_m)
            yfill True
            spacing gui.pad_m
            ## LEFT -- the recessed battlefield WELL (dark ground). The four
            ## lanes are individually framed cards (combat_plate) sitting on it;
            ## that sectioned look comes from the plates, not a shell frame. The
            ## floating combat text rises over the centre of the field.
            frame:
                background Solid(gui.breach_stage_color)
                xsize lanes_w
                yfill True
                padding (gui.pad_m, gui.pad_m)
                fixed:
                    xfill True
                    yfill True
                    ## the four framed lane cards + the no-man's-land seam
                    hbox:
                        align (0.5, 0.0)
                        spacing gui.pad_s
                        use combat_plate(combat, actor, "party", "back", "Party Backline", mode, pending, pending_option, reckless, p_chips, plate_w, plate_h, active_lane, show_active)
                        use combat_plate(combat, actor, "party", "front", "Party Frontline", mode, pending, pending_option, reckless, p_chips, plate_w, plate_h, active_lane, show_active)
                        add Solid(gui.breach_seam_color) xsize gui.pad_s ysize plate_h
                        use combat_plate(combat, actor, "enemy", "front", "Enemy Frontline", mode, pending, pending_option, reckless, p_chips, plate_w, plate_h, active_lane, show_active)
                        use combat_plate(combat, actor, "enemy", "back", "Enemy Backline", mode, pending, pending_option, reckless, p_chips, plate_w, plate_h, active_lane, show_active)
                    ## floating combat text, centred over the battlefield
                    use combat_floats()
            ## RIGHT -- the info sidebar: the rolled initiative order (top) over
            ## the scrolling combat log (fills the rest).
            use combat_sidebar(combat, actor, sidebar_w)


## The floating combat-text feed (GDD 15.6): newest brightest. Reads the
## module-level breach_floats_view the encounter loop drains into.
screen combat_floats():
    vbox:
        align (0.5, 0.5)
        spacing gui.pad_xs
        $ fl_n = len(breach_floats_view)
        for fl_i, fl in enumerate(breach_floats_view):
            $ fl_who = fl["who"]
            $ fl_text = fl["text"]
            $ fl_color = breach_float_color(fl["kind"])
            $ fl_alpha = max(0.3, 1.0 - 0.18 * (fl_n - 1 - fl_i))
            frame:
                background Solid(gui.breach_seam_color)
                padding (gui.pad_s, gui.pad_xs)
                xalign 0.5
                at Transform(alpha=fl_alpha)
                hbox:
                    spacing gui.pad_s
                    text fl_who size gui.size_micro color gui.muted_text_color yalign 0.5
                    text fl_text size gui.size_small color fl_color yalign 0.5


## Band 3 -- the active panel (GDD 15.6): a lit portrait seat, the class
## resource gauges, and the command buttons. The brightest lip runs along its
## top edge -- the eye anchors where the decision is made.
screen combat_action_panel(combat, actor, achar, p_pc, p_playable, mode, pending, spells, abilities, bonus_abilities, p_items, reckless, p_cancel, breach_tt, c_panel_y, c_panel_h):
    ## the panel's slate fill; the shared gold nineslice is added over the
    ## band below (a positioned screen-level overlay, so the body keeps its
    ## layout). Inner padding clears the corner ornament.
    frame:
        background Solid(gui.panel_color)
        xpos 0
        ypos c_panel_y
        xfill True
        ysize c_panel_h
        padding (gui.panel_frame_pad, gui.panel_frame_pad)
        if not p_playable:
            ## enemy turn / condition-blocked turn: a deliberate CENTERED
            ## state (who is acting + their telegraph), filling the panel --
            ## not a gaping void.
            use combat_wait_panel(actor)
        else:
            vbox:
                spacing gui.pad_s
                xfill True

                ## The tooltip readout line: condition chips, greyed targets,
                ## telegraphs, and list reasons all land here on hover.
                text (breach_tt or " ") size gui.size_small color gui.accent_bright_color

                hbox:
                    spacing gui.pad_l
                    xfill True

                    ## the active actor's lit seat -- the brightest thing in
                    ## the panel; a concentration ring when it applies.
                    frame:
                        background Solid(gui.breach_lit_panel_color)
                        padding (gui.pad_s, gui.pad_s)
                        yalign 0.5
                        if actor["concentration"]:
                            use combat_conc_ring(size=128):
                                use portrait_chip(achar, size=128)
                        else:
                            use portrait_chip(achar, size=128)
                    vbox:
                        spacing gui.pad_xs
                        xsize gui.combat_actor_col_w
                        yalign 0.5
                        $ p_actor_name = actor["name"]
                        text breach_lit(p_actor_name) style "breach_display_text"
                        text achar["class"].upper() style "breach_label_text"
                        ## resources read as one row each; a full caster (6 slot
                        ## tiers + Channel + pools) would overrun the panel, so
                        ## a long list scrolls inside the band instead of
                        ## spilling onto the quick-menu. Short lists render flat.
                        $ p_res = list(bch.resource_row(REG, achar).items())
                        if len(p_res) > 6:
                            viewport:
                                mousewheel True
                                scrollbars "vertical"
                                ysize gui.combat_list_h
                                xsize gui.combat_actor_col_w
                                vbox:
                                    spacing gui.pad_xs
                                    for res_key, res_entry in p_res:
                                        use breach_resource(res_entry["label"], res_entry["current"], res_entry["max"])
                        else:
                            for res_key, res_entry in p_res:
                                use breach_resource(res_entry["label"], res_entry["current"], res_entry["max"])

                    if mode == "main":
                        use combat_main_buttons(combat, actor, achar, spells, abilities, bonus_abilities, p_items, reckless)
                    elif mode == "spell_list":
                        use combat_spell_list(spells, p_cancel)
                    elif mode == "ability_list":
                        use combat_ability_list(abilities, p_cancel)
                    elif mode == "ability_option":
                        use combat_ability_options(abilities, achar, pending, p_cancel)
                    elif mode == "item_list":
                        use combat_item_list(p_items, p_cancel)
                    else:
                        vbox:
                            spacing gui.pad_s
                            yalign 0.5
                            text breach_mode_caption(mode, pending) size gui.size_base color gui.breach_text_color
                            textbutton "Cancel":
                                style "breach_frame_button"
                                action p_cancel
    ## the shared gold nineslice, positioned over the action-panel band
    add gui.panel_frame:
        xpos 0
        ypos c_panel_y
        xsize config.screen_width
        ysize c_panel_h


## The action panel's enemy-turn / blocked-turn state: centered in the panel,
## the acting combatant's name (display tier) over its telegraph/intent line,
## so the wait reads as deliberate rather than a void.
screen combat_wait_panel(actor):
    $ wp_tele = breach_telegraph_text(actor)
    $ wp_wait = ("%s acts..." % actor["name"] if actor["side"] == "enemy"
                 else "%s cannot act." % actor["name"])
    fixed:
        xfill True
        yfill True
        vbox:
            align (0.5, 0.5)
            spacing gui.pad_s
            text breach_lit(wp_wait) style "breach_display_text" xalign 0.5
            if wp_tele:
                text breach_lit(wp_tele):
                    size gui.size_base
                    color gui.breach_telegraph_color
                    xalign 0.5


## Overlays: the full log and the reactions settings page (15.6). One dark
## scrim sinks the whole stage so the modal is the only lit object.
screen combat_overlays(combat, overlay):
    if overlay:
        button:
            xsize config.screen_width
            ysize config.screen_height
            background Solid(gui.breach_scrim_color)
            action SetScreenVariable("overlay", None)
    if overlay == "log":
        frame:
            align (0.5, 0.5)
            xsize gui.modal_w_l
            background None
            use breach_modal():
                vbox:
                    spacing gui.pad_m
                    xfill True
                    use section_header("Combat Log")
                    viewport:
                        scrollbars "vertical"
                        mousewheel True
                        yinitial 1.0
                        ysize gui.list_well_h
                        vbox:
                            spacing gui.pad_xs
                            for log_line in combat["log"]:
                                text breach_lit(log_line) size gui.size_small color gui.breach_text_color
                    textbutton "Close":
                        style "breach_frame_button"
                        xalign 1.0
                        action SetScreenVariable("overlay", None)
    elif overlay == "reactions":
        use reaction_settings(SetScreenVariable("overlay", None))


## Lane cards: each lane is its OWN framed panel (the shared gold nineslice)
## sitting in a row on the recessed well -- the reference's sectioned look,
## NOT one frame around the whole battlefield. A lane is a clickable Move /
## lane-spell hotspot only when it is a candidate (so a unit-card button is
## never nested inside a plate button). The gold frame carries the STATE: a
## valid target wears the SELECTED frame (hovering it the HOVER frame), an
## invalid target the DISABLED frame; the active lane (current actor) wears
## the SELECTED frame, every other lane the normal frame. The party Backline
## turns danger the moment the Frontline empties (GDD 5.4 / 15.6).

screen combat_plate(combat, actor, side, lane, label, mode, pending, pending_option, reckless, p_chips, plate_w, plate_h, active_lane, show_active):
    $ pl_cand, pl_ok, pl_reason, pl_intent = breach_plate_target(combat, actor, side, lane, mode, pending)
    $ pl_exposed = (side == "party" and lane == "back" and bcombat.frontline_empty(combat, "party"))
    $ pl_active = (show_active and (side, lane) == active_lane)
    $ pl_fill = (gui.danger_color if pl_exposed else gui.panel_color)
    $ pl_members = [m for m in bcombat.combatants_on(combat, side, lane, alive_only=False) if not m["dead"]]
    if pl_cand:
        ## a Move / lane-spell target: the interactive framed panel -- the
        ## state frames mark valid (selected), hovered (hover) and invalid
        ## (insensitive -> disabled).
        button:
            style "breach_panel_button"
            background Solid(pl_fill)
            xsize plate_w
            ysize plate_h
            selected pl_ok
            sensitive pl_ok
            action (Return(pl_intent) if pl_ok else NullAction())
            tooltip (pl_reason if not pl_ok else label)
            use combat_plate_body(combat, actor, side, label, pl_exposed, pl_members, mode, pending, pending_option, reckless, False)
    else:
        ## a non-interactive lane: the active lane wears the SELECTED frame,
        ## every other lane the normal frame. Empty and populated lanes use
        ## this same card, so every lane reads consistently.
        frame:
            background Solid(pl_fill)
            foreground (gui.panel_frame_selected if pl_active else gui.panel_frame)
            xsize plate_w
            ysize plate_h
            padding (gui.panel_frame_pad, gui.panel_frame_pad)
            use combat_plate_body(combat, actor, side, label, pl_exposed, pl_members, mode, pending, pending_option, reckless, p_chips)


## A plate's contents: the lane header, then one unit card per occupant.
## In a single-target mode an occupant is a button (valid targets show an
## accent border via the same nested-frame technique).

screen combat_plate_body(combat, actor, side, label, exposed, members, mode, pending, pending_option, reckless, chips_active):
    vbox:
        spacing gui.pad_s
        xfill True
        ## the lane header is CENTERED so it clears the gold corner ornaments
        ## (which sit at the card's top corners); on an exposed (danger-red)
        ## card the caption goes light so it reads against the red fill.
        $ cap_color = (gui.breach_text_color if exposed else gui.muted_text_color)
        hbox:
            spacing gui.pad_s
            xalign 0.5
            text label.upper() style "breach_label_text" color cap_color
            if exposed:
                text "EXPOSED" style "breach_label_text" color gui.breach_text_color
        for m in members:
            $ u_cand, u_ok, u_reason, u_intent = breach_tile_target(combat, actor, m, mode, pending, pending_option, reckless)
            $ u_invalid = (u_cand and not u_ok)
            ## one transform per unit: Downed and invalid targets desaturate
            ## (sink into the dark); Hidden stays a translucent figure.
            python:
                if m["downed"]:
                    u_alpha = 0.55
                elif u_invalid:
                    u_alpha = 0.45
                elif "hidden" in m["conditions"]:
                    u_alpha = 0.5
                else:
                    u_alpha = 1.0
                if m["downed"] or u_invalid:
                    u_xform = Transform(matrixcolor=SaturationMatrix(0.0), alpha=u_alpha)
                else:
                    u_xform = Transform(alpha=u_alpha)
            if u_cand:
                button:
                    xfill True
                    background Solid(gui.breach_accent_color if u_ok else gui.panel_border_color)
                    hover_background Solid(gui.accent_bright_color if u_ok else gui.panel_border_color)
                    padding (gui.hairline, gui.hairline)
                    at u_xform
                    action (Return(u_intent) if u_ok else NullAction())
                    tooltip (u_reason if not u_ok else m["name"])
                    frame:
                        ## a valid target is lit by a soft amber wash behind
                        ## the card; the accent border is the reliable signal.
                        background Solid(gui.breach_accent_glow_color if u_ok else gui.bg_color)
                        xfill True
                        padding (gui.pad_s, gui.pad_s)
                        use combat_unit_card(combat, m, actor, False)
            else:
                frame:
                    xfill True
                    background Solid(gui.bg_color)
                    padding (gui.pad_s, gui.pad_s)
                    at u_xform
                    use combat_unit_card(combat, m, actor, chips_active)


## The unit card: placeholder portrait (colored rect + initials -- same
## pipeline as portrait_chip) beside the name and a RED HP bar with numbers
## (15.6). Condition / concentration / Bloodied / Downed / telegraph marks
## are preserved.

screen combat_unit_card(combat, c, actor, chips_active):
    $ uc_key = (c["char"]["class"] if c["kind"] == "pc" else c["cid"])
    $ uc_name = c["name"]
    $ uc_name_color = (gui.breach_accent_color if c["cid"] == actor["cid"]
                       else (gui.muted_text_color if c["downed"]
                             else gui.breach_text_color))
    $ uc_tele = breach_telegraph_text(c)
    hbox:
        spacing gui.pad_s
        xfill True
        ## placeholder portrait (colored rect + initials, real art later) with
        ## its state marks ON the figure: a cool concentration ring, a
        ## blood-drop at Bloodied, a threat-red telegraph caret (GDD 15.6).
        fixed:
            fit_first True
            yalign 0.5
            if c["concentration"]:
                use combat_conc_ring(size=64):
                    frame:
                        xysize (64, 64)
                        background Solid(breach_placeholder_color(uc_key))
                        padding (0, 0)
                        text breach_initials(uc_name):
                            align (0.5, 0.5)
                            size gui.size_base
                            color gui.breach_text_color
            else:
                frame:
                    xysize (64, 64)
                    background Solid(breach_placeholder_color(uc_key))
                    padding (0, 0)
                    text breach_initials(uc_name):
                        align (0.5, 0.5)
                        size gui.size_base
                        color gui.breach_text_color
            if bcombat.bloodied(c):
                text "●" size gui.size_small color gui.breach_blood_color align (1.0, 1.0)
            if uc_tele:
                if chips_active:
                    textbutton "!":
                        align (1.0, 0.0)
                        style "breach_chip"
                        text_color gui.breach_telegraph_color
                        action NullAction()
                        tooltip uc_tele
                else:
                    text "!" size gui.size_small color gui.breach_telegraph_color align (1.0, 0.0)
        vbox:
            spacing gui.pad_xs
            yalign 0.5
            text uc_name:
                size gui.size_small
                color uc_name_color
                xmaximum gui.combat_card_name_w
            if c["downed"]:
                text "Downed" size gui.size_micro color gui.muted_text_color
            else:
                use hp_bar(c["hp"], c["hp_max"], width=gui.combat_card_hp_w)
                if c["temp_hp"]:
                    $ uc_temp = c["temp_hp"]
                    text "+[uc_temp] temporary" size gui.size_micro color gui.muted_text_color
                if c["conditions"]:
                    hbox:
                        spacing gui.pad_xs
                        for cond_id in c["conditions"]:
                            $ uc_cond = REG["conditions"].get(cond_id)
                            $ uc_cond_name = (uc_cond["name"] if uc_cond else cond_id.replace("_", " ").title())
                            $ uc_cond_tip = (breach_player_text(REG, "conditions", cond_id, uc_cond["effect"]) if uc_cond else "")
                            if chips_active:
                                textbutton uc_cond_name:
                                    style "breach_chip"
                                    action NullAction()
                                    tooltip uc_cond_tip
                            else:
                                text uc_cond_name size gui.size_micro color gui.breach_accent_color
                ## the telegraph caret above carries the warning on hover; in
                ## targeting modes hover is busy with target reasons, so spell
                ## the warning out here too (GDD 5.8 / 15.6: hover reads it).
                if uc_tele and not chips_active:
                    text uc_tele size gui.size_micro color gui.breach_telegraph_color


## The main command rows: Attack · Spells · Abilities · Item · Move ·
## End Turn · Flee (authored-optional fights only), plus the Bonus Action
## row that exists ONLY while something grants a usable bonus ability —
## the only-when-granted rule as literal interface (GDD 5.2 / 15.6).

screen combat_main_buttons(combat, actor, achar, spells, abilities, bonus_abilities, p_items, reckless):
    $ mb_action_free = not actor["acted"]["action"]
    $ mb_move_ok, mb_move_reason = breach_move_check(actor)
    $ mb_reckless_owner = bch.has_feature(achar, "barbarian_reckless_attack")
    vbox:
        spacing gui.pad_s
        yalign 0.5
        ## Row 1 -- the primary actions (first position + the row split carry
        ## the hierarchy).
        hbox:
            spacing gui.pad_s
            textbutton "Attack":
                style "breach_frame_button"
                sensitive mb_action_free
                tooltip ("Action spent." if not mb_action_free else None)
                action SetScreenVariable("mode", "attack")
            if mb_reckless_owner:
                ## the reckless toggle rides the next Attack (GDD 7.5)
                textbutton "Reckless":
                    style "breach_frame_button"
                    selected reckless
                    tooltip breach_player_text(REG, "features", "barbarian_reckless_attack", REG["features"]["barbarian_reckless_attack"]["effect"])
                    action ToggleScreenVariable("reckless")
            textbutton "Spells":
                style "breach_frame_button"
                sensitive bool(spells)
                action SetScreenVariable("mode", "spell_list")
            textbutton "Abilities":
                style "breach_frame_button"
                sensitive bool(abilities)
                action SetScreenVariable("mode", "ability_list")
            textbutton "Item":
                style "breach_frame_button"
                sensitive (mb_action_free and bool(p_items))
                action SetScreenVariable("mode", "item_list")
            textbutton "Move":
                style "breach_frame_button"
                sensitive mb_move_ok
                tooltip mb_move_reason
                action SetScreenVariable("mode", "move")
        ## Row 2 -- turn management (quieter, same style)
        hbox:
            spacing gui.pad_s
            textbutton "End Turn":
                style "breach_frame_button"
                action Return(("end",))
            textbutton "Reactions":
                style "breach_frame_button"
                action SetScreenVariable("overlay", "reactions")
            if combat["flee_allowed"]:
                textbutton "Flee":
                    style "breach_frame_button"
                    action Return(("flee",))
        ## Bonus Action row -- ONLY when something grants one (GDD 5.2 /
        ## 15.6): a light turns on. The amber wash + lamplit ledge mark the
        ## granted extra action; nothing renders (no reserved space) otherwise.
        if bonus_abilities:
            frame:
                background Solid(gui.breach_accent_glow_color)
                padding (gui.pad_s, gui.pad_xs)
                vbox:
                    spacing gui.pad_xs
                    use breach_lip(gui.breach_accent_color)
                    hbox:
                        spacing gui.pad_s
                        text "BONUS ACTION" style "breach_label_text" color gui.breach_accent_color yalign 0.5
                        for ba in bonus_abilities:
                            $ ba_id = ba["id"]
                            $ ba_fid = bhooks.ABILITY_IMPL[ba_id]["feature"]
                            $ ba_action = breach_ability_click(ba)
                            textbutton ba["name"]:
                                style "breach_frame_button"
                                tooltip breach_player_text(REG, "features", ba_fid, REG["features"][ba_fid]["effect"])
                                action ba_action


screen combat_spell_list(spells, p_cancel):
    vbox:
        spacing gui.pad_s
        xfill True
        text "SPELLS" style "breach_label_text"
        viewport:
            scrollbars "vertical"
            mousewheel True
            ysize gui.combat_list_h
            xfill True
            vbox:
                spacing gui.pad_xs
                xfill True
                for sp_entry in spells:
                    $ sp_id = sp_entry["id"]
                    $ sp_rec = REG["spells"][sp_id]
                    $ sp_click = breach_spell_click(sp_rec)
                    $ sp_reaction = (sp_rec.get("action") == "reaction")
                    $ sp_usable = (sp_entry["castable"] and sp_click != "unsupported" and not sp_reaction)
                    $ sp_reason = (sp_entry["reason"] if not sp_entry["castable"]
                                   else ("Casts itself from its reaction prompt." if sp_reaction
                                         else ("Not supported yet." if sp_click == "unsupported" else None)))
                    $ sp_tags = (("Cantrip" if sp_entry["tier"] == 0 else "Tier %d" % sp_entry["tier"])
                                 + (" · Bonus" if sp_rec.get("action") == "bonus" else "")
                                 + (" · Concentration" if sp_rec.get("concentration") else ""))
                    $ sp_action = ([SetScreenVariable("pending", sp_id), SetScreenVariable("mode", "spell_lane")]
                                   if sp_click == "lane"
                                   else (Return(("cast", sp_id, None, None))
                                         if sp_click == "self"
                                         else [SetScreenVariable("pending", sp_id), SetScreenVariable("mode", "spell_target")]))
                    button:
                        style "breach_card"
                        sensitive sp_usable
                        action sp_action
                        tooltip breach_player_text(REG, "spells", sp_id, sp_rec["effect"])
                        hbox:
                            spacing gui.pad_m
                            xfill True
                            text sp_entry["name"]:
                                size gui.size_base
                                color (gui.breach_text_color if sp_usable else gui.muted_text_color)
                            text sp_tags size gui.size_small color gui.muted_text_color yalign 0.5
                            if sp_reason:
                                text sp_reason size gui.size_small color gui.muted_text_color yalign 0.5 xalign 1.0
        textbutton "Cancel":
            style "breach_frame_button"
            action p_cancel


screen combat_ability_list(abilities, p_cancel):
    vbox:
        spacing gui.pad_s
        xfill True
        text "ABILITIES" style "breach_label_text"
        viewport:
            scrollbars "vertical"
            mousewheel True
            ysize gui.combat_list_h
            xfill True
            vbox:
                spacing gui.pad_xs
                xfill True
                for ab in abilities:
                    $ ab_id = ab["id"]
                    $ ab_fid = bhooks.ABILITY_IMPL[ab_id]["feature"]
                    $ ab_kind = {"action": "Action", "bonus": "Bonus", "free": "Free"}.get(ab["action"], ab["action"])
                    $ ab_tags = ab_kind + ("" if ab["uses_left"] is None else " · %d left" % ab["uses_left"])
                    $ ab_action = breach_ability_click(ab)
                    button:
                        style "breach_card"
                        sensitive ab["usable"]
                        action ab_action
                        tooltip breach_player_text(REG, "features", ab_fid, REG["features"][ab_fid]["effect"])
                        hbox:
                            spacing gui.pad_m
                            xfill True
                            text ab["name"]:
                                size gui.size_base
                                color (gui.breach_text_color if ab["usable"] else gui.muted_text_color)
                            text ab_tags size gui.size_small color gui.muted_text_color yalign 0.5
                            if ab["reason"]:
                                text ab["reason"] size gui.size_small color gui.muted_text_color yalign 0.5 xalign 1.0
        textbutton "Cancel":
            style "breach_frame_button"
            action p_cancel


## The ability option menu (hooks.use_ability option=): Aspects, Divine
## Spark's radiant/necrotic choice, Open Hand techniques riding Flurry.
## Labels and rules text come from the owning feature's registry options;
## abilities whose option is not required also offer a plain use (GDD
## 7.11 L825-826: each Flurry hit MAY impose a technique).

screen combat_ability_options(abilities, achar, pending, p_cancel):
    $ ao_ab = ([a for a in abilities if a["id"] == pending] or [None])[0]
    $ ao_opts = ao_ab["options"] if ao_ab else []
    $ ao_target = bool(ao_ab and ao_ab["needs_target"])
    $ ao_required = bool(bhooks.ABILITY_IMPL.get(pending, {}).get("option_required"))
    vbox:
        spacing gui.pad_s
        xfill True
        yalign 0.5
        text breach_mode_caption("ability_option", pending) size gui.size_base color gui.breach_text_color
        hbox:
            spacing gui.pad_s
            for ao_opt in ao_opts:
                $ ao_name, ao_tip = breach_ability_option_info(achar, ao_opt)
                $ ao_action = ([SetScreenVariable("pending_option", ao_opt),
                                SetScreenVariable("mode", "ability_target")]
                               if ao_target
                               else Return(("ability", pending, None, ao_opt)))
                textbutton ao_name:
                    style "breach_frame_button"
                    tooltip ao_tip
                    action ao_action
            if not ao_required:
                $ ao_plain = ([SetScreenVariable("pending_option", None),
                               SetScreenVariable("mode", "ability_target")]
                              if ao_target
                              else Return(("ability", pending, None, None)))
                textbutton "None":
                    style "breach_frame_button"
                    tooltip "Use without an option."
                    action ao_plain
        textbutton "Cancel":
            style "breach_frame_button"
            action p_cancel


screen combat_item_list(p_items, p_cancel):
    vbox:
        spacing gui.pad_s
        xfill True
        text "CONSUMABLES (SHARED INVENTORY)" style "breach_label_text"
        viewport:
            scrollbars "vertical"
            mousewheel True
            ysize gui.combat_list_h
            xfill True
            vbox:
                spacing gui.pad_xs
                xfill True
                for it_id, it_count in p_items:
                    $ it_rec = REG["consumables"][it_id]
                    use item_card(it_id, it_rec, count=it_count,
                                  action=[SetScreenVariable("pending", it_id),
                                          SetScreenVariable("mode", "item_target")],
                                  info=breach_player_text(REG, "consumables", it_id, it_rec["effect"]))
        textbutton "Cancel":
            style "breach_frame_button"
            action p_cancel


## The reaction prompt: a modal card with the trigger and the cost, plus
## the inline set-to-Always/Never links (GDD 5.2 / 15.6 L1553-1556).

screen reaction_prompt(card):
    modal True
    add Solid(gui.breach_scrim_color)
    $ rp_trigger = str(card.get("trigger") or "").replace("_", " ")
    $ rp_cost = card.get("cost") or "Reaction"
    frame:
        align (0.5, 0.4)
        xsize gui.modal_w_s
        background None
        use breach_tooltip():
            vbox:
                spacing gui.pad_m
                xfill True
                use section_header(card["title"])
                text "Trigger: [rp_trigger]" size gui.size_micro color gui.muted_text_color
                text "Cost: [rp_cost]" size gui.size_small color gui.breach_accent_color
                hbox:
                    spacing gui.pad_m
                    textbutton "Use":
                        style "breach_frame_button"
                        action Return(True)
                    textbutton "Pass":
                        style "breach_frame_button"
                        action Return(False)
                hbox:
                    spacing gui.pad_m
                    textbutton "Always use this":
                        style "breach_chip"
                        action [Function(breach_set_reaction_pref, card, "always"), Return(True)]
                    textbutton "Never use this":
                        style "breach_chip"
                        action [Function(breach_set_reaction_pref, card, "never"), Return(False)]


## The reactions management page (15.6): per-ability Ask / Always / Never,
## written straight into each character's reaction_preferences.

screen reaction_settings(close_action):
    frame:
        align (0.5, 0.5)
        xsize gui.modal_w_l
        background None
        use breach_modal():
            vbox:
                spacing gui.pad_m
                xfill True
                use section_header("Reactions")
                text "Ask prompts in combat; Always resolves silently; Never declines." size gui.size_small color gui.muted_text_color
                viewport:
                    scrollbars "vertical"
                    mousewheel True
                    ysize gui.list_well_h
                    xfill True
                    vbox:
                        spacing gui.pad_s
                        xfill True
                        for member in gs["party"]:
                            text member["name"] size gui.size_base color gui.breach_accent_color
                            for r_aid, r_name, r_default in breach_reaction_abilities(member):
                                $ r_cur = member["reaction_preferences"].get(r_aid, r_default)
                                hbox:
                                    spacing gui.pad_s
                                    text r_name size gui.size_small xsize gui.stat_label_w yalign 0.5
                                    for r_mode in ("ask", "always", "never"):
                                        textbutton r_mode.capitalize():
                                            style "breach_chip"
                                            selected (r_cur == r_mode)
                                            action SetDict(member["reaction_preferences"], r_aid, r_mode)
                textbutton "Close":
                    style "breach_frame_button"
                    xalign 1.0
                    action close_action


## Victory (15.6): XP with threshold progress and the level-up badge —
## results were already flushed to the party by finish_combat.

screen combat_victory(combat, summary):
    modal True
    add Solid(gui.bg_color)
    $ v_xp = summary.get("xp", 0)
    $ v_mc = gs["party"][0]
    $ v_name = v_mc["name"]
    $ v_cur = v_mc["xp"]
    $ v_badge = bch.can_level_up(REG, v_mc)
    frame:
        align (0.5, 0.4)
        xsize gui.modal_w
        background None
        use breach_modal():
            vbox:
                spacing gui.pad_m
                xfill True
                use section_header("Victory")
                text "+[v_xp] XP" size gui.size_title color gui.success_color
                if v_mc["level"] >= 12:
                    text "[v_name]: [v_cur] XP — max level" size gui.size_base color gui.breach_text_color
                else:
                    $ v_lo = bch.xp_threshold(REG, v_mc["level"])
                    $ v_hi = bch.xp_threshold(REG, v_mc["level"] + 1)
                    text "[v_name]: [v_cur] / [v_hi] XP" size gui.size_base color gui.breach_text_color
                    ## the shared progress component (one bar style everywhere)
                    use breach_progress(min(v_cur, v_hi) - v_lo, max(1, v_hi - v_lo))
                if v_badge:
                    use breach_lip(gui.breach_accent_color)
                    text "Level up available — open the character sheet." size gui.size_base color gui.breach_accent_color
                $ v_loot = summary.get("loot") or {}
                if v_loot.get("items") or v_loot.get("gold"):
                    use breach_lip(gui.success_color)
                    use section_header("Loot")
                    for v_iid in v_loot.get("items", []):
                        text breach_lit(breach_item_name(v_iid)) size gui.size_base color gui.breach_text_color
                    if v_loot.get("gold"):
                        $ v_gold = v_loot["gold"]
                        text "[v_gold] gold" size gui.size_base color gui.breach_accent_color
                textbutton "Continue":
                    style "breach_frame_button"
                    xalign 1.0
                    action Return(None)


## Defeat (GDD 5.5 / 11.2): the whole party Downed is the end — no
## exceptions. Continue goes to the main menu.

screen combat_defeat(combat):
    modal True
    add Solid(gui.bg_color)
    frame:
        align (0.5, 0.4)
        xsize gui.modal_w
        background None
        use breach_modal():
            vbox:
                spacing gui.pad_m
                xfill True
                use section_header("Game Over")
                text "The whole party is Downed. The game is over." size gui.size_base color gui.danger_color
                textbutton "Continue":
                    style "breach_frame_button"
                    xalign 1.0
                    action MainMenu(confirm=False)
