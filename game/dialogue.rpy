# Dialogue: the conversational dialogue-HUB system and the game's authored NPC
# conversations (GDD 15.7). A hub is a native `menu:` loop whose questions are
# gated by plain `if`s -- ONE-SHOT questions vanish once asked, CONDITIONAL
# questions appear only when their predicate holds. All spoken text is OWNER
# content; unwritten lines ship as "[[TO BE WRITTEN BY THE PROJECT OWNER]" and
# speakers are the Character() objects in characters.rpy.
#
# Rollback discipline (GDD 16.1): the .rpy layer calls renpy.block_rollback()
# immediately after every committed mutation (here: marking a question asked,
# and any quest start) -- core never does.
#
# (The earlier placeholder skill-check demo dialogues -- dlg_townsperson /
# dlg_merchant / dlg_questgiver and the skill_menu choice screen -- were removed
# along with the placeholder city districts that reached them. A skill-tagged
# dialogue UI (GDD 15.7 L1597-1606) will return when real skill-gated
# conversations are authored.)


init python:

    # --- Conversational dialogue-hub helpers (the Imara pattern, GDD 15.7) ---
    #
    # A dialogue hub is a native `menu:` loop where each question is gated by a
    # plain `if`: a ONE-SHOT question reads `if not breach_asked(npc, qid)` so it
    # vanishes once asked, and a CONDITIONAL question adds its own predicate so
    # it only appears when the condition holds. The "asked" set lives in the
    # save -- gs["flags"], flat namespaced keys "dlg:<npc>:<qid>" -- so it
    # survives save/load and never collides with story flags. Marking a question
    # asked is a committed mutation, so we block rollback immediately after
    # (CLAUDE.md / 16.1); that is also what makes "asked -> gone" impossible to
    # undo by rolling back.

    def breach_asked(npc, qid):
        """True if question `qid` has already been asked of `npc`."""
        if gs is None:
            return False
        return bool(gs.get("flags", {}).get("dlg:%s:%s" % (npc, qid)))

    def breach_mark_asked(npc, qid):
        """Record that `qid` was asked of `npc`, and commit it past rollback."""
        gs["flags"]["dlg:%s:%s" % (npc, qid)] = True
        renpy.block_rollback()                       # commit; "asked -> gone"


## --------------------------------------------------------------------------
## Imara at the Lamplighter Guildhall -- the first authored NPC and the first
## conversational dialogue HUB (GDD 15.7). Reached from the guild-hall hotspot
## (data/locations.py hs_guildhall_imara -> kind "character" ->
## ("dialogue", "dlg_imara"), dispatched by city_free_loop via `call
## expression`). The spoken lines are OWNER placeholders ("[TO BE WRITTEN...]")
## and the question captions are bracketed placeholders too; what this label
## actually exercises is the HUB SYSTEM:
##   - ONE-SHOT questions vanish once asked  (`if not breach_asked(...)`)
##   - CONDITIONAL questions appear only when their predicate holds
##     (a follow-up gated on an earlier question; a members-only line gated on
##      the prologue's flags["lamplighter_member"]).
## The native `menu:` keeps Imara's last line in the dialogue box behind the
## choices (config.choice_empty_window = extend, options.rpy). Every question
## captions with "[[" so the literal "[" shows instead of being read as Ren'Py
## text interpolation (the project's owner-placeholder convention).
##
## NOTE (art): no guildhall background exists, so the hub plays over the current
## scene like every other dialogue label; drop a `scene` in once art lands.
## --------------------------------------------------------------------------

label dlg_imara:
    # Opening line each time the player talks to her (owner prose).
    imara "[[TO BE WRITTEN BY THE PROJECT OWNER]"

label dlg_imara_hub:
    menu:
        # One-shot: a plain question that disappears once it has been asked.
        "[[Question A]" if not breach_asked("imara", "guild"):
            $ breach_mark_asked("imara", "guild")
            imara "[[TO BE WRITTEN BY THE PROJECT OWNER]"
            jump dlg_imara_hub

        # Conditional + one-shot: a follow-up that only appears AFTER Question A
        # has been asked (and then disappears once it, too, has been asked).
        "[[Follow-up to A]" if breach_asked("imara", "guild") and not breach_asked("imara", "guild_followup"):
            $ breach_mark_asked("imara", "guild_followup")
            imara "[[TO BE WRITTEN BY THE PROJECT OWNER]"
            jump dlg_imara_hub

        # Conditional + one-shot: only a registered Guild member sees this (the
        # prologue sets flags["lamplighter_member"] at registration, #17.2).
        "[[Members-only question]" if gs["flags"].get("lamplighter_member") and not breach_asked("imara", "member"):
            $ breach_mark_asked("imara", "member")
            imara "[[TO BE WRITTEN BY THE PROJECT OWNER]"
            jump dlg_imara_hub

        # Always available: end the conversation and return to the hall.
        "That's all for now.":
            pass
    return


## --------------------------------------------------------------------------
## Vekshara and Reinecke -- two more Guild Hall NPCs (owner canon). Same
## conversational HUB format as Imara above (one-shot + conditional placeholder
## questions; see that block for the mechanics). Spoken lines and question
## captions are owner placeholders; the asked-set is namespaced per NPC, so the
## three hubs never collide.
## --------------------------------------------------------------------------

label dlg_vekshara:
    vekshara "[[TO BE WRITTEN BY THE PROJECT OWNER]"

label dlg_vekshara_hub:
    menu:
        # One-shot: vanishes once asked.
        "[[Question A]" if not breach_asked("vekshara", "q1"):
            $ breach_mark_asked("vekshara", "q1")
            vekshara "[[TO BE WRITTEN BY THE PROJECT OWNER]"
            jump dlg_vekshara_hub

        # Conditional + one-shot: appears only after Question A has been asked.
        "[[Follow-up to A]" if breach_asked("vekshara", "q1") and not breach_asked("vekshara", "q1_followup"):
            $ breach_mark_asked("vekshara", "q1_followup")
            vekshara "[[TO BE WRITTEN BY THE PROJECT OWNER]"
            jump dlg_vekshara_hub

        # Conditional + one-shot: only a registered Guild member sees this.
        "[[Members-only question]" if gs["flags"].get("lamplighter_member") and not breach_asked("vekshara", "member"):
            $ breach_mark_asked("vekshara", "member")
            vekshara "[[TO BE WRITTEN BY THE PROJECT OWNER]"
            jump dlg_vekshara_hub

        "That's all for now.":
            pass
    return


label dlg_reinecke:
    reinecke "[[TO BE WRITTEN BY THE PROJECT OWNER]"

label dlg_reinecke_hub:
    menu:
        # One-shot: vanishes once asked.
        "[[Question A]" if not breach_asked("reinecke", "q1"):
            $ breach_mark_asked("reinecke", "q1")
            reinecke "[[TO BE WRITTEN BY THE PROJECT OWNER]"
            jump dlg_reinecke_hub

        # Conditional + one-shot: appears only after Question A has been asked.
        "[[Follow-up to A]" if breach_asked("reinecke", "q1") and not breach_asked("reinecke", "q1_followup"):
            $ breach_mark_asked("reinecke", "q1_followup")
            reinecke "[[TO BE WRITTEN BY THE PROJECT OWNER]"
            jump dlg_reinecke_hub

        # Conditional + one-shot: only a registered Guild member sees this.
        "[[Members-only question]" if gs["flags"].get("lamplighter_member") and not breach_asked("reinecke", "member"):
            $ breach_mark_asked("reinecke", "member")
            reinecke "[[TO BE WRITTEN BY THE PROJECT OWNER]"
            jump dlg_reinecke_hub

        "That's all for now.":
            pass
    return


## --------------------------------------------------------------------------
## Anouk (Anouk's Anvil, basic weapons) and Oswin (Helms and Plates, basic
## armor) -- the two shopkeepers (owner canon). Same conversational HUB format
## as Imara, with one extra ALWAYS-available option: "Browse the wares." opens
## their shop (data/shop.py) and returns to the hub. Spoken lines / question
## captions are owner placeholders; "Browse the wares." is a UI action, not
## prose.
## --------------------------------------------------------------------------

label dlg_anouk:
    anouk "[[TO BE WRITTEN BY THE PROJECT OWNER]"

label dlg_anouk_hub:
    menu:
        "[[Question A]" if not breach_asked("anouk", "q1"):
            $ breach_mark_asked("anouk", "q1")
            anouk "[[TO BE WRITTEN BY THE PROJECT OWNER]"
            jump dlg_anouk_hub

        "[[Follow-up to A]" if breach_asked("anouk", "q1") and not breach_asked("anouk", "q1_followup"):
            $ breach_mark_asked("anouk", "q1_followup")
            anouk "[[TO BE WRITTEN BY THE PROJECT OWNER]"
            jump dlg_anouk_hub

        "[[Members-only question]" if gs["flags"].get("lamplighter_member") and not breach_asked("anouk", "member"):
            $ breach_mark_asked("anouk", "member")
            anouk "[[TO BE WRITTEN BY THE PROJECT OWNER]"
            jump dlg_anouk_hub

        # Always available: open her shop (the basic weapons), then back to talk.
        "Browse the wares.":
            call screen shop_screen("anouks_anvil")
            jump dlg_anouk_hub

        "That's all for now.":
            pass
    return


label dlg_oswin:
    oswin "[[TO BE WRITTEN BY THE PROJECT OWNER]"

label dlg_oswin_hub:
    menu:
        "[[Question A]" if not breach_asked("oswin", "q1"):
            $ breach_mark_asked("oswin", "q1")
            oswin "[[TO BE WRITTEN BY THE PROJECT OWNER]"
            jump dlg_oswin_hub

        "[[Follow-up to A]" if breach_asked("oswin", "q1") and not breach_asked("oswin", "q1_followup"):
            $ breach_mark_asked("oswin", "q1_followup")
            oswin "[[TO BE WRITTEN BY THE PROJECT OWNER]"
            jump dlg_oswin_hub

        "[[Members-only question]" if gs["flags"].get("lamplighter_member") and not breach_asked("oswin", "member"):
            $ breach_mark_asked("oswin", "member")
            oswin "[[TO BE WRITTEN BY THE PROJECT OWNER]"
            jump dlg_oswin_hub

        # Always available: open his shop (the basic armor), then back to talk.
        "Browse the wares.":
            call screen shop_screen("helms_and_plates")
            jump dlg_oswin_hub

        "That's all for now.":
            pass
    return
