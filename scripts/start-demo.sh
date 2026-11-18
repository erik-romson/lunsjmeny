#!/usr/bin/env bash
# Creates one draupnir clone per demo issue and starts the norn pipeline in each, in its own
# detached tmux session. Safe to run again: existing clones and sessions are left alone.
#
#   scripts/start-demo.sh            create the clones and start the runs
#   tmux attach -t lunsj-3           watch a run (Ctrl-b d to leave it running)
#
# Overrides: NORN (the norn command), NORN_DIR (the norn checkout).
set -euo pipefail

# TODO: norn reads Jira keys (ABC-123) only. The key for a GitHub issue is not decided yet.
KEY_PREFIX="LUNSJ"
PIPELINE="fix_jira_issue_v3"
TEST_CMD="uv run pytest -q"

# Issue number and folder name. The folder starts with the issue number.
ISSUES=(
    "1 1-dagene-i-riktig-rekkefolge"
    "2 2-vis-og-filtrer-allergener"
    "3 3-fremhev-dagens-rett"
)

NORN_DIR="${NORN_DIR:-$HOME/projects/erik.romson/norn/main}"
read -r -a NORN <<< "${NORN:-uv run --project $NORN_DIR norn}"

REPO_ROOT="$(git -C "$(dirname "$0")" rev-parse --show-toplevel)"
WORKSPACE="$(dirname "$REPO_ROOT")"

fail() {
    echo "error: $*" >&2
    exit 1
}

check_tools() {
    local tool
    for tool in draupnir tmux uv; do
        command -v "$tool" > /dev/null || fail "$tool is not on PATH"
    done
    [[ -f "$WORKSPACE/draupnir.toml" ]] || fail "$WORKSPACE is not a draupnir workspace"
    [[ -d "$NORN_DIR" ]] || fail "norn checkout not found: $NORN_DIR (set NORN_DIR)"
}

create_clone() {
    local branch="$1" folder="$2"
    if [[ -d "$WORKSPACE/$folder" ]]; then
        echo "clone $folder exists, skipping"
        return
    fi
    draupnir -C "$WORKSPACE" new "$branch" --folder "$folder"
}

start_run() {
    local key="$1" folder="$2" session="$3"
    if tmux has-session -t "$session" 2> /dev/null; then
        echo "session $session is running, skipping"
        return
    fi
    local command
    command="$(printf '%q ' "${NORN[@]}" run "$PIPELINE" "$key" auto --arg "test_cmd=$TEST_CMD")"
    tmux new-session -d -s "$session" -c "$WORKSPACE/$folder"
    tmux send-keys -t "$session" "$command" Enter
    echo "started $key in $folder (tmux attach -t $session)"
}

main() {
    if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
        sed -n '2,8p' "$0" | sed 's/^# \{0,1\}//'
        exit 0
    fi
    [[ $# -eq 0 ]] || fail "unknown argument: $1 (see --help)"

    check_tools
    local entry number folder key
    for entry in "${ISSUES[@]}"; do
        read -r number folder <<< "$entry"
        key="$KEY_PREFIX-$number"
        create_clone "$key-${folder#*-}" "$folder"
        start_run "$key" "$folder" "lunsj-$number"
    done
}

main "$@"
