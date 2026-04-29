#!/usr/bin/env python3

import unittest

from rom_naming import normalize_rom_title, parse_rom_name, should_keep


class RomNamingTests(unittest.TestCase):
    def test_goodtools_us_verified_release_is_kept(self):
        parsed = parse_rom_name("Aladdin [U] [!].smc", convention="goodtools")
        self.assertTrue(should_keep(parsed))
        self.assertEqual(parsed.title, "Aladdin")
        self.assertEqual(parsed.regions, frozenset({"usa"}))

    def test_goodtools_hack_shorthand_is_deleted(self):
        parsed = parse_rom_name("Aladdin [U] [h1].smc", convention="goodtools")
        self.assertFalse(should_keep(parsed))

    def test_no_intro_us_release_is_kept(self):
        parsed = parse_rom_name("Aladdin (USA) (Rev 1).zip", convention="no-intro")
        self.assertTrue(should_keep(parsed))

    def test_no_intro_beta_release_is_deleted(self):
        parsed = parse_rom_name("Aladdin (USA) (Beta).zip", convention="no-intro")
        self.assertFalse(should_keep(parsed))

    def test_no_intro_revision_without_allowed_region_is_deleted(self):
        parsed = parse_rom_name("Aladdin (Rev 1).zip", convention="no-intro")
        self.assertFalse(should_keep(parsed))

    def test_auto_normalization_strips_both_tag_styles(self):
        self.assertEqual(normalize_rom_title("Aladdin (USA) [!].smc"), "Aladdin")


if __name__ == "__main__":
    unittest.main()
