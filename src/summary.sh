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
color=true
#######################################
get_ratio () {
	local _obj=$1
	local _numerator=$2
	local _denominator=$3
	local _latest=$(jq -r --arg key "$_numerator" '.[] | .[$key] | keys | max' <<<"$_obj")
	local _numer=$(jq -r --arg key "$_numerator" --arg date "$_latest" '.[] | .[$key] | .[$date]' <<<"$_obj")
	local _denom=$(jq -r --arg key "$_denominator" --arg date "$_latest" '.[] | .[$key] | .[$date]' <<<"$_obj")
	if [[ ${_numer,,} == nan || ${_denom,,} == nan ]]; then
		printf '-'
	fi
	awk -v debt="$_numer" -v equity="$_denom" 'BEGIN{printf "%.2f", debt / equity}'
}
quick_ratio () {
	local _obj=$1
	local _latest=$(jq -r --arg key "Current Assets" '.[] | .[$key] | keys | max' <<<"$_obj")
	local _assets=$(jq -r --arg key "Current Assets" --arg date "$_latest" '.[] | .[$key] | .[$date]' <<<"$_obj")
	local _inventory=$(jq -r --arg key "Inventory" --arg date "$_latest" '.[] | .[$key] | .[$date]' <<<"$_obj")
	local _liabilities=$(jq -r --arg key "Current Liabilities" --arg date "$_latest" '.[] | .[$key] | .[$date]' <<<"$_obj")
	if [[ ${_assets,,} == nan || ${_inventory,,} == nan || ${_liabilities,,} == nan ]]; then
		printf '-'
	fi
	awk -v assets="$_assets" -v inventory="$_inventory" -v liabilities="$_liabilities" 'BEGIN{printf "%.2f", (assets-inventory)/liabilities}'
}
roe () {
	local _bs=$1
	local _is=$2
	local _latest=$(jq -r --arg key "Net Income" '.[] | .[$key] | keys | max' <<<"$_is")
	local _income=$(jq -r --arg key "Net Income" --arg date "$_latest" '.[] | .[$key] | .[$date]' <<<"$_is")
	local _equity=$(jq -r --arg key "Stockholders Equity" --arg date "$_latest" '.[] | .[$key] | .[$date]' <<<"$_bs")
	awk -v income="$_income" -v equity="$_equity" 'BEGIN{printf "%.2f%%", (income/equity)*100}'
}
colorize_low () {
	local _num=$1
	local _low=$2
	local _high=$3
	local _colorize=${4:-true}
	local _comp=$(awk -vn="$_num" 'BEGIN{print n/1}')

	if [[ $_colorize == false || "$_comp" == 0 ]]; then
		echo "$_num"
	elif (( $(echo "$_comp< $_low" | bc -l) )); then
        echo -e "\e[32m$_num\e[0m"  # Green
    elif (( $(echo "$_comp >= $_low && $_comp <= $_high" | bc -l) )); then
        echo -e "\e[33m$_num\e[0m"  # Orange/Yellow
    else
        echo -e "\e[31m$_num\e[0m"  # Red
    fi
}
colorize_high () {
	local _num=$1
	local _low=$2
	local _high=$3
	local _colorize=${4:-true}
	local _comp=$(awk -vn="$_num" 'BEGIN{print n/1}')

	if [[ $_colorize == false || "$_comp" == 0 ]]; then
		echo "$_num"
	elif (( $(echo "$_comp< $_low" | bc -l) )); then
		echo -e "\e[31m$_num\e[0m"  # Red
    elif (( $(echo "$_comp >= $_low && $_comp <= $_high" | bc -l) )); then
        echo -e "\e[33m$_num\e[0m"  # Orange/Yellow
    else
        echo -e "\e[32m$_num\e[0m"  # Green        
    fi
}
pad () {
	local _lhs=$1
	local _rhs=$2
	printf '%-22s%s\n' "$_lhs" "$_rhs"
}
main () {
	local _t=$1
	local _balance_sheet=$(fetch_data "$_t" balance_sheet | to_json)
	local _income_sheet=$(fetch_data "$_t" income_statement | to_json)
	local _cashflow_sheet=$(fetch_data "$_t" cash_flow | to_json)
	local _info=$(fetch_data "$_t" info)
	local _debt_to_equity=$(get_ratio "$_balance_sheet" "Total Debt" "Stockholders Equity")
	local _current_ratio=$(get_ratio "$_balance_sheet" "Total Assets" "Current Liabilities")
	local _quick_ratio=$(quick_ratio "$_balance_sheet")
	local _revenue_growth=$(avg_change "$(trend "Total Revenue" "$_income_sheet" | awk -F',' '{for (i=2; i<NF; i++) if ($i ~ /^-?[0-9]+(\.[0-9]+)?%$/) printf "%s%s", $i, (i<NF-1 ? "," : "\n")}')")
	local _net_profit_margin=$(get_ratio "$_income_sheet" "Net Income" "Total Revenue")
	local _net_profit_margin=$(awk -v npm="$_net_profit_margin" 'BEGIN{printf "%.2f%%", npm*100}')
	local _roe=$(roe "$_balance_sheet" "$_income_sheet")
	local _eps=$(get_values "Basic EPS" "$_income_sheet" | head -1)
	local _pe=$(jq -r .trailingPE <<<"$_info")
	local _fcf _fcft _fcfh
	mapfile -t _fcf < <(get_values "Free Cash Flow" "$_cashflow_sheet")
	_fcft=$(trend2 "${_fcf[@]}" | tr ',' ' ')
	for f in "${_fcf[@]}"; do
		_fcfh+=($(make_human "$f"))
	done
	printf '%s\n' "${_t^^}"
	printf '%-40s\n' "-" | tr ' ' '-'
	pad "Debt-to-equity:" "$(colorize_low "$_debt_to_equity" 0.5 1 "$color")"
	pad "Current Ratio:" "$(colorize_high "$_current_ratio" 1 1 "$color")"
	pad "Quick Ratio:" "$(colorize_high "$_quick_ratio" 1 1 "$color")"
	pad "Avg Revenue Growth:" "$(colorize_high "$_revenue_growth" 5 7 "$color")"
	pad "Profit Margin:" "$(colorize_high "$_net_profit_margin" 10 15 "$color")"
	pad "ROE:" "$(colorize_high "$_roe" 10 15 "$color")"
	pad "EPS:" "$_eps"
	pad "P/E:" "$(colorize_low "$_pe" 5 10 "$color")"
	pad "Free cashflow:" "${_fcfh[*]}"
	pad "Free cashflow trend:" "${_fcft[*]}"
	printf '%-40s\n' "=" | tr ' ' '='
}
#######################################
while getopts t:hpHC opt; do
	case $opt in
		t)	ticker=$OPTARG;;
		p)	parsable=true;;
		H)	human=false;;
		C)	color=false;;
		h)	usage;;
	esac
done
#######################################
main "$ticker"
