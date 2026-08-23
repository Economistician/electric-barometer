#!/usr/bin/env python3
"""Synchronize leaf-package changelogs into the umbrella macro CHANGELOG.

Discovers sibling leaf package directories, parses the latest dated Keep a
Changelog section from each leaf ``CHANGELOG.md``, and synthesizes (or
verifies) a unified entry in ``electric-barometer/CHANGELOG.md``.

Zero-drift modes:
  (default)  Write / update the macro changelog for the target date.
  --check    Exit non-zero if the on-disk macro changelog differs from the
             synthesized content (CI drift gate).

Environment:
  EB_ECOSYSTEM_ROOT  Optional absolute path to the directory that contains
                     leaf package checkouts (default: parent of this repo).
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass, field
import os
from pathlib import Path
import re
import sys

LEAF_PACKAGES: tuple[str, ...] = (
    "eb-metrics",
    "eb-evaluation",
    "eb-contracts",
    "eb-optimization",
    "eb-features",
    "eb-adapters",
    "eb-examples",
)

# Macro grouping order requested for the system release entry.
MACRO_CATEGORIES: tuple[str, ...] = (
    "Breaking Changes",
    "Performance",
    "Added",
    "Fixed",
)

# Map Keep a Changelog / leaf headings onto macro categories.
CATEGORY_ALIASES: dict[str, str] = {
    "breaking changes": "Breaking Changes",
    "breaking change": "Breaking Changes",
    "breaking": "Breaking Changes",
    "removed": "Breaking Changes",
    "performance": "Performance",
    "added": "Added",
    "fixed": "Fixed",
    "changed": "Fixed",
    "deprecated": "Fixed",
    "security": "Fixed",
}

SECTION_HEADER_RE = re.compile(
    r"^##\s+\[(?P<label>[^\]]+)\]\s*-\s*(?P<date>\d{4}-\d{2}-\d{2})\s*$",
    re.MULTILINE,
)
CATEGORY_HEADER_RE = re.compile(r"^###\s+(?P<name>.+?)\s*$", re.MULTILINE)
BULLET_RE = re.compile(r"^[-*]\s+(?P<text>.+)$", re.MULTILINE)

SYSTEM_RELEASE_LABEL = "System Release 0.2.9"
DEFAULT_DATE = "2026-08-22"

PREAMBLE = """\
# Changelog

All notable changes to the Electric Barometer ecosystem will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Leaf package changelogs are the source of truth. This macro changelog is
synthesized by ``scripts/sync_changelogs.py`` and must not drift from the
leaf entries for a given release date.

## [Unreleased]

"""


@dataclass
class LeafSection:
    package: str
    version_label: str
    date: str
    # category -> bullet texts (order preserved)
    categories: dict[str, list[str]] = field(default_factory=dict)


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def ecosystem_root() -> Path:
    override = os.environ.get("EB_ECOSYSTEM_ROOT")
    if override:
        return Path(override).expanduser().resolve()
    return repo_root().parent


def discover_leaf_changelogs(root: Path) -> list[tuple[str, Path]]:
    found: list[tuple[str, Path]] = []
    missing: list[str] = []
    for name in LEAF_PACKAGES:
        changelog = root / name / "CHANGELOG.md"
        if changelog.is_file():
            found.append((name, changelog))
        else:
            missing.append(name)
    if missing:
        missing_list = ", ".join(missing)
        raise FileNotFoundError(
            f"Missing CHANGELOG.md for: {missing_list} "
            f"(searched under {root}). Set EB_ECOSYSTEM_ROOT if needed."
        )
    return found


def _normalize_category(raw: str) -> str | None:
    key = raw.strip().lower()
    return CATEGORY_ALIASES.get(key)


def parse_latest_dated_section(package: str, text: str) -> LeafSection:
    matches = list(SECTION_HEADER_RE.finditer(text))
    if not matches:
        raise ValueError(f"{package}: no dated ## [version] - YYYY-MM-DD section found")

    # Prefer the chronologically latest date; ties keep document order (first wins).
    best = max(
        matches,
        key=lambda m: (m.group("date"), -matches.index(m)),
    )
    start = best.end()
    # Section body ends at the next ## heading (or EOF).
    next_heading = re.search(r"^##\s+", text[start:], re.MULTILINE)
    end = start + next_heading.start() if next_heading else len(text)
    body = text[start:end]

    categories: dict[str, list[str]] = {name: [] for name in MACRO_CATEGORIES}
    current: str | None = None
    for line in body.splitlines():
        cat_match = CATEGORY_HEADER_RE.match(line)
        if cat_match:
            current = _normalize_category(cat_match.group("name"))
            continue
        if current is None:
            continue
        bullet = BULLET_RE.match(line)
        if bullet:
            categories[current].append(bullet.group("text").strip())

    return LeafSection(
        package=package,
        version_label=best.group("label"),
        date=best.group("date"),
        categories=categories,
    )


def parse_leaves_for_date(
    leaf_paths: list[tuple[str, Path]],
    target_date: str,
) -> list[LeafSection]:
    sections: list[LeafSection] = []
    for package, path in leaf_paths:
        section = parse_latest_dated_section(package, path.read_text(encoding="utf-8"))
        if section.date != target_date:
            raise ValueError(
                f"{package}: latest dated section is {section.date}, "
                f"expected {target_date} (label={section.version_label!r})"
            )
        sections.append(section)
    return sections


def synthesize_system_release(
    sections: list[LeafSection],
    *,
    label: str,
    date: str,
) -> str:
    lines: list[str] = [f"## [{label}] - {date}", ""]
    for section in sections:
        lines.append(f"### {section.package}")
        lines.append("")
        any_bullets = False
        for category in MACRO_CATEGORIES:
            bullets = section.categories.get(category) or []
            if not bullets:
                continue
            any_bullets = True
            lines.append(f"#### {category}")
            lines.append("")
            for item in bullets:
                lines.append(f"- {item}")
            lines.append("")
        if not any_bullets:
            lines.append("- _(no categorized entries)_")
            lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _extract_system_release_block(text: str, label: str, date: str) -> str | None:
    pattern = re.compile(
        rf"^##\s+\[{re.escape(label)}\]\s*-\s*{re.escape(date)}\s*$",
        re.MULTILINE,
    )
    match = pattern.search(text)
    if not match:
        return None
    start = match.start()
    rest = text[match.end() :]
    next_heading = re.search(r"^##\s+", rest, re.MULTILINE)
    end = match.end() + next_heading.start() if next_heading else len(text)
    return text[start:end].rstrip() + "\n"


def render_macro_changelog(
    existing: str | None,
    system_block: str,
    *,
    label: str,
    date: str,
) -> str:
    if not existing or not existing.strip():
        return PREAMBLE + system_block

    # Replace an existing matching system-release section, or insert after Unreleased.
    existing_block = _extract_system_release_block(existing, label, date)
    if existing_block is not None:
        return existing.replace(existing_block, system_block, 1)

    unreleased = re.search(
        r"^##\s+\[Unreleased\]\s*$",
        existing,
        re.MULTILINE,
    )
    if unreleased:
        # Insert immediately after the Unreleased section body.
        after = unreleased.end()
        next_heading = re.search(r"^##\s+", existing[after:], re.MULTILINE)
        insert_at = after + next_heading.start() if next_heading else len(existing)
        return (
            existing[:insert_at].rstrip()
            + "\n\n"
            + system_block
            + "\n"
            + existing[insert_at:].lstrip()
        )

    # No Unreleased heading — prepend after the file preamble / first content.
    return existing.rstrip() + "\n\n" + system_block


def build_macro_text(
    leaf_paths: list[tuple[str, Path]],
    *,
    target_date: str,
    label: str,
    macro_path: Path,
) -> str:
    sections = parse_leaves_for_date(leaf_paths, target_date)
    system_block = synthesize_system_release(sections, label=label, date=target_date)
    existing = macro_path.read_text(encoding="utf-8") if macro_path.is_file() else None
    return render_macro_changelog(existing, system_block, label=label, date=target_date)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--date",
        default=DEFAULT_DATE,
        help=f"ISO date of the leaf sections to sync (default: {DEFAULT_DATE})",
    )
    parser.add_argument(
        "--label",
        default=SYSTEM_RELEASE_LABEL,
        help=f"Macro release label (default: {SYSTEM_RELEASE_LABEL})",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Verify macro CHANGELOG matches synthesis; do not write",
    )
    parser.add_argument(
        "--ecosystem-root",
        type=Path,
        default=None,
        help="Directory containing leaf package checkouts (overrides EB_ECOSYSTEM_ROOT)",
    )
    args = parser.parse_args(argv)

    root = (
        args.ecosystem_root.expanduser().resolve()
        if args.ecosystem_root is not None
        else ecosystem_root()
    )
    macro_path = repo_root() / "CHANGELOG.md"

    try:
        leaf_paths = discover_leaf_changelogs(root)
        rendered = build_macro_text(
            leaf_paths,
            target_date=args.date,
            label=args.label,
            macro_path=macro_path,
        )
    except (FileNotFoundError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.check:
        if not macro_path.is_file():
            print(f"error: missing macro changelog at {macro_path}", file=sys.stderr)
            return 1
        on_disk = macro_path.read_text(encoding="utf-8")
        if on_disk != rendered:
            print(
                f"error: changelog drift detected in {macro_path}. "
                "Re-run without --check to regenerate.",
                file=sys.stderr,
            )
            return 1
        print(f"ok: {macro_path} matches leaf changelogs for {args.date}")
        return 0

    macro_path.write_text(rendered, encoding="utf-8", newline="\n")
    print(f"wrote {macro_path} ({args.label} - {args.date})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
