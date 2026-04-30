#!/usr/bin/env python3

from __future__ import annotations

import sys
from unittest.mock import patch

import pytest

import rom_cleaner


def test_dry_run_reports_changes_without_deleting_files(tmp_path, monkeypatch, capsys):
    kept_file = tmp_path / "Aladdin [U] [!].smc"
    deleted_file = tmp_path / "Aladdin [E].smc"
    kept_file.write_text("", encoding="utf-8")
    deleted_file.write_text("", encoding="utf-8")

    monkeypatch.setattr(sys, "argv", ["rom_cleaner.py", "--dry-run", str(tmp_path)])

    assert rom_cleaner.main() == 0

    output = capsys.readouterr().out
    assert "Keeping:" in output
    assert "Deleting:" in output
    assert kept_file.exists()
    assert deleted_file.exists()


def test_run_deletes_bad_variants_and_skips_subdirectories(tmp_path, monkeypatch):
    kept_file = tmp_path / "Aladdin [U] [!].smc"
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


def test_regions_flag_keeps_japan_when_specified(tmp_path, monkeypatch):
    japan_file = tmp_path / "Aladdin [J] [!].smc"
    europe_file = tmp_path / "Aladdin [E].smc"
    japan_file.write_text("", encoding="utf-8")
    europe_file.write_text("", encoding="utf-8")

    monkeypatch.setattr(sys, "argv", ["rom_cleaner.py", "--regions", "usa,japan", str(tmp_path)])

    assert rom_cleaner.main() == 0

    assert japan_file.exists()
    assert not europe_file.exists()


def test_regions_flag_invalid_exits(tmp_path, monkeypatch):
    monkeypatch.setattr(sys, "argv", ["rom_cleaner.py", "--regions", "invalid", str(tmp_path)])

    with pytest.raises(SystemExit) as exc_info:
        rom_cleaner.main()

    assert exc_info.value.code != 0


def test_homebrew_flag_deletes_homebrew_files(tmp_path, monkeypatch):
    homebrew_file = tmp_path / "Cave Story by Pixel.smc"
    homebrew_file.write_text("", encoding="utf-8")

    monkeypatch.setattr(sys, "argv", ["rom_cleaner.py", "--homebrew", str(tmp_path)])

    assert rom_cleaner.main() == 0

    assert not homebrew_file.exists()


def test_no_intro_revision_without_region_is_kept(tmp_path, monkeypatch):
    kept_usa = tmp_path / "Aladdin (USA).zip"
    kept_rev = tmp_path / "Aladdin (Rev 1).zip"
    kept_usa.write_text("", encoding="utf-8")
    kept_rev.write_text("", encoding="utf-8")

    monkeypatch.setattr(
        sys, "argv",
        ["rom_cleaner.py", "--convention", "no-intro", str(tmp_path)],
    )

    assert rom_cleaner.main() == 0

    assert kept_usa.exists()
    assert kept_rev.exists()


def test_trash_flag_routes_through_send2trash(tmp_path, monkeypatch):
    deleted_file = tmp_path / "Aladdin [E].smc"
    deleted_file.write_text("x", encoding="utf-8")

    monkeypatch.setattr(sys, "argv", ["rom_cleaner.py", "--trash", str(tmp_path)])

    trashed = []
    removed = []

    import types
    import rom_naming

    fake_st = types.SimpleNamespace(send2trash=lambda p: trashed.append(p))
    monkeypatch.setattr(rom_naming, "send2trash", fake_st)
    with patch("os.remove", side_effect=lambda p: removed.append(p)):
        rom_cleaner.main()

    assert len(trashed) == 1
    assert len(removed) == 0


def test_summary_stats_printed(tmp_path, monkeypatch, capsys):
    kept_file = tmp_path / "Aladdin [U] [!].smc"
    deleted_file = tmp_path / "Aladdin [E].smc"
    kept_file.write_bytes(b"x" * 1024)
    deleted_file.write_bytes(b"x" * 2048)

    monkeypatch.setattr(sys, "argv", ["rom_cleaner.py", "--dry-run", str(tmp_path)])

    assert rom_cleaner.main() == 0

    output = capsys.readouterr().out
    assert "Kept: 1" in output
    assert "Deleted: 1" in output
    assert "Errors: 0" in output


def test_oserror_does_not_abort_run(tmp_path, monkeypatch, capsys):
    file1 = tmp_path / "Aladdin [E].smc"
    file2 = tmp_path / "Batman [E].smc"
    file1.write_text("x", encoding="utf-8")
    file2.write_text("x", encoding="utf-8")

    monkeypatch.setattr(sys, "argv", ["rom_cleaner.py", str(tmp_path)])

    call_count = {"n": 0}

    def flaky_delete(path, trash=False):
        call_count["n"] += 1
        if call_count["n"] == 1:
            raise OSError("permission denied")
        return 1  # pretend 1 byte freed

    with patch("rom_cleaner.delete_path", side_effect=flaky_delete):
        result = rom_cleaner.main()

    assert result == 0
    output = capsys.readouterr().out
    assert "Errors: 1" in output
    assert "Deleted: 1" in output
