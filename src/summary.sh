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
	local _numer=$(jq -r --arg key "$_numerator" '.[] | if has($key) then .[$key] | to_entries | max_by(.key) | .value else "nan" end' <<<"$_obj")
	local _denom=$(jq -r --arg key "$_denominator" '.[] | if has($key) then .[$key] | to_entries | max_by(.key) | .value else "nan" end' <<<"$_obj")
	if [[ ${_numer,,} == nan || ${_denom,,} == nan ]]; then
		printf '-'
		return
	fi
	if [[ $(awk -vd="$_denom" 'BEGIN{print d/1}') -eq 0 ]] || [[ -z "$_denom" ]]; then
		printf '-'
		return
	fi
	awk -v numer="$_numer" -v denom="$_denom" 'BEGIN{printf "%.2f", numer / denom}'
}
quick_ratio () {
	local _obj=$1
	local _assets=$(jq -r --arg key "Current Assets" '.[] | if has($key) then .[$key] | to_entries | max_by(.key) | .value else "nan" end' <<<"$_obj")
	local _inventory=$(jq -r --arg key "Inventory" '.[] | if has($key) then .[$key] | to_entries | max_by(.key) | .value else "nan" end' <<<"$_obj" 2>/dev/null)
	local _liabilities=$(jq -r --arg key "Current Liabilities" '.[] | if has($key) then .[$key] | to_entries | max_by(.key) | .value else "nan" end' <<<"$_obj")
	if [[ ${_assets,,} == nan ]]; then
		_assets=0
	fi
	if [[ ${_inventory,,} == nan ]]; then
		_inventory=0
	fi
	if [[ ${_liabilities,,} == nan ]]; then
		_liabilities=$(jq -r --arg key "Total Liabilities Net Minority Interest" '.[] | if has($key) then .[$key] | to_entries | max_by(.key) | .value else "nan" end' <<<"$_obj")
	fi
	awk -v assets="$_assets" -v inventory="$_inventory" -v liabilities="$_liabilities" 'BEGIN{printf "%.2f", (assets-inventory)/liabilities}'
}
roe () {
	local _bs=$1
	local _is=$2
	local _income=$(jq -r --arg key "Net Income" '.[] | if has($key) then .[$key] | to_entries | max_by(.key) | .value else "nan" end' <<<"$_is")
	local _equity=$(jq -r --arg key "Stockholders Equity" '.[] | if has($key) then .[$key] | to_entries | max_by(.key) | .value else "nan" end' <<<"$_bs")
	awk -v income="$_income" -v equity="$_equity" 'BEGIN{printf "%.2f%%", (income/equity)*100}'
}
debt_to_earnings () {
	local _bs=$1
	local _is=$2
	local _out
	#local _debt=$(jq -r '.[]."Total Debt" | to_entries | max_by(.key) | .value' <<<"$_bs")
	local _debt=$(jq -r --arg key "Total Debt" '.[] | if has($key) then .[$key] | to_entries | max_by(.key) | .value else "foo" end' <<<"$_bs")
	#local _earnings=$(jq -r '.[]."Gross Profit" | to_entries | max_by(.key) | .value' <<<"$_is" 2>/dev/null)
	local _earnings=$(jq -r --arg key "Gross Profit" '.[] | if has($key) then .[$key] | to_entries | max_by(.key) | .value else "foo" end' <<<"$_is")
	
	if [[ "$_earnings" == foo ]]; then
		_earnings=$(jq -r --arg key "Pretax Income" '.[] | if has($key) then .[$key] | to_entries | max_by(.key) | .value else "nan" end' <<<"$_is")
	fi
	if [[ "$_debt" == foo ]]; then
		_debt=$(jq -r --arg key "Total Liabilities Net Minority Interest" '.[] | if has($key) then .[$key] | to_entries | max_by(.key) | .value else "nan" end' <<<"$_bs")
	fi
	[[ "${_earnings,,}" == nan ]] && _earnings=0
	[[ "${_debt,,}" == nan ]] && _debt=0

	if [[ "$(echo "$_earnings == 0" | bc -l)" -eq 1 ]]; then
		printf '%s' NaN
		return
	fi
	if [[ "$(echo "$_debt == 0" | bc -l)" -eq 1 ]]; then
		printf '%d' 0
		return
	fi
	
	_out=$(awk -v debt="$_debt" -v earnings="$_earnings" 'BEGIN{printf "%.2f", debt/earnings}')
	if is_negative "$_out"; then
		printf '%.2f' "${_out#-}"
	else
		printf '%.2f' "$_out"
	fi

}
earnings_yield () {
	local _obj=$1
	local _income=$(jq -r .netIncomeToCommon <<<"$_obj")
	local _cap=$(jq -r .marketCap <<<"$_obj")
	if [[ $_cap == null ]]; then
		printf '-'
		return 1
	fi
	awk -v income="$_income" -v cap="$_cap" 'BEGIN{printf "%.2f", income/cap}'
}
colorize_low () {
	local _num=$1
	local _low=$2
	local _high=$3
	local _colorize=${4:-true}
	local _comp=$(awk -vn="$_num" 'BEGIN{printf "%.2f", n/1}')

	if ! is_number "$_num" || [[ $_colorize == false || "$_comp" == 0 ]]; then
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
	local _comp=$(awk -vn="$_num" 'BEGIN{printf "%.2f", n/1}')

	if ! is_number "$_num" || [[ $_colorize == false || "$_comp" == 0 ]]; then
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
	if [[ $parsable == true ]]; then
		printf '%s,%s\n' "$_lhs" "$_rhs"
	else
		printf '%-22s%s\n' "${_lhs}:" "$_rhs"
	fi
}
is_empty_json () {
	local _json=$1
	local _is_empty=$(jq -e 'length == 0' <<<"$_json")
	if [[ $_is_empty == false ]]; then
		return 1
	fi
}
main () {
	local _t=$1
	local _balance_sheet=$(fetch_data "$_t" balance_sheet | to_json)
	local _income_sheet=$(fetch_data "$_t" income_statement | to_json)
	local _cashflow_sheet=$(fetch_data "$_t" cash_flow | to_json)
	local _info=$(fetch_data "$_t" info)
	if is_empty_json "$_balance_sheet" || is_empty_json "$_income_sheet" ||
	is_empty_json "$_cashflow_sheet" || is_empty_json "$_info"; then
		printf 'This company [%s] sucks yo\n' "$_t"
		return 1
	fi
	local _debt_to_equity=$(get_ratio "$_balance_sheet" "Total Debt" "Stockholders Equity")
	is_negative "$_debt_to_equity" && _debt_to_equity=${_debt_to_equity#-}
	local _debt_to_earnings=$(debt_to_earnings "$_balance_sheet" "$_income_sheet")
	local _earnings_yield=$(earnings_yield "$_info")
	local _current_ratio=$(get_ratio "$_balance_sheet" "Total Assets" "Total Liabilities Net Minority Interest")
	local _quick_ratio=$(quick_ratio "$_balance_sheet")
	local _revenue_growth=$(avg_change "$(trend "Total Revenue" "$_income_sheet" | awk -F',' '{for (i=2; i<NF; i++) if ($i ~ /^-?[0-9]+(\.[0-9]+)?%$/) printf "%s%s", $i, (i<NF-1 ? "," : "\n")}')")
	local _net_profit_margin=$(get_ratio "$_income_sheet" "Net Income" "Total Revenue")
	local _net_profit_margin=$(awk -v npm="$_net_profit_margin" 'BEGIN{printf "%.2f%%", npm*100}')
	local _roe=$(roe "$_balance_sheet" "$_income_sheet")
	local _eps=$(jq -r .trailingEps <<<"$_info")
	local _pe=$(jq -r .trailingPE <<<"$_info")
	local _cap=$(jq -r .marketCap <<<"$_info")
	#local _net_debt=$(jq -r '.[]."Net Debt" | to_entries | max_by(.key) | .value' <<<"$_balance_sheet")
	local _fcf _fcft _fcfh
	mapfile -t _fcf < <(get_values "Free Cash Flow" "$_cashflow_sheet")
	if [[ $parsable == true ]]; then
		_fcft=$(trend2 "${_fcf[@]}")
	else
		_fcft=$(trend2 "${_fcf[@]}" | tr ',' ' ')
	fi
	for f in "${_fcf[@]}"; do
		_fcfh+=($(make_human "$f"))
	done
	if [[ $parsable == false ]]; then
		printf '%s\nCap: %s\n' "${_t^^}" "$(make_human "$_cap")"
		printf '%-40s\n' "-" | tr ' ' '-'
	fi
	pad "Debt-to-equity" "$(colorize_low "$_debt_to_equity" 0.5 1 "$color")"
	pad "Debt-to-earnings" "$(colorize_low "$_debt_to_earnings" 1 2 "$color")"
	pad "Earnings Yield" "$(colorize_high "$_earnings_yield" 1 2 "$color")" 
	pad "Current Ratio" "$(colorize_high "$_current_ratio" 1 1 "$color")"
	pad "Quick Ratio" "$(colorize_high "$_quick_ratio" 1 1 "$color")"
	pad "Avg Revenue Growth" "$(colorize_high "$_revenue_growth" 5 7 "$color")"
	pad "Profit Margin" "$(colorize_high "$_net_profit_margin" 10 15 "$color")"
	pad "ROE" "$(colorize_high "$_roe" 10 15 "$color")"
	pad "EPS" "$(colorize_high "$_eps" 0 1 "$color")"
	pad "P/E" "$(colorize_low "$_pe" 5 20 "$color")"
	if [[ $parsable == true ]]; then
		pad "Free cashflow" "$(IFS=,; echo "${_fcf[*]}")"
	else
		pad "Free cashflow" "${_fcfh[*]}"
	fi
	pad "Free cashflow trend" "${_fcft[*]}"
}
#######################################
while getopts t:hpC opt; do
	case $opt in
		t)	ticker=$OPTARG;;
		p)	parsable=true;;
		C)	color=false;;
		h)	usage;;
	esac
done
#######################################
main "$ticker"
