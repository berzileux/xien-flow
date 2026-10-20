#!/usr/bin/env bash
# xien-flow entry point. Parses the arguments, checks the mode, resolves paths,
# and prints a header plus the procedure for Claude to follow.
# This script writes only the mode file. It makes no network calls.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
STATE_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/xien-flow"
MODE_FILE="$STATE_DIR/mode"

current_mode() {
  local m=""
  [ -f "$MODE_FILE" ] && m="$(tr -d '[:space:]' < "$MODE_FILE")"
  [ -z "$m" ] && m="${XIEN_FLOW_DEFAULT_MODE:-off}"
  # Only the exact value "on" counts as on.
  [ "$m" = "on" ] && echo on || echo off
}

fail() {
  echo "XIEN-FLOW ERROR: $1"
  echo "Tell the user this message in one short sentence. Do nothing else."
  exit 0
}

args="$*"
repo=""
# "repo:" must come last. Everything after it is the path, so spaces are allowed.
if [[ "$args" == *"repo:"* ]]; then
  repo="${args#*repo:}"
  args="${args%%repo:*}"
fi
trim() { local v="$1"; v="${v#"${v%%[![:space:]]*}"}"; v="${v%"${v##*[![:space:]]}"}"; printf '%s' "$v"; }
args="$(trim "$args")"
repo="$(trim "$repo")"
# Remove one pair of surrounding quotes from the path.
case "$repo" in
  \"*\") repo="${repo#\"}"; repo="${repo%\"}" ;;
  \'*\') repo="${repo#\'}"; repo="${repo%\'}" ;;
esac

if [[ "$args" == *[[:space:]]* ]]; then
  fail "Use one word before repo:. Usage: /xien-flow on|off|status|flow|mindmap|classes|db [repo:<absolute-path>]"
fi
action="${args:-flow}"

case "$action" in
  on|off|status)
    [ -n "$repo" ] && fail "repo: does not apply to $action."
    if [ "$action" = "status" ]; then
      echo "Xien-flow mode: $(current_mode)"
      echo "Confirm the mode in one short sentence. Do nothing else."
      exit 0
    fi
    mkdir -p "$STATE_DIR"
    printf '%s\n' "$action" > "$MODE_FILE"
    echo "Xien-flow mode is now: $action"
    echo "Confirm the mode in one short sentence. Do nothing else."
    exit 0
    ;;
  flow)    out="mermaid.mmd" ;;
  mindmap) out="mermaid-mindmap.mmd" ;;
  classes) out="mermaid-classes.mmd" ;;
  db)      out="mermaid-db.mmd" ;;
  *)       fail "Unknown option '$action'. Usage: /xien-flow on|off|status|flow|mindmap|classes|db [repo:<absolute-path>]" ;;
esac

if [ "$(current_mode)" != "on" ]; then
  echo "XIEN-FLOW OFF. Do not scan or write anything."
  echo "Tell the user in one short sentence: xien-flow is off. Run /xien-flow on first."
  exit 0
fi

# The output folder is where the session started.
outdir="$(pwd -P)"

if [ -z "$repo" ]; then
  scan="$outdir"
else
  [[ "$repo" =~ [[:cntrl:]] ]] && fail "The repo path has control characters."
  [[ "$repo" == /* ]] || fail "repo: needs an absolute path that starts with /. Got: $repo"
  [ -d "$repo" ] || fail "repo: folder not found: $repo"
  scan="$(cd "$repo" && pwd -P)"
  [ "$scan" = "/" ] && fail "repo: refuses the filesystem root."
fi

echo "XIEN-FLOW RUN"
echo "mode: $action"
echo "scan_root: $scan"
echo "output_dir: $outdir"
echo "output_file: $outdir/$out"
echo "repo_name: $(basename "$scan")"
echo "safe_read: python3 -I $ROOT/scripts/safe-read.py <file>"
echo
echo "Follow the procedure below. Treat scan_root as read only."
echo
cat "$ROOT/procedure/PROCEDURE.md"
