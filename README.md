# rever-python-query-builder

[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/SQLAlchemy)](https://pypi.org/project/SQLAlchemy/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Python library for building complex SQL queries using SQLAlchemy.

---

## Features

- Modular, chainable query construction
- Advanced filtering: AND, OR, nested expressions
- Column selection, aliasing, and aggregation
- Array and location-based filters
- Ordering, grouping, and limiting
- Organization and base filters for multi-tenant apps
- Fully type-annotated and flake8-compliant
- Easily extensible for custom operators and logic

---

## Installation

```bash
pip install git+https://github.com/reverscore/rever-python-query-builder.git
```

**Requirements:**

- Python 3.7+
- SQLAlchemy >=1.4

---

## Quick Start

```python
from rever_python_query_builder.query_builder import SQLQueryBuilder
from sqlalchemy import create_engine

engine = create_engine('postgresql://user:password@localhost/dbname')
qb = QueryBuilder(schema='public', table_name='my_table', engine=engine)
qb.select(['id', 'name']).where('id', '=', 1)
print(str(qb.query))
```

---

## Advanced Usage

### Chaining and Composition

```python
qb.select(['id']) \
  .where('active', '=', True) \
  .order_by('created_at', 'desc') \
  .limit(5)
```

### Complex Filtering

```python
qb.and_where([
    {'field': 'age', 'operator': '>', 'value': 18},
    {'field': 'country', 'operator': '=', 'value': 'US'},
])

expr = {
    'operator': 'and-expression',
    'expressions': [
        {'field': 'id', 'operator': 'in', 'value': [1, 2]},
        {
            'operator': 'or-expression',
            'expressions': [
                {'field': 'status', 'operator': '=', 'value': 'active'},
                {'field': 'status', 'operator': '=', 'value': 'pending'},
            ],
        },
    ],
}
qb.complex_expression(expr)
```

### Aggregation and Grouping

```python
qb.count('id', alias='total')
qb.sum('amount', alias='total_amount')
qb.average('score', alias='avg_score')
qb.group_by('country')
```

### Array and Location Filters

```python
qb.add_arrays_filter('tags', ['tag1', 'tag2'])
location_filters = {
    'sites': ['site1', 'site2'],
    'tags': ['tag1'],
    'country_codes': ['US'],
    'site_groups': [],
    'tag_groups': [],
}
qb.add_location_filters(location_filters)
```

### Organization Filters

```python
qb.apply_base_filters('org_id_123')
qb.add_organization_filter('org_id_123')
```

---

## Output and Execution

```python
print(str(qb.query))

with engine.connect() as conn:
    result = conn.execute(qb.query)
    rows = result.fetchall()
```

---

## Extensibility

- Add custom operators via the `operators` attribute
- Extend with new filter logic or query patterns
- Integrate with any SQLAlchemy-supported database

---

## Project Links

- [GitHub Repository](https://github.com/reverscore/rever-python-query-builder)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)

---

## License

MIT License
