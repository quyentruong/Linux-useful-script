#!/usr/bin/env sh

RED='\033[0;31m'
BOLD='\033[1m'
NC='\033[0m'
api_domain='bash.ws'
api_domain2='ipinfo.io'
error_code=1

COLOUR_RESET='\e[0m'
gCOLOUR='\e[38;5;154m'
GREEN_SEPARATOR="$gCOLOUR:$COLOUR_RESET"
GREEN_LINE=" $gCOLOUR─────────────────────────────────────────────────────$COLOUR_RESET"
GREEN_BULLET=" $gCOLOUR-$COLOUR_RESET"

function increment_error_code {
    error_code=$((error_code + 1))
}

function echo_bold {
    echo -e "${BOLD}${1}${NC}"
}

function echo_error {
    (>&2 echo -e "${RED}${1}${NC}")
}

function program_exit {
    command -v $1 > /dev/null
    if [ $? -ne 0 ]; then
        echo_error "Please, install \"$1\""
        exit $error_code
    fi
    increment_error_code
}

function check_internet_connection () {
    local api_domain="$1"
    curl --silent --head  --request GET "https://${api_domain}" | grep "200" > /dev/null
    if [ $? -ne 0 ]; then
        echo_error "No internet connection."
        exit $error_code
    fi
    increment_error_code
}

program_exit curl
program_exit ping
program_exit jq

check_internet_connection "$api_domain"
check_internet_connection "$api_domain2"

if hash shuf 2>/dev/null; then
    id=$(shuf -i 1000000-9999999 -n 1)
else
    id=$(jot -w %i -r 1 1000000 9999999)
fi

for i in $(seq 1 10); do
    ping -c 1 "${i}.${id}.${api_domain}" > /dev/null 2>&1
done

function print_servers {
    echo ${result_json} | \
        jq  --monochrome-output \
        --raw-output \
        ".[] | select(.type == \"${1}\") | \"\(.ip)\(if .country_name != \"\" and  .country_name != false then \" [\(.country_name)\(if .asn != \"\" and .asn != false then \" \(.asn)\" else \"\" end)]\" else \"\" end)\""
}

result_json=$(curl --silent "https://${api_domain}/dnsleak/test/${id}?json")


function print_servers2 {
    curl -sSfLm 3 -s $api_domain2 2>&1 | jq -r '"\(.ip) [\(.country), \(.org)]"'
}

dns_count=$(print_servers "dns" | wc -l)

echo -e "$GREEN_LINE"
echo -e " $(grep '^PRETTY' /etc/os-release | cut -d "=" -f2 | cut -d '"' -f2) $GREEN_SEPARATOR $(date "+%H:%M - %a %m/%d/%Y")"
echo -e "$GREEN_LINE"

echo -e "$GREEN_BULLET 1st Test WAN IP $GREEN_SEPARATOR $(print_servers2)"
echo -e "$GREEN_BULLET 2nd Test WAN IP $GREEN_SEPARATOR $(print_servers "ip")"

if [ ${dns_count} -eq "0" ];then
    echo -e "$GREEN_BULLET DNS server(s) $GREEN_SEPARATOR No DNS servers found" 
elif [ ${dns_count} -eq 1 ]; then
    # Print single DNS server on the same line
    echo -e "$GREEN_BULLET DNS server(s) $GREEN_SEPARATOR $(print_servers "dns")"
else
    # Print header, then each DNS server indented
    echo -e "$GREEN_BULLET DNS server(s) $GREEN_SEPARATOR"
    print_servers "dns" | while read -r line; do
        echo -e "    $line"
    done
fi

echo -e "$GREEN_BULLET Conclusion $GREEN_SEPARATOR $(print_servers "conclusion")"

echo -e "$GREEN_LINE"
