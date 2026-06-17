# -*- coding: utf-8 -*-
"""Aggregates the spell pool (GDD #9: 94 spells -- 12 cantrips + 16+16+16+
13+11+10 across tiers 1-6) and the upcasting rules (#9.3).
"""

from data.spells import cantrips, tier1, tier2, tier3, tier4, tier5, tier6

SPELLS = {}
for _mod in (cantrips, tier1, tier2, tier3, tier4, tier5, tier6):
    for _sid, _spell in _mod.SPELLS.items():
        if _sid in SPELLS:
            raise ValueError("duplicate spell id: %r" % (_sid,))
        SPELLS[_sid] = _spell

# GDD #9.3 (L982-1009): a generic rule per spell role, resolved by the
# engine with no per-spell text; plus the only bespoke upcast lines in the
# game. Per-spell "upcast" fields: None = generic by role, "none" = no
# upcast, dict = bespoke (must match an entry here).
UPCAST_RULES = {
    "by_role": {
        # per tier above the spell's base tier:
        "damage": {"add_primary_die_per_tier": 1},          # §9.3 L986
        "heal": {"add_die_per_tier": 1},                    # §9.3 L987
        "true_heal": {"add_die_per_tier": 1},               # §9.3 L987
        "buff_single": {"add_target_per_tier": 1},          # §9.3 L988
        "control_single": {"add_target_per_tier": 1},       # §9.3 L988
        "lane_buff_debuff": {"small_to_large_at_plus_tiers": 2},  # §9.3 L989-990
        "summon": {"hp_per_tier": 5,
                   "attack_damage_ac_per_tier": 1},          # §9.3 L991
        # single-target Debuffs mirror single-target Control, per owner
        # adjudication, P0 round 2 (G-010)
        "debuff_single": {"add_target_per_tier": 1},
    },
    # Dual-role spells with a damage component upcast by the DAMAGE rule
    # (Radiant Smite +1d8/tier, Whispered Dread +1d6/tier); dual-role
    # without damage uses the first-listed role. Owner adjudication,
    # P0 round 2 (G-010).
    "dual_role": {"with_damage": "damage", "without_damage": "first_role"},
    # Cantrips never upcast; they scale with character level (§9.3 L992-993)
    "cantrip_dice_by_level": {1: 1, 5: 2, 11: 3},
    # Flat utility spells: no upcast effect (§9.3 L994-995)
    "flat_utility": "none",
    "exceptions": {                                          # §9.3 L997-1006
        "arc_bolt": {"add_dart_per_tier": 1,
                     "dart": "1d4+1", "split_freely": True},
        "slumber": {"base_hp_budget": "5d8", "add_per_tier": "2d8"},
        "counterspell": {"auto_counter_at_or_below_cast_tier": True,
                         "higher_tiers_contested": True},
        "banish": {"add_target_per_tier": 1},
        "quarrys_mark": "none",
        "dominate": "none",
        "battle_haste": "none",
        "veil": "none",
    },
    # Pact Magic auto-upcasts every cast to the pact slot's tier using these
    # same rules (§9.3 L1008-1009).
    "pact_magic_uses_same_rules": True,
    "src": "§9.3 L982-1009",
}
