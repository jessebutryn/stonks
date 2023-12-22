#######################################
balance_metrics=(
	"Current Liabilities"
	"Total Debt"
	"Net Debt"
	"Total Assets"
	"Cash Cash Equivalents And Short Term Investments"
	"Invested Capital"
	"Working Capital"
)
income_metrics=(
	"Total Revenue"
	"Cost Of Revenue"
	"Operating Expense"
	"Operating Income"
	"Gross Profit"
	"Net Income"
)
#######################################
to_json () {
	perl -MJSON::PP -ae '
  if (/^(.*):$/) {$sheet = $1}
  elsif (/^\h+\d/) {$n = (@dates = @F)}
  elsif (/^(.*?)((?:\h+)\H+){$n}$/) {
    $i = -$n;
    $j{$sheet}->{$1} = {map {$_ => $F[$i++]} @dates}
  }
  END {print JSON::PP->new->pretty->encode(\%j)}' </dev/stdin
}

fetch_data () {
	local _ticker=$1
	local _sheet=$2
	"${0%/*}/get_data.py" "$_ticker" "$_sheet"
}

make_human () {
	local _num=${1%.*}
	local _length=${_num#-}
	_length=${#_length}
	if [[ ${_num,,} == nan ]]; then
		printf '-'
	elif [[ $human == false ]]; then
		printf '%d\n' "$_num"
	elif ((_length>=13)); then
		awk -vn="$_num" 'BEGIN{printf "%.2fT\n", n/1000000000000}'
	elif ((_length>=10)); then
		awk -vn="$_num" 'BEGIN{printf "%.2fB\n", n/1000000000}'
	elif ((_length>=7)); then
		awk -vn="$_num" 'BEGIN{printf "%.2fM\n", n/1000000}'
	elif ((_length>=4)); then
		awk -vn="$_num" 'BEGIN{printf "%.2fK\n", n/1000}'
	else
		printf '%.2f\n' "$_num"
	fi
}

print_values () {
	local _attr=$1
	local _data=$2
	local _obj=$(jq --arg attr "$_attr" '.[] | .[$attr]' <<<"$_data")
	local _res _values
	_res+=("$_attr")
	mapfile -t _dates < <(jq -r 'keys[]' <<<"$_obj" | sort -rd)
	for n in "${!_dates[@]}"; do
		d=${_dates[$n]}
		v=$(jq -r --arg date "$d" '.[$date]' <<<"$_obj")
		_res+=("$(make_human "$v")")
	done
	(IFS=,; echo "${_res[*]}")
}

is_number() {
	if [[ $1 =~ ^[+-]?[0-9]*\.?[0-9]+$ ]]; then
		return 0
	else
		return 1
	fi
}

is_negative () {
	local _num=$1
	if (( $(echo "$_num < 0" | bc -l) )); then
		return 0
	else
		return 1
	fi
}

get_values () {
	local _attr=$1
	local _data=$2
	local _obj=$(jq --arg attr "$_attr" '.[] | .[$attr]' <<<"$_data")
	local _dates _res _v
	mapfile -t _dates < <(jq -r 'keys[]' <<<"$_obj" | sort -rd)
	for d in "${_dates[@]}"; do
		jq -r --arg date "$d" '.[$date]' <<<"$_obj"
	done
}

trend2 () {
	local _data=("$@")
	for d in "${!_data[@]}"; do
		_v1=${_data[$d+1]}
		_v2=${_data[$d]}
		if is_number "$_v1" && is_number "$_v2"; then
			_res+=("$(awk -v old="$_v1" -v new="$_v2" 'BEGIN { change = ((new - old) / (old == 0 ? 1 : (old < 0 ? -old : old))) * 100; printf "%.2f%\n", change }')")
		else
			_res+=(-)
		fi
	done
	(IFS=,; echo "${_res[*]}")
}

trend () {
	local _attr=$1
	local _data=$2
	local _obj=$(jq --arg attr "$_attr" '.[] | .[$attr]' <<<"$_data")
	local _dates _res _m
	_res+=("${_attr} trend")
	mapfile -t _dates < <(jq -r 'keys[]' <<<"$_obj" | sort -rd)
	for n in "${!_dates[@]}"; do
		_m=$((n+1))
		_d1=${_dates[$_m]}
		_d2=${_dates[$n]}
		_v1=$(jq -r --arg date "$_d1" '.[$date]' <<<"$_obj")
		_v2=$(jq -r --arg date "$_d2" '.[$date]' <<<"$_obj")
		if is_number "$_v1" && is_number "$_v2"; then
			_res+=("$(awk -v old="$_v1" -v new="$_v2" 'BEGIN { change = ((new - old) / (old == 0 ? 1 : (old < 0 ? -old : old))) * 100; printf "%.2f%\n", change }')")
		else
			_res+=(-)
		fi
	done
	(IFS=,; echo "${_res[*]}")
}

avg_change () {
	local _values=$1
	local _count=$(awk -F, '{print NF}' <<<"$_values")
	local _avg=$(echo "($(echo "$_values" | tr ',' '+' | tr -d '%'))/3" | bc -l)
	printf '%.2f%%' "$_avg"
}
