# -*- coding: utf-8 -*-
"""The choice-stepper navigation logic (GDD #3 step 4, #15.2), extracted
from the Ren'Py screen layer so it is unit-testable. The Ren'Py wrapper
(choice_steps.rpy) supplies a `present` callback that shows the modal step
and returns ("ok", selection) or ("back",); everything else here is pure.

Root cause A (owner adjudication, P1 review): a Back/Cancel signal is a
navigation result, NEVER a selection -- apply_choice is only ever reached
with an ("ok", selection) result.
"""

import copy

from core import character as ch
from core import ui_options as uo


def run_choices(registry, char, pending, present, summarize=None):
    """Drive the stepper. `present(char, choice, opts)` returns
    ("ok", selection) or ("back",) (or any other value, treated as Back).
    `summarize(choice, selection)` -> str builds the confirm-screen log
    line (defaults to a registry-free summary).

    Mutates `char` in place as choices commit; on Back it restores the
    pre-choice snapshot. Returns {"status": "done", "log": [(title, summary)]}
    or {"status": "back"} when the player backs out of the first choice."""
    if summarize is None:
        summarize = lambda choice, sel: _SUMMARY(sel)
    queue = list(pending)
    log = []
    history = []   # pre-state snapshots of each APPLIED presented step
    while queue:
        choice = queue[0]
        opts = uo.options_for(registry, char, choice)
        # zero-pick list choices auto-resolve: no screen, no Back stop
        if opts["mode"] == "list" and opts["pick"] == 0:
            ch.apply_choice(registry, char, choice, [])
            queue.pop(0)
            continue
        snap = {"char": copy.deepcopy(char),
                "queue": list(queue), "log": list(log)}
        result = present(char, choice, opts)
        if not (isinstance(result, (tuple, list)) and len(result) >= 1
                and result[0] == "ok"):
            # BACK (or any stray value): never reaches apply_choice
            if history:
                prev = history.pop()
                char.clear()
                char.update(prev["char"])
                queue = prev["queue"]
                log = prev["log"]
                continue
            return {"status": "back"}
        selection = result[1] if len(result) >= 2 else None
        history.append(snap)
        follow = ch.apply_choice(registry, char, choice, selection)
        queue.pop(0)
        queue = list(follow or []) + queue
        log.append((uo.choice_title(choice), summarize(choice, selection)))
    return {"status": "done", "log": log}


def _SUMMARY(selection):
    # placeholder hook; the Ren'Py wrapper passes a registry-aware
    # summarizer. Kept minimal here so the pure module has no Ren'Py deps.
    if isinstance(selection, dict):
        if selection.get("mode") == "asi":
            return ", ".join("%s +%d" % (a.upper(), n)
                             for a, n in selection["scores"].items())
        if selection.get("mode") == "talent":
            return str(selection.get("talent", "")).replace("_", " ").title()
        if "cantrips" in selection:
            return "%s initiate" % str(selection.get("class", "")).title()
    if isinstance(selection, (list, set, tuple)):
        return ", ".join(str(s).replace("_", " ").title() for s in selection) \
            or "(none)"
    return str(selection).replace("_", " ").title()
