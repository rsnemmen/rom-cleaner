#!/usr/bin/env python3
"""Shared ROM filename parsing, normalization, and delete helpers."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from typing import Literal

VERSION = "1.1.0"

try:
    import send2trash
except ImportError:
    send2trash = None  # type: ignore[assignment]

Convention = Literal["goodtools", "no-intro", "auto"]
SUPPORTED_CONVENTIONS: tuple[Convention, ...] = ("goodtools", "no-intro", "auto")

BRACKET_TAG_PATTERN = re.compile(r"\[([^\]]+)\]")
PAREN_TAG_PATTERN = re.compile(r"\(([^)]+)\)")
ALL_TAG_PATTERN = re.compile(r"\[[^\]]+\]|\([^)]+\)")
WHITESPACE_PATTERN = re.compile(r"\s+")

# GoodTools region codes. Single letters a,b,f,h,o,p,t are deliberately excluded:
# those are quality flags and would collide (e.g. [a]=alternate misread as Australia).
GOODTOOLS_REGION_MAP: dict[str, str] = {
    "u": "usa",
    "j": "japan",
    "e": "europe",
    "k": "korea",
    "nl": "netherlands",
    "hk": "hongkong",
    "tw": "taiwan",
}

NOINTRO_REGION_MAP: dict[str, str] = {
    "usa": "usa",
    "us": "usa",
    "united states": "usa",
    "japan": "japan",
    "jp": "japan",
    "europe": "europe",
    "eu": "europe",
    "pal": "europe",
    "world": "world",
    "asia": "asia",
    "korea": "korea",
    "kr": "korea",
    "australia": "australia",
    "au": "australia",
    "brazil": "brazil",
    "br": "brazil",
    # Spelled-out names only — 2-letter codes like fr/de/it/es/nl are ISO language
    # codes and would collide with no-intro language tags like (En,Fr,De).
    "germany": "germany",
    "france": "france",
    "italy": "italy",
    "spain": "spain",
    "netherlands": "netherlands",
    "china": "china",
}

# All canonical region values — used for --regions flag validation.
ALL_REGIONS: frozenset[str] = frozenset(NOINTRO_REGION_MAP.values())

# ISO 639-1-ish language codes in no-intro parenthetical tags — benign metadata.
NOINTRO_LANGUAGE_CODES: frozenset[str] = frozenset({
    "en", "fr", "de", "es", "it", "ja", "ko", "zh", "pt", "nl", "sv",
    "da", "fi", "no", "pl", "ru", "tr",
})

# GoodTools quality flags (case-sensitive): [a]=alternate, [b]=bad dump, [f]=fixed,
# [o]=overdump, [p]=pirate, [t]=trained; optional digit suffix [b1], [o2], etc.
_QUALITY_FLAG_RE = re.compile(r"^[abfopt]\d*$")
_REVISION_RE = re.compile(r"^(?:rev\s*[\w.]+|v\d[\w.]*)$", re.IGNORECASE)
_DISC_RE = re.compile(r"^(?:disc|disk|side)\s*\w+$", re.IGNORECASE)


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
    is_bad_quality: bool              # [a],[b],[f],[o],[p],[t] and numbered variants
    is_revision: bool                 # (Rev N), (v1.x)
    is_disc: bool                     # (Disc N), (Disk N), (Side A/B)
    is_language_only_paren: bool      # all paren tags are language codes only
    has_only_benign_paren_tags: bool  # no bracket tags; all parens are rev/disc/lang/region
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


def _is_paren_tag_benign(tag: str) -> bool:
    """True if the paren tag is benign metadata (revision, disc, language, or region)."""
    stripped = tag.strip()
    parts = [p.strip().lower() for p in stripped.split(",")]
    if all(
        NOINTRO_REGION_MAP.get(p) is not None or p in NOINTRO_LANGUAGE_CODES
        for p in parts
    ):
        return True
    if _REVISION_RE.fullmatch(stripped):
        return True
    if _DISC_RE.fullmatch(stripped):
        return True
    return False


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
    is_bad_quality = any(
        bool(_QUALITY_FLAG_RE.fullmatch(tag.strip())) for tag in bracket_tags
    ) or any(tag.strip().lower() in {"bad", "bad dump"} for tag in paren_tags)
    is_revision = any(bool(_REVISION_RE.fullmatch(tag.strip())) for tag in paren_tags)
    is_disc = any(bool(_DISC_RE.fullmatch(tag.strip())) for tag in paren_tags)
    is_language_only_paren = bool(paren_tags) and all(
        all(p.strip().lower() in NOINTRO_LANGUAGE_CODES for p in tag.split(","))
        for tag in paren_tags
    )

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

    has_only_benign_paren_tags = (
        bool(paren_tags)
        and not bracket_tags
        and all(_is_paren_tag_benign(tag) for tag in paren_tags)
    )

    title = normalize_rom_title(filename)

    # Check for "by Author" in post-strip title (case-sensitive: "Stand By Me" has
    # capital B so is not matched). Also catches explicit (by X) / (Homebrew) paren tags.
    is_homebrew = " by " in title or any(
        bool(re.fullmatch(r"by\s+\S.*|homebrew", tag.strip(), re.IGNORECASE))
        for tag in paren_tags
    )

    return ParsedRomName(
        filename=os.path.basename(filename),
        stem=stem,
        title=title,
        convention=active_convention,
        regions=frozenset(regions),
        is_verified=is_verified,
        is_hack=is_hack,
        is_beta=is_beta,
        is_prototype=is_prototype,
        is_bad_quality=is_bad_quality,
        is_revision=is_revision,
        is_disc=is_disc,
        is_language_only_paren=is_language_only_paren,
        has_only_benign_paren_tags=has_only_benign_paren_tags,
        has_convention_tags=has_convention_tags,
        is_homebrew=is_homebrew,
    )


def should_keep(
    parsed: ParsedRomName,
    include_homebrew: bool = False,
    keep_regions: frozenset[str] = frozenset({"usa"}),
) -> bool:
    if parsed.is_bad_quality:
        return False
    if parsed.is_hack or parsed.is_beta or parsed.is_prototype:
        return False
    if include_homebrew and parsed.is_homebrew:
        return False
    if parsed.regions & keep_regions:
        return True
    if parsed.regions and not (parsed.regions & keep_regions):
        return False
    if not parsed.has_convention_tags:
        return True
    if parsed.has_only_benign_paren_tags:
        return True
    # [!] with no region = universal/original release
    if parsed.is_verified and not parsed.regions:
        return True
    return False


def format_bytes(n: int) -> str:
    if n < 1024:
        return f"{n} B"
    for unit, divisor in (("KB", 1024), ("MB", 1_048_576), ("GB", 1_073_741_824)):
        if n < divisor * 1024:
            return f"{n / divisor:.1f} {unit}"
    return f"{n / 1_073_741_824:.1f} GB"


def delete_path(path: str, trash: bool = False) -> int:
    """Delete path and return bytes freed. Uses send2trash when trash=True."""
    size = os.path.getsize(path)
    if trash:
        if send2trash is None:
            raise ImportError("send2trash is required for --trash: pip install send2trash")
        send2trash.send2trash(path)
    else:
        os.remove(path)
    return size
