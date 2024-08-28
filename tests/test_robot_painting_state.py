import unittest
from unittest.mock import patch, MagicMock
from skills.planning.state.instances.robot_painting_state import RobotPaintingState, RobotPosition, Status
from enum import Enum, auto

class TestRobotPaintingState(unittest.TestCase):

    def test_from_conditions_list_valid(self):
        conditions = [
            "On(Robot, Floor)",
            "Painted(Ceiling)",
            "Dry(Ceiling)",
            "Painted(Ladder)",
            "Dry(Ladder)"
        ]
        state = RobotPaintingState.from_conditions_list(conditions)
        self.assertEqual(state.robot_position, RobotPosition.ON_FLOOR)
        self.assertIn(Status.PAINTED, state.ceiling_status)
        self.assertIn(Status.DRY, state.ceiling_status)
        self.assertIn(Status.PAINTED, state.ladder_status)
        self.assertIn(Status.DRY, state.ladder_status)

    def test_from_conditions_list_invalid_robot_position(self):
        conditions = [
            "On(Robot, Sky)",  # Invalid position
            "Painted(Ceiling)"
        ]
        with self.assertRaises(ValueError) as context:
            RobotPaintingState.from_conditions_list(conditions)
        self.assertEqual(str(context.exception),
                         "Invalid 'On(Robot, ...)' condition. Must be 'On(Robot, Floor)' or 'On(Robot, Ladder)'.")

    def test_from_conditions_list_missing_robot_position(self):
        conditions = [
            "Painted(Ceiling)"
        ]
        with self.assertRaises(ValueError) as context:
            RobotPaintingState.from_conditions_list(conditions)
        self.assertEqual(str(context.exception),
                         "Missing 'On(Robot, ...)' condition. Must specify robot position (e.g., 'On(Robot, Floor)').")

    def test_is_goal_state_true(self):
        state1 = RobotPaintingState(RobotPosition.ON_FLOOR, {Status.PAINTED}, {Status.DRY})
        state2 = RobotPaintingState(RobotPosition.ON_FLOOR, {Status.PAINTED}, {Status.DRY})
        self.assertTrue(state1.is_goal_state(state2))

    def test_is_goal_state_false(self):
        state1 = RobotPaintingState(RobotPosition.ON_FLOOR, {Status.PAINTED}, {Status.DRY})
        state2 = RobotPaintingState(RobotPosition.ON_LADDER, {Status.PAINTED}, {Status.DRY})
        self.assertFalse(state1.is_goal_state(state2))

    def test_apply_operator_climb_ladder(self):
        initial_state = RobotPaintingState(RobotPosition.ON_FLOOR, {Status.PAINTED}, {Status.DRY})
        operator = MagicMock(name='climb-ladder')
        new_state = initial_state.apply_operator(operator)
        self.assertEqual(new_state.robot_position, RobotPosition.ON_LADDER)
        self.assertEqual(new_state.ceiling_status, {Status.PAINTED})
        self.assertEqual(new_state.ladder_status, {Status.DRY})

    def test_apply_operator_paint_ceiling(self):
        initial_state = RobotPaintingState(RobotPosition.ON_LADDER, set(), set())
        operator = MagicMock(name='paint-ceiling')
        new_state = initial_state.apply_operator(operator)
        self.assertIn(Status.PAINTED, new_state.ceiling_status)
        self.assertIn(Status.NOT_DRY, new_state.ceiling_status)

    def test_check_if_state_clobbers_operator_not_implemented(self):
        initial_state = RobotPaintingState(RobotPosition.ON_FLOOR, {Status.PAINTED}, {Status.DRY})
        operator = MagicMock()
        with self.assertRaises(NotImplementedError):
            initial_state.check_if_state_clobbers_operator(operator)

    def test_check_if_state_matches_operator_not_implemented(self):
        initial_state = RobotPaintingState(RobotPosition.ON_FLOOR, {Status.PAINTED}, {Status.DRY})
        operator = MagicMock()
        with self.assertRaises(NotImplementedError):
            initial_state.check_if_state_matches_operator(operator)

    def test_return_eligible_goal_conditions_not_implemented(self):
        initial_state = RobotPaintingState(RobotPosition.ON_FLOOR, {Status.PAINTED}, {Status.DRY})
        with self.assertRaises(NotImplementedError):
            initial_state.return_eligible_goal_conditions()

    def test_format_state(self):
        state = RobotPaintingState(RobotPosition.ON_FLOOR, {Status.PAINTED, Status.DRY}, {Status.NOT_DRY})
        formatted = state.format_state()
        expected = "On(Robot, Floor) ^ Painted(Ceiling) ^ Dry(Ceiling) ^ ¬Dry(Ladder)"
        self.assertEqual(formatted, expected)