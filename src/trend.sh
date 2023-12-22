#!/usr/bin/env bash
#
[[ $DEBUG == true ]] && set -x
#######################################
if [[ -f "${0%/*}/../lib/stonks.sh" ]]; then
	. "${0%/*}/../lib/stonks.sh"
else
	printf 'ERROR: %s not found\n' "${0%/*}/../lib/stonks.sh" >&2
	exit 1
fi
if ! [[ -f "${0%/*}/get_data.py" ]]; then
	printf 'ERROR: %s not found\n' "${0%/*}/get_data.py" >&2
	exit 1
fi
#######################################
parsable=false
human=true
#######################################
print_header () {
	local _attr=$1
	local _data=$2
	local _obj=$(jq --arg attr "$_attr" '.[] | .[$attr]' <<<"$_data")
	local _foo
	mapfile -t _dates < <(jq -r 'keys[]' <<<"$_obj" | sort -rd)
	_foo=(' ' "${_dates[@]}")
	(IFS=,; echo "${_foo[*]}")
}
main () {
	print_header "Total Debt" "$balance_sheet"
	for metric in "${balance_metrics[@]}"; do 
		print_values "$metric" "$balance_sheet"
		trend "$metric" "$balance_sheet"
	done
	for metric in "${income_metrics[@]}"; do
		print_values "$metric" "$income_sheet"
		trend  "$metric" "$income_sheet"
	done
}
#######################################
while getopts t:hpH opt; do
	case $opt in
		t)	ticker=$OPTARG;;
		p)	parsable=true;;
		H)	human=false;;
		h)	usage;;
	esac
done
#######################################
balance_sheet=$(fetch_data "$ticker" balance_sheet | to_json)
income_sheet=$(fetch_data "$ticker" income_statement | to_json)

if [[ $parsable == false ]]; then
	main | column -s, -t
else
	main
fi
