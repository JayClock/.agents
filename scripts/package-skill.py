#!/usr/bin/env python3
"""Package a skill as a standalone .skill archive.

Source skills may reference shared repository files using paths like:
  ../_shared/name.md
  ../../_shared/name.md

A .skill archive should be self-contained, so this script stages a temporary
copy of the skill, copies referenced shared files into staged references/, and
rewrites those links to point at the staged copies before zipping.
"""

from __future__ import annotations

import fnmatch
import os
import re
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path

EXCLUDE_DIRS = {"__pycache__", "node_modules"}
EXCLUDE_GLOBS = {"*.pyc"}
EXCLUDE_FILES = {".DS_Store"}
ROOT_EXCLUDE_DIRS = {"evals"}
SHARED_REF_RE = re.compile(r"(?P<prefix>(?:\.\./)+)_shared/(?P<name>[A-Za-z0-9_.-]+)")


def usage() -> None:
    print(
        "Usage:\n"
        "  scripts/package-skill.py <skill-name-or-path> [output-dir]\n"
        "  scripts/package-skill.py --all [output-dir]\n\n"
        "Default output-dir: dist/",
        file=sys.stderr,
    )


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def resolve_skill(arg: str) -> Path:
    p = Path(arg)
    if p.exists():
        return p.resolve()
    candidate = repo_root() / "skills" / arg
    if candidate.exists():
        return candidate.resolve()
    raise FileNotFoundError(f"Skill not found: {arg}")


def should_exclude(rel_path: Path) -> bool:
    parts = rel_path.parts
    if any(part in EXCLUDE_DIRS for part in parts):
        return True
    if len(parts) > 1 and parts[1] in ROOT_EXCLUDE_DIRS:
        return True
    if rel_path.name in EXCLUDE_FILES:
        return True
    return any(fnmatch.fnmatch(rel_path.name, pat) for pat in EXCLUDE_GLOBS)


def rel_link(from_file: Path, to_file: Path) -> str:
    rel = os.path.relpath(to_file, start=from_file.parent)
    return Path(rel).as_posix()


def materialize_shared_refs(staged_skill: Path, source_shared: Path) -> list[str]:
    """Copy referenced shared files into references/ and rewrite links."""
    copied: set[str] = set()
    rewritten_files: list[str] = []

    for file_path in staged_skill.rglob("*"):
        if not file_path.is_file():
            continue
        if file_path.suffix.lower() not in {".md", ".txt", ".json", ".yaml", ".yml"}:
            continue
        try:
            text = file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue

        changed = False

        def replace(match: re.Match[str]) -> str:
            nonlocal changed
            name = match.group("name")
            shared_file = source_shared / name
            if not shared_file.exists():
                raise FileNotFoundError(
                    f"{file_path.relative_to(staged_skill)} references missing shared file: {shared_file}"
                )

            dest = staged_skill / "references" / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            if name not in copied:
                shutil.copy2(shared_file, dest)
                copied.add(name)
            changed = True
            return rel_link(file_path, dest)

        new_text = SHARED_REF_RE.sub(replace, text)
        if changed:
            file_path.write_text(new_text, encoding="utf-8")
            rewritten_files.append(str(file_path.relative_to(staged_skill)))

    return sorted(copied)


def package_one(skill_path: Path, output_dir: Path) -> Path:
    if not (skill_path / "SKILL.md").exists():
        raise FileNotFoundError(f"SKILL.md not found in {skill_path}")

    root = repo_root()
    shared = root / "skills" / "_shared"
    output_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="skill-package-") as tmp:
        tmp_root = Path(tmp)
        staged_parent = tmp_root / "stage"
        staged_parent.mkdir()
        staged_skill = staged_parent / skill_path.name
        shutil.copytree(skill_path, staged_skill)

        copied_shared = materialize_shared_refs(staged_skill, shared)

        output_file = output_dir / f"{skill_path.name}.skill"
        if output_file.exists():
            output_file.unlink()

        with zipfile.ZipFile(output_file, "w", zipfile.ZIP_DEFLATED) as zipf:
            for file_path in staged_skill.rglob("*"):
                if not file_path.is_file():
                    continue
                arcname = file_path.relative_to(staged_parent)
                if should_exclude(arcname):
                    continue
                zipf.write(file_path, arcname)

        print(f"packaged {skill_path.name} -> {output_file}")
        if copied_shared:
            print(f"  included shared: {', '.join(copied_shared)}")
        return output_file


def all_skill_paths() -> list[Path]:
    skills_dir = repo_root() / "skills"
    return sorted(
        p for p in skills_dir.iterdir()
        if p.is_dir() and p.name != "_shared" and (p / "SKILL.md").exists()
    )


def main(argv: list[str]) -> int:
    if len(argv) < 2 or argv[1] in {"-h", "--help"}:
        usage()
        return 0 if len(argv) >= 2 else 2

    output_dir = Path(argv[2]).resolve() if len(argv) >= 3 else repo_root() / "dist"

    try:
        if argv[1] == "--all":
            for skill in all_skill_paths():
                package_one(skill, output_dir)
        else:
            package_one(resolve_skill(argv[1]), output_dir)
    except Exception as exc:  # keep CLI errors readable
        print(f"error: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
