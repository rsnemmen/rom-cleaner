#!/usr/bin/env python3

from __future__ import annotations

import sys

import pytest


def test_load_keep_list_skips_blank_lines(tmp_path, load_keep_top_module):
    keep_file = tmp_path / "keep.txt"
    keep_file.write_text("aladdin\n\nsuper mario world\n", encoding="utf-8")
    keep_top = load_keep_top_module(lambda keep_list, files_cleaned: {})

    assert keep_top.load_keep_list(str(keep_file)) == ["aladdin", "super mario world"]


def test_load_keep_list_exits_when_file_is_missing(
    tmp_path,
    load_keep_top_module,
    capsys,
):
    keep_top = load_keep_top_module(lambda keep_list, files_cleaned: {})

    with pytest.raises(SystemExit) as excinfo:
        keep_top.load_keep_list(str(tmp_path / "missing.txt"))

    assert excinfo.value.code == 1
    assert "was not found" in capsys.readouterr().out


def test_dry_run_keeps_all_variants_of_a_matching_clean_title(
    tmp_path,
    load_keep_top_module,
    monkeypatch,
    capsys,
):
    keep_file = tmp_path / "keep.txt"
    keep_file.write_text("aladdin\n", encoding="utf-8")
    rom_dir = tmp_path / "roms"
    rom_dir.mkdir()

    matching_files = [
        rom_dir / "Aladdin [U] [!].smc",
        rom_dir / "Aladdin (USA) (Rev 1).zip",
    ]
    deleted_file = rom_dir / "Batman [E].smc"
    for file_path in [*matching_files, deleted_file]:
        file_path.write_text("", encoding="utf-8")

    def fake_file_matching(keep_list, files_cleaned):
        assert keep_list == ["aladdin"]
        assert sorted(files_cleaned) == ["Aladdin", "Aladdin", "Batman"]
        return {"aladdin": ("Aladdin", 99)}

    keep_top = load_keep_top_module(fake_file_matching)
    monkeypatch.setattr(
        sys,
        "argv",
        ["keep-top.py", str(rom_dir), str(keep_file), "--dry-run"],
    )

    assert keep_top.main() is None

    output = capsys.readouterr().out
    assert "Aladdin [U] [!].smc" in output
    assert "Aladdin (USA) (Rev 1).zip" in output
    assert "Dry run: 1 file(s) would be deleted." in output
    assert deleted_file.exists()


def test_threshold_filters_out_low_scoring_matches(
    tmp_path,
    load_keep_top_module,
    monkeypatch,
    capsys,
):
    keep_file = tmp_path / "keep.txt"
    keep_file.write_text("aladdin\n", encoding="utf-8")
    rom_dir = tmp_path / "roms"
    rom_dir.mkdir()
    rom_file = rom_dir / "Aladdin [U] [!].smc"
    rom_file.write_text("", encoding="utf-8")

    keep_top = load_keep_top_module(
        lambda keep_list, files_cleaned: {"aladdin": ("Aladdin", 49)},
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "keep-top.py",
            str(rom_dir),
            str(keep_file),
            "--dry-run",
            "--threshold",
            "50",
        ],
    )

    assert keep_top.main() is None

    output = capsys.readouterr().out
    assert "No files match the keep list. All files will be deleted." in output
    assert "Dry run: 1 file(s) would be deleted." in output
    assert rom_file.exists()


def test_confirmed_run_deletes_unmatched_files(
    tmp_path,
    load_keep_top_module,
    monkeypatch,
    capsys,
):
    keep_file = tmp_path / "keep.txt"
    keep_file.write_text("aladdin\n", encoding="utf-8")
    rom_dir = tmp_path / "roms"
    rom_dir.mkdir()
    kept_file = rom_dir / "Aladdin [U] [!].smc"
    deleted_file = rom_dir / "Batman [E].smc"
    kept_file.write_text("", encoding="utf-8")
    deleted_file.write_text("", encoding="utf-8")

    keep_top = load_keep_top_module(
        lambda keep_list, files_cleaned: {"aladdin": ("Aladdin", 98)},
    )
    monkeypatch.setattr(
        sys,
        "argv",
        ["keep-top.py", str(rom_dir), str(keep_file)],
    )
    monkeypatch.setattr("builtins.input", lambda prompt: "y")

    assert keep_top.main() is None

    output = capsys.readouterr().out
    assert kept_file.exists()
    assert not deleted_file.exists()
    assert "1 unmatched file deleted." in output


def test_cancelled_run_keeps_files_in_place(
    tmp_path,
    load_keep_top_module,
    monkeypatch,
    capsys,
):
    keep_file = tmp_path / "keep.txt"
    keep_file.write_text("aladdin\n", encoding="utf-8")
    rom_dir = tmp_path / "roms"
    rom_dir.mkdir()
    rom_file = rom_dir / "Batman [E].smc"
    rom_file.write_text("", encoding="utf-8")

    keep_top = load_keep_top_module(
        lambda keep_list, files_cleaned: {"aladdin": ("Batman", 0)},
    )
    monkeypatch.setattr(
        sys,
        "argv",
        ["keep-top.py", str(rom_dir), str(keep_file)],
    )
    monkeypatch.setattr("builtins.input", lambda prompt: "n")

    assert keep_top.main() is None

    output = capsys.readouterr().out
    assert rom_file.exists()
    assert "Operation cancelled." in output
