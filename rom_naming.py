#!/usr/bin/env python3
"""Shared ROM filename parsing and normalization helpers."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from typing import Literal


Convention = Literal["goodtools", "no-intro", "auto"]
SUPPORTED_CONVENTIONS: tuple[Convention, ...] = ("goodtools", "no-intro", "auto")

BRACKET_TAG_PATTERN = re.compile(r"\[([^\]]+)\]")
PAREN_TAG_PATTERN = re.compile(r"\(([^)]+)\)")
ALL_TAG_PATTERN = re.compile(r"\[[^\]]+\]|\([^)]+\)")
WHITESPACE_PATTERN = re.compile(r"\s+")

GOODTOOLS_REGION_MAP = {
    "u": "usa",
    "j": "japan",
}

NOINTRO_REGION_MAP = {
    "usa": "usa",
    "us": "usa",
    "united states": "usa",
    "japan": "japan",
    "jp": "japan",
}


@dataclass(frozen=True)
class ParsedRomName:
    filename: str
    stem: str
    title: str
    convention: Convention
    regions: frozenset[str]
    is_verified: bool
    is_hack: bool
    is_beta: bool
    is_prototype: bool
    has_convention_tags: bool
    is_homebrew: bool


def _normalize_convention(convention: str) -> Convention:
    if convention not in SUPPORTED_CONVENTIONS:
        raise ValueError(f"Unsupported convention: {convention}")
    return convention


def normalize_rom_title(filename: str) -> str:
    stem, _ = os.path.splitext(os.path.basename(filename))
    cleaned = ALL_TAG_PATTERN.sub("", stem)
    cleaned = cleaned.replace("_", " ")
    cleaned = WHITESPACE_PATTERN.sub(" ", cleaned).strip(" ._-")
    return cleaned or stem


def _tag_matches_beta(tag: str) -> bool:
    return bool(re.fullmatch(r"beta(?:\s+[\w.-]+)?", tag, flags=re.IGNORECASE))


def _tag_matches_proto(tag: str) -> bool:
    return bool(
        re.fullmatch(
            r"proto(?:type)?(?:\s+[\w.-]+)?",
            tag,
            flags=re.IGNORECASE,
        )
    )


def _collect_goodtools_regions(tags: list[str]) -> set[str]:
    regions: set[str] = set()
    for tag in tags:
        mapped = GOODTOOLS_REGION_MAP.get(tag.strip().lower())
        if mapped is not None:
            regions.add(mapped)
    return regions


def _collect_nointro_regions(tags: list[str]) -> set[str]:
    regions: set[str] = set()
    for tag in tags:
        for part in tag.split(","):
            mapped = NOINTRO_REGION_MAP.get(part.strip().lower())
            if mapped is not None:
                regions.add(mapped)
    return regions


def parse_rom_name(filename: str, convention: str = "goodtools") -> ParsedRomName:
    active_convention = _normalize_convention(convention)
    stem, _ = os.path.splitext(os.path.basename(filename))
    bracket_tags = BRACKET_TAG_PATTERN.findall(stem)
    paren_tags = PAREN_TAG_PATTERN.findall(stem)
    literal_hack = re.search(r"hack", stem, flags=re.IGNORECASE) is not None

    is_hack = literal_hack or any(
        re.fullmatch(r"h\d*", tag.strip(), flags=re.IGNORECASE)
        for tag in bracket_tags
    ) or any("hack" in tag.lower() for tag in paren_tags)
    is_beta = any(_tag_matches_beta(tag.strip()) for tag in paren_tags + bracket_tags)
    is_prototype = any(_tag_matches_proto(tag.strip()) for tag in paren_tags + bracket_tags)

    regions: set[str] = set()
    has_convention_tags = False
    is_verified = False

    if active_convention in {"goodtools", "auto"}:
        has_convention_tags = has_convention_tags or bool(bracket_tags)
        regions.update(_collect_goodtools_regions(bracket_tags))
        is_verified = is_verified or any(tag.strip() == "!" for tag in bracket_tags)

    if active_convention in {"no-intro", "auto"}:
        has_convention_tags = has_convention_tags or bool(paren_tags)
        regions.update(_collect_nointro_regions(paren_tags))

    return ParsedRomName(
        filename=os.path.basename(filename),
        stem=stem,
        title=normalize_rom_title(filename),
        convention=active_convention,
        regions=frozenset(regions),
        is_verified=is_verified,
        is_hack=is_hack,
        is_beta=is_beta,
        is_prototype=is_prototype,
        has_convention_tags=has_convention_tags,
        is_homebrew=" by " in stem,
    )


def should_keep(parsed: ParsedRomName, include_homebrew: bool = False) -> bool:
    if parsed.is_hack or parsed.is_beta or parsed.is_prototype:
        return False

    if include_homebrew and parsed.is_homebrew:
        return False

    if parsed.is_verified:
        return True

    if parsed.regions.intersection({"usa", "japan"}):
        return True

    return not parsed.has_convention_tags
