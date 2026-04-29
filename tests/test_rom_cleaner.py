#!/usr/bin/env python3

from __future__ import annotations

import sys

import rom_cleaner


def test_dry_run_reports_changes_without_deleting_files(tmp_path, monkeypatch, capsys):
    kept_file = tmp_path / "Aladdin [U] [!].smc"
    deleted_file = tmp_path / "Aladdin [E].smc"
    kept_file.write_text("", encoding="utf-8")
    deleted_file.write_text("", encoding="utf-8")

    monkeypatch.setattr(
        sys,
        "argv",
        ["rom_cleaner.py", "--dry-run", str(tmp_path)],
    )

    assert rom_cleaner.main() == 0

    output = capsys.readouterr().out
    assert "Keeping:" in output
    assert "Deleting:" in output
    assert kept_file.exists()
    assert deleted_file.exists()


def test_run_deletes_bad_variants_and_skips_subdirectories(tmp_path, monkeypatch):
    kept_file = tmp_path / "Aladdin [J] [!].smc"
    deleted_file = tmp_path / "Aladdin [E].smc"
    nested_dir = tmp_path / "nested"
    nested_file = nested_dir / "Aladdin [E].smc"

    kept_file.write_text("", encoding="utf-8")
    deleted_file.write_text("", encoding="utf-8")
    nested_dir.mkdir()
    nested_file.write_text("", encoding="utf-8")

    monkeypatch.setattr(sys, "argv", ["rom_cleaner.py", str(tmp_path)])

    assert rom_cleaner.main() == 0

    assert kept_file.exists()
    assert not deleted_file.exists()
    assert nested_file.exists()


def test_homebrew_flag_deletes_homebrew_files(tmp_path, monkeypatch):
    homebrew_file = tmp_path / "Cave Story by Pixel.smc"
    homebrew_file.write_text("", encoding="utf-8")

    monkeypatch.setattr(
        sys,
        "argv",
        ["rom_cleaner.py", "--homebrew", str(tmp_path)],
    )

    assert rom_cleaner.main() == 0

    assert not homebrew_file.exists()


def test_no_intro_convention_deletes_revision_without_allowed_region(
    tmp_path,
    monkeypatch,
):
    kept_file = tmp_path / "Aladdin (USA).zip"
    deleted_file = tmp_path / "Aladdin (Rev 1).zip"
    kept_file.write_text("", encoding="utf-8")
    deleted_file.write_text("", encoding="utf-8")

    monkeypatch.setattr(
        sys,
        "argv",
        ["rom_cleaner.py", "--convention", "no-intro", str(tmp_path)],
    )

    assert rom_cleaner.main() == 0

    assert kept_file.exists()
    assert not deleted_file.exists()
