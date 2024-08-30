import unittest
import json
from unittest.mock import mock_open, patch
from skills.planning.operator.operator import Operator  # Replace with the correct import path


class TestOperator(unittest.TestCase):

    def test_operator_initialization(self):
        name = "paint-ceiling"
        preconditions = ["On(Robot, Ladder)", "¬Dry(Ceiling)"]
        postconditions = ["Painted(Ceiling)", "Dry(Ceiling)"]

        operator = Operator(name, preconditions, postconditions)

        self.assertEqual(operator.name, name)
        self.assertEqual(operator.preconditions, preconditions)
        self.assertEqual(operator.postconditions, postconditions)

    def test_operator_initialization_with_empty_conditions(self):
        name = "climb-ladder"
        preconditions = []
        postconditions = ["On(Robot, Ladder)"]

        operator = Operator(name, preconditions, postconditions)

        self.assertEqual(operator.name, name)
        self.assertEqual(operator.preconditions, preconditions)
        self.assertEqual(operator.postconditions, postconditions)

    def test_operator_repr(self):
        operator = Operator("paint-ceiling", ["On(Robot, Ladder)"], ["Painted(Ceiling)"])
        expected_repr = "Operator(name=paint-ceiling, preconditions=['On(Robot, Ladder)'], postconditions=['Painted(Ceiling)'])"
        self.assertEqual(repr(operator), expected_repr)


class TestReadOperatorsFromJson(unittest.TestCase):

    @patch('builtins.open', new_callable=mock_open, read_data='''
    [
        {
            "name": "climb-ladder",
            "preconditions": ["On(Robot, Floor)"],
            "postconditions": ["On(Robot, Ladder)"]
        },
        {
            "name": "paint-ceiling",
            "preconditions": ["On(Robot, Ladder)", "¬Dry(Ceiling)"],
            "postconditions": ["Painted(Ceiling)", "Dry(Ceiling)"]
        }
    ]
    ''')
    def test_read_operators_from_json(self, mock_file):
        file_path = "mock/path/to/operators.json"
        operators = read_operators_from_json(file_path)

        self.assertEqual(len(operators), 2)
        self.assertIn("climb-ladder", operators)
        self.assertIn("paint-ceiling", operators)

        climb_ladder_op = operators["climb-ladder"]
        paint_ceiling_op = operators["paint-ceiling"]

        self.assertEqual(climb_ladder_op.name, "climb-ladder")
        self.assertEqual(climb_ladder_op.preconditions, ["On(Robot, Floor)"])
        self.assertEqual(climb_ladder_op.postconditions, ["On(Robot, Ladder)"])

        self.assertEqual(paint_ceiling_op.name, "paint-ceiling")
        self.assertEqual(paint_ceiling_op.preconditions, ["On(Robot, Ladder)", "¬Dry(Ceiling)"])
        self.assertEqual(paint_ceiling_op.postconditions, ["Painted(Ceiling)", "Dry(Ceiling)"])

    @patch('builtins.open', new_callable=mock_open, read_data="[]")
    def test_read_operators_from_empty_json(self, mock_file):
        file_path = "mock/path/to/operators.json"
        operators = read_operators_from_json(file_path)
        self.assertEqual(len(operators), 0)

    @patch('builtins.open', new_callable=mock_open, read_data="invalid json")
    def test_read_operators_from_invalid_json(self, mock_file):
        file_path = "mock/path/to/operators.json"
        with self.assertRaises(json.JSONDecodeError):
            read_operators_from_json(file_path)