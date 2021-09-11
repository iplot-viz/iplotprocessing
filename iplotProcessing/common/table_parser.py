def get_value(row, col_name: str, type_func=str):
    if row[col_name] is None:
        return type_func()
    return type_func(row[col_name])
