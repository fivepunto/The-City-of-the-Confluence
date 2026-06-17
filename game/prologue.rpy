# The scripted prologue, "The Road to Veycross" (GDD #17.2). This implements
# the BEATS exactly as written; it does NOT write story content (CLAUDE.md P5).
# Every owner-authored line is a single bracketed placeholder
# ("[TO BE WRITTEN BY THE PROJECT OWNER]"); the one line the GDD quotes
# verbatim -- the trader's "Hey, you. You're finally awake." -- is rendered as
# written. The interface stays hidden (the prologue is dialogue mode
# throughout, #13.1) until Free Mode begins at guild membership.
#
# Owner-authored, per #17.2 L1739-1741: the trader's name + dialogue set, the
# guard dialogue, the receptionist's name + dialogue, the intro-card prose, and
# the districts reachable at Free Mode start (GAPS G-038). Bracketed speakers
# stand in for the owner-named characters; bracketed lines mark every beat.

image black = Solid(gui.bg_color)


## The intro card (#17.2 step 4): full-screen centred text. The prose is
## owner content; click to continue.
screen breach_intro_card(card_text):
    modal True
    add Solid(gui.bg_color)
    text card_text:
        align (0.5, 0.5)
        size gui.size_heading
        color gui.breach_text_color
        text_align 0.5
        xmaximum 1200
    button:
        xfill True
        yfill True
        background None
        action Return(None)


label prologue:
    $ gs = bstate.new_game_state(REG)
    $ store.hud_visible = False          # scripted: no interface yet (#13.1)

    # 1-2. Start -> character creation, including the Race display step (#3).
    call character_creation

    # 3. A one-second fade to black (#17.2 L1718).
    scene black with Fade(1.0, 0.0, 0.0)

    # 4. An intro card introducing Veycross -- owner prose (#17.2 L1719-1720).
    call screen breach_intro_card("[[Intro card — TO BE WRITTEN BY THE PROJECT OWNER]")

    # 5. The protagonist wakes in a trader's caravan (#17.2 L1721-1724). The
    #    trader's opening line is quoted in the doc; the rest is owner content.
    scene black
    "[[Trader]" "Hey, you. You're finally awake."
    "[[Trader]" "[[TO BE WRITTEN BY THE PROJECT OWNER]"
    # ...he asks the protagonist's plans in Veycross -> dialogue options.
    menu:
        "[[First option — TO BE WRITTEN BY THE PROJECT OWNER]":
            pass
        "[[Second option — TO BE WRITTEN BY THE PROJECT OWNER]":
            pass

    # 6. He's glad the journey was safe -- and a wolf approaches as he says it;
    #    the bargain (protection for passage) comes due (#17.2 L1725-1727).
    "[[Trader]" "[[TO BE WRITTEN BY THE PROJECT OWNER]"
    "[[TO BE WRITTEN BY THE PROJECT OWNER]"

    # 7. Tutorial combat: the protagonist alone vs one Young Wolf (#11.2).
    #    Losing is a real game over -- combat_defeat returns to the main menu
    #    (#17.2 L1728-1729).
    call combat_encounter(["young_wolf"])

    # 8. After the fight: the city entrance; their paths split (#17.2 L1730).
    scene black
    "[[TO BE WRITTEN BY THE PROJECT OWNER]"

    # 9. The gate: a guard asks the protagonist's business; whatever the
    #    answer, he directs them to the Guildhall (#17.2 L1731-1733).
    "[[Gate Guard]" "[[TO BE WRITTEN BY THE PROJECT OWNER]"
    menu:
        "[[First option — TO BE WRITTEN BY THE PROJECT OWNER]":
            pass
        "[[Second option — TO BE WRITTEN BY THE PROJECT OWNER]":
            pass
    "[[Gate Guard]" "[[TO BE WRITTEN BY THE PROJECT OWNER]"

    # 10. The Guildhall: the receptionist -> the protagonist becomes a member
    #     of the Lamplighter Guild (#17.2 L1734-1736).
    "[[Receptionist]" "[[TO BE WRITTEN BY THE PROJECT OWNER]"
    "[[Receptionist]" "[[TO BE WRITTEN BY THE PROJECT OWNER]"
    $ gs["flags"]["lamplighter_member"] = True

    # 11. Free Mode begins: the full interface enables, including the city map
    #     (#17.2 L1737, #13.1 L1390-1393). The interface arriving IS the signal.
    "[[TO BE WRITTEN BY THE PROJECT OWNER]"
    call city_free_mode
    return
