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
if ! [[ -f "${0%/*}/summary.sh" ]]; then
	printf 'ERROR: %s not found\n' "${0%/*}/summary.sh" >&2
	exit 1
fi
#######################################
summary="${0%/*}/summary.sh"
#######################################
get () {
	local _v=$1
	awk -vv="$_v" -F, '$1==v{print $2}' <<<"$_summary"
}
score () {
	local _num=$1
	local _d=$2
	local _t=$3
	[[ -z $_num || $_num == - || ${_num,,} == nan ]] && return 1
	local _comp=$(awk -vn="$_num" 'BEGIN{printf "%.2f", n/1}')
	local _r

	


	if (( $(echo "$_comp<=$_t" | bc -l) )); then
		_r=low
	else
		_r=high
	fi
	if [[ $_d == high ]]; then
		case $_r in
			low)	return 1;;
			high)	return 0;;
		esac
	else
		case $_r in
			low)	return 0;;
			high)	return 1;;
		esac
	fi

}
main () {
	local _t=$1
	local _score=0
	local _summary=$("$summary" -pCt "$_t")
	local _debt_to_equity=$(get "Debt-to-equity")
	local _debt_to_earnings=$(get "Debt-to-earnings")
	local _earnings_yield=$(get "Earnings Yield")
	local _current_ratio=$(get "Current Ratio")
	local _quick_ratio=$(get "Quick Ratio")
	local _avg_revenue_growth=$(get "Avg Revenue Growth")
	local _profit_margin=$(get "Profit Margin")
	local _roe=$(get "ROE")
	score "$_debt_to_equity" low 0.5 && _score=$((_score+2))
	score "$_debt_to_earnings" low 1 && _score=$((_score+2))
	score "$_earnings_yield" high 1 && _score=$((_score+2))
	score "$_current_ratio" high 1 && _score=$((_score+2))
	score "$_quick_ratio" high 1 && _score=$((_score+2))
	score "$_avg_revenue_growth" high 7 && ((_score++))
	score "$_profit_margin" high 15 && _score=$((_score+2))
	score "$_roe" high 15 && _score=$((_score+2))
	printf '%s:%d\n' "${_t^^}" "$_score"
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
main "$ticker"
