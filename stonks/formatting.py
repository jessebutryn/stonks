import re
import pandas as pd

# def colorize(value, condition, low_threshold, high_threshold, use_color):
#     # This function will take a numeric value and colorize it either red, yellow, 
#     # or green depending on whether that number is determined to be "good", "neutral",
#     # or "bad". 
#     #
#     # You provide the following parameters to the function:
#     # value             =   The numerical value to be colorized
#     #                       (supports percentages and numbers with currency suffixes ('K','M','B',etc))
#     # condition         =   'low' or 'high'
#     #                       If condition is 'low' being less than threshold is green
#     #                       If condition is 'high' being greater than threshold is green
#     # low_threshold     =   The numerical value for low threshold
#     # high_threshold    =   The numerical value for high threshold
#     # use_color         =   This carries over the use_color parameter from main.  If --no_color
#     #                       is specified this function will simply return the value as is.
#     #
#     value_str = str(value)
#     # If the value has a non digit suffix store it and remove it
#     # suffix = value_str[-1] if not value_str[-1].isdigit() else None
#     # value_str = value_str[:-1] if suffix else value_str

#     suffix = ''.join([char for char in reversed(value_str) if not char.isdigit() and char != '.'])[::-1]
#     value_str = value_str[:-len(suffix)] if suffix else value_str

#     value_num = pd.to_numeric(value_str, errors='coerce')
    
#     if pd.notna(value_num):
#         # Convert value to float
#         value_float = float(value_num)
#     else:
#         return value
    
#     if not use_color:
#         return value

#     # Make condition determinations
#     if condition == "high":
#         if value_float > high_threshold:
#             color = '\033[92m'  # Green
#         elif low_threshold <= value_float <= high_threshold:
#             color = '\033[93m'  # Yellow
#         else:
#             color = '\033[91m'  # Red
#     elif condition == "low":
#         if value_float > high_threshold:
#             color = '\033[91m'  # Red
#         elif low_threshold <= value_float <= high_threshold:
#             color = '\033[93m'  # Yellow
#         else:
#             color = '\033[92m'  # Green
#     else:
#         color = '\033[0m'  # Default color

#     # Convert value to a 2 digit float
#     formatted_value = f"{value_float:.2f}"

#     reset_color = '\033[0m'

#     # Print value with color.  If there is a suffix add it back on.
#     return f"{color}{formatted_value}{suffix}{reset_color}" if suffix else f"{color}{formatted_value}{reset_color}"

def colorize(value, condition, low_threshold, high_threshold, use_color):
    # ... (rest of the function remains unchanged)

    value_str = str(value)

    # Check if the value is negative and store the sign
    is_negative = value_str.startswith('-')
    value_str = value_str[1:] if is_negative else value_str

    # If the value has a non-digit suffix, store it and remove it
    suffix = ''.join([char for char in reversed(value_str) if not char.isdigit() and char != '.'])[::-1]
    value_str = value_str[:-len(suffix)] if suffix else value_str

    # Special handling for percent sign
    percent_sign = '%' if value_str.endswith('%') else ''
    value_str = value_str.rstrip('%')

    # Extract numeric part of the value and convert to float
    value_num = pd.to_numeric(value_str, errors='coerce')
    
    if pd.notna(value_num):
        value_float = float(value_num)
    else:
        return value

    if not use_color:
        return value

    # Make condition determinations
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

    # Convert value to a 2 digit float
    formatted_value = f"{value_float:.2f}"

    reset_color = '\033[0m'

    # Add the negative sign, suffix, and percent sign back if they were present
    formatted_value = f"-{value_float:.2f}" + suffix + percent_sign if is_negative else f"{value_float:.2f}" + suffix + percent_sign

    # ... (rest of the function remains unchanged)

    # Print value with color. If there is a suffix, percent sign, or negative sign, add them back on.
    return f"{color}{formatted_value}{reset_color}"
    
def remove_color(value):
    # Remove all color values from input.
    if isinstance(value, str):
        ansi_escape = re.compile(r'\033\[[0-9;]*[mG]')
        return ansi_escape.sub('', value)
    else:
        return value

def remove_colors_from_table(table):
    # Remove all color values from the inputted table.
    cleaned_table = {key: remove_color(value) for key, value in table.items()}
    return cleaned_table

def parse_info(value):
    # Custom function to parse multiple values for --info
    return value.split()
