#!/usr/bin/env bash

RED='\033[0;31m'
BOLD='\033[1m'
NC='\033[0m'
api_domain='bash.ws'
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

function check_internet_connection {
    curl --silent --head  --request GET "https://${api_domain}" | grep "200 OK" > /dev/null
    if [ $? -ne 0 ]; then
        echo_error "No internet connection."
        exit $error_code
    fi
    increment_error_code
}

program_exit curl
program_exit ping
check_internet_connection

if command -v jq &> /dev/null; then
    jq_exists=1
else
    jq_exists=0
fi

if hash shuf 2>/dev/null; then
    id=$(shuf -i 1000000-9999999 -n 1)
else
    id=$(jot -w %i -r 1 1000000 9999999)
fi

for i in $(seq 1 10); do
    ping -c 1 "${i}.${id}.${api_domain}" > /dev/null 2>&1
done

function print_servers {

    if (( $jq_exists )); then

        echo ${result_json} | \
            jq  --monochrome-output \
            --raw-output \
            ".[] | select(.type == \"${1}\") | \"\(.ip)\(if .country_name != \"\" and  .country_name != false then \" [\(.country_name)\(if .asn != \"\" and .asn != false then \" \(.asn)\" else \"\" end)]\" else \"\" end)\""

    else

        while IFS= read -r line; do
            if [[ "$line" != *${1} ]]; then
                continue
            fi

            ip=$(echo $line | cut -d'|' -f 1)
            code=$(echo $line | cut -d'|' -f 2)
            country=$(echo $line | cut -d'|' -f 3)
            asn=$(echo $line | cut -d'|' -f 4)

            if [ -z "${ip// }" ]; then
                 continue
            fi

            if [ -z "${country// }" ]; then
                 echo "$ip"
            else
                 if [ -z "${asn// }" ]; then
                     echo "$ip [$country]"
                 else
                     echo "$ip [$country, $asn]"
                 fi
            fi
        done <<< "$result_txt"

    fi
}


if (( $jq_exists )); then
    result_json=$(curl --silent "https://${api_domain}/dnsleak/test/${id}?json")
else
    result_txt=$(curl --silent "https://${api_domain}/dnsleak/test/${id}?txt")
fi

dns_count=$(print_servers "dns" | wc -l)

echo -e "$GREEN_LINE"
echo -e " $(grep '^PRETTY' /etc/os-release | cut -d "=" -f2 | cut -d '"' -f2) $GREEN_SEPARATOR $(date "+%H:%M - %a %m/%d/%Y")"
echo -e "$GREEN_LINE"

echo -e "$GREEN_BULLET 1st Test WAN IP $GREEN_SEPARATOR $(curl -sSfLm 3 https://freegeoip.app/csv/ 2>&1 | mawk -F, '($5){r=$5" "}{print $1" "r$3}')"
echo -e "$GREEN_BULLET 2nd Test WAN IP $GREEN_SEPARATOR $(print_servers "ip")"

if [ ${dns_count} -eq "0" ];then
    echo -e "$GREEN_BULLET DNS server(s) $GREEN_SEPARATOR No DNS servers found" 
else
    echo -e "$GREEN_BULLET DNS server(s) $GREEN_SEPARATOR $(print_servers "dns")" 
fi


echo -e "$GREEN_BULLET Weather $GREEN_SEPARATOR $(curl -sSfLm 3 https://wttr.in/?format=4 2>&1)"

echo -e "$GREEN_BULLET Conclusion $GREEN_SEPARATOR $(print_servers "conclusion")"

echo -e "$GREEN_LINE"
