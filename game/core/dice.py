"""Seedable dice. All game randomness flows through this module so the debug
hub can seed it for reproducible fights (CLAUDE.md P0).

Rolls happen at resolution time and are never pre-computed into state
(GDD #16.1, L1583-1588).
"""

import random
import re

_rng = random.Random()

_DICE_RE = re.compile(r"^\s*(\d+)d(\d+)\s*(?:([+-])\s*(\d+))?\s*$")


def seed(value):
    """Seed the shared RNG. None reseeds from system entropy."""
    _rng.seed(value)


def d(sides):
    """Roll one die."""
    return _rng.randint(1, sides)


def parse(notation):
    """'3d6+2' -> (count, sides, flat). Raises ValueError on bad notation."""
    m = _DICE_RE.match(notation)
    if not m:
        raise ValueError("bad dice notation: %r" % (notation,))
    count, sides = int(m.group(1)), int(m.group(2))
    flat = int(m.group(4) or 0)
    if m.group(3) == "-":
        flat = -flat
    return count, sides, flat


def roll(notation, bonus=0):
    """Roll dice notation plus an optional flat bonus. Returns the total."""
    count, sides, flat = parse(notation)
    return sum(d(sides) for _ in range(count)) + flat + bonus


def roll_detail(notation, bonus=0):
    """Like roll(), but returns {'dice': [..], 'flat': n, 'total': n}."""
    count, sides, flat = parse(notation)
    dice = [d(sides) for _ in range(count)]
    return {"dice": dice, "flat": flat + bonus, "total": sum(dice) + flat + bonus}


def d20(advantage=0):
    """One d20 test die. advantage: +1 advantage, -1 disadvantage, 0 normal.

    Multiple sources never stack and adv+dis cancel to a single die
    (GDD #2.2, L60-63) -- callers pass the already-cancelled net value.
    Returns (kept, all_rolls).
    """
    if advantage > 0:
        rolls = [d(20), d(20)]
        return max(rolls), rolls
    if advantage < 0:
        rolls = [d(20), d(20)]
        return min(rolls), rolls
    r = d(20)
    return r, [r]


def d20_test(modifier, dc, advantage=0):
    """Resolve one d20 test per GDD #2.2 (L53-58). Returns a result dict.

    Natural 1/20 special-casing applies to ATTACKS only (GDD #2.4, L79-83);
    attack resolution layers that on in the combat engine (P2).
    """
    kept, rolls = d20(advantage)
    total = kept + modifier
    return {
        "die": kept,
        "rolls": rolls,
        "modifier": modifier,
        "total": total,
        "dc": dc,
        "success": total >= dc,
        "margin": total - dc,
    }
