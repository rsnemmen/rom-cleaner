#!/usr/bin/env python3

import pytest

from rom_naming import normalize_rom_title, parse_rom_name, should_keep


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
    assert parsed.regions == frozenset({"usa"})


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


def test_no_intro_revision_without_allowed_region_is_deleted():
    parsed = parse_rom_name("Aladdin (Rev 1).zip", convention="no-intro")

    assert parsed.has_convention_tags
    assert not should_keep(parsed)


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
