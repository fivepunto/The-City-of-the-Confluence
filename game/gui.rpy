################################################################################
## Initialization
################################################################################

## The init offset statement causes the initialization statements in this file
## to run before init statements in any other file.
init offset = -2

## Calling gui.init resets the styles to sensible default values, and sets the
## width and height of the game.
init python:
    gui.init(1920, 1080)

## Enable checks for invalid or unstable properties in screens or transforms
define config.check_conflicting_properties = True

################################################################################
## Breach style source (CLAUDE.md "Visual & GUI discipline")
##
## ALL interface colors, text sizes, and spacing values are defined HERE,
## once. Screens reference these constants -- hardcoding a hex color or
## pixel padding inside a screen is a violation. The owner retunes the look
## by editing these constants only.
################################################################################

## Starter palette: dark slate + lamplight amber.
define gui.bg_color = '#14161a'
define gui.panel_color = '#1f232a'
define gui.panel_hover_color = '#262b34'      # brightened panel (hover state)
define gui.panel_border_color = '#3a404c'
define gui.breach_text_color = '#e8e4d8'
define gui.muted_text_color = '#8b8f99'
define gui.breach_accent_color = '#d9a441'    # accent / lamplight
define gui.accent_bright_color = '#e7bc6a'    # brightened accent (hover)
define gui.danger_color = '#b54a3f'
define gui.success_color = '#5d9e6b'
define gui.hp_bar_color = gui.danger_color    # HP bars are red everywhere (D7)
define gui.rarity_colors = {
    'common': '#b8b8b8', 'uncommon': '#5d9e6b',
    'rare': '#4a7fb5', 'very_rare': '#9b59b6'}
define gui.textbox_color = '#1f232ae6'        # panel at dialogue alpha

## One size scale: small / base / heading / title. The CLAUDE.md example
## scale (16/20/26/34) x1.5 for this project's 1920x1080 canvas -- same
## ratios, readable physical size (DECISIONS.md D-019). No ad-hoc sizes.
define gui.size_small = 24
define gui.size_base = 30
define gui.size_heading = 39
define gui.size_title = 51

## One spacing scale (CLAUDE.md): paddings and margins only from these.
define gui.pad_xs = 4
define gui.pad_s = 8
define gui.pad_m = 16
define gui.pad_l = 24

## Placeholder-art pipeline colors (CONTENT placeholders: colored rects +
## labels). Muted hues keyed by stable hash; real art replaces the screens,
## not these constants.
define gui.placeholder_colors = [
    '#4a5d7e', '#5d7e4a', '#7e4a5d', '#7e6a4a',
    '#4a7e76', '#6a4a7e', '#7e4a4a', '#4a7e5d']


## Combat-screen depth & focal layer (refines the dark-slate / lamplight
## identity -- "lamplight in the dark"). Atmosphere comes ONLY from value
## layering + alpha Solids + focal contrast, never from art. The value
## ladder, darkest -> lightest:  seam < stage < bg < panel < panel_hover <
## lit_panel. These are reusable by the other screens (a recessed stage, a
## lit focal surface, a spent/dim accent) once the look is approved.
define gui.breach_stage_color = '#0d0f12'          # recessed battlefield well (one step below bg)
define gui.breach_seam_color = '#0a0b0e'           # darkest: no-man's-land divider + float backing
define gui.breach_lit_panel_color = '#2b313b'      # the lit focal surface (one step above panel_hover)
define gui.breach_accent_dim_color = '#7a5d28'     # lamplight burning low: spent / depleted
define gui.breach_accent_glow_color = '#d9a44133'  # accent @ ~20% alpha: the soft focal/target wash
define gui.breach_conc_ring_color = '#4a7fb5'      # concentration ring = the rare-blue (cool focus)
define gui.breach_blood_color = '#8f2f28'          # dried-blood Bloodied marker (deeper than HP red)
define gui.breach_telegraph_color = gui.danger_color  # boss intent: danger red, set apart by position
define gui.breach_scrim_color = '#0a0b0ecc'        # ~80% near-black modal scrim (every overlay)

## One caption tier BELOW size_small, so cards and captions gain a true
## three-level hierarchy (micro / small / base). Use only at named caption
## and data sites (lane labels, the ROUND sublabel, condition/resource text).
define gui.size_micro = 20

## Names the 2px precision-rule / nested-frame-border thickness as a concept
## (replaces the literal 2s in the nested-frame technique and the lit lips).
define gui.hairline = 2

## Combat layout geometry -- so no band height, plate size, or y-position is a
## magic number in the screen. The stage height, the lanes-well width, and the
## plate width are all DERIVED in the screen from these + the canvas (see
## combat_screen): the initiative ribbon (turn order) runs across the TOP, the
## battlefield (lanes) fills the LEFT, the info sidebar (rolled initiative order
## + combat log) takes a fixed RIGHT column, and the action panel the bottom.
define gui.combat_ribbon_h = 96      # top initiative ribbon (turn-order chips)
define gui.combat_panel_h = 320      # bottom action-panel band
define gui.combat_sidebar_w = 380    # right column: initiative order + combat log
define gui.combat_chip_size = 48     # initiative portrait-chip swatch
define gui.combat_chip_name_w = 240  # ribbon chip name cap
define gui.combat_init_val_w = 56    # sidebar initiative-value column (right edge)
define gui.combat_card_hp_w = 120    # HP-bar width inside a (narrow) lane unit card
define gui.combat_card_name_w = 180  # unit-card name wrap width (long names wrap, never clip)
define gui.combat_actor_col_w = 380  # action-panel name/resource column
define gui.combat_list_h = 170       # spell/ability/item list viewport cap (scrolls beyond)
define gui.combat_watchdog_limit = 200  # forward-progress guard: max loop iterations stuck on one (actor,turn,round) before the engine raises


## Shared screen-layout geometry (CLAUDE.md "one style source"). The
## out-of-combat menu/content screens (sheet, inventory, shop, quests, camp,
## creation, level-up, maps, dialogue) reference THESE instead of literal
## pixels -- so every two-pane split, modal width, list-viewport height, and
## row-meta column retunes from one place. (Combat owns its own band geometry
## above; this block is for the rest of the game.)
define gui.screen_pad = gui.pad_l         # full-screen content inset
define gui.pane_gap = gui.pad_m           # gap between two-pane columns
define gui.list_pane_w = 1110             # the wide list column (inventory/shop list)
define gui.detail_pane_w = 740            # the narrow detail / paper-doll column
define gui.split_list_w = 760             # left list in a list+detail split (quests/sheet)
define gui.pane_h = 820                   # tall two-pane viewport height
define gui.list_well_h = 620              # list-well viewport height
define gui.card_thumb_size = 48           # standard list-row / swatch thumbnail square
define gui.row_meta_w = 220               # right-aligned meta column in a list row
define gui.stat_label_w = 260             # fixed label column in a label|value data row
define gui.summary_col_w = 520            # creation-summary review column (the two equal columns)
define gui.summary_col_w_wide = 560       # creation-summary third (slightly wider) review column

## Centred-modal widths (every dialog = scrim + one lit panel). One ladder.
define gui.modal_w_s = 720                # compact (confirm, reaction prompt, manage)
define gui.modal_w = 900                  # standard (hunt picker, breather, name step)
define gui.modal_w_l = 1200               # large (level-up, skill menu, point-buy)
define gui.modal_h_l = 940                # large-modal fixed height (the choice stepper)
define gui.modal_body_h_l = 560           # large-modal scrollable-body cap (level-up wizard) -- keeps the action row on-screen
define gui.panel_w_narrow = 460           # narrow menu panel (manage / free-mode menu)
define gui.menu_title_size = gui.size_title   # menu page title, on the type scale
define gui.namebox_rule_width = 0.22      # speaker-name underline width (fraction of textbox)
define gui.expedition_node_w = 240        # expedition-map node-plate footprint (authored coords)
define gui.expedition_node_h = 120


## Type-hierarchy & frame extensions (the reference's display tier).
## ----------------------------------------------------------------------
## Small-caps label spacing: the amber/muted micro labels are UPPERCASED and
## tracked out (the reference's section captions -- lane headers, ROUND,
## resource labels, list headers). One kerning value drives them all.
define gui.kerning_label = 3

## Class-resource readouts switch from segmented PIPS to a continuous bar
## above this pool size: small discrete pools (slots, Focus, Rage, Channel)
## read as pips; large pools (Lay on Hands) read as a bar.
define gui.resource_pip_cap = 8

## Panel frame -- THE one shared nineslice ornament, wired into breach_panel /
## breach_panel_lit in style.rpy. The PNG is a transparent gold frame (ornate
## corners + thin gold edge lines) drawn ON TOP of the panel's slate fill, so
## the fill colour shows through and the gold reads at the edges. ONE place
## tunes it for the whole game:
##   - panel_frame_scale : how big the ornament renders. The current source is
##     1024px with thin (~4px) gold lines and a small (~27px) corner, so it is
##     rendered near 1:1 -- scaling it DOWN made the lines sub-pixel and
##     invisible. RAISE this (e.g. 1.3) for a bolder gold line (mild upscale
##     softness); LOWER it for a finer line.
##   - panel_frame_border : the 9-slice corner size in SCALED pixels. It MUST
##     cover the corner-bracket ornament (~86px in the cropped source) or the
##     bracket gets sliced and the corners/edges no longer connect; the thin
##     straight edge between corners stretches. (The PNG is cropped tight to
##     the gold, so the frame sits flush at the panel edge -- no margin.)
##   - panel_frame_pad : internal content padding so text clears the gold
##     edge line (the corner brackets are sparse, so this need not equal the
##     full border).
define gui.panel_frame_scale = 1.0
define gui.panel_frame_border = 88
define gui.panel_frame_pad = 36
define gui.panel_frame = Frame(Transform("gui/frames/panel_frame.png", zoom=gui.panel_frame_scale), gui.panel_frame_border, gui.panel_frame_border)

## State variants of the shared frame for INTERACTIVE panels (same geometry,
## recoloured): hover, selected (lit amber + glow), and disabled (dimmed).
## Driven by the SAME scale/border, so they swap cleanly. Used by the
## breach_panel_button style and the combat lane cards.
define gui.panel_frame_hover = Frame(Transform("gui/frames/panel_frame_hover.png", zoom=gui.panel_frame_scale), gui.panel_frame_border, gui.panel_frame_border)
define gui.panel_frame_selected = Frame(Transform("gui/frames/panel_frame_selected.png", zoom=gui.panel_frame_scale), gui.panel_frame_border, gui.panel_frame_border)
define gui.panel_frame_disabled = Frame(Transform("gui/frames/panel_frame_disabled.png", zoom=gui.panel_frame_scale), gui.panel_frame_border, gui.panel_frame_border)

## Purpose-built frames for specific chrome (cropped flush; rendered at their
## native size, so each carries its OWN 9-slice border = its corner size):
##   modal   -- centred modal dialogs (combat overlays, victory/defeat): a
##              bolder, thicker gold than the inline panels.
##   tooltip -- small framed cards (the reaction prompt).
## (The dialogue textbox/namebox frames live in frames.rpy as breach_frame_textbox
## and a background-None namebox -- not here.)
define gui.modal_frame = Frame("gui/frames/ui_frame_modal.png", 38, 38)
define gui.modal_frame_pad = 44
define gui.tooltip_frame = Frame("gui/frames/ui_frame_tooltip.png", 29, 29)
define gui.tooltip_frame_pad = 28

## The panel fills (shown THROUGH the frame's transparent centre): the quiet
## slate panel and the lit focal surface. Swapping these is how a panel reads
## quiet vs active; the gold frame itself is shared by both.
define gui.panel_frame_fill = Solid(gui.panel_color)
define gui.panel_frame_fill_lit = Solid(gui.breach_lit_panel_color)



################################################################################
## GUI Configuration Variables
################################################################################


## Colors ######################################################################
##
## The colors of text in the interface.

## An accent color used throughout the interface to label and highlight text.
define gui.accent_color = gui.breach_accent_color

## The color used for a text button when it is neither selected nor hovered.
define gui.idle_color = gui.muted_text_color

## The small color is used for small text, which needs to be brighter/darker to
## achieve the same effect.
define gui.idle_small_color = '#a4a8b0'

## The color that is used for buttons and bars that are hovered.
define gui.hover_color = gui.accent_bright_color

## The color used for a text button when it is selected but not focused. A
## button is selected if it is the current screen or preference value.
define gui.selected_color = gui.breach_text_color

## The color used for a text button when it cannot be selected.
define gui.insensitive_color = '#8b8f997f'

## Colors used for the portions of bars that are not filled in. These are not
## used directly, but are used when re-generating bar image files.
define gui.muted_color = gui.panel_border_color
define gui.hover_muted_color = '#4a5160'

## The colors used for dialogue and menu choice text.
define gui.text_color = gui.breach_text_color
define gui.interface_text_color = gui.breach_text_color


## Fonts and Font Sizes ########################################################

## The font used for in-game text -- dialogue, narration, quest prose:
## Spectral Medium, a humanist serif (the upright reading face).
define gui.text_font = "gui/fonts/Spectral-Medium.ttf"

## The font used for character names (the dialogue speaker nameplate):
## Marcellus SC, a classical small-caps serif.
define gui.name_text_font = "gui/fonts/MarcellusSC-Regular.ttf"

## The UI / out-of-game font -- labels, tabs, stats, buttons, HUD numbers:
## IBM Plex Sans Condensed (the workhorse interface face). The base `text`
## style is bound to this in style.rpy so every unspecified screen string
## (combat included) renders in it; dialogue (gui.text_font) and the display
## tier (gui.display_font) stay distinct.
define gui.interface_text_font = "gui/fonts/IBMPlexSansCondensed-Medium.ttf"

## The DISPLAY typeface -- focal names, section headers, screen titles, the
## ROUND counter: Cinzel, an engraved-capitals serif. breach_display_text and
## breach_header_text in style.rpy route here, so this one token drives every
## display-tier string at once.
define gui.display_font = "gui/fonts/Cinzel-Medium.ttf"

## The size of normal dialogue text.
define gui.text_size = gui.size_base

## The size of character names.
define gui.name_text_size = gui.size_heading

## The size of text in the game's user interface.
define gui.interface_text_size = gui.size_base

## The size of labels in the game's user interface.
define gui.label_text_size = gui.size_heading

## The size of text on the notify screen.
define gui.notify_text_size = gui.size_small

## The size of the game's title.
define gui.title_text_size = gui.size_title


## Main and Game Menus #########################################################

## The images used for the main and game menus.
define gui.main_menu_background = Solid(gui.bg_color)
define gui.game_menu_background = Solid(gui.bg_color)


## Dialogue ####################################################################
##
## These variables control how dialogue is displayed on the screen one line at a
## time.

## The height of the textbox containing dialogue.
define gui.textbox_height = 300

## The dialogue box is margined (not full-bleed) to match the reference
## composition, lifted a little off the screen bottom so the quick-menu bar
## clears beneath it. Interior padding clears the gold frame's edge.
define gui.textbox_width = 1720
define gui.textbox_bottom_gap = 36
define gui.dialogue_pad_x = 72
define gui.dialogue_pad_y = 48

## Gap between the inline speaker name and the dialogue line.
define gui.namebox_text_gap = 8

## The placement of the textbox vertically on the screen. 0.0 is the top, 0.5 is
## center, and 1.0 is the bottom.
define gui.textbox_yalign = 1.0


## The placement of the speaking character's name, relative to the textbox.
## These can be a whole number of pixels from the left or top, or 0.5 to center.
define gui.name_xpos = 360
define gui.name_ypos = 0

## The horizontal alignment of the character's name. This can be 0.0 for left-
## aligned, 0.5 for centered, and 1.0 for right-aligned.
define gui.name_xalign = 0.0

## The width, height, and borders of the box containing the character's name.
## Fixed to the nameplate frame's native size (gui.namebox_frame) so the gold
## frame renders undistorted (its corner is large relative to a tiny box).
define gui.namebox_width = 600
define gui.namebox_height = 96

## The borders of the box containing the character's name, in left, top, right,
## bottom order.
## Nameplate text padding -- clears the gold of the breach_frame_namebox
## (56/40 border); the name is vertically centred (say_label yalign 0.5).
define gui.namebox_borders = Borders(40, 10, 40, 10)

## If True, the background of the namebox will be tiled, if False, the
## background of the namebox will be scaled.
define gui.namebox_tile = False


## The placement of dialogue relative to the textbox. These can be a whole
## number of pixels relative to the left or top side of the textbox, or 0.5 to
## center.
define gui.dialogue_xpos = 402
define gui.dialogue_ypos = 75

## The maximum width of dialogue text, in pixels.
define gui.dialogue_width = 1116

## The horizontal alignment of the dialogue text. This can be 0.0 for left-
## aligned, 0.5 for centered, and 1.0 for right-aligned.
define gui.dialogue_text_xalign = 0.0


## Buttons #####################################################################
##
## These variables, along with the image files in gui/button, control aspects of
## how buttons are displayed.

## The width and height of a button, in pixels. If None, Ren'Py computes a size.
define gui.button_width = None
define gui.button_height = None

## The borders on each side of the button, in left, top, right, bottom order.
define gui.button_borders = Borders(6, 6, 6, 6)

## If True, the background image will be tiled. If False, the background image
## will be linearly scaled.
define gui.button_tile = False

## The font used by the button.
define gui.button_text_font = gui.interface_text_font

## The size of the text used by the button.
define gui.button_text_size = gui.interface_text_size

## The color of button text in various states.
define gui.button_text_idle_color = gui.idle_color
define gui.button_text_hover_color = gui.hover_color
define gui.button_text_selected_color = gui.selected_color
define gui.button_text_insensitive_color = gui.insensitive_color

## The horizontal alignment of the button text. (0.0 is left, 0.5 is center, 1.0
## is right).
define gui.button_text_xalign = 0.0


## These variables override settings for different kinds of buttons. Please see
## the gui documentation for the kinds of buttons available, and what each is
## used for.
##
## These customizations are used by the default interface:

define gui.radio_button_borders = Borders(27, 6, 6, 6)

define gui.check_button_borders = Borders(27, 6, 6, 6)

define gui.confirm_button_text_xalign = 0.5

define gui.page_button_borders = Borders(15, 6, 15, 6)

define gui.quick_button_borders = Borders(15, 6, 15, 0)
define gui.quick_button_text_size = gui.size_small
define gui.quick_button_text_idle_color = gui.idle_small_color
define gui.quick_button_text_selected_color = gui.accent_color

## You can also add your own customizations, by adding properly-named variables.
## For example, you can uncomment the following line to set the width of a
## navigation button.

# define gui.navigation_button_width = 250


## Choice Buttons ##############################################################
##
## Choice buttons are used in the in-game menus.

define gui.choice_button_width = 1185
define gui.choice_button_height = None
define gui.choice_button_tile = False
define gui.choice_button_borders = Borders(150, 8, 150, 8)
define gui.choice_button_text_font = gui.text_font
define gui.choice_button_text_size = gui.text_size
define gui.choice_button_text_xalign = 0.5
define gui.choice_button_text_idle_color = gui.muted_text_color
define gui.choice_button_text_hover_color = gui.breach_text_color
define gui.choice_button_text_insensitive_color = '#8b8f997f'


## File Slot Buttons ###########################################################
##
## A file slot button is a special kind of button. It contains a thumbnail
## image, and text describing the contents of the save slot. A save slot uses
## image files in gui/button, like the other kinds of buttons.

## The save slot button.
define gui.slot_button_width = 414
define gui.slot_button_height = 309
define gui.slot_button_borders = Borders(15, 15, 15, 15)
define gui.slot_button_text_size = gui.size_small
define gui.slot_button_text_xalign = 0.5
define gui.slot_button_text_idle_color = gui.idle_small_color
define gui.slot_button_text_selected_idle_color = gui.selected_color
define gui.slot_button_text_selected_hover_color = gui.hover_color

## The width and height of thumbnails used by the save slots.
define config.thumbnail_width = 384
define config.thumbnail_height = 216

## The number of columns and rows in the grid of save slots.
define gui.file_slot_cols = 3
define gui.file_slot_rows = 2


## Positioning and Spacing #####################################################
##
## These variables control the positioning and spacing of various user interface
## elements.

## The position of the left side of the navigation buttons, relative to the left
## side of the screen.
define gui.navigation_xpos = 60

## The vertical position of the skip indicator.
define gui.skip_ypos = 15

## The vertical position of the notify screen.
define gui.notify_ypos = 68

## The spacing between menu choices.
define gui.choice_spacing = 33

## Buttons in the navigation section of the main and game menus.
define gui.navigation_spacing = 6

## Controls the amount of spacing between preferences.
define gui.pref_spacing = 15

## Controls the amount of spacing between preference buttons.
define gui.pref_button_spacing = 0

## The spacing between file page buttons.
define gui.page_spacing = 0

## The spacing between file slots.
define gui.slot_spacing = 15

## The position of the main menu text.
define gui.main_menu_text_xalign = 1.0


## Frames ######################################################################
##
## These variables control the look of frames that can contain user interface
## components when an overlay or window is not present.

## Generic frames.
define gui.frame_borders = Borders(6, 6, 6, 6)

## The frame that is used as part of the confirm screen.
define gui.confirm_frame_borders = Borders(60, 60, 60, 60)

## The frame that is used as part of the skip screen.
define gui.skip_frame_borders = Borders(24, 8, 75, 8)

## The frame that is used as part of the notify screen.
define gui.notify_frame_borders = Borders(24, 8, 60, 8)

## Should frame backgrounds be tiled?
define gui.frame_tile = False


## Bars, Scrollbars, and Sliders ###############################################
##
## These control the look and size of bars, scrollbars, and sliders.
##
## The default GUI only uses sliders and vertical scrollbars. All of the other
## bars are only used in creator-written screens.

## The height of horizontal bars, scrollbars, and sliders. The width of vertical
## bars, scrollbars, and sliders.
define gui.bar_size = 38
define gui.scrollbar_size = 18
define gui.slider_size = 38

## True if bar images should be tiled. False if they should be linearly scaled.
define gui.bar_tile = False
define gui.scrollbar_tile = False
define gui.slider_tile = False

## Horizontal borders.
define gui.bar_borders = Borders(6, 6, 6, 6)
define gui.scrollbar_borders = Borders(6, 6, 6, 6)
define gui.slider_borders = Borders(6, 6, 6, 6)

## Vertical borders.
define gui.vbar_borders = Borders(6, 6, 6, 6)
define gui.vscrollbar_borders = Borders(6, 6, 6, 6)
define gui.vslider_borders = Borders(6, 6, 6, 6)

## What to do with unscrollable scrollbars in the game menu. "hide" hides them,
## while None shows them.
define gui.unscrollable = "hide"


## History #####################################################################
##
## The history screen displays dialogue that the player has already dismissed.

## The number of blocks of dialogue history Ren'Py will keep.
define config.history_length = 250

## The height of a history screen entry, or None to make the height variable at
## the cost of performance.
define gui.history_height = 210

## Additional space to add between history screen entries.
define gui.history_spacing = 0

## The position, width, and alignment of the label giving the name of the
## speaking character.
define gui.history_name_xpos = 233
define gui.history_name_ypos = 0
define gui.history_name_width = 233
define gui.history_name_xalign = 1.0

## The position, width, and alignment of the dialogue text.
define gui.history_text_xpos = 255
define gui.history_text_ypos = 3
define gui.history_text_width = 1110
define gui.history_text_xalign = 0.0


## NVL-Mode ####################################################################
##
## The NVL-mode screen displays the dialogue spoken by NVL-mode characters.

## The borders of the background of the NVL-mode background window.
define gui.nvl_borders = Borders(0, 15, 0, 30)

## The maximum number of NVL-mode entries Ren'Py will display. When more entries
## than this are to be show, the oldest entry will be removed.
define gui.nvl_list_length = 6

## The height of an NVL-mode entry. Set this to None to have the entries
## dynamically adjust height.
define gui.nvl_height = 173

## The spacing between NVL-mode entries when gui.nvl_height is None, and between
## NVL-mode entries and an NVL-mode menu.
define gui.nvl_spacing = 15

## The position, width, and alignment of the label giving the name of the
## speaking character.
define gui.nvl_name_xpos = 645
define gui.nvl_name_ypos = 0
define gui.nvl_name_width = 225
define gui.nvl_name_xalign = 1.0

## The position, width, and alignment of the dialogue text.
define gui.nvl_text_xpos = 675
define gui.nvl_text_ypos = 12
define gui.nvl_text_width = 885
define gui.nvl_text_xalign = 0.0

## The position, width, and alignment of nvl_thought text (the text said by the
## nvl_narrator character.)
define gui.nvl_thought_xpos = 360
define gui.nvl_thought_ypos = 0
define gui.nvl_thought_width = 1170
define gui.nvl_thought_xalign = 0.0

## The position of nvl menu_buttons.
define gui.nvl_button_xpos = 675
define gui.nvl_button_xalign = 0.0


## Localization ################################################################

## This controls where a line break is permitted. The default is suitable
## for most languages. A list of available values can be found at https://
## www.renpy.org/doc/html/style_properties.html#style-property-language

define gui.language = "unicode"


################################################################################
## Mobile devices
################################################################################

init python:

    ## This increases the size of the quick buttons to make them easier to touch
    ## on tablets and phones.
    @gui.variant
    def touch():

        gui.quick_button_borders = Borders(60, 21, 60, 0)

    ## This changes the size and spacing of various GUI elements to ensure they
    ## are easily visible on phones.
    @gui.variant
    def small():

        ## Font sizes.
        gui.text_size = 45
        gui.name_text_size = 54
        gui.notify_text_size = 38
        gui.interface_text_size = 45
        gui.button_text_size = 45
        gui.label_text_size = 51

        ## Adjust the location of the textbox.
        gui.textbox_height = 360
        gui.name_xpos = 120
        gui.dialogue_xpos = 135
        gui.dialogue_width = 1650

        ## Change the size and spacing of various things.
        gui.slider_size = 54

        gui.choice_button_width = 1860
        gui.choice_button_text_size = 45

        gui.navigation_spacing = 30
        gui.pref_button_spacing = 15

        gui.history_height = 285
        gui.history_text_width = 1035

        gui.quick_button_text_size = 30

        ## File button layout.
        gui.file_slot_cols = 2
        gui.file_slot_rows = 2

        ## NVL-mode.
        gui.nvl_height = 255

        gui.nvl_name_width = 458
        gui.nvl_name_xpos = 488

        gui.nvl_text_width = 1373
        gui.nvl_text_xpos = 518
        gui.nvl_text_ypos = 8

        gui.nvl_thought_width = 1860
        gui.nvl_thought_xpos = 30

        gui.nvl_button_width = 1860
        gui.nvl_button_xpos = 30
