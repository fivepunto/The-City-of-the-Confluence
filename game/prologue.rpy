# The scripted prologue, "The Road to Veycross" (GDD #17.2). The BEATS are
# locked by the GDD; the dialogue prose dropped into those beats is the PROJECT
# OWNER's, authored content (no story is invented here, CLAUDE.md P5). The MC
# never speaks -- menu choices carry the player's intent; the NPCs and the
# narrator carry the scene.
#
# Engine wiring uses the REAL call forms (verified against the codebase, not the
# draft's best-guess names): gs init via bstate.new_game_state, the creation
# wizard via `call character_creation`, the tutorial fight via
# `call combat_encounter`, Free Mode via `call city_free_mode`, and the guild
# membership flag gs["flags"]["lamplighter_member"]. The interface stays hidden
# (dialogue mode, #13.1) until Free Mode begins; from there city_free_mode owns
# HUD visibility, so the prologue never forces it on.
#
# Speakers follow the established codebase convention -- string-literal speaker
# names, no Character() objects (the project defines none). Relpak = the trader;
# Imara = the guild receptionist; the gate guard is generic per the owner draft.
#
# GAPS surfaced rather than invented (CLAUDE.md iron rules):
#   - Art: no caravan-road / city-gate / guildhall backgrounds and no NPC or
#     wolf sprites exist, so every beat uses `scene black` and the narrator
#     carries the setting. Each scene marks the intended bg in a GAP(art) note;
#     drop in `scene <bg> with fade` once the art lands.
#   - Audio: there are no SFX assets, so the wolf's growl cue is omitted, not
#     faked with a missing-file `play` (which would only warn and play silence).
#   - Quests: the owner's "Enter the Breach" / "Find a companion" quest records
#     are not authored yet (data/quests.py ships only placeholders); the start
#     hook is left ready at beat 11. Authoring those records is owner content.
#   - The "Bronze Medallion" first-rank key item IS added (data/relics.py
#     KEY_ITEMS) from the owner's prose so the grant is real; confirm its src.

image black = Solid(gui.bg_color)


## The intro card (#17.2 step 4): full-screen centred text. Click to continue.
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
    # Build the save and drop into scripted/dialogue mode (no interface yet,
    # #13.1). gs is the Ren'Py store instance so saves/rollback see it.
    $ gs = bstate.new_game_state(REG)
    $ store.hud_visible = False

    # 1-2. Character creation wizard (#3): Name -> Race display -> Class ->
    #      Point Buy 27 -> derived sheet. Commits gs["party"][0] = the MC and
    #      blocks rollback itself.
    call character_creation

    # The MC's player-entered name and class display name, escaped for literal
    # display (breach_lit) so a name containing [] / {} can't break Ren'Py text
    # markup. Used in the trader's and receptionist's lines below as [mc_name] /
    # [mc_class].
    $ mc_name = breach_lit(gs["party"][0]["name"])
    $ mc_class = breach_lit(REG["classes"][gs["party"][0]["class"]]["name"])

    # 3. One-second fade to black (#17.2).
    scene black with Fade(1.0, 0.0, 0.0)

    # 4. Intro cards introducing Veycross -- owner prose, click to advance.
    call screen breach_intro_card("Veycross - The City of the great Confluence.")
    call screen breach_intro_card("A city of opportunity, a city of danger. A city built on the edge of a hole in the world.")
    call screen breach_intro_card("Three hundred years ago, the archmage named Vekke tore a hole in the world.\n\nHe was never seen again. The hole never closed.")
    call screen breach_intro_card("They call it the Breach — a door onto a dead and ruined world, and everything that still crawls inside it.\n\nAround that door, a city grew.")
    call screen breach_intro_card("It is now an adventuring hub for mercenaries, traders, and fortune-seekers from all over the world.")
    call screen breach_intro_card("What brings you to Veycross? Coin? Glory? A fresh start? Or something else entirely?")

    # 5. The MC wakes in Relpak's caravan on the road to Veycross (#17.2). The
    #    opening line is quoted verbatim in the GDD; the rest is owner prose.
    #    GAP(art): bg "caravan_road" + Relpak sprite.
    scene black
    "Relpak" "Hey, you. You're finally awake."
    "Relpak" "Slept like the dead since the last waystation. I was starting to think I'd hired a corpse for company."
    "The cart rocks under you. Open country rolls past — and ahead, low on the horizon, smoke and rooftops."
    "Relpak" "That there's Veycross. Couple hours out, give or take a wheel."
    "Relpak" "So. What's a person like you headed all that way for?"

    # Reactive options -- they never assume who the MC is (#3 writing rule).
    menu:
        "\"Coin. Same as everyone.\"":
            "Relpak" "Honest answer. Most folk dress it up prettier and mean the exact same thing."
        "\"I'm going to enter the Breach.\"":
            "Relpak" "The Breach, eh? Brave. Or broke. Usually both, in my experience."
        "\"Haven't decided yet.\"":
            "Relpak" "Then you'll fit right in. Half that city's still making up its mind about something."
        "\"That's my business.\"":
            "Relpak" "Fair enough. Quiet ones make the best passengers anyhow."

    # 6. The jinx: a wolf comes out of the brush and the bargain (protection for
    #    passage) comes due (#17.2). GAP(audio): the wolf's growl cue belongs
    #    here -- no SFX assets exist, so it is omitted, not faked. GAP(art):
    #    wolf sprite.
    "Relpak" "Well, whatever it is — we'll get you to the gate in one piece. Road's been kind the whole way down. Not so much as a—"
    "Relpak" "...Ah. Hm."
    "Something low and grey has come out of the brush. It is watching you the way hungry things watch."
    "Relpak" "Right. Here's where you earn the ride, friend. Passage to Veycross — protection on the road. That was the deal."
    "Relpak" "It's just the one. A [mc_class] of your caliber can manage just the one."

    # 7. Tutorial combat: the MC alone vs one Young Wolf (#11.2 / #17.2.7).
    #    Solo (the party is just the MC at this point); flee is disabled
    #    (combat_encounter's flee_allowed default is False); a loss is a real
    #    game over (combat_defeat routes to the main menu, handled inside the
    #    encounter -- the prologue needs no defeat branch). The result is locked
    #    against rollback (#16.1).
    call combat_encounter(["young_wolf"])
    $ renpy.block_rollback()

    # 8a. The aftermath, still on the road. GAP(art): bg "caravan_road".
    scene black with fade
    "Relpak" "Ha! Hah. Look at you."
    "Relpak" "Bit of a rough start, but you got the job done. Not everyone can say that. You earned your keep, that's for sure."

    # 8b. The city gate; the MC and Relpak part ways (#17.2). GAP(art): bg
    #     "veycross_gate_exterior".
    scene black with fade
    "The walls of Veycross rise ahead of you, close now — taller than anything you passed on the road, and louder."
    "Relpak" "This is me, then. I've cargo to move and a buyer who hates waiting."
    "Relpak" "You want the Lamplighters, you head for the middle of the city, huge Guild Headquarters, can't miss it."
    "Relpak" "Watch yourself in there."
    "And then the crowd takes him, and you are one more stranger at the gate."

    # 9. The gate guard. Whatever the answer, he sends the MC to the Guildhall
    #    (#17.2).
    "Gate Guard" "Hold up. New face. State your business in Veycross."
    menu:
        "\"I'm here to register with the Lamplighters.\"":
            "Gate Guard" "Another one. Good luck to you."
        "\"Work. Whatever pays.\"":
            "Gate Guard" "Then you'll want the Guild like everyone else who says that. Coin in this city comes up out of the Breach."
        "\"Just passing through.\"":
            "Gate Guard" "Nobody just passes through Veycross. There's only one road out and it goes the wrong direction. Try the Guild."
    "Gate Guard" "Lamplighter Guildhall. They'll sort you a medallion. Move along."

    # 10. The Guildhall: Imara registers the MC into the Lamplighter Guild
    #     (#17.2). GAP(art): bg "guildhall_interior" + Imara sprite.
    scene black with fade
    "Imara" "Welcome to the Lamplighter Guild. If you're here to gawk, the door's behind you. If you're here to register, the line forms at me."

    # The "just looking" option loops until the MC chooses to register.
    $ registered = False
    while not registered:
        menu:
            "\"Registering. What do I do?\"":
                "Imara" "You tell me your name, I write it down, you get your medallion. That's the whole ceremony."
                $ registered = True
            "\"Just looking around.\"":
                "Imara" "Well, you can look around all you want, but if you're not here to register, you can look around somewhere else. Line's over there."

    "Imara" "Name?"
    "You give it."
    "Imara" "[mc_name]. Right."

    # Grant the Bronze Medallion (first-rank guild token, #15.4 key item) and
    # set the membership flag, then commit against rollback (#16.1).
    $ bstate.add_item(gs, "bronze_medallion", 1)
    $ gs["flags"]["lamplighter_member"] = True
    $ renpy.block_rollback()

    "Imara" "Bronze. First rank. Welcome to the Guild."
    "Imara" "Now before you head straight into the Breach, you should know a few things."
    "Imara" "See that notice board over there? That's where the Guild, citizens, and other parties post their jobs. You might want to check it out — it's how most people get work around here."
    "Imara" "Second, explore the city. If you head straight into the Breach without any companions or gear, you're gonna have a bad time. The city is your best bet for finding both."
    "Imara" "Good luck out there."

    # 11. Free Mode begins. The interface arriving IS the signal (#13.1):
    #     city_free_mode owns HUD visibility, so the prologue does not force it.
    scene black with fade
    "You stand in the Guildhall."
    "The medallion is warm in your hand. Wherever you go now is your own choice."

    # GAP(quests): the owner's beat adds two quests here -- "Enter the Breach"
    # and "Find a companion" -- but neither exists as a record in data/quests.py
    # yet (only placeholder quests do). Authoring those records (title, giver,
    # location, objectives) is owner content; do not invent it (CLAUDE.md).
    # Imara's lines above already deliver the guidance verbally. Once the records
    # exist, start them here exactly like dialogue.rpy does:
    #     python:
    #         for _qid in ("quest_enter_breach", "quest_find_companion"):
    #             try:
    #                 bquests.start_quest(REG, gs, _qid)
    #             except ValueError:
    #                 pass
    #         renpy.block_rollback()

    call city_free_mode
    return
