# game/frames.rpy -- THE single style source for the lamplight 9-slice frame
# set (CLAUDE.md "one style source"; DESIGN.md). Presentation only.
#
# Each frame is a transparent gold border drawn over a fill; the gold is BAKED
# into the art, so it NO LONGER reads gui.breach_accent_color -- retuning the
# accent means re-exporting the 15 PNGs as a set (see DECISIONS.md). Every
# frame carries its OWN 9-slice border (never shared); the border values live
# here, ONCE -- no screen calls Frame() with a literal path or border.
#
# The frames are HOLLOW: breach_framed() stacks a gui.* solid fill BEHIND the
# border, so callers get a filled, framed surface from ONE displayable -- as a
# style background (the state-swap styles below) or a screen panel.

init -1 python:

    def breach_framed(frame, fill=None):
        """A hollow 9-slice border over a solid fill -- one displayable for a
        filled, framed surface (DESIGN s5.6 / task s3). Pass a lit fill
        (gui.breach_lit_panel_color) for selected / focal surfaces."""
        return Fixed(Solid(fill if fill is not None else gui.panel_color),
                     frame, fit_first=False)


# --- The named frames: the ONLY place a frame path + border literal lives.
# Border is (left, top, right, bottom); a single value = all four sides.
# (GAPS.md: the spec names the default panel "panel_frame_default.png"; the
# placed file is "panel_frame.png" -- referencing the placed name; repoint
# this one line if the asset lands under the spec name.)
# The panel-frame border is shared with gui.panel_frame (gui.rpy) so the SAME
# PNG never renders at two different 9-slice borders -- one value per asset.
define breach_frame_textbox        = Frame("gui/frames/ui_frame_textbox.png", 110, 110)
define breach_frame_portrait       = Frame("gui/frames/ui_frame_portrait.png", 72, 72)
define breach_frame_list_row       = Frame("gui/frames/ui_frame_list_row.png", 20, 20)
define breach_frame_list_row_sel   = Frame("gui/frames/ui_frame_list_row_selected.png", 20, 20)
define breach_frame_button_idle    = Frame("gui/frames/ui_frame_button_idle.png", 28, 20, 48, 20)
define breach_frame_button_hover   = Frame("gui/frames/ui_frame_button_hover.png", 28, 20, 48, 20)
define breach_frame_button_sel     = Frame("gui/frames/ui_frame_button_selected.png", 28, 20, 48, 20)
define breach_frame_button_disabled = Frame("gui/frames/ui_frame_button_disabled.png", 28, 20, 48, 20)

# --- Filled-frame surfaces (fill behind frame), per role/state. ONE place.
# Selected / focal states sit on the lit fill (gui.breach_lit_panel_color).
define breach_bg_textbox        = breach_framed(breach_frame_textbox, gui.textbox_color)
define breach_bg_list_row          = breach_framed(breach_frame_list_row)
define breach_bg_list_row_selected = breach_framed(breach_frame_list_row_sel, gui.breach_lit_panel_color)
## Distinct HOVER (brighter slate fill, idle frame -- NOT the amber-lit selected
## frame) and DISABLED (sunk to the darkest fill) list-row surfaces, so hover,
## selected, and unavailable each read apart. No new art -- fills behind the
## shared idle frame.
define breach_bg_list_row_hover    = breach_framed(breach_frame_list_row, gui.panel_hover_color)
define breach_bg_list_row_disabled = breach_framed(breach_frame_list_row, gui.bg_color)
define breach_bg_button          = breach_framed(breach_frame_button_idle)
define breach_bg_button_hover    = breach_framed(breach_frame_button_hover)
define breach_bg_button_selected = breach_framed(breach_frame_button_sel, gui.breach_lit_panel_color)
define breach_bg_button_disabled = breach_framed(breach_frame_button_disabled, gui.bg_color)

# --- Frame content paddings (clear the border art). ONE place; never per
# screen. The button frame's marker (selected ediamond) lives on the RIGHT,
# so its right padding is larger than its left (task s4).
define gui.frame_btn_pad_l   = 28    # clears the left cap + leaves room for an icon
define gui.frame_btn_pad_r   = 44    # clears the right marker zone
define gui.frame_btn_pad_y   = 12    # button height stays compact with the label


# --- State-swap styles: ONE style carries all states (task s2). The frame
# swaps on background / hover_ / selected_ / selected_hover_ / insensitive_;
# each background is a filled-frame surface, so the fill rides with it.

## A framed button (tabs, menu items, command buttons). Icon + label are the
## CONTENT (hbox child), inset so the left clears the icon and the right
## clears the selected-marker zone (task s4).
style breach_frame_button is button:
    background breach_bg_button
    hover_background breach_bg_button_hover
    selected_background breach_bg_button_selected
    selected_hover_background breach_bg_button_selected
    insensitive_background breach_bg_button_disabled
    padding (gui.frame_btn_pad_l, gui.frame_btn_pad_y, gui.frame_btn_pad_r, gui.frame_btn_pad_y)

style breach_frame_button_text is button_text:
    size gui.size_base
    idle_color gui.breach_text_color
    hover_color gui.accent_bright_color
    selected_color gui.breach_accent_color
    insensitive_color gui.muted_text_color

## A framed list row (inventory / shop / quest / spell rows): idle vs
## hover/selected.
style breach_frame_row is button:
    background breach_bg_list_row
    hover_background breach_bg_list_row_hover
    selected_background breach_bg_list_row_selected
    selected_hover_background breach_bg_list_row_selected
    insensitive_background breach_bg_list_row_disabled
    ## compact rows (a 1-line row ~46px, a title+subtitle row ~70px). The RIGHT
    ## inset reserves room for a vertical scrollbar so the right-meta (price,
    ## count, modifier) never hides behind it in a scrolling list.
    padding (gui.pad_l, gui.pad_s, gui.pad_l + gui.scrollbar_size, gui.pad_s)
    xfill True

## Text style for a `textbutton ... style "breach_frame_row"` (e.g. dialogue
## choices) -- shares the framed-button text tier so colour/states match.
style breach_frame_row_text is breach_frame_button_text

## A gear SOCKET -- the framed row with SYMMETRIC padding (no scrollbar inset),
## for the paper-doll where sockets are NOT in a scrolling list and need every
## pixel of width for the equipped-item name.
style breach_frame_socket is breach_frame_row:
    padding (gui.pad_l, gui.pad_s)
