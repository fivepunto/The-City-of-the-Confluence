# The character sheet (GDD 15.3): three tabs, all party portraits on top,
# click to select (no arrow-cycling). View-only -- the Level up button
# returns ("levelup", char_id) to the caller; spell PREPARATION never
# happens here (readying is a Camp activity, 15.2/15.3).
#
# All rules text comes from the registry (features/talents/traits "effect"
# fields); this file contains only UI labels.

screen character_sheet(initial_index=0):
    modal True
    add Solid(gui.bg_color)

    default sel_index = initial_index
    default sheet_tab = "overview"

    $ sel = min(sel_index, len(gs["party"]) - 1)
    $ member = gs["party"][sel]
    $ caster = bch.caster_info(REG, member)
    # A non-caster has no Spells tab; fall back if one was left selected.
    $ cur_tab = ("overview" if (sheet_tab == "spells" and not caster)
                 else sheet_tab)
    # Tabs are data-derived: Spells appears only for casters (15.3).
    $ sheet_tabs = [("overview", "Overview"), ("features", "Features")]
    if caster:
        $ sheet_tabs = sheet_tabs + [("spells", "Spells")]

    frame:
        background None
        align (0.5, 0.5)
        xsize 1720
        ysize 1020

        vbox:
            spacing gui.pad_m
            xfill True

            ## Header band: the sheet's chrome -- title + exits on one line
            ## (title left / actions right, the reference HUD split), the party
            ## row (the selected member is the lit focal chip), then the tabs --
            ## raised over the content with a lamplit lip beneath.
            frame:
                style "breach_band"
                xfill True
                padding (gui.pad_l, gui.pad_m)
                vbox:
                    spacing gui.pad_m
                    xfill True

                    ## Title left, the sheet's two exits right.
                    hbox:
                        xfill True
                        yalign 0.5
                        use breach_title("Character Sheet")
                        null:
                            xfill True
                        hbox:
                            spacing gui.pad_s
                            yalign 0.5
                            xalign 1.0
                            if bch.can_level_up(REG, member):
                                textbutton "Level up":
                                    style "breach_frame_button"
                                    action Return(("levelup", member["id"]))
                            textbutton "Close":
                                style "breach_frame_button"
                                action Return(None)

                    ## All party portraits: click to select (15.3).
                    hbox:
                        spacing gui.pad_m
                        for i, m in enumerate(gs["party"]):
                            use portrait_chip(m, size=128,
                                              action=SetScreenVariable("sel_index", i),
                                              selected=(i == sel),
                                              show_hp=True,
                                              badge=bch.can_level_up(REG, m))

                    ## Tab row -- the shared small-caps tab bar.
                    use tab_bar(sheet_tabs, cur_tab,
                                lambda k: SetScreenVariable("sheet_tab", k),
                                tab_style="breach_frame_button")
            use breach_lip(gui.breach_accent_color)

            use breach_panel():
                viewport:
                    scrollbars "vertical"
                    mousewheel True
                    draggable True
                    xfill True
                    ysize gui.list_well_h

                    if cur_tab == "overview":
                        use charsheet_overview(member)
                    elif cur_tab == "features":
                        use charsheet_features(member)
                    else:
                        use charsheet_spells(member)


## Overview tab (15.3): the player's own numbers are the only visible math
## in the game -- portrait, class/level, XP, abilities, AC/HP/initiative/
## proficiency, saves, skills, and the per-class resource row.

screen charsheet_overview(member):
    ## A two-column composition; each region is its own framed card so it
    ## reads as a panel, not a flat run of text. The identity card is the ONE
    ## lit focal surface of the body; the stat panels stay quiet around it.
    hbox:
        spacing gui.pane_gap
        xfill True

        ## Left column: identity (focal), combat numbers, resources.
        vbox:
            spacing gui.pad_m
            xsize gui.split_list_w
            use charsheet_identity(member)
            use charsheet_combat(member)
            use charsheet_resources(member)

        ## Right column: abilities, saves, skills.
        vbox:
            spacing gui.pad_m
            xsize gui.detail_pane_w
            use charsheet_abilities(member)
            use charsheet_saves(member)
            use charsheet_skills(member)


## Overview region -- the identity card: portrait, name, class/level, and the
## XP bar (progress to the next level; full at the level cap). This is the
## body's ONE lit focal surface (breach_panel_lit).
screen charsheet_identity(member):
    use breach_panel_lit():
        vbox:
            spacing gui.pad_l
            xfill True
            $ cls_name = REG["classes"][member["class"]]["name"]
            hbox:
                spacing gui.pad_l
                use portrait_chip(member, size=128)
                vbox:
                    spacing gui.pad_xs
                    yalign 0.5
                    text breach_lit(member["name"]):
                        style "breach_display_text"
                        size gui.size_title
                        color gui.breach_text_color
                    text breach_lit("%s — Level %d" % (cls_name, member["level"])):
                        style "breach_label_text"
                        size gui.size_small

            ## XP: progress from this level's threshold to the next; a full
            ## bar at the level cap (12).
            vbox:
                spacing gui.pad_xs
                xfill True
                text "EXPERIENCE" style "breach_label_text"
                if member["level"] >= 12:
                    use breach_progress(1, 1, label="%d XP — max level" % member["xp"])
                else:
                    $ xp_lo = bch.xp_threshold(REG, member["level"])
                    $ xp_hi = bch.xp_threshold(REG, member["level"] + 1)
                    use breach_progress(min(member["xp"], xp_hi) - xp_lo,
                                        max(1, xp_hi - xp_lo),
                                        label="%d / %d XP" % (member["xp"], xp_hi))


## Overview region -- the combat numbers: AC / Initiative / Proficiency as one
## instrument cluster, and the HP bar with any temporary HP.
screen charsheet_combat(member):
    use breach_panel():
        vbox:
            spacing gui.pad_m
            xfill True
            use section_header("Combat")
            ## The stat triple, seated in a recessed strip so the three
            ## numbers read as one instrument cluster (the reference HUD group).
            frame:
                style "breach_well"
                xfill True
                hbox:
                    xfill True
                    use breach_stat_cell("AC", bch.ac(REG, member))
                    null:
                        xfill True
                    use breach_stat_cell("Initiative",
                                         "%+d" % bch.initiative_mod(member))
                    null:
                        xfill True
                    use breach_stat_cell("Proficiency",
                                         "+%d" % bch.proficiency(member),
                                         value_color=gui.breach_accent_color)
            vbox:
                spacing gui.pad_xs
                text "HEALTH" style "breach_label_text"
                use hp_bar(member["hp"], member["hp_max"])
                if member["temp_hp"]:
                    text "+[member['temp_hp']] temporary" size gui.size_micro color gui.muted_text_color


## Overview region -- the per-class resource pools as amber gauges (lit fill
## vs dim track).
screen charsheet_resources(member):
    use breach_panel():
        vbox:
            spacing gui.pad_m
            xfill True
            use section_header("Resources")
            $ res_rows = bch.resource_row(REG, member)
            if res_rows:
                vbox:
                    spacing gui.pad_s
                    for res_key, res_entry in res_rows.items():
                        use breach_resource_gauge(res_entry["label"], res_entry["current"], res_entry["max"])
            else:
                use breach_empty_state("No tracked resources")


## Overview region -- the six ability scores and modifiers (one row per
## ability, the shared list-row vocabulary).
screen charsheet_abilities(member):
    use breach_panel():
        vbox:
            spacing gui.pad_m
            xfill True
            use section_header("Abilities")
            vbox:
                spacing gui.pad_s
                for ability in bch.ABILITIES:
                    use breach_list_row(
                        bui.creation_ability_word(ability),
                        subtitle="Score %d" % member["abilities"][ability],
                        meta="%+d" % bch.ability_mod(member, ability),
                        meta_color=gui.breach_accent_color)


## Overview region -- the saving throws (proficiency marker + modifier).
screen charsheet_saves(member):
    use breach_panel():
        vbox:
            spacing gui.pad_m
            xfill True
            use section_header("Saving Throws")
            vbox:
                spacing gui.pad_s
                for ability in bch.ABILITIES:
                    $ save_prof = ability in member["save_proficiencies"]
                    use breach_list_row(
                        bui.creation_ability_word(ability),
                        subtitle=("Proficient" if save_prof else ""),
                        meta="%+d" % bch.save_mod(member, ability),
                        title_color=(gui.breach_accent_color if save_prof
                                     else gui.breach_text_color),
                        meta_color=gui.breach_accent_color)


## Overview region -- the nine skills (proficiency marker, accent-tinted name
## when proficient, ability, modifier, expertise marker).
screen charsheet_skills(member):
    use breach_panel():
        vbox:
            spacing gui.pad_m
            xfill True
            use section_header("Skills")
            vbox:
                spacing gui.pad_s
                for skill in REG["skills"].values():
                    $ skill_prof = skill["id"] in member["skills"]["proficiencies"]
                    $ skill_exp = skill["id"] in member["skills"]["expertise"]
                    # Subtitle = governing ability, plus an expertise marker.
                    $ skill_sub = bui.creation_ability_word(skill["ability"])
                    if skill_exp:
                        $ skill_sub = skill_sub + " · Expertise"
                    # Proficient skill names tint with the accent (15.7).
                    use breach_list_row(
                        skill["name"],
                        subtitle=skill_sub,
                        meta="%+d" % bch.skill_mod(REG, member, skill["id"]),
                        title_color=(gui.breach_accent_color if skill_prof
                                     else gui.breach_text_color),
                        meta_color=gui.breach_accent_color)


## Features tab (15.3): class features in level order (the LEVELUP
## manifest), then talents, then the human traits -- all text from the
## shared registry, each as a framed detail row.

screen charsheet_features(member):
    vbox:
        spacing gui.pad_l
        xfill True

        use breach_panel():
            vbox:
                spacing gui.pad_m
                xfill True
                use section_header("Class Features")
                vbox:
                    spacing gui.pad_s
                    for lvl in range(1, member["level"] + 1):
                        for fid in REG["classes"][member["class"]]["levelup"][lvl]["features"]:
                            $ feat = REG["features"][fid]
                            use breach_list_row(
                                feat["name"],
                                subtitle=breach_player_text(REG, "features", fid, feat["effect"]),
                                meta="Level %d" % lvl,
                                title_color=gui.breach_accent_color,
                                meta_color=gui.muted_text_color)

        use breach_panel():
            vbox:
                spacing gui.pad_m
                xfill True
                use section_header("Talents")
                if member["talents"]:
                    vbox:
                        spacing gui.pad_s
                        for tid in member["talents"]:
                            $ talent = REG["talents"][tid]
                            use breach_list_row(
                                talent["name"],
                                subtitle=breach_player_text(REG, "talents", tid, talent["effect"]),
                                title_color=gui.breach_accent_color)
                else:
                    use breach_empty_state("No talents yet")

        use breach_panel():
            vbox:
                spacing gui.pad_m
                xfill True
                use section_header("Human Traits")
                vbox:
                    spacing gui.pad_s
                    for trait in REG["core"]["human"]["traits"].values():
                        use breach_list_row(
                            trait["name"],
                            subtitle=breach_player_text(REG, "human", trait["id"], trait["effect"]),
                            title_color=gui.breach_accent_color)


## Spells tab (15.3, casters only): cantrips and the prepared list,
## view-only, labeled "Prepared at Camp." Readying happens at Camp (15.2).

screen charsheet_spells(member):
    vbox:
        spacing gui.pad_l
        xfill True

        use breach_panel():
            vbox:
                spacing gui.pad_m
                xfill True
                text "Prepared at Camp." style "breach_label_text"
                use section_header("Cantrips")
                if member["spells"]["cantrips"]:
                    vbox:
                        spacing gui.pad_s
                        for sid in member["spells"]["cantrips"]:
                            use breach_list_row(REG["spells"][sid]["name"],
                                                icon_key=sid)
                else:
                    use breach_empty_state("No cantrips known")

        use breach_panel():
            vbox:
                spacing gui.pad_m
                xfill True
                use section_header("Prepared Spells")
                $ always_ids = bch.always_prepared(REG, member)
                if member["spells"]["prepared"] or always_ids:
                    vbox:
                        spacing gui.pad_s
                        for sid in member["spells"]["prepared"]:
                            use breach_list_row(REG["spells"][sid]["name"],
                                                icon_key=sid)
                        for sid in always_ids:
                            use breach_list_row(REG["spells"][sid]["name"],
                                                icon_key=sid,
                                                meta="always prepared",
                                                meta_color=gui.breach_accent_color)
                else:
                    use breach_empty_state("Nothing prepared")
