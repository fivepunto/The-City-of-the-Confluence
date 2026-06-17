# -*- coding: utf-8 -*-
"""Aggregates the twelve class modules (GDD #7) plus shared features.

Each class module exports:
  CLASS    -- the chassis dict, including the 'levelup' manifest (levels 1-12)
  FEATURES -- {feature_id: record} for that class's own features
"""

from data.classes import _shared
from data.classes import (
    fighter, rogue, cleric, wizard, barbarian, ranger,
    warlock, bard, paladin, druid, monk, sorcerer,
)

_MODULES = (fighter, rogue, cleric, wizard, barbarian, ranger,
            warlock, bard, paladin, druid, monk, sorcerer)

CLASSES = {}
FEATURES = dict(_shared.FEATURES)

for _mod in _MODULES:
    _cls = _mod.CLASS
    if _cls["id"] in CLASSES:
        raise ValueError("duplicate class id: %r" % (_cls["id"],))
    CLASSES[_cls["id"]] = _cls
    for _fid, _feat in _mod.FEATURES.items():
        if _fid in FEATURES:
            raise ValueError("duplicate feature id: %r" % (_fid,))
        FEATURES[_fid] = _feat
