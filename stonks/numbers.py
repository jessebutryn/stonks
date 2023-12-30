from currency_converter import CurrencyConverter

def exchange_currency(value, rate):
    try:

        if rate == 1:
            return value
        
        exchanged_value = value * rate

        return exchanged_value
    
    except (ValueError, TypeError):
        return 'NaN'
    
def get_rate(from_currency):

    fallback_rates = {
        'KRW': 0.000766,
        'COP': 0.00026,
        'TWD': 0.03,
        'ARS': 0.0012,
        'CLP': 0.0011,
        'EGP': 0.03,
        'PEN': 0.27,
        'VND': 0.000041,
    }

    if from_currency == 'USD':
        return 1
    
    if not isinstance(from_currency, str) or len(from_currency) != 3:
        raise ValueError("The 'from_currency' parameter must be a 3-letter currency code.")
    
    to_currency = 'USD'
    value = 100

    try:
        # Perform currency conversion using the ExchangeRate-API backend
        c = CurrencyConverter()
        result = c.convert(value, from_currency, to_currency)
        rate = result / value
        return rate
    except Exception as e:
        # If the currency is in the fallback_rates dictionary, use the fallback rate
        if from_currency in fallback_rates:
            return fallback_rates[from_currency]
        else:
            # Handle other exceptions
            print(f"An error occurred: {e}")
            return None

def format_currency(value):
    # Convert long currency values into a more human readable format.  This is
    # accomplished by setting an object of suffixes K, M, B, T, and Q.  If you
    # can divide the number by 1000 use suffix K, if you can divide it by 1000
    # again use suffix M, repeat until you can no longer divide by 1000
    try:
        if str(value).endswith('*'):
            ending = '*'
            value = str(value).rstrip('*')
        else:
            ending = ''

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
        
        return f'{sign}{formatted_value}{suffixes[order_of_magnitude]}{ending}'
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
