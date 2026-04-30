#!/usr/bin/env python3

import pytest

from rom_naming import normalize_rom_title, parse_rom_name, should_keep


# --- existing tests (updated for new defaults) ---

@pytest.mark.parametrize(
    ("filename", "convention"),
    [
        ("Aladdin [U] [!].smc", "goodtools"),
        ("Aladdin (USA) (Rev 1).zip", "no-intro"),
        ("Aladdin (USA) [!].smc", "auto"),
    ],
)
def test_preferred_us_variants_are_kept(filename, convention):
    parsed = parse_rom_name(filename, convention=convention)
    assert should_keep(parsed)
    assert "usa" in parsed.regions


def test_japan_variant_kept_when_region_included():
    parsed = parse_rom_name("Aladdin [J] [!].smc", convention="goodtools")
    assert should_keep(parsed, keep_regions=frozenset({"usa", "japan"}))
    assert parsed.regions == frozenset({"japan"})


def test_japan_variant_deleted_under_usa_only_default():
    parsed = parse_rom_name("Aladdin [J] [!].smc", convention="goodtools")
    assert not should_keep(parsed)


def test_goodtools_us_verified_release_preserves_clean_title():
    parsed = parse_rom_name("Aladdin [U] [!].smc", convention="goodtools")
    assert parsed.title == "Aladdin"
    assert parsed.is_verified


def test_goodtools_hack_shorthand_is_deleted():
    parsed = parse_rom_name("Aladdin [U] [h1].smc", convention="goodtools")
    assert parsed.is_hack
    assert not should_keep(parsed)


def test_no_intro_beta_release_is_deleted():
    parsed = parse_rom_name("Aladdin (USA) (Beta).zip", convention="no-intro")
    assert parsed.is_beta
    assert not should_keep(parsed)


def test_no_intro_revision_without_region_is_kept():
    parsed = parse_rom_name("Aladdin (Rev 1).zip", convention="no-intro")
    assert parsed.is_revision
    assert parsed.has_only_benign_paren_tags
    assert should_keep(parsed)


def test_untagged_file_is_kept():
    parsed = parse_rom_name("Chrono Trigger.smc", convention="goodtools")
    assert not parsed.has_convention_tags
    assert should_keep(parsed)


def test_homebrew_is_only_deleted_when_flag_is_enabled():
    parsed = parse_rom_name("Cave Story by Pixel.smc", convention="goodtools")
    assert parsed.is_homebrew
    assert should_keep(parsed)
    assert not should_keep(parsed, include_homebrew=True)


def test_auto_mode_detects_prototypes_from_parenthetical_tags():
    parsed = parse_rom_name("Aladdin (Japan) (Proto 1).zip", convention="auto")
    assert parsed.is_prototype
    assert not should_keep(parsed)


def test_auto_normalization_strips_both_tag_styles_and_underscores():
    assert normalize_rom_title("Super_Mario_World (USA) [!].smc") == "Super Mario World"


# --- bad quality flag tests ---

def test_bad_dump_overrides_region_and_verified():
    parsed = parse_rom_name("Aladdin [U][b1].smc", convention="goodtools")
    assert parsed.is_bad_quality
    assert not should_keep(parsed)


@pytest.mark.parametrize("tag", ["a", "a1", "b", "b1", "f", "o", "o1", "p", "t"])
def test_quality_flags_set_is_bad_quality(tag):
    parsed = parse_rom_name(f"Game [{tag}].smc", convention="goodtools")
    assert parsed.is_bad_quality, f"[{tag}] should set is_bad_quality"
    assert not should_keep(parsed)


def test_goodtools_bracket_a_is_not_a_region():
    parsed = parse_rom_name("Game [a].smc", convention="goodtools")
    assert parsed.is_bad_quality
    assert "australia" not in parsed.regions


def test_verified_no_region_is_kept():
    parsed = parse_rom_name("Chrono Trigger [!].smc", convention="goodtools")
    assert parsed.is_verified
    assert not parsed.regions
    assert should_keep(parsed)


# --- homebrew false-positive fix ---

def test_stand_by_me_is_not_homebrew():
    parsed = parse_rom_name("Stand By Me.smc", convention="goodtools")
    assert not parsed.is_homebrew


def test_cave_story_with_region_tag_is_still_homebrew():
    parsed = parse_rom_name("Cave Story by Pixel (USA).smc", convention="no-intro")
    assert parsed.is_homebrew


# --- expanded region coverage ---

def test_europe_region_recognized_no_intro():
    parsed = parse_rom_name("Sonic (Europe).md", convention="no-intro")
    assert parsed.regions == frozenset({"europe"})
    assert not should_keep(parsed)
    assert should_keep(parsed, keep_regions=frozenset({"europe"}))


def test_multi_region_usa_europe_kept_under_usa_default():
    parsed = parse_rom_name("Sonic (USA, Europe).md", convention="no-intro")
    assert "usa" in parsed.regions
    assert "europe" in parsed.regions
    assert should_keep(parsed)


def test_goodtools_europe_tag_recognized():
    parsed = parse_rom_name("Aladdin [E].smc", convention="goodtools")
    assert parsed.regions == frozenset({"europe"})
    assert not should_keep(parsed)
    assert should_keep(parsed, keep_regions=frozenset({"europe"}))


# --- benign paren tags ---

def test_language_only_paren_is_benign_and_kept():
    parsed = parse_rom_name("Sonic (En,Fr,De).md", convention="no-intro")
    assert parsed.is_language_only_paren
    assert parsed.has_only_benign_paren_tags
    assert should_keep(parsed)


def test_usa_with_language_tag_is_kept():
    parsed = parse_rom_name("Aladdin (USA) (En,Fr,De).zip", convention="no-intro")
    assert "usa" in parsed.regions
    assert should_keep(parsed)


def test_disc_tag_is_benign_and_kept():
    parsed = parse_rom_name("Final Fantasy VII (Disc 1).zip", convention="no-intro")
    assert parsed.is_disc
    assert parsed.has_only_benign_paren_tags
    assert should_keep(parsed)


def test_revision_plus_beta_is_deleted():
    parsed = parse_rom_name("Game (Rev 1) (Beta).zip", convention="no-intro")
    assert parsed.is_beta
    assert not should_keep(parsed)
