# game/toast.rpy -- the shared, non-blocking toast channel.
#
# ONE mechanism, reused everywhere a short status line must surface without
# pausing play: the GDD 15.1 "Quest updated" toast (top-left) and the GDD
# 15.5 mandatory "Quest completed / Quest failed" line (the ONLY end-of-quest
# signal). Quests, the shop, and dialogue all call breach_toast(msg) -- they
# never roll their own corner notice.
#
# Why not renpy.notify: that renders bottom-centre (the wrong corner) and is a
# single-slot channel. A breach toast lands TOP-LEFT and several can stack, so
# a burst of updates ("Quest updated" then "Reward: 50 gold") all read.
#
# Mechanism: a small store-level queue of (id, text). breach_toast appends and
# restarts the interaction so the always-live overlay re-renders at once. Each
# queued entry carries its own self-dismiss timer that pops itself by id after
# about three seconds. Empty queue renders nothing.


## The queue: a list of (id, text). Store-level so helpers and the overlay
## share it; persists through rollback like any default.
default breach_toast_queue = []


init python:

    # A monotonic id so a timer pops exactly its OWN entry, even after earlier
    # entries have already drained and shifted the list. Module-scope, mutated
    # via store. (Not a default: it need not survive rollback -- ids only have
    # to be unique among entries alive at once.)
    store.breach_toast_next_id = 0

    def breach_toast(message):
        """Enqueue a short status line to show TOP-LEFT, auto-dismissing
        after ~3s. Non-blocking: never pauses play. Safe to call from any
        screen action, label, or python block."""
        if not message:
            return
        tid = store.breach_toast_next_id
        store.breach_toast_next_id = tid + 1
        store.breach_toast_queue.append((tid, message))
        # Force the always-live overlay to re-render now so the toast appears
        # immediately rather than at the next interaction.
        renpy.restart_interaction()

    def breach_toast_dismiss(tid):
        """A toast's own timer fired: drop just that entry (matched by id, so
        draining is order-independent) and re-render."""
        store.breach_toast_queue = [
            entry for entry in store.breach_toast_queue if entry[0] != tid]
        renpy.restart_interaction()


## Register the overlay always-live, mirroring screens.rpy's quick_menu
## registration so it rides on top of every screen (city, combat, sheet...).
init python:
    config.overlay_screens.append("breach_toast_overlay")


## A toast card: the shared nested-frame panel look (border colour + hairline
## pad, panel fill) -- the same recipe as breach_panel, so the overlay reads as
## the same game as every other screen. notify_frame is already restyled to
## Solid(gui.panel_color) in style.rpy; the bordered card gives a crisper
## top-left notice that a lamplit lip then marks as "a status just lit up."
style breach_toast_frame is default:
    # the accent border is the toast's "a status lit up" signal (a lamplit
    # edge), the panel fill its body -- a small nested-frame card.
    background Solid(gui.breach_accent_color)
    padding (gui.hairline, gui.hairline)

style breach_toast_inner is default:
    background Solid(gui.panel_color)
    padding (gui.pad_m, gui.pad_s)

## micro/small caption tier -- a quiet, non-blocking notice never shouts.
style breach_toast_text is text:
    size gui.notify_text_size
    color gui.breach_text_color


## A short ease-in (and ease-out as the entry drains) so the notice glides like
## the built-in notify (~.25s in / .4s out) instead of popping in and snapping
## away. The on-hide fade plays when a toast's timer removes it from the queue.
transform breach_toast_anim:
    on show:
        alpha 0.0
        ease 0.25 alpha 1.0
    on hide:
        ease 0.4 alpha 0.0


## The overlay: top-left, high zorder, non-modal (play continues underneath).
## Renders nothing when the queue is empty. Each queued message is its own
## card with its own self-dismiss timer.
screen breach_toast_overlay():

    zorder 200

    if breach_toast_queue:
        vbox:
            xalign 0.0
            yalign 0.0
            xoffset gui.pad_l
            yoffset gui.pad_l
            spacing gui.pad_s

            for breach_toast_id, breach_toast_msg in breach_toast_queue:
                frame:
                    style "breach_toast_frame"
                    at breach_toast_anim
                    ## a small amber-edged card: the accent border IS the "a
                    ## status lit up" signal -- no full-width lip (this frame is
                    ## content-sized, so a lip would stretch it across the screen).
                    frame:
                        style "breach_toast_inner"
                        # breach_lit: a toast may carry a data-derived name;
                        # show it literally, never as [interpolation] (D-031).
                        text breach_lit(breach_toast_msg) style "breach_toast_text"

                # Each entry dismisses ITSELF by id (~3s), so a later toast
                # never cuts an earlier one short.
                timer 3.0:
                    action Function(breach_toast_dismiss, breach_toast_id)
