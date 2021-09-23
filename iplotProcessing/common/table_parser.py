import numpy as np
from iplotLogging import setupLogger as sl

logger = sl.get_logger(__name__, level="INFO")

def str_to_arr(value: str):
    if value is None:
        return None
    else:
        str_list = [e.strip() for e in value.split(',')]
        for v in reversed(str_list):
            if v == '':
                str_list.pop(str_list.index(v))
        return str_list if len(str_list) else None

def get_value(row, col_name: str, type_func=str):
    v = row[col_name]
    if type_func == bool and v not in ['1', 1, 'True', 'true']:
        v = ''
    if v is None:
        return type_func()
    try:
        return type_func(v)
    except ValueError:
        return type_func()

# str.isnumeric() does not work for negative numbers
def is_numeric(val):
    try:
        float(val)
    except:
        return False
    else:
        return True


# TODO: Check for 0 and pass it as number (it is prbably cheked fot rue/false)
# TODO: Is pulse number is overrider we discard start_time and end_time
# TODO: Check if overriding any value at row level resets all values from timerangeselector
# TODO: Use min/max from all plots when sharing x axis
def parse_timestamp(value):
    if isinstance(value, str):
        try:
            if is_numeric(value):
                return int(value) if float(value) > 10**15 else float(value)
            else:
                return int(np.datetime64(value, 'ns'))
        except:
            if len(value) > 0:
                logger.error(
                    f"Unable to parse string '{value}' as timestamp")
            pass

    return None