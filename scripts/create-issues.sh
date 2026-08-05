#!/usr/bin/env bash
# File the task briefs in docs/tasks/ as GitHub issues.
#
#   ./scripts/create-issues.sh            preview only - creates nothing
#   ./scripts/create-issues.sh --create   actually create them
#
# Previewing is the default on purpose: creating thirty issues is hard to undo.
# Needs the GitHub CLI (https://cli.github.com) and write access to the repo.

set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TASKS_DIR="$ROOT/docs/tasks"
CREATE=0
[ "${1:-}" = "--create" ] && CREATE=1

if [ ! -d "$TASKS_DIR" ]; then
  echo "No docs/tasks/ directory found." >&2
  exit 1
fi

if [ "$CREATE" -eq 1 ]; then
  command -v gh >/dev/null 2>&1 || {
    echo "The GitHub CLI (gh) is not installed: https://cli.github.com" >&2
    exit 1
  }
  gh auth status >/dev/null 2>&1 || {
    echo "Not signed in. Run: gh auth login" >&2
    exit 1
  }
fi

# Pull one `key: value` out of the YAML front matter at the top of a brief.
front_matter() {
  awk -v key="$2" '
    NR == 1 && $0 == "---" { inside = 1; next }
    inside && $0 == "---"  { exit }
    inside && $0 ~ "^" key ":" {
      sub("^" key ": *", "")
      gsub(/^"|"$/, "")
      print
      exit
    }
  ' "$1"
}

count=0
for brief in "$TASKS_DIR"/*.md; do
  [ -e "$brief" ] || continue

  title=$(front_matter "$brief" title)
  labels=$(front_matter "$brief" labels | tr -d '[]' | tr -s ' ')
  [ -n "$title" ] || { echo "skipping $(basename "$brief") - no title in front matter"; continue; }

  # The brief itself is the issue body, minus the front matter.
  body=$(awk 'NR == 1 && $0 == "---" { inside = 1; next }
              inside && $0 == "---"  { inside = 0; next }
              !inside' "$brief")

  count=$((count + 1))

  if [ "$CREATE" -eq 1 ]; then
    printf 'creating: %s\n' "$title"
    gh issue create --title "$title" --body "$body" \
      ${labels:+--label "$labels"} >/dev/null || echo "  failed - does the label exist?"
  else
    printf '  %-70s [%s]\n' "$title" "$labels"
  fi
done

echo
if [ "$CREATE" -eq 1 ]; then
  echo "Created $count issues."
else
  echo "$count issues would be created. Re-run with --create to do it."
  echo "Labels must already exist in the repo, or gh will reject the issue."
fi
