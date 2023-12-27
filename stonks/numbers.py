def format_currency(value):
    # Convert long currency values into a more human readable format.  This is
    # accomplished by setting an object of suffixes K, M, B, T, and Q.  If you
    # can divide the number by 1000 use suffix K, if you can divide it by 1000
    # again use suffix M, repeat until you can no longer divide by 1000
    try:
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
    except (ValueError, TypeError):
        return 0

def extract_numeric_value(value, default):
    # In the event we need to get the raw number that was converted to human
    # readable currency format this function will strip the currency suffix.
    try:
        if isinstance(value, str):
            value = value.rstrip('%').rstrip('M').rstrip('B').rstrip('T').rstrip('Q').rstrip('K').rstrip('*')
            
        return float(value)

    except (ValueError, TypeError):
        return default
