#!/usr/bin/env python3

from __future__ import annotations

import subprocess


def test_parse_dirs_uses_script_relative_path_and_forwards_args(
    tmp_path,
    parse_dirs_script,
):
    rom_dir = tmp_path / "roms"
    rom_dir.mkdir()
    kept_file = rom_dir / "Aladdin (USA).zip"
    deleted_file = rom_dir / "Aladdin (Europe).zip"
    kept_file.write_text("", encoding="utf-8")
    deleted_file.write_text("", encoding="utf-8")
    missing_dir = tmp_path / "missing"

    result = subprocess.run(
        [
            "bash",
            str(parse_dirs_script),
            "--dry-run",
            "--convention",
            "no-intro",
            str(rom_dir),
            str(missing_dir),
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert f'Processing directory: "{rom_dir}"' in result.stdout
    assert f"Error: '{missing_dir}' is not a valid directory. Skipping..." in result.stdout
    assert "Keeping:" in result.stdout
    assert "Deleting:" in result.stdout
    assert kept_file.exists()
    assert deleted_file.exists()  # dry-run: nothing actually deleted
