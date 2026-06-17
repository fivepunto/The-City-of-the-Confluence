# -*- coding: utf-8 -*-
"""Skill-check primitive (#4.2 L189): one helper, skill_check, returning a
result object consumed by dialogue/exploration branches.

This is the single composition point of core.character.skill_mod (the
proficiency/expertise-aware modifier) into core.dice.d20_test. Branches read
result["success"] / result["margin"]; nothing else interprets a roll.

Display vs data discipline:
  - The result LINE players see -- e.g. "Presence -- Failed (9 vs 15)" -- is a
    DISPLAY concern formatted by the .rpy layer (#15.7 L1597-1602), NOT this
    module. We return numbers only.
  - The "proficient" flag is returned so the dialogue UI can tint the skill
    TAG when the acting character is proficient (#15.7 L1600) WITHOUT ever
    revealing the dc.

Rollback discipline (#16.1 L1624): the roll happens here, at resolution time,
and is never pre-computed into state. The CALLER (the .rpy layer) MUST call
renpy.block_rollback() immediately after this resolves so the committed result
cannot be rerolled by in-place rollback. This module is pure Python: no renpy
imports, no block_rollback() call here.
"""

from core import character as ch
from core import dice


def skill_check(registry, actor, skill, dc, adv=0):
    """Resolve one skill check for `actor` against `dc`.

    Composes character.skill_mod(registry, actor, skill) -- the
    proficiency/expertise/Jack-of-all-Trades-aware modifier -- as the modifier
    into dice.d20_test(modifier, dc, adv). `adv` passes straight through as
    d20_test's advantage: +1 advantage, -1 disadvantage, 0 normal (#2.2).

    Returns the d20_test result dict (die, rolls, modifier, total, dc, success,
    margin) augmented with:
      - "skill": the skill id that was rolled
      - "proficient": whether `actor` is proficient in that skill

    The caller must renpy.block_rollback() immediately after this resolves
    (#16.1 L1624). Display formatting is the .rpy layer's job (#15.7).
    """
    modifier = ch.skill_mod(registry, actor, skill)
    result = dice.d20_test(modifier, dc, adv)
    result["skill"] = skill
    result["proficient"] = skill in actor["skills"]["proficiencies"]
    return result
