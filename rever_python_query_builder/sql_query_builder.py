
from typing import Any, Optional, Sequence

from sqlalchemy import (
    MetaData, Table, and_, func, or_, select, text
)
from sqlalchemy.engine import Engine
from sqlalchemy.sql.elements import ClauseElement
from sqlalchemy.sql.selectable import Select
from sqlalchemy.sql.schema import Table as SQLATable

from rever_python_query_builder.types import (
    OrderDirection, BaseFilters, WhereOperators, Expression, LocationFilters
)
from rever_python_query_builder.operators import OPERATORS
from rever_python_query_builder.constants import (
    common_supported_filters,
    order_mapping,
)


class SQLQueryBuilder:

    operators = OPERATORS

    order_mapping = order_mapping

    def __init__(self, schema: str, table_name: str, engine: Engine):
        self.table: SQLATable = Table(
                table_name,
                MetaData(),
                autoload_with=engine,
                schema=schema,
            )
        self.query: Select = select(self.table.columns)
        self.selected_columns: list[Any] = []

    def select(
        self,
        columns: Sequence[str] | str,
    ) -> 'SQLQueryBuilder':
        if columns == '*':
            columns_to_add = [
                col for col in self.table.columns
                if col not in self.selected_columns
            ]
            self.selected_columns.extend(columns_to_add)
        else:
            columns_to_add = [
                self.table.columns[col]
                for col in columns
                if self.table.columns[col] not in self.selected_columns
            ]
            self.selected_columns.extend(columns_to_add)
        self.query = self.query.with_only_columns(*self.selected_columns)
        return self

    def select_column(
        self,
        column: str,
        alias: Optional[str] = None,
    ) -> 'SQLQueryBuilder':
        col_obj = self.table.columns[column]
        if alias:
            col_obj = col_obj.label(alias)
        if col_obj not in self.selected_columns:
            self.selected_columns.append(col_obj)
        self.query = self.query.with_only_columns(*self.selected_columns)
        return self

    def where(
        self,
        field: str,
        operator: WhereOperators,
        filter_value: Any = None,
    ) -> 'SQLQueryBuilder':
        column = self.table.columns[field]
        condition_func = self.operators.get(operator)
        condition = condition_func(column, filter_value)
        self.query = self.query.where(condition)
        return self

    def or_where(
        self,
        expressions: list[Expression],
    ) -> 'SQLQueryBuilder':
        conditions = [
            self._build_expression(expression)
            for expression in expressions
        ]
        self.query = self.query.where(or_(*conditions))
        return self

    def and_where(
        self,
        expressions: list[Expression],
    ) -> 'SQLQueryBuilder':
        conditions = [
            self._build_expression(expression)
            for expression in expressions
        ]
        self.query = self.query.where(and_(*conditions))
        return self

    def complex_expression(
        self,
        expressions: Expression,
    ) -> 'SQLQueryBuilder':
        condition_expression = self._build_expression(expressions)
        self.query = self.query.where(condition_expression)
        return self

    def _build_expression(
        self,
        expression: Expression,
    ) -> ClauseElement:
        if 'field' in expression:
            condition_func = self.operators[expression.get('operator')]
            column = self.table.c[expression.get('field')]
            return condition_func(column, expression.get('value'))

        if 'expressions' in expression:
            sub_conditions = [
                self._build_expression(sub_cond)
                for sub_cond in expression.get('expressions')
            ]
            condition_func = {
                'and-expression': and_,
                'or-expression': or_,
            }[expression.get('operator')]
            return condition_func(*sub_conditions)

    def order_by(
        self,
        column: str,
        order: OrderDirection,
    ) -> 'SQLQueryBuilder':
        order_function = self.order_mapping[order]
        self.query = self.query.order_by(order_function(text(column)))
        return self

    def group_by(
        self,
        column: str,
    ) -> 'SQLQueryBuilder':
        self.query = self.query.group_by(self.table.c[column])
        return self

    def count(
        self,
        column: str,
        alias: Optional[str] = None,
    ) -> 'SQLQueryBuilder':
        select_column = func.count(text(column))
        if (alias):
            select_column = select_column.label(alias)
        if select_column not in self.selected_columns:
            self.selected_columns.append(select_column)
        self.query = self.query.with_only_columns(*self.selected_columns)
        return self

    def sum(
        self,
        column: str,
        alias: Optional[str] = None,
    ) -> 'SQLQueryBuilder':
        select_column = func.sum(text(column))
        if (alias):
            select_column = select_column.label(alias)
        if select_column not in self.selected_columns:
            self.selected_columns.append(select_column)
        self.query = self.query.with_only_columns(*self.selected_columns)
        return self

    def first(
        self,
        column: str,
        alias: Optional[str] = None,
    ) -> 'SQLQueryBuilder':
        select_column = func.first(text(column))

        if (alias):
            select_column = select_column.label(alias)
        if select_column not in self.selected_columns:
            self.selected_columns.append(select_column)

        self.query = self.query.with_only_columns(*self.selected_columns)
        return self

    def limit(
        self,
        limit_value: int,
    ) -> 'SQLQueryBuilder':
        self.query = self.query.limit(limit_value)
        return self

    def apply_base_filters(
        self,
        filters: BaseFilters,
    ) -> 'SQLQueryBuilder':
        organization_id = filters.get('organization_id')
        self.where('organization_id', '=', organization_id)
        return self

    def add_organization_filter(
        self,
        organization_id: str,
    ) -> 'SQLQueryBuilder':
        self.where('organization_id', '=', organization_id)
        return self

    def add_arrays_filter(
        self,
        column: str,
        array: list[Any],
    ) -> 'SQLQueryBuilder':
        self.query = self.query.where(
            func.arrays_overlap(self.table.c[column], func.array(*array)),
        )
        return self

    def average(
        self,
        column: str,
        alias: Optional[str] = None,
    ) -> 'SQLQueryBuilder':
        select_column = func.avg(text(column))
        if alias:
            select_column = select_column.label(alias)
        if select_column not in self.selected_columns:
            self.selected_columns.append(select_column)
        self.query = self.query.with_only_columns(*self.selected_columns)
        return self

    def add_location_filters(
        self,
        filters: LocationFilters,
        supported_filters: set[str] = common_supported_filters,
    ) -> 'SQLQueryBuilder':
        if filters['sites'] and 'site_id' in supported_filters:
            self.where('site_id', 'in', filters['sites'])
        if filters['sites'] and 'site_ids' in supported_filters:
            self.add_arrays_filter('site_ids', filters['sites'])
        if filters['tags'] and 'tag_ids' in supported_filters:
            self.add_arrays_filter('tag_ids', filters['tags'])
        if filters['country_codes'] and 'country_codes' in supported_filters:
            self.add_arrays_filter('country_codes', filters['country_codes'])
        if filters['site_groups'] and 'site_group_ids' in supported_filters:
            self.add_arrays_filter('site_group_ids', filters['site_groups'])
        if filters['tag_groups'] and 'tag_group_ids' in supported_filters:
            self.add_arrays_filter('tag_group_ids', filters['tag_groups'])
        return self
