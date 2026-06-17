"""Doc-integrity suite: the assembled registry must be structurally valid, free
of unresolved content placeholders, and complete per the level cap. These mirror
the in-engine "Validate content" button (core.registry.content_problems) and the
dev-mode boot assert (registry.validate) so a headless `pytest` catches the same
drift before the game is even launched.
"""
import data
from core import registry as reg

REG = data.REGISTRY


def test_structural_validate_clean():
    assert reg.validate(REG) == []


def test_content_problems_clean():
    # structural validate + GDD 9.2 spell-slice counts + DISPLAY placeholder scan
    assert reg.content_problems(REG) == []


def test_every_class_levelup_covers_1_to_12():
    for cid, cls in REG["classes"].items():
        assert set(cls["levelup"].keys()) == set(range(1, 13)), cid


def test_spell_slice_matrix_nonempty_for_casters():
    matrix = reg.derive_slice_matrix(REG["spells"])
    for caster in ("wizard", "cleric", "druid", "bard", "sorcerer", "warlock"):
        assert sum(matrix.get(caster, {}).values()) > 0, caster
