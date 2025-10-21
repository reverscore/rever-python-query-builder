from typing import Literal, Optional
from typing import Any, List, TypedDict

OrderDirection = Literal['asc', 'desc']
WhereOperators = Literal[
    'in',
    'not_in',
    'between',
    'is_null',
    'is_not_null',
    '=',
    '!=',
    '<',
    '<=',
    '>',
    '>=',
]


class BaseFilters(TypedDict):
    organization_id: str


class Expression(TypedDict):
    field: str
    operator: str
    value: Any
    expressions: List['Expression']


class LocationFilters(TypedDict):
    sites: Optional[List[str]]
    tags: Optional[List[str]]
    country_codes: Optional[List[str]]
    site_groups: Optional[List[str]]
    tag_groups: Optional[List[str]]
