# game/style.rpy -- shared interface styles and component library
# (CLAUDE.md "Visual & GUI discipline": shared styles live here,
# colors/sizes/spacing constants live in gui.rpy). Moved out of
# screens.rpy per the updated one-style-source rule.

################################################################################
## Breach interface kit (CLAUDE.md "Visual & GUI discipline")
##
## Shared components, defined once: panel frame, standard button, section
## header, HP bar, portrait chip, item card. Every game screen uses these.
## All colors/sizes/spacings come from the gui.* constants in gui.rpy.
################################################################################

## Built-in chrome overrides: solid palette colors replace the template's
## generated PNGs so the save/load, preferences, main menu, and history
## screens match the game.

## The say screen chrome -- the lamplight frame set (game/frames.rpy). The
## textbox is a HOLLOW gold frame over its fill; breach_bg_textbox supplies
## fill + frame as one background. The speaker name is INLINE inside the box
## (dialogue reference), so the namebox carries no plate of its own.
style window:
    background breach_bg_textbox

style namebox:
    background None

style frame:
    background Solid(gui.panel_color)

style confirm_frame:
    background Solid(gui.panel_color)

style notify_frame:
    background Solid(gui.panel_color)

style nvl_window:
    background Solid(gui.textbox_color)

style skip_frame:
    background Solid(gui.panel_color)

style choice_button:
    background Solid(gui.panel_color)
    hover_background Solid(gui.panel_hover_color)

style bar:
    left_bar Solid(gui.accent_color)
    right_bar Solid(gui.muted_color)

style vbar:
    top_bar Solid(gui.accent_color)
    bottom_bar Solid(gui.muted_color)

## Lamplight scrollbars: a recessed near-black track with an accent-dim thumb
## that warms to full lamplight on hover -- styled once here for every viewport
## (inventory, shop, sheet, quests, save/load, preferences, history).
style scrollbar:
    base_bar Solid(gui.breach_stage_color)
    thumb Solid(gui.breach_accent_dim_color)
    hover_thumb Solid(gui.breach_accent_color)

style vscrollbar:
    base_bar Solid(gui.breach_stage_color)
    thumb Solid(gui.breach_accent_dim_color)
    hover_thumb Solid(gui.breach_accent_color)

style slider:
    base_bar Solid(gui.muted_color)
    thumb Solid(gui.accent_color)

style vslider:
    base_bar Solid(gui.muted_color)
    thumb Solid(gui.accent_color)

style slot_button:
    background Solid(gui.panel_color)
    hover_background Solid(gui.panel_hover_color)


## The base face for ALL generic screen/UI text is the condensed sans
## (gui.interface_text_font: IBM Plex Sans Condensed) -- stats, numbers,
## lists, captions, the combat HUD. Dialogue overrides via say_dialogue
## (-> gui.text_font, Spectral) and the display tier via breach_display_text
## (-> gui.display_font, Cinzel); neither inherits this, so the three faces
## stay cleanly separated.
style text:
    font gui.interface_text_font


## Type tiers (the reference's hierarchy). The DISPLAY tier is the warm serif
## (gui.display_font) for focal names and section headers; the LABEL tier is
## the uppercased, tracked-out small-caps caption (lane headers, ROUND,
## resource + list labels, class/role). Sizes/colours come from gui tokens;
## callers may override size/colour inline (e.g. an accent or exposed-light
## label). Uppercasing is the caller's job (.upper()) so the label tier never
## mangles a data-driven name.
style breach_display_text is text:
    font gui.display_font
    size gui.size_heading
    color gui.breach_accent_color

style breach_label_text is text:
    font gui.interface_text_font
    size gui.size_micro
    color gui.muted_text_color
    kerning gui.kerning_label


## The panel frame -- THE one reusable framed box for every screen. The slate
## fill (gui.panel_frame_fill) is drawn first; the content sits on it, inset
## by gui.panel_frame_pad so it clears the corner ornament; the shared gold
## nineslice (gui.panel_frame) is drawn LAST, on top, so its transparent
## centre shows the fill and its gold corners/edges frame the panel. Tuning
## lives ENTIRELY in gui.rpy (scale / border / pad / fill) -- never hand-roll
## a panel border per screen; use this component (or breach_panel_lit).
screen breach_panel():
    fixed:
        fit_first True
        frame:
            background gui.panel_frame_fill
            padding (gui.panel_frame_pad, gui.panel_frame_pad)
            transclude
        add gui.panel_frame xsize 1.0 ysize 1.0


## A centred MODAL dialog box: same fill-then-gold recipe as breach_panel, but
## with the bolder modal frame -- for the combat overlays, victory/defeat, the
## reactions page. (Use breach_tooltip for small pop cards.)
screen breach_modal():
    fixed:
        fit_first True
        frame:
            background gui.panel_frame_fill
            padding (gui.modal_frame_pad, gui.modal_frame_pad)
            transclude
        add gui.modal_frame xsize 1.0 ysize 1.0


## A small framed CARD (the tooltip frame) -- the reaction prompt and other
## compact pop-ups.
screen breach_tooltip():
    fixed:
        fit_first True
        frame:
            background gui.panel_frame_fill
            padding (gui.tooltip_frame_pad, gui.tooltip_frame_pad)
            transclude
        add gui.tooltip_frame xsize 1.0 ysize 1.0


## An INTERACTIVE framed panel: the SAME shared gold frame, drawn as the
## button's FOREGROUND (on top of the slate fill, so its transparent centre
## shows the content) and SWAPPED per state -- hover, selected, and
## unavailable use the matching frame art. Set the fill via `background
## Solid(...)` and `selected` / `sensitive` at the call site (insensitive
## shows the disabled frame). Used by the combat lane cards and the
## selectable cards rolled out in later screens.
style breach_panel_button is button:
    background gui.panel_frame_fill
    padding (gui.panel_frame_pad, gui.panel_frame_pad)
    foreground gui.panel_frame
    hover_foreground gui.panel_frame_hover
    selected_foreground gui.panel_frame_selected
    selected_hover_foreground gui.panel_frame_hover
    insensitive_foreground gui.panel_frame_disabled


## The standard button.

style breach_button is button:
    background Solid(gui.panel_color)
    hover_background Solid(gui.panel_hover_color)
    selected_background Solid(gui.panel_hover_color)
    insensitive_background Solid(gui.bg_color)
    padding (gui.pad_m, gui.pad_s)

style breach_button_text is button_text:
    size gui.size_base
    idle_color gui.breach_text_color
    hover_color gui.accent_bright_color
    selected_color gui.breach_accent_color
    insensitive_color gui.muted_text_color

## A stepper +/- button (point-buy): NO background box in ANY state (the
## owner asked for backgroundless step buttons). The button never changes
## shape or shifts the row; enabled vs disabled is shown purely by text
## color. Hover brightens the glyph only -- no box, no shape change.
style breach_step_button is button:
    background None
    hover_background None
    insensitive_background None
    selected_background None
    padding (gui.pad_s, gui.pad_s)
    xalign 0.5

style breach_step_button_text is button_text:
    size gui.size_heading
    xalign 0.5
    idle_color gui.breach_text_color
    hover_color gui.accent_bright_color
    insensitive_color gui.muted_text_color


## The section header.

## Section headers ride the DISPLAY (serif) tier -- one place, so the serif
## swap lights up every screen's headers at once.
style breach_header_text is breach_display_text:
    size gui.size_heading
    color gui.breach_accent_color

screen section_header(label):
    vbox:
        spacing gui.pad_xs
        # breach_lit: headers often carry data-driven names (an item, a party
        # member) that may contain brackets -- show them literally (D-031).
        text breach_lit(label) style "breach_header_text"
        add Solid(gui.panel_border_color) xsize 1.0 ysize 2


## A bare header TITLE (serif amber display tier) -- like section_header but
## WITHOUT the full-width rule, so it can sit in a header hbox beside right-
## aligned actions/breadcrumb WITHOUT the rule expanding to fill the row and
## shoving them off-screen. Use this in top bars; the band's own lip carries
## the rule. (section_header stays for vertical section contexts.)
screen breach_title(label):
    text breach_lit(label) style "breach_header_text"


## The HP bar: bar AND numbers; danger color at Bloodied (at or below half,
## GDD 5.3).

screen hp_bar(current, maximum, width=240, height=12):
    # HP bars are red everywhere (owner adjudication, P1 review, D7); the
    # Bloodied state is signalled separately by the blood-drop marker. A slim
    # red fill over a recessed near-black track reads as a lit wound-line; the
    # count sits quiet to its right (the reference look).
    hbox:
        spacing gui.pad_s
        bar:
            value StaticValue(current, max(1, maximum))
            xsize width
            ysize height
            yalign 0.5
            left_bar Solid(gui.hp_bar_color)
            right_bar Solid(gui.breach_stage_color)
        text ("%s/%s" % (current, maximum)) size gui.size_small color gui.muted_text_color yalign 0.5


## The portrait chip: the placeholder-art pipeline for portraits (colored
## rect + label; real art replaces this one screen, no code changes).

init python:
    def breach_placeholder_color(key):
        return gui.placeholder_colors[hash(key) % len(gui.placeholder_colors)]

    def breach_initials(name):
        parts = name.split()
        return "".join(p[0] for p in parts[:2]).upper() if parts else "?"

    def breach_lit(s):
        """Escape a data-driven string for LITERAL display. Ren'Py runs square
        and curly markup on shown text, so an owner placeholder name would be
        py_eval'd and CRASH at render. Doubling the openers makes it show
        verbatim. Use at every site that renders a registry name/label/title
        that may contain brackets."""
        return (s or "").replace("[", "[[").replace("{", "{{")

screen portrait_chip(char, size=128, action=None, selected=False,
                     show_hp=False, badge=False):
    ## Selected/hover state shows a 2px accent border via the nested-frame
    ## technique: the outer button background is the border colour with 2px
    ## padding, the inner frame fills with the placeholder colour. (A Solid
    ## Frame foreground would fill the whole chip and hide the portrait.)
    button:
        xsize size
        ysize size
        padding (2, 2)
        background Solid(gui.breach_accent_color if selected else breach_placeholder_color(char["class"]))
        hover_background Solid(gui.accent_bright_color if action is not None else breach_placeholder_color(char["class"]))
        selected_background Solid(gui.breach_accent_color)
        action action
        sensitive (action is not None)
        frame:
            background Solid(breach_placeholder_color(char["class"]))
            xfill True
            yfill True
            padding (0, 0)
            vbox:
                align (0.5, 0.5)
                spacing gui.pad_xs
                text breach_initials(char["name"]):
                    size gui.size_heading
                    xalign 0.5
                    color gui.breach_text_color
                text char["class"].capitalize():
                    size gui.size_small
                    xalign 0.5
                    color gui.muted_text_color
            if show_hp:
                bar:
                    value StaticValue(char["hp"], max(1, char["hp_max"]))
                    xsize size
                    ysize 6
                    yalign 1.0
                    left_bar Solid(gui.hp_bar_color)   # red everywhere (D7)
                    right_bar Solid(gui.muted_color)
        if badge:
            text "+" size gui.size_base color gui.breach_accent_color:
                align (1.0, 0.0)


## The item card: inventory, shop, and loot all use this one screen.

style breach_card is breach_button:
    xfill True

screen item_card(item_id, record, count=1, action=None, selected=False,
                 info="", meta=""):
    ## The shared inventory / shop / loot row, now on the bronze framed
    ## list-row (frames.rpy): idle frame normally, the amber-edge + soft-glow
    ## lit frame when selected or hovered. The count rides the right-meta
    ## column (a caller `meta` string overrides it); the name tints by rarity.
    button:
        style "breach_frame_row"
        action action
        sensitive (action is not None)
        selected selected
        hbox:
            spacing gui.pad_m
            xfill True
            yalign 0.5
            add Solid(breach_placeholder_color(item_id)) xsize gui.card_thumb_size ysize gui.card_thumb_size yalign 0.5
            $ breach_card_meta = meta or (("x%d" % count) if count > 1 else "")
            vbox:
                xfill True
                spacing gui.pad_xs
                yalign 0.5
                $ breach_rarity = record.get("rarity") if record else None
                ## name on the left, count/meta pushed to the right (always
                ## visible, clear of any scrollbar); the info line wraps below.
                hbox:
                    xfill True
                    text breach_lit(record["name"] if record else item_id):
                        size gui.size_base
                        color gui.rarity_colors.get(breach_rarity, gui.breach_text_color)
                    if breach_card_meta:
                        null:
                            xfill True
                        text breach_lit(breach_card_meta):
                            size gui.size_small
                            color gui.muted_text_color
                            yalign 0.5
                            text_align 1.0
                if info:
                    text breach_lit(info) size gui.size_small color gui.muted_text_color


## The attribute allocator grid (point-buy at creation AND the level-up
## ASI step share this ONE component so they can never drift). Fixed-width
## columns: name (hard 360px container) | minus | value | plus | modifier |
## a caller-supplied last column. Rows full-width + left-pinned + trailing
## null spacer so every column lands at the same x on every row.
##
## `rows` -- list of dicts, each:
##   name (str), value (int), modifier (int),
##   can_dec (bool), dec_action, can_inc (bool), inc_action, last (str)
## The displayed value IS the caller's screen-variable score (mutated by a
## Set-style action), so it re-renders on every +/- (no stale display).
screen attribute_allocator(rows, last_header="Cost of next"):
    vbox:
        spacing gui.pad_xs
        xfill True

        hbox:
            spacing gui.pad_m
            xfill True
            fixed:
                xsize 360
                yfit True
                yalign 0.5
                text "Attribute" size gui.size_small color gui.muted_text_color xmaximum 360 text_align 0.0 xalign 0.0
            text "" xsize 64
            text "Score" size gui.size_small color gui.muted_text_color xsize 70 xalign 0.5
            text "" xsize 64
            text "Modifier" size gui.size_small color gui.muted_text_color xsize 130 xalign 0.5
            text last_header size gui.size_small color gui.muted_text_color xsize 220
            null:
                xfill True

        for alloc_row in rows:
            hbox:
                spacing gui.pad_m
                xfill True
                fixed:
                    xsize 360
                    yfit True
                    yalign 0.5
                    text alloc_row["name"] size gui.size_base xmaximum 360 text_align 0.0 xalign 0.0
                textbutton "−":
                    style "breach_step_button"
                    xsize 64
                    sensitive alloc_row["can_dec"]
                    action alloc_row["dec_action"]
                text str(alloc_row["value"]) size gui.size_heading xsize 70 xalign 0.5 yalign 0.5 color gui.breach_accent_color
                textbutton "+":
                    style "breach_step_button"
                    xsize 64
                    sensitive alloc_row["can_inc"]
                    action alloc_row["inc_action"]
                text ("%+d" % alloc_row["modifier"]) size gui.size_base xsize 130 xalign 0.5 yalign 0.5 color gui.muted_text_color
                text alloc_row["last"] size gui.size_small xsize 220 color gui.muted_text_color yalign 0.5
                null:
                    xfill True


## Shared tab bar (defined ONCE, CLAUDE.md "Shared components"). The
## character sheet and inventory hand-rolled this idiom; the quest tab and
## shop MUST use this instead of making a third/fourth copy. `tabs` is a list
## of (key, label); `current` is the selected key; `onselect` is a callable
## key -> action (e.g. a lambda returning a SetScreenVariable list).
style breach_tab_button is breach_button:
    background None
    hover_background Solid(gui.panel_hover_color)
    selected_background Solid(gui.panel_color)
    padding (gui.pad_m, gui.pad_s)

style breach_tab_button_text is breach_button_text:
    idle_color gui.muted_text_color
    hover_color gui.accent_bright_color
    selected_color gui.breach_accent_color

screen tab_bar(tabs, current, onselect, tab_style="breach_tab_button"):
    hbox:
        spacing gui.pad_xs
        for tab_key, tab_label in tabs:
            textbutton tab_label:
                style tab_style
                selected (current == tab_key)
                action onselect(tab_key)


## Depth & focal kit (CLAUDE.md "shared styles live here"). The combat screen
## established this language; these are the GENERIC, reusable pieces EVERY
## screen draws on so the whole game shares one look. The kit is breach_*;
## combat-only helpers keep the combat_ prefix.
##
## Value ladder (gui.rpy tokens), darkest -> lightest:
##   breach_seam < breach_stage < bg < panel < panel_hover < breach_lit_panel.

## A recessed dark "ground" -- content sunk BELOW the chrome (the battlefield
## well, a list drawer, a map field). Depth from value, never art.
style breach_well is default:
    background Solid(gui.breach_stage_color)
    padding (gui.pad_m, gui.pad_m)

## A raised, lamplit chrome band -- top/bottom bars share one recipe so they
## read as the same material at the same height.
style breach_band is default:
    background Solid(gui.panel_color)

## A LIT focal panel: the selected / active surface (the selected party member,
## a focused card, the modal that owns the moment) -- the SAME shared gold
## frame as breach_panel, over the brighter lit fill (gui.panel_frame_fill_lit).
screen breach_panel_lit():
    fixed:
        fit_first True
        frame:
            background gui.panel_frame_fill_lit
            padding (gui.panel_frame_pad, gui.panel_frame_pad)
            transclude
        add gui.panel_frame xsize 1.0 ysize 1.0

## Desaturate to "lamplight burning low": spent / inactive / unavailable
## elements lose color and sink into the dark (pair with a dimmed alpha at the
## call site for downed / disabled states).
transform breach_desaturate:
    matrixcolor SaturationMatrix(0.0)

## A horizontal hairline lip -- chrome catching lamplight. Band / panel top
## edges, the ledge above a "a light turns on" row, the Victory level-up ledge.
screen breach_lip(color):
    add Solid(color) xsize 1.0 ysize gui.hairline


## A clean amber OUTLINE (four hairline edges, no fill) -- the "active /
## valid target" cue, drawn OVER a panel to mark the one lit thing without a
## muddy accent wash. Fills its parent (use inside a sized fixed/frame).
screen breach_accent_edge():
    add Solid(gui.breach_accent_color) xsize 1.0 ysize gui.hairline yalign 0.0
    add Solid(gui.breach_accent_color) xsize 1.0 ysize gui.hairline yalign 1.0
    add Solid(gui.breach_accent_color) xsize gui.hairline ysize 1.0 xalign 0.0
    add Solid(gui.breach_accent_color) xsize gui.hairline ysize 1.0 xalign 1.0

## A small chip button: tags, toggles, inline links, hover-tooltip markers.
style breach_chip is breach_button:
    padding (gui.pad_xs, gui.pad_xs)

style breach_chip_text is breach_button_text:
    size gui.size_small

## Class resource readouts. ONE entry point -- breach_resource -- picks the
## right shape by pool size: SEGMENTED PIPS for small discrete pools (spell
## slots, Focus, Rage, Channel Divinity...) -- the reference's segmented
## gauge -- and a continuous AMBER bar for large pools (Lay on Hands). Both
## stay thinner than the red HP bar so the two never read alike. Lit segment
## = lamplight; spent segment = burning low (depth by value). Callers use
## breach_resource and forget the distinction.
screen breach_resource(label, current, maximum):
    if 0 < maximum <= gui.resource_pip_cap:
        use breach_resource_pips(label, current, maximum)
    else:
        use breach_resource_gauge(label, current, maximum)

screen breach_resource_pips(label, current, maximum):
    hbox:
        spacing gui.pad_s
        yalign 0.5
        text label.upper() style "breach_label_text" yalign 0.5
        hbox:
            spacing gui.pad_xs
            yalign 0.5
            for pip_i in range(maximum):
                add Solid(gui.breach_accent_color if pip_i < current else gui.breach_accent_dim_color) xsize gui.pad_m ysize gui.pad_s
        text ("%s/%s" % (current, maximum)) style "breach_label_text" yalign 0.5

screen breach_resource_gauge(label, current, maximum):
    hbox:
        spacing gui.pad_s
        text label.upper() style "breach_label_text" yalign 0.5
        bar:
            value StaticValue(current, max(1, maximum))
            xsize 160
            ysize 10
            yalign 0.5
            left_bar Solid(gui.breach_accent_color)
            right_bar Solid(gui.breach_accent_dim_color)
        text ("%s/%s" % (current, maximum)) style "breach_label_text" yalign 0.5


## Combat-only helper: the concentration ring (cool rare-blue hairline annulus
## around a portrait; the size-px portrait transcludes inside). GDD 15.6.
screen combat_conc_ring(size):
    frame:
        xysize (size + gui.hairline * 2, size + gui.hairline * 2)
        background Solid(gui.breach_conc_ring_color)
        padding (gui.hairline, gui.hairline)
        transclude


## ---------------------------------------------------------------------------
## Reference-layout shared components (CLAUDE.md "shared components, defined
## once"). The menu/content screens COMPOSE these, so every list row, empty
## state, labelled number, tag, and progress bar reads identically game-wide.
## All values come from the gui.* tokens -- no screen reinvents these.

## THE shared framed list row -- inventory / shop / quest / camp / level-up /
## sheet lists (the reference's  icon | title (+ subtitle) | right-meta  row).
## Rides the bronze list-row frame (frames.rpy): the idle frame normally, the
## amber-edge + soft-glow lit frame when selected/hovered. `icon_key` colours
## the leading placeholder swatch (None hides it); `meta` is the right-aligned
## value column; `selected`/`action` drive the focal + click. Pass RAW
## data-driven strings -- this escapes them with breach_lit.
screen breach_list_row(title, subtitle="", meta="", icon_key=None, action=None, selected=False, title_color=None, meta_color=None):
    button:
        style "breach_frame_row"
        action action
        sensitive (action is not None)
        selected selected
        hbox:
            spacing gui.pad_m
            xfill True
            yalign 0.5
            if icon_key is not None:
                add Solid(breach_placeholder_color(icon_key)) xsize gui.card_thumb_size ysize gui.card_thumb_size yalign 0.5
            vbox:
                xfill True
                spacing gui.pad_xs
                yalign 0.5
                ## title row: name on the left, the right-meta pushed to the
                ## right by a filler -- so the meta (price/count/modifier) is
                ## always visible and never hides behind a scrollbar.
                hbox:
                    xfill True
                    text breach_lit(title):
                        size gui.size_base
                        color (title_color or gui.breach_text_color)
                    if meta:
                        null:
                            xfill True
                        text breach_lit(meta):
                            size gui.size_small
                            color (meta_color or gui.muted_text_color)
                            yalign 0.5
                            text_align 1.0
                if subtitle:
                    text breach_lit(subtitle) size gui.size_micro color gui.muted_text_color


## A centred, structured empty state -- never a bare floating line. Drop it
## inside a panel/well; a quiet glyph mark over a line and optional caption.
screen breach_empty_state(message, sub=""):
    vbox:
        align (0.5, 0.5)
        spacing gui.pad_s
        text "—" size gui.size_title color gui.panel_border_color xalign 0.5
        text breach_lit(message) size gui.size_base color gui.muted_text_color xalign 0.5
        if sub:
            text breach_lit(sub) size gui.size_micro color gui.muted_text_color xalign 0.5


## A labelled-number CELL: caption (micro, muted, small-caps) over a value
## (heading). The reference's instrument cluster -- AC/Init/Prof, camp and
## expedition readouts, the point-buy figure. Center-aligned for a row of cells.
screen breach_stat_cell(label, value, value_color=None):
    vbox:
        spacing gui.pad_xs
        text label.upper() style "breach_label_text" xalign 0.5
        text breach_lit(str(value)) size gui.size_heading color (value_color or gui.breach_text_color) xalign 0.5


## A  label | value  data ROW (level-up ledger, summary key/values). Fixed
## label column (gui.stat_label_w) so values align down a list.
screen breach_stat_line(label, value, value_color=None):
    hbox:
        spacing gui.pad_m
        xfill True
        text breach_lit(label) size gui.size_small color gui.muted_text_color xsize gui.stat_label_w yalign 0.5
        text breach_lit(str(value)) size gui.size_base color (value_color or gui.breach_text_color) yalign 0.5


## A read-only TAG chip (role tags, "always prepared", reward items, node
## kind). Small-caps on a recessed ground; colour conveys the category.
screen breach_tag(label, color=None):
    frame:
        background Solid(gui.breach_stage_color)
        padding (gui.pad_s, gui.pad_xs)
        text breach_lit(label).upper():
            size gui.size_micro
            color (color or gui.breach_accent_color)
            kerning gui.kerning_label


## An amber PROGRESS bar (XP / generic fill) -- sibling to hp_bar (red) and
## breach_resource (amber pool), so progress reads alike everywhere.
screen breach_progress(current, maximum, width=320, height=16, label=""):
    hbox:
        spacing gui.pad_s
        bar:
            value StaticValue(current, max(1, maximum))
            xsize width
            ysize height
            yalign 0.5
            left_bar Solid(gui.breach_accent_color)
            right_bar Solid(gui.breach_stage_color)
        if label:
            text breach_lit(label) size gui.size_small color gui.muted_text_color yalign 0.5
