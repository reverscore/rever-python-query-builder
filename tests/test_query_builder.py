import unittest
from unittest.mock import Mock, patch

from ordered_set import OrderedSet
from sqlalchemy import (
    Column,
    Integer,
    MetaData,
    String,
    Table,
    create_engine,
    select,
)
from rever_python_query_builder.sql_query_builder import SQLQueryBuilder


def mock_query_builder_init(schema, table_name, metadata, mock_table):
    with patch.object(
        SQLQueryBuilder,
        '__init__',
        lambda _, schema, table_name, metadata: None,
    ):
        query_builder = SQLQueryBuilder(schema, table_name, metadata)
        query_builder.table = mock_table
        query_builder.query = select([mock_table])
        query_builder.selected_columns = OrderedSet()
    return query_builder


def compile_query(query):
    return str(query.compile(compile_kwargs={'literal_binds': True}))


class TestSQLQueryBuilder(unittest.TestCase):  # noqa: WPS214

    def setUp(self):
        self.schema = 'test_schema'
        self.table_name = 'test_table'

        self.metadata = MetaData()
        self.engine = create_engine('sqlite:///:memory:')

        self.metadata.bind = self.engine

        self.mock_table = Table(
            self.table_name,
            self.metadata,
            Column('id', Integer, primary_key=True),
            Column('name', String),
            Column('value', Integer),
            Column('organization_id', String),
            Column('tags', String),
            Column('site_id', String),
            Column('tag_ids', String),
            Column('country_codes', String),
            Column('site_group_ids', String),
            Column('tag_group_ids', String),
        )

        self.metadata.create_all(self.engine)
        self.mocked_query_builder = mock_query_builder_init(
            self.schema,
            self.table_name,
            self.metadata,
            self.mock_table,
        )

    def test_add_arrays_filter(self):
        query_builder = self.mocked_query_builder
        query_builder.add_arrays_filter('tags', ['tag1', 'tag2'])
        query = compile_query(query_builder.query)  # noqa: WPS204
        expected_condition = (
            "arrays_overlap(test_table.tags, array('tag1', 'tag2'))"
        )
        self.assertIn(expected_condition, query)

    def test_add_location_filters(self):
        query_builder = self.mocked_query_builder
        report_input = Mock()
        report_input.sites = ['site1', 'site2']
        report_input.tags = ['tag1', 'tag2']
        report_input.country_codes = ['US']
        report_input.site_groups = []
        report_input.tag_groups = []

        query_builder.add_location_filters(report_input)
        query = compile_query(query_builder.query)
        self.assertIn("test_table.site_id IN ('site1', 'site2')", query)
        self.assertIn(
            "arrays_overlap(test_table.tag_ids, array('tag1', 'tag2'))",
            query,
        )
        self.assertIn(
            "arrays_overlap(test_table.country_codes, array('US'))",
            query,
        )

    def test_select(self):
        query_builder = self.mocked_query_builder
        query_builder.select(['id', 'name'])
        query = compile_query(query_builder.query)
        self.assertIn('SELECT id, name', query)

    def test_select_empty(self):
        query_builder = self.mocked_query_builder
        query_builder.select([])
        query = compile_query(query_builder.query)
        self.assertIn('SELECT', query)

    def test_select_star(self):
        query_builder = self.mocked_query_builder
        query_builder.select('*')
        query = compile_query(query_builder.query)
        self.assertIn('SELECT', query)

    def test_select_duplicate(self):
        query_builder = self.mocked_query_builder
        query_builder.select(['id', 'id'])
        query = compile_query(query_builder.query)
        self.assertIn('id', query)

    def test_select_chain(self):
        query_builder = self.mocked_query_builder
        result = query_builder.select(['id']).select(['name'])
        self.assertIsInstance(result, SQLQueryBuilder)

    def test_select_column(self):
        query_builder = self.mocked_query_builder
        query_builder.select_column('id', 'identifier')
        query = compile_query(query_builder.query)
        self.assertIn('id AS identifier', query)

    def test_select_column_none_alias(self):
        query_builder = self.mocked_query_builder
        query_builder.select_column('id', None)
        query = compile_query(query_builder.query)
        self.assertIn('id', query)

    def test_select_column_duplicate(self):
        query_builder = self.mocked_query_builder
        query_builder.select_column('id')
        query_builder.select_column('id')
        query = compile_query(query_builder.query)
        self.assertIn('id', query)

    def test_where(self):
        query_builder = self.mocked_query_builder
        query_builder.where('name', '=', 'test')
        query = compile_query(query_builder.query)
        self.assertIn("test_table.name = 'test'", query)

    def test_where_in(self):
        query_builder = self.mocked_query_builder
        query_builder.where('id', 'in', [1, 2])
        query = compile_query(query_builder.query)
        self.assertIn('IN', query)

    def test_where_is_null(self):
        query_builder = self.mocked_query_builder
        query_builder.where('name', 'is_null')
        query = compile_query(query_builder.query)
        self.assertIn('IS NULL', query)

    def test_where_chain(self):
        query_builder = self.mocked_query_builder
        result = query_builder.where('id', '=', 1).where('name', '=', 'A')
        self.assertIsInstance(result, SQLQueryBuilder)

    def test_or_where(self):
        query_builder = self.mocked_query_builder
        expressions = [
            {'field': 'name', 'operator': '=', 'value': 'test1'},
            {'field': 'name', 'operator': '=', 'value': 'test2'},
        ]
        report_input = Mock()
        report_input.organization_id = 'org123'

        query_builder.apply_base_filters(report_input)
        query_builder.or_where(expressions)
        query = compile_query(query_builder.query)
        print(query)
        self.assertIn(
            "(test_table.name = 'test1' OR test_table.name = 'test2')",
            query,
        )

    def test_or_where_empty(self):
        query_builder = self.mocked_query_builder
        query_builder.or_where([])
        query = compile_query(query_builder.query)
        self.assertIn('SELECT', query)

    def test_and_where(self):
        query_builder = self.mocked_query_builder
        expressions = [
            {'field': 'name', 'operator': '=', 'value': 'test1'},
            {'field': 'value', 'operator': '>', 'value': 10},
        ]
        report_input = Mock()
        report_input.organization_id = 'org123'

        query_builder.apply_base_filters(report_input)
        query_builder.and_where(expressions)
        query = compile_query(query_builder.query)
        print(query)
        self.assertIn(
            "test_table.name = 'test1' AND test_table.value > 10",
            query,
        )

    def test_and_where_empty(self):
        query_builder = self.mocked_query_builder
        query_builder.and_where([])
        query = compile_query(query_builder.query)
        self.assertIn('SELECT', query)

    def test_complex_expression_and(self):
        query_builder = self.mocked_query_builder
        expr = {
            'operator': 'and-expression',
            'expressions': [
                {'field': 'id', 'operator': '=', 'value': 1},
                {'field': 'name', 'operator': '=', 'value': 'A'},
            ],
        }
        query_builder.complex_expression(expr)
        query = compile_query(query_builder.query)
        self.assertIn('AND', query)

    def test_complex_expression_or(self):
        query_builder = self.mocked_query_builder
        expr = {
            'operator': 'or-expression',
            'expressions': [
                {'field': 'id', 'operator': '=', 'value': 1},
                {'field': 'name', 'operator': '=', 'value': 'A'},
            ],
        }
        query_builder.complex_expression(expr)
        query = compile_query(query_builder.query)
        self.assertIn('OR', query)

    def test_order_by(self):
        query_builder = self.mocked_query_builder
        query_builder.order_by('name', 'asc')
        query = compile_query(query_builder.query)
        self.assertIn('ORDER BY name ASC', query)

    def test_order_by_desc(self):
        query_builder = self.mocked_query_builder
        query_builder.order_by('id', 'desc')
        query = compile_query(query_builder.query)
        self.assertIn('DESC', query)

    def test_group_by(self):
        query_builder = self.mocked_query_builder
        query_builder.group_by('name')
        query = compile_query(query_builder.query)
        self.assertIn('GROUP BY test_table.name', query)

    def test_group_by_multiple(self):
        query_builder = self.mocked_query_builder
        query_builder.group_by('id')
        query_builder.group_by('name')
        query = compile_query(query_builder.query)
        self.assertIn('GROUP BY', query)

    def test_count(self):
        query_builder = self.mocked_query_builder
        query_builder.count('id', 'total')
        query = compile_query(query_builder.query)
        self.assertIn('count(id) AS total', query)

    def test_count_no_alias(self):
        query_builder = self.mocked_query_builder
        query_builder.count('id')
        query = compile_query(query_builder.query)
        self.assertIn('count(id)', query)

    def test_sum(self):
        query_builder = self.mocked_query_builder
        query_builder.sum('value', 'total_value')
        query = compile_query(query_builder.query)
        self.assertIn('sum(value) AS total_value', query)

    def test_sum_no_alias(self):
        query_builder = self.mocked_query_builder
        query_builder.sum('value')
        query = compile_query(query_builder.query)
        self.assertIn('sum(value)', query)

    def test_limit(self):
        query_builder = self.mocked_query_builder
        query_builder.limit(10)
        query = compile_query(query_builder.query)
        self.assertIn('LIMIT 10', query)

    def test_limit_zero(self):
        query_builder = self.mocked_query_builder
        query_builder.limit(0)
        query = compile_query(query_builder.query)
        self.assertIn('LIMIT 0', query)

    def test_average(self):
        query_builder = self.mocked_query_builder
        query_builder.average('value')
        query = compile_query(query_builder.query)
        self.assertIn('avg(value)', query)

    def test_average_with_alias(self):
        query_builder = self.mocked_query_builder
        query_builder.average('value', 'avg_value')
        query = compile_query(query_builder.query)
        self.assertIn('avg(value) AS avg_value', query)

    def test_apply_base_filters(self):
        query_builder = self.mocked_query_builder
        report_input = Mock()
        report_input.organization_id = 'org123'
        query_builder.apply_base_filters(report_input)
        query = compile_query(query_builder.query)
        self.assertIn(
            "test_table.organization_id = 'org123'",
            query,
        )
