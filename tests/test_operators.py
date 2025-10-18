import unittest
from sqlalchemy import column
from rever_python_query_builder.operators import (
    op_in, op_array_contains, op_array_not_contains, op_not_in, op_between,
    op_is_null, op_is_not_null, op_eq, op_neq, op_lt, op_lte, op_gt, op_gte,
    OPERATORS,
)


def get_col():
    return column('x')


class TestOperators(unittest.TestCase):
    def test_op_in(self):
        col = get_col()
        expr = op_in(col, [1, 2])
        self.assertEqual(str(expr), 'x IN (:x_1, :x_2)')

    def test_op_array_contains(self):
        col = get_col()
        expr = op_array_contains(col, [1, 2])
        self.assertIn('ARRAY_CONTAINS', str(expr))

    def test_op_array_not_contains(self):
        col = get_col()
        expr = op_array_not_contains(col, [1, 2])
        self.assertIn('NOT ARRAY_CONTAINS', str(expr))

    def test_op_not_in(self):
        col = get_col()
        expr = op_not_in(col, [1, 2])
        self.assertTrue('NOT' in str(expr) or '~' in str(expr))

    def test_op_between(self):
        col = get_col()
        expr = op_between(col, [1, 2])
        self.assertIn('BETWEEN', str(expr))

    def test_op_is_null(self):
        col = get_col()
        expr = op_is_null(col, None)
        self.assertIn('IS NULL', str(expr))

    def test_op_is_not_null(self):
        col = get_col()
        expr = op_is_not_null(col, None)
        self.assertIn('IS NOT NULL', str(expr))

    def test_op_eq(self):
        col = get_col()
        expr = op_eq(col, 5)
        self.assertEqual(str(expr), 'x = :x_1')

    def test_op_neq(self):
        col = get_col()
        expr = op_neq(col, 5)
        self.assertEqual(str(expr), 'x != :x_1')

    def test_op_lt(self):
        col = get_col()
        expr = op_lt(col, 5)
        self.assertEqual(str(expr), 'x < :x_1')

    def test_op_lte(self):
        col = get_col()
        expr = op_lte(col, 5)
        self.assertIn('<=', str(expr))

    def test_op_gt(self):
        col = get_col()
        expr = op_gt(col, 5)
        self.assertEqual(str(expr), 'x > :x_1')

    def test_op_gte(self):
        col = get_col()
        expr = op_gte(col, 5)
        self.assertIn('>=', str(expr))

    def test_operators_dict(self):
        self.assertIn('in', OPERATORS)
        self.assertTrue(callable(OPERATORS['in']))
        self.assertIn('!=', OPERATORS)
        self.assertTrue(callable(OPERATORS['!=']))
