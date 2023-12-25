import re

def colorize(value, condition, low_threshold, high_threshold, use_color):
    if not use_color:
        return str(value)

    value_str = str(value)

    if value_str.lower() == 'nan':
        return value_str

    suffix = value_str[-1] if not value_str[-1].isdigit() else None
    value_str = value_str[:-1] if suffix else value_str

    value_float = float(value_str)

    if condition == "high":
        if value_float > high_threshold:
            color = '\033[92m'  # Green
        elif low_threshold <= value_float <= high_threshold:
            color = '\033[93m'  # Yellow
        else:
            color = '\033[91m'  # Red
    elif condition == "low":
        if value_float > high_threshold:
            color = '\033[91m'  # Red
        elif low_threshold <= value_float <= high_threshold:
            color = '\033[93m'  # Yellow
        else:
            color = '\033[92m'  # Green
    else:
        color = '\033[0m'  # Default color

    formatted_value = f"{value_float:.2f}"

    reset_color = '\033[0m'

    return f"{color}{formatted_value}{suffix}{reset_color}" if suffix else f"{color}{formatted_value}{reset_color}"
    
def remove_color(value):
    if isinstance(value, str):
        ansi_escape = re.compile(r'\033\[[0-9;]*[mG]')
        return ansi_escape.sub('', value)
    else:
        return value

def remove_colors_from_table(table):
    cleaned_table = {key: remove_color(value) for key, value in table.items()}
    return cleaned_table
