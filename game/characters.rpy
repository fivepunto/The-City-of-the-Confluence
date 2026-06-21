# Speaker definitions -- the ONE place every named speaker is declared (the
# prologue cast, #17.2, plus the placeholder city NPCs). The project used to
# write speakers as string literals inline ("Imara" "..."); they are centralised
# here as Ren'Py Character objects so each name is written ONCE and the story
# layer refers to the variable (imara "...") rather than repeating the literal.
# Renaming a character is now a one-line edit here, not a find-replace.
#
# Character NAMES are OWNER content. The three prologue cast members are
# owner-authored canon (#17.2). The townsperson / merchant / quest-giver are
# still bracketed PLACEHOLDERS for the owner to name -- the leading "[[" escapes
# Ren'Py text interpolation so the literal "[" shows in the namebox (the same
# convention the old inline placeholders used). Replace the placeholder strings
# (and ideally the variable names) once the owner names these roles.
#
# Styling: these are deliberately PLAIN Character objects. The namebox look (the
# gold-underlined nameplate) is owned by the say / namebox styles
# (screens.rpy + gui.rpy), so every speaker inherits the one shared nameplate
# and the on-screen result is identical to the old string-literal speakers. If a
# character ever needs a distinct nameplate, add options here (e.g. who_color)
# -- one place, one character, no screen change.
#
# The narrator (bare "..." lines with no speaker) stays the built-in narrator
# and needs no definition here.


# --- Prologue cast (owner canon, #17.2) ---
define relpak = Character("Relpak")        # the trader on the road to Veycross
define guard  = Character("Gate Guard")    # the Veycross gate guard (a role)
define imara  = Character("Imara")          # the Lamplighter Guild receptionist


# --- Guild Hall NPCs (owner canon) ---
define vekshara = Character("Vekshara")     # Guild Hall NPC
define reinecke = Character("Reinecke")     # Guild Hall NPC


# --- Shopkeepers (owner canon) ---
define anouk = Character("Anouk")           # Anouk's Anvil (basic weapons)
define oswin = Character("Oswin")           # Helms and Plates (basic armor)


# --- Placeholder city NPCs (owner to name; bracketed like the old inline ones) ---
define townsperson = Character("[[Townsperson]")
define merchant    = Character("[[Merchant]")
define questgiver  = Character("[[Quest Giver]")
