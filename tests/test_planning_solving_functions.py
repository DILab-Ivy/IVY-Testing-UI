import unittest
from unittest.mock import patch, MagicMock
from skills.planning.planner.instances.robot_painting_planner import RobotPaintingPlanner
from skills.planning.state.instances.robot_painting_state import RobotPaintingState, RobotPosition, Status
from skills.planning.operator.operator import Operator
from skills.planning.planning_solving_functions import _get_planner, _get_state_object, apply_operator, create_plan, handle_create_plan, handle_apply_operator


class TestPlanningModule(unittest.TestCase):

    def test_get_planner_robot(self):
        """Test that the correct planner is returned for 'robot'."""
        planner = _get_planner('robot')
        self.assertIsInstance(planner, RobotPaintingPlanner)

    def test_get_planner_invalid_type(self):
        """Test that ValueError is raised for an unsupported problem type."""
        with self.assertRaises(ValueError):
            _get_planner('unknown_type')

    def test_get_state_object_robot(self):
        """Test that the correct state object is returned for 'robot'."""
        state = _get_state_object('robot', ["On(Robot, Floor)", "Painted(Ceiling)", "Dry(Ladder)"])
        self.assertIsInstance(state, RobotPaintingState)
        self.assertEqual(state.robot_position, RobotPosition.ON_FLOOR)
        self.assertIn(Status.PAINTED, state.ceiling_status)
        self.assertIn(Status.DRY, state.ladder_status)

    def test_get_state_object_invalid_type(self):
        """Test that ValueError is raised for an unsupported problem type in state object creation."""
        with self.assertRaises(ValueError):
            _get_state_object('unknown_type', ["On(Robot, Floor)"])

    def test_apply_operator_valid_operator(self):
        """Test that the operator is applied correctly to the state."""
        start_state_conditions = ["On(Robot, Floor)", "Dry(Ceiling)", "Dry(Ladder)"]
        operator = "paint-ladder"
        result = apply_operator(start_state_conditions, operator, problem_type='robot')
        expected_result = "The result of applying the 'paint-ladder' operator to start state 'On(Robot, Floor) ^ Dry(Ceiling) ^ Dry(Ladder)' is the resulting state 'On(Robot, Floor) ^ Dry(Ceiling) ^ Dry(Ladder)'"
        self.assertEqual(expected_result, result)

    def test_apply_operator_valid_operator_cant_be_applied(self):
        """Test that the operator is applied correctly to the state."""
        start_state_conditions = ["On(Robot, Floor)", "Dry(Ceiling)", "Dry(Ladder)"]
        operator = "paint-ceiling"
        result = apply_operator(start_state_conditions, operator, problem_type='robot')
        expected_result = "The provided operator 'paint-ceiling' cannot be applied to start state 'On(Robot, Floor) ^ Dry(Ceiling) ^ Dry(Ladder)' for the following reason: Precondition 'On(Robot, Ladder)' is not met."
        self.assertEqual(expected_result, result)

    def test_apply_operator_invalid_operator(self):
        """Test error handling for an invalid operator."""
        start_state_conditions = ["On(Robot, Floor)", "Dry(Ceiling)", "Dry(Ladder)"]
        operator = "invalid-operator"
        result = apply_operator(start_state_conditions, operator, problem_type='robot')
        self.assertIn("Error: Operator not valid for robot", result)

    def test_apply_operator_invalid_problem_type(self):
        """Test error handling for an unsupported problem type."""
        start_state_conditions = ["On(Robot, Floor)", "Dry(Ceiling)", "Dry(Ladder)"]
        operator = "paint-ceiling"
        with self.assertRaises(ValueError):
            apply_operator(start_state_conditions, operator, problem_type='unknown')

    def test_create_plan_valid(self):
        """Test that a valid plan is created for the given start and goal state."""
        start_state_conditions = ["On(Robot, Floor)", "Dry(Ceiling)", "Dry(Ladder)"]
        goal_state_conditions = ["Painted(Ladder)", "Painted(Ceiling)"]
        result = create_plan(start_state_conditions, goal_state_conditions, problem_type='robot')
        self.assertIsInstance(result, str)  # Assuming the function returns a string representation of the plan

    def test_create_plan_valid_single_goal(self):
        """Test that a valid plan is created for the given start and goal state."""
        start_state_conditions = ["On(Robot, Floor)", "Dry(Ceiling)", "Dry(Ladder)"]
        goal_state_conditions = ["Painted(Ceiling)"]
        result = create_plan(start_state_conditions, goal_state_conditions, problem_type='robot')
        self.assertIsInstance(result, str)

    # TODO: implement when multiple problem_type handling added
    # def test_create_plan_invalid_problem_type(self):
    #     """Test error handling for create_plan with unsupported problem type."""
    #     start_state_conditions = ["On(Robot, Floor)", "Dry(Ceiling)", "Dry(Ladder)"]
    #     goal_state_conditions = ["Painted(Ladder)", "Painted(Ceiling)"]
    #     with self.assertRaises(ValueError):
    #         create_plan(start_state_conditions, goal_state_conditions, problem_type='unknown')

    def test_handle_apply_operator_missing_args(self):
        tool = MagicMock()
        tool.id = "123"
        tool.function.arguments = "{}"
        tool_outputs = []
        handle_apply_operator(tool, tool_outputs)
        self.assertTrue(any("Error: MissingArguments - No arguments provided" in output["output"] for output in tool_outputs))

    def test_handle_create_plan_missing_args(self):
        tool = MagicMock()
        tool.id = "123"
        tool.function.arguments = "{}"
        tool_outputs = []
        handle_create_plan(tool, tool_outputs)
        self.assertTrue(any("Error: MissingArguments - No arguments provided" in output["output"] for output in tool_outputs))

    def test_handle_apply_operator_invalid_start_conditions_format(self):
        tool = MagicMock()
        tool.id = "123"
        tool.function.arguments = "{'start_conditions': 'On(Robot, Floor)', 'operator': 'climb-ladder'}"  # Invalid format: should be a list
        tool_outputs = []
        handle_apply_operator(tool, tool_outputs)
        self.assertTrue(any("Invalid format for 'start_conditions'" in output["output"] for output in tool_outputs))

    def test_handle_apply_operator_invalid_operator_format(self):
        tool = MagicMock()
        tool.id = "123"
        tool.function.arguments = "{'start_conditions': ['On(Robot, Floor)'], 'operator': ['climb-ladder']}"  # Invalid format: operator should be a string
        tool_outputs = []
        handle_apply_operator(tool, tool_outputs)
        self.assertTrue(any("Invalid format for 'operator'" in output["output"] for output in tool_outputs))

    def test_handle_create_plan_invalid_start_conditions_format(self):
        tool = MagicMock()
        tool.id = "123"
        tool.function.arguments = "{'start_conditions': 'On(Robot, Floor)', 'goal_conditions': ['Painted(Ceiling)']}"  # Invalid format: should be a list
        tool_outputs = []
        handle_create_plan(tool, tool_outputs)
        self.assertTrue(any("Invalid format for 'start_conditions'" in output["output"] for output in tool_outputs))

    def test_handle_create_plan_invalid_goal_conditions_format(self):
        tool = MagicMock()
        tool.id = "123"
        tool.function.arguments = "{'start_conditions': ['On(Robot, Floor)'], 'goal_conditions': 'Painted(Ceiling)'}"  # Invalid format: should be a list
        tool_outputs = []
        handle_create_plan(tool, tool_outputs)
        self.assertTrue(any("Invalid format for 'goal_conditions'" in output["output"] for output in tool_outputs))

    def test_handle_apply_operator_invalid_operator(self):
        tool = MagicMock()
        tool.id = "123"
        tool.function.arguments = "{'start_conditions': ['On(Robot, Floor)', 'Dry(Ladder)', 'Dry(Ceiling)'], 'operator': 'invalid-operator'}"
        tool_outputs = []
        handle_apply_operator(tool, tool_outputs)
        self.assertTrue(any("Invalid operator" in output["output"] for output in tool_outputs))

    def test_handle_create_plan_missing_painted_conditions(self):
        tool = MagicMock()
        tool.id = "123"
        tool.function.arguments = "{'start_conditions': ['On(Robot, Ladder)', 'Dry(Ladder)', '¬Dry(Ceiling)'], 'goal_conditions': ['¬Dry(Ladder)']}"
        tool_outputs = []
        handle_create_plan(tool, tool_outputs)
        self.assertTrue(any(
            "Goal conditions must include at least 'Painted(Ceiling)' or 'Painted(Ladder)'" in output["output"] for
            output in tool_outputs))

    def test_handle_create_plan_valid_conditions(self):
        tool = MagicMock()
        tool.id = "123"
        tool.function.arguments = "{'start_conditions': ['On(Robot, Ladder)', 'Dry(Ladder)', 'Painted(Ceiling)'], 'goal_conditions': ['Painted(Ladder)']}"
        tool_outputs = []
        handle_create_plan(tool, tool_outputs)
        self.assertTrue(any("Painted(Ladder)" in output["output"] for output in tool_outputs))

    def test_handle_apply_operator_invalid_start_conditions_format(self):
        tool = MagicMock()
        tool.id = "123"
        tool.function.arguments = "{'start_conditions': 'On(Robot, Floor)', 'operator': 'climb-ladder'}"  # Invalid format: should be a list
        tool_outputs = []
        handle_apply_operator(tool, tool_outputs)
        self.assertTrue(any("Invalid format for 'start_conditions'" in output["output"] for output in tool_outputs))

    def test_handle_apply_operator_invalid_operator_format(self):
        tool = MagicMock()
        tool.id = "123"
        tool.function.arguments = "{'start_conditions': ['On(Robot, Floor)'], 'operator': ['climb-ladder']}"  # Invalid format: operator should be a string
        tool_outputs = []
        handle_apply_operator(tool, tool_outputs)
        self.assertTrue(any("Invalid format for 'operator'" in output["output"] for output in tool_outputs))

    def test_handle_apply_operator_missing_robot_condition(self):
        tool = MagicMock()
        tool.id = "123"
        tool.function.arguments = "{'start_conditions': ['Dry(Ladder)', 'Painted(Ceiling)'], 'operator': 'climb-ladder'}"
        tool_outputs = []
        handle_apply_operator(tool, tool_outputs)
        self.assertTrue(any(
            "Exactly one valid 'On(Robot, {location})' condition must be provided" in output["output"] for output in
            tool_outputs))

    def test_handle_apply_operator_invalid_ladder_conditions(self):
        tool = MagicMock()
        tool.id = "123"
        tool.function.arguments = "{'start_conditions': ['On(Robot, Floor)', 'Dry(Ladder)', 'Painted(Ladder)'], 'operator': 'climb-ladder'}"  # Invalid: Dry and Painted together
        tool_outputs = []
        handle_apply_operator(tool, tool_outputs)
        self.assertTrue(any("Invalid ladder conditions" in output["output"] for output in tool_outputs))

    def test_handle_apply_operator_valid_conditions(self):
        tool = MagicMock()
        tool.id = "123"
        tool.function.arguments = "{'start_conditions': ['On(Robot, Floor)', 'Dry(Ladder)', 'Painted(Ceiling)'], 'operator': 'climb-ladder'}"
        tool_outputs = []
        handle_apply_operator(tool, tool_outputs)
        self.assertTrue(any("result of applying" in output["output"] for output in tool_outputs))

    def test_handle_create_plan_invalid_ceiling_conditions(self):
        tool = MagicMock()
        tool.id = "123"
        tool.function.arguments = "{'start_conditions': ['On(Robot, Ladder)', 'Dry(Ceiling)', 'Painted(Ceiling)'], 'goal_conditions': ['Painted(Ladder)']}"  # Invalid: Dry and Painted together
        tool_outputs = []
        handle_create_plan(tool, tool_outputs)
        self.assertTrue(any("Invalid ceiling conditions" in output["output"] for output in tool_outputs))

    def test_handle_create_plan_invalid_general_conditions(self):
        tool = MagicMock()
        tool.id = "123"
        tool.function.arguments = "{'start_conditions': ['Not On(Robot, Ladder)', 'Dry(Ceiling)', 'Painted(Ceiling)'], 'goal_conditions': ['Painted(Ladder)']}"
        tool_outputs = []
        handle_create_plan(tool, tool_outputs)
        self.assertTrue(any("Invalid start condition(s) detected" in output["output"] for output in tool_outputs))

    def test_handle_apply_operator_invalid_general_conditions(self):
        tool = MagicMock()
        tool.id = "123"
        tool.function.arguments = "{'start_conditions': ['On(Robot, Floor)', 'Dry(Ladder)', 'Not Painted(Ladder)'], 'operator': 'climb-ladder'}"
        tool_outputs = []
        handle_apply_operator(tool, tool_outputs)
        self.assertTrue(any("Invalid condition(s) detected" in output["output"] for output in tool_outputs))



