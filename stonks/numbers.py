def format_currency(value):
    value = float(value)
    
    sign = '-' if value < 0 else ''
    
    abs_value = abs(value)

    suffixes = ['', 'K', 'M', 'B', 'T', 'Q']
    order_of_magnitude = 0
    
    while abs_value >= 1000 and order_of_magnitude < len(suffixes) - 1:
        abs_value /= 1000.0
        order_of_magnitude += 1
    
    formatted_value = f'{abs_value:.2f}'
    
    if '.' in formatted_value and formatted_value.endswith('00'):
        formatted_value = formatted_value[:-3]
    
    return f'{sign}{formatted_value}{suffixes[order_of_magnitude]}'

def extract_numeric_value(value):
    if isinstance(value, str):
        value = value.rstrip('%').rstrip('M').rstrip('B').rstrip('T').rstrip('Q').rstrip('K')

    try:
        return float(value)
    except ValueError:
        return None
