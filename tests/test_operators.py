import unittest
import json
from unittest.mock import mock_open, patch
from skills.planning.operator.operator import Operator  # Replace with the correct import path
from skills.planning.operator.instances.robot_painting_operator import RobotPaintingOperator


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

    def test_get_precondition_for_reverse_search(self):
        # Test case where the precondition list includes 'On(Robot, ...)' conditions
        operator = RobotPaintingOperator(
            name="climb-ladder",
            preconditions=["On(Robot, Floor)", "Dry(Ceiling)", "Painted(Ceiling)"],
            postconditions=["On(Robot, Ladder)"]
        )

        result = operator._get_precondition_for_reverse_search()
        assert result == "On(Robot, Floor)", f"Expected 'On(Robot, Floor)', got {result}"

        # Test case where no 'On(Robot, ...)' conditions are present
        operator = RobotPaintingOperator(
            name="paint-ceiling",
            preconditions=["Dry(Ceiling)", "Painted(Ceiling)"],
            postconditions=["Painted(Ceiling)", "¬Dry(Ceiling)"]
        )

        result = operator._get_precondition_for_reverse_search()
        assert result == "", f"Expected '', got {result}"

        # Test case with a different 'On(Robot, ...)' condition
        operator = RobotPaintingOperator(
            name="descend-ladder",
            preconditions=["On(Robot, Ladder)", "Dry(Ladder)"],
            postconditions=["On(Robot, Floor)"]
        )

        result = operator._get_precondition_for_reverse_search()
        assert result == "On(Robot, Ladder)", f"Expected 'On(Robot, Ladder)', got {result}"

    def test_get_precondition_for_conflict_check(self):
        # Test case where the precondition list includes both 'Dry' and '¬Dry' conditions
        operator = RobotPaintingOperator(
            name="paint-ceiling",
            preconditions=["On(Robot, Floor)", "Dry(Ceiling)"],
            postconditions=["Painted(Ceiling)"]
        )

        result = operator._get_precondition_for_conflict_check()
        expected_result = "Dry(Ceiling)"
        assert result == expected_result, f"Expected '{expected_result}', got '{result}'"


