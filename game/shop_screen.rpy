# The shop screen (GDD #15.8 L1608-1612, economy #14.3/#14.5). Buy and Sell
# tabs; the shop stock on the left, the shared party inventory on the right,
# the party's gold kept prominent up top. Pricing, the "never sold" gates,
# and the Rare-plus sell confirmation all live in core.shop -- this screen
# only displays what shop_listing / can_sell / needs_sell_confirm return and
# surfaces the engine's own refusal reasons (CLAUDE.md: one registry).
#
# Rollback (GDD #16.1): core.shop never blocks rollback; the buy/sell helpers
# below call renpy.block_rollback() in THIS layer immediately after every
# committed purchase or sale.
#
# This screen reuses the shared item_card / tab_bar / panel / section_header
# components (CLAUDE.md "Shared components"); it never recreates them.

default breach_shop_error = None


init python:

    def breach_shop_item_record(item_id):
        """The record for the item card, looked up across the catalogues a
        shop can deal in. Falls back to a display-name-only record so a
        listing never crashes on an unpriced curiosity."""
        for table in ("consumables", "magic_items", "relics", "weapons", "armor"):
            rec = REG.get(table, {}).get(item_id)
            if rec is not None:
                return rec
        return {"name": str(item_id).replace("_", " ").title()}

    def breach_shop_item_info(item_id):
        """A one-line description for the item card (GDD #15.0). Consumables /
        relics / magic items route through the DISPLAY voice layer (the voice
        gate covers them). Weapons and armor have no authored blurb, so they
        show their mechanical line instead -- the BG3-style mechanical readout
        the UI is allowed to surface (CLAUDE.md)."""
        for table in ("consumables", "relics", "magic_items"):
            if item_id in REG.get(table, {}):
                fallback = REG[table][item_id].get("effect", "")
                return breach_player_text(REG, table, item_id, fallback)
        w = REG.get("weapons", {}).get(item_id)
        if w is not None:
            return "%s %s" % (w["dice"], w["damage_type"])
        a = REG.get("armor", {}).get(item_id)
        if a is not None:
            return "AC %d" % a["base_ac"]
        return ""

    def breach_shop_buy(shop_id, item_id):
        """Buy one unit; on success block rollback (a committed purchase,
        GDD #16.1) and toast. Failures are re-voiced (#15.0) -- the engine's
        raw text can carry an internal id, so never surface it verbatim."""
        try:
            bshop.buy(REG, gs, shop_id, item_id)
            renpy.block_rollback()
            store.breach_shop_error = None
            breach_toast("Purchased %s." % breach_shop_item_record(item_id)["name"])
        except ValueError as e:
            store.breach_shop_error = ("Not enough gold."
                                       if "gold" in str(e)
                                       else "That is unavailable right now.")

    def breach_shop_sell(item_id):
        """Sell one unit; on success block rollback (a committed sale, GDD
        #16.1) and toast the gold credited. The specific can-sell reason is
        already shown beside the (insensitive) Sell button, so the failure
        path here is a re-voiced backstop (#15.0)."""
        try:
            credit = bshop.sell(REG, gs, item_id)
            renpy.block_rollback()
            store.breach_shop_error = None
            breach_toast("Sold for %d gold." % credit)
        except ValueError:
            store.breach_shop_error = "This vendor will not buy that."

    def breach_shop_sell_rows():
        """The shared inventory ids that have a sell credit (relics, gear)
        -- everything else isn't sellable here (core.shop.sell_credit)."""
        return [iid for iid in sorted(gs["inventory"])
                if bshop.sell_credit(REG, iid) is not None]


## The shop. shop_id keys REG["shops"]; the screen reads the live listing
## and the shared party inventory, and returns nothing meaningful.

screen shop_screen(shop_id):
    modal True
    add Solid(gui.bg_color)

    default mode = "buy"
    default sel = None

    $ shop_name = REG["shops"][shop_id]["name"]

    frame:
        background None
        xfill True
        yfill True
        padding (gui.pad_l, gui.pad_l)

        vbox:
            spacing gui.pad_m
            xfill True

            ## Header band: name, gold, Close, Buy/Sell tabs.
            use breach_shop_header(shop_name, mode)
            use breach_lip(gui.breach_accent_color)

            ## The two columns sink onto a recessed stage ground so the panels
            ## read as chrome raised over a darker field (combat/inventory
            ## depth language). Depth from value only -- no art.
            frame:
                style "breach_well"
                xfill True
                padding (gui.pad_m, gui.pad_m)
                hbox:
                    spacing gui.pane_gap
                    xfill True
                    ## LEFT: the list -- shop stock (Buy) or sellable inventory (Sell).
                    use breach_shop_list(shop_id, mode, sel)
                    ## RIGHT: the action panel for the selected item.
                    use breach_shop_detail_panel(shop_id, mode, sel)


## --- shop regions (composed by shop_screen via `use`) ----------------------
## State (mode / sel) lives on shop_screen; each region receives what it reads
## and its SetScreenVariable actions resolve against the shown screen.

## Header band: the shop's chrome -- the name on the left, gold PROMINENT on
## the right (the shop is where gold matters, #15.8), the Close exit, then the
## Buy / Sell tabs.
screen breach_shop_header(shop_name, mode):
    frame:
        style "breach_band"
        xfill True
        padding (gui.pad_l, gui.pad_m)
        vbox:
            spacing gui.pad_m
            xfill True

            ## Top tier: shop name + breadcrumb caption LEFT (the loudest
            ## title), party gold framed as a top-right resource readout, Close.
            hbox:
                xfill True
                ## Left block: title over a small-caps role caption.
                vbox:
                    spacing gui.pad_xs
                    yalign 0.5
                    use breach_title(shop_name)
                    text "SHOP" style "breach_label_text"
                null:
                    xfill True
                ## Right block: gold as a framed resource chip + Close.
                hbox:
                    spacing gui.pad_m
                    xalign 1.0
                    yalign 0.5
                    frame:
                        style "breach_well"
                        padding (gui.pad_m, gui.pad_s)
                        yalign 0.5
                        hbox:
                            spacing gui.pad_s
                            yalign 0.5
                            add Solid(gui.breach_accent_color) xsize gui.pad_m ysize gui.pad_m yalign 0.5
                            text "GOLD" style "breach_label_text" yalign 0.5
                            text ("%d" % gs["gold"]):
                                size gui.size_heading
                                color gui.breach_accent_color
                                yalign 0.5
                    textbutton "Close Shop":
                        style "breach_frame_button"
                        yalign 0.5
                        action Return(None)

            ## Buy / Sell tabs (shared tab_bar). Switching a tab clears the
            ## selection and any stale refusal message.
            use tab_bar([("buy", "Buy"), ("sell", "Sell")], mode,
                        lambda k: [SetScreenVariable("mode", k),
                                   SetScreenVariable("sel", None),
                                   SetVariable("breach_shop_error", None)])


## LEFT region: the list -- shop stock (Buy) or sellable party inventory
## (Sell). The list is sunk into a recessed well; framed rows rise on panel
## above it (DESIGN s6: lists on breach_well, rows on the bronze frame). Rows
## carry the reference anatomy -- icon | name (rarity-tinted) | blurb | the
## money in its own right-aligned meta column. The Buy/Sell wells share ONE
## body screen (shop_list_well) so the two tabs cannot drift.
screen breach_shop_list(shop_id, mode, sel):
    frame:
        background None
        xsize gui.list_pane_w
        use breach_panel():
            vbox:
                spacing gui.pad_m
                xfill True

                if mode == "buy":
                    use section_header("Available Stock")
                    $ breach_shop_rows = bshop.shop_listing(REG, gs, shop_id)
                    use shop_list_well():
                        if breach_shop_rows:
                            for row in breach_shop_rows:
                                $ b_id = row["item_id"]
                                $ b_rec = row["record"]
                                $ b_price = row["price"]
                                $ b_rem = row["remaining"]
                                $ b_sold = row["sold_out"]
                                if b_rem is None:
                                    $ b_stock = ""
                                elif b_rem == 0:
                                    $ b_stock = "Sold out"
                                else:
                                    $ b_stock = "%d in stock" % b_rem
                                $ b_name = (b_rec["name"] if b_rec else b_id)
                                $ b_blurb = breach_shop_item_info(b_id)
                                $ b_rarity = (b_rec.get("rarity") if b_rec else None)
                                $ b_meta = ("%d gold" % b_price) + ("\n" + b_stock if b_stock else "")
                                ## Sold-out rows sink: desaturate + dim and go
                                ## unclickable (action None). Live and sold-out
                                ## rows share ONE row component -- identical DOM,
                                ## so heights/alignment never diverge.
                                if b_sold:
                                    frame:
                                        background None
                                        xfill True
                                        at [breach_desaturate, Transform(alpha=0.5)]
                                        use breach_list_row(b_name,
                                            subtitle=b_blurb,
                                            meta=b_meta,
                                            icon_key=b_id,
                                            title_color=gui.rarity_colors.get(b_rarity, gui.breach_text_color))
                                else:
                                    use breach_list_row(b_name,
                                        subtitle=b_blurb,
                                        meta=b_meta,
                                        icon_key=b_id,
                                        action=[SetVariable("breach_shop_error", None),
                                                SetScreenVariable("sel", b_id)],
                                        selected=(sel == b_id),
                                        title_color=gui.rarity_colors.get(b_rarity, gui.breach_text_color),
                                        meta_color=gui.breach_accent_color)
                        else:
                            use breach_empty_state("Nothing for sale here.",
                                sub="This vendor has emptied their shelves.")

                else:
                    use section_header("Sellable Goods")
                    $ breach_sell_rows = breach_shop_sell_rows()
                    use shop_list_well():
                        if breach_sell_rows:
                            for s_id in breach_sell_rows:
                                $ s_rec = breach_shop_item_record(s_id)
                                $ s_credit = bshop.sell_credit(REG, s_id)
                                $ s_count = gs["inventory"][s_id]
                                $ s_blurb = breach_shop_item_info(s_id)
                                $ s_rarity = s_rec.get("rarity")
                                $ s_meta = ("Sell for %d gold" % s_credit) + ("\nx%d" % s_count if s_count > 1 else "")
                                use breach_list_row(s_rec["name"],
                                    subtitle=s_blurb,
                                    meta=s_meta,
                                    icon_key=s_id,
                                    action=[SetVariable("breach_shop_error", None),
                                            SetScreenVariable("sel", s_id)],
                                    selected=(sel == s_id),
                                    title_color=gui.rarity_colors.get(s_rarity, gui.breach_text_color),
                                    meta_color=gui.breach_accent_color)
                        else:
                            use breach_empty_state("Nothing sellable here.",
                                sub="This vendor buys relics and magic gear.")


## The shared list well: ONE recessed scrolling ground both tabs pour their
## rows into, so the Buy and Sell lists can never drift in height, padding, or
## ground. The caller transcludes the rows (or the empty state).
screen shop_list_well():
    frame:
        style "breach_well"
        xfill True
        viewport:
            scrollbars "vertical"
            mousewheel True
            ysize gui.list_well_h
            vbox:
                spacing gui.pad_s
                xfill True
                transclude


## RIGHT region: the action panel for the selected item -- a lit focal panel
## when an item is in hand, a quiet panel otherwise; both share
## shop_detail_body (DESIGN s3/s6).
screen breach_shop_detail_panel(shop_id, mode, sel):
    $ shop_has_sel = ((mode == "buy" and bool(sel))
                      or (mode == "sell" and bool(sel)
                          and gs["inventory"].get(sel, 0) > 0))
    frame:
        background None
        xsize gui.detail_pane_w
        yfill True
        if shop_has_sel:
            use breach_panel_lit():
                use shop_detail_body(shop_id, mode, sel)
        else:
            use breach_panel():
                use shop_detail_body(shop_id, mode, sel)


## The detail / action body for the selected item: name (rarity-tinted),
## the re-voiced blurb, the price or sell credit (accent), the Buy / Sell
## action, and any refusal reason. Defined once so the lit and quiet panel
## wrappers share it (the same idiom as combat_plate_body).

screen shop_detail_body(shop_id, mode, sel):
    vbox:
        spacing gui.pad_l
        xfill True
        use section_header("Item Details")

        if mode == "buy" and sel:
            $ buy_rows = bshop.shop_listing(REG, gs, shop_id)
            $ buy_row = ([r for r in buy_rows if r["item_id"] == sel] or [None])[0]
            if buy_row:
                $ buy_rec = buy_row["record"]
                $ buy_price = buy_row["price"]
                $ buy_sold = buy_row["sold_out"]
                $ buy_can_afford = (gs["gold"] >= buy_price)
                $ buy_info = breach_shop_item_info(sel)
                if buy_sold:
                    $ buy_reason = "Sold out."
                elif not buy_can_afford:
                    $ buy_reason = "Not enough gold."
                else:
                    $ buy_reason = ""
                use shop_detail_card(
                    item_id=sel,
                    name=(buy_rec["name"] if buy_rec else sel),
                    rarity=(buy_rec.get("rarity") if buy_rec else None),
                    blurb=buy_info,
                    money_label=("%d gold" % buy_price),
                    money_caption="Price",
                    button_label="Buy",
                    action=Function(breach_shop_buy, shop_id, sel),
                    sensitive=(buy_can_afford and not buy_sold),
                    reason=buy_reason)

        elif mode == "sell" and sel and gs["inventory"].get(sel, 0) > 0:
            $ sell_rec = breach_shop_item_record(sel)
            $ sell_name = sell_rec["name"]
            $ sell_credit = bshop.sell_credit(REG, sel)
            $ sell_ok, sell_reason = bshop.can_sell(REG, sel)
            $ sell_info = breach_shop_item_info(sel)
            $ sell_money = ("%d gold" % sell_credit) if sell_credit is not None else ""
            ## A Rare-plus sale asks first (#14.5); the "never sold" gates
            ## (Very Rare, +3, quest items) come back as can_sell reasons.
            if sell_ok and bshop.needs_sell_confirm(REG, sel):
                $ sell_action = Confirm(
                    "Sell %s for %d gold?" % (breach_lit(sell_name), sell_credit),
                    yes=Function(breach_shop_sell, sel))
            else:
                $ sell_action = Function(breach_shop_sell, sel)
            use shop_detail_card(
                item_id=sel,
                name=sell_name,
                rarity=sell_rec.get("rarity"),
                blurb=sell_info,
                money_label=sell_money,
                money_caption="Sell for",
                button_label="Sell",
                action=sell_action,
                sensitive=sell_ok,
                reason=("" if sell_ok else sell_reason))

        else:
            ## The designed resting state -- one focal empty composition,
            ## centred and padded, never a bare floating line.
            $ shop_empty_sub = ("Choose something from the list to buy."
                                if mode == "buy"
                                else "Choose something from the list to sell.")
            use breach_empty_state("No item selected", sub=shop_empty_sub)

        ## The engine's refusal text (out of stock, not enough gold, a
        ## blocked sale) -- shown verbatim.
        if breach_shop_error:
            text breach_lit(breach_shop_error):
                size gui.size_micro
                color gui.danger_color
                xalign 0.5


## ONE detail / action card, fed resolved values, so the Buy and Sell branches
## share the same anatomy and cannot drift. Title block (icon swatch + the
## rarity-tinted name) -> hairline rule -> re-voiced blurb -> the money as the
## focal value (caption over an accent figure) -> the framed action button ->
## any danger reason. All strings arrive raw and are escaped here.
screen shop_detail_card(item_id, name, rarity, blurb, money_label, money_caption, button_label, action, sensitive, reason):
    vbox:
        spacing gui.pad_l
        xfill True

        ## Title block: bevelled icon swatch beside the rarity-tinted name.
        hbox:
            spacing gui.pad_m
            xfill True
            yalign 0.5
            frame:
                style "breach_well"
                padding (gui.pad_xs, gui.pad_xs)
                yalign 0.5
                add Solid(breach_placeholder_color(item_id)) xsize gui.card_thumb_size ysize gui.card_thumb_size
            text breach_lit(name):
                size gui.size_heading
                color gui.rarity_colors.get(rarity, gui.breach_text_color)
                yalign 0.5

        add Solid(gui.panel_border_color) xsize 1.0 ysize gui.hairline

        if blurb:
            text breach_lit(blurb):
                size gui.size_small
                color gui.muted_text_color

        ## The money -- the focal "what it costs / commit" value.
        if money_label:
            vbox:
                spacing gui.pad_xs
                text money_caption.upper() style "breach_label_text"
                text breach_lit(money_label):
                    size gui.size_heading
                    color gui.breach_accent_color

        textbutton button_label:
            style "breach_frame_button"
            sensitive sensitive
            action action

        if reason:
            text breach_lit(reason):
                size gui.size_micro
                color gui.danger_color
