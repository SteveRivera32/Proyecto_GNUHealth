from tabulate import tabulate
from datetime import date, datetime
import pandas as pd
import math

def normalize_value(val):
    if pd.isna(val) or val is None:
        return ""
    elif isinstance(val, (datetime, date)):
        return val.isoformat()
    elif isinstance(val, pd.Timestamp):
        return val.isoformat()
    elif isinstance(val, float) and math.isnan(val):
        return ""
    else:
        return str(val)

def format_json_to_table(data):
    normalized_data = [
        {k: normalize_value(v) for k, v in entry.items()} for entry in data
    ]
    return tabulate(normalized_data, headers="keys", tablefmt="github")

