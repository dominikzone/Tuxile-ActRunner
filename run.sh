#!/bin/bash

# ─── ANSI colors ────────────────────────────────────────────────────────────
RESET='\033[0m'
CYAN='\033[1;36m'
GREEN='\033[1;32m'
WHITE='\033[1;37m'
GRAY='\033[0;90m'
YELLOW='\033[1;33m'
RED='\033[1;31m'

# ─── Locate project & python ────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PYTHON="$SCRIPT_DIR/venv/bin/python3"

if [ ! -f "$PYTHON" ] && [ -f "$SCRIPT_DIR/.venv/bin/python3" ]; then
    PYTHON="$SCRIPT_DIR/.venv/bin/python3"
fi

if [ ! -f "$PYTHON" ]; then
    echo "Virtual environment not found in $SCRIPT_DIR/venv or $SCRIPT_DIR/.venv"
    exit 1
fi

# ─── Launch app before anything else ────────────────────────────────────────
cd "$SCRIPT_DIR"
nohup "$PYTHON" main.py > /dev/null 2>&1 &
disown

# ─── UI ─────────────────────────────────────────────────────────────────────
clear

printf "\n"
printf "  ${CYAN}[ Tuxile — Act Runner ]${RESET}\n"
printf "\n"
printf "  ${GREEN}App launched successfully.${RESET}\n"
printf "  ${WHITE}Have fun in the game, Exile!${RESET}\n"
printf "\n"
printf "  ${GRAY}$(printf '%0.s-' {1..44})${RESET}\n"
printf "\n"

# ─── Countdown ──────────────────────────────────────────────────────────────
TOTAL=10

for i in $(seq $TOTAL -1 1); do
    # Pick color based on remaining seconds
    if [ "$i" -le 3 ]; then
        BAR_COLOR="$RED"
    elif [ "$i" -le 6 ]; then
        BAR_COLOR="$YELLOW"
    else
        BAR_COLOR="$CYAN"
    fi

    # Build progress bar: filled = i, empty = TOTAL-i
    FILLED=$i
    EMPTY=$(( TOTAL - i ))
    BAR=""
    for (( f=0; f<FILLED; f++ )); do BAR="${BAR}#"; done
    for (( e=0; e<EMPTY;  e++ )); do BAR="${BAR} "; done

    printf "\r  ${BAR_COLOR}Terminal closing in: %2ds [%s]${RESET}" "$i" "$BAR"
    sleep 1
done

printf "\r  ${GREEN}App is running. Enjoy!           ${RESET}\n"
printf "\n"

# Terminal opened by the .desktop launcher closes on its own when the script exits.
exit 0
