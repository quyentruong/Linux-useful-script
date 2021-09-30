#!/bin/sh

clear

COLOUR_RESET='\e[0m'
gCOLOUR='\e[38;5;154m'
GREEN_SEPARATOR="$gCOLOUR:$COLOUR_RESET"
GREEN_LINE=" $gCOLOUR─────────────────────────────────────────────────────$COLOUR_RESET"
GREEN_BULLET=" $gCOLOUR-$COLOUR_RESET"

echo -e "$GREEN_LINE"
echo -e " $(grep '^PRETTY' /etc/os-release | cut -d "=" -f2 | cut -d '"' -f2) $GREEN_SEPARATOR $(date "+%H:%M - %a %m/%d/%Y")"
echo -e "$GREEN_LINE"

echo -e "$GREEN_BULLET WAN IP $GREEN_SEPARATOR $(curl -sSfLm 3 https://freegeoip.app/csv/ 2>&1 | mawk -F, '($5){r=$5" "}{print $1" "r$3}')"
echo -e "$GREEN_BULLET Weather $GREEN_SEPARATOR $(curl -sSfLm 3 https://wttr.in/?format=4 2>&1)"

echo -e "$GREEN_LINE"
