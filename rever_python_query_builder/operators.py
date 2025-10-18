from sqlalchemy import text


def op_in(column, criteria):
    return column.in_(criteria)


def op_array_contains(column, criteria):
    return text(f"ARRAY_CONTAINS({column}, '{criteria}')")


def op_array_not_contains(column, criteria):
    return text(f"NOT ARRAY_CONTAINS({column}, '{criteria}')")


def op_not_in(column, criteria):
    return ~column.in_(criteria)


def op_between(column, criteria):
    return text(f"{column} BETWEEN '{criteria[0]}' AND '{criteria[1]}'")


def op_is_null(column, _):
    return column.is_(None)


def op_is_not_null(column, _):
    return column.isnot(None)


def op_eq(column, criteria):
    return column == criteria


def op_neq(column, criteria):
    return column != criteria


def op_lt(column, criteria):
    return column < criteria


def op_lte(column, criteria):
    return text(f"{column} <= '{criteria}'")


def op_gt(column, criteria):
    return column > criteria


def op_gte(column, criteria):
    return text(f"{column} >= '{criteria}'")


OPERATORS = {
    'in': op_in,
    'array_contains': op_array_contains,
    'array_not_contains': op_array_not_contains,
    'not_in': op_not_in,
    'between': op_between,
    'is_null': op_is_null,
    'is_not_null': op_is_not_null,
    '=': op_eq,
    '!=': op_neq,
    '<': op_lt,
    '<=': op_lte,
    '>': op_gt,
    '>=': op_gte,
}
