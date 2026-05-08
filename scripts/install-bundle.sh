#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  scripts/install-bundle.sh <bundle-name> [target-skills-dir] [--force]
  scripts/install-bundle.sh --list

Default target:
  ${AGENTS_HOME:-$HOME/.agents}/skills

Bundles are defined in bundles.json.
USAGE
}

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
bundles_file="$repo_root/bundles.json"
target_dir="${2:-${AGENTS_HOME:-$HOME/.agents}/skills}"
force="false"

if [[ "${2:-}" == "--force" ]]; then
  target_dir="${AGENTS_HOME:-$HOME/.agents}/skills"
  force="true"
elif [[ "${3:-}" == "--force" ]]; then
  force="true"
fi

if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
  usage
  exit 0
fi

if [[ "${1:-}" == "--list" ]]; then
  python3 - "$bundles_file" <<'PY'
import json
import sys

with open(sys.argv[1], "r", encoding="utf-8") as f:
    bundles = json.load(f)["bundles"]

for name, info in bundles.items():
    skills = ", ".join(info["skills"])
    print(f"{name}: {skills}")
    print(f"  {info['description']}")
PY
  exit 0
fi

bundle_name="${1:-}"
if [[ -z "$bundle_name" ]]; then
  usage >&2
  exit 2
fi

skills_output="$(python3 - "$bundles_file" "$bundle_name" <<'PY'
import json
import sys

with open(sys.argv[1], "r", encoding="utf-8") as f:
    bundles = json.load(f)["bundles"]

name = sys.argv[2]
if name not in bundles:
    available = ", ".join(sorted(bundles))
    print(f"Unknown bundle: {name}. Available: {available}", file=sys.stderr)
    sys.exit(1)

for skill in bundles[name]["skills"]:
    print(skill)
PY
)
"

mkdir -p "$target_dir"

count=0
while IFS= read -r skill; do
  [[ -z "$skill" ]] && continue
  source_dir="$repo_root/skills/$skill"
  if [[ ! -d "$source_dir" ]]; then
    echo "Bundle '$bundle_name' references missing skill: $skill" >&2
    exit 1
  fi

  if [[ -e "$target_dir/$skill" && "$force" != "true" ]]; then
    echo "Target already exists: $target_dir/$skill" >&2
    echo "Re-run with --force to replace existing installed skills." >&2
    exit 1
  fi

  if [[ "$force" == "true" ]]; then
    rm -rf "$target_dir/$skill"
  fi

  cp -R "$source_dir" "$target_dir/$skill"
  echo "installed $skill -> $target_dir/$skill"
  count=$((count + 1))
done <<< "$skills_output"

echo "installed bundle '$bundle_name' ($count skills)"
