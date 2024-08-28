import unittest
from unittest.mock import patch, MagicMock
from skills.planning.state.instances.robot_painting_state import RobotPaintingState, RobotPosition, Status
from skills.planning.operator.operator import Operator
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

    def test_apply_operator_climb_ladder_success(self):
        initial_state = RobotPaintingState(RobotPosition.ON_FLOOR, {Status.PAINTED}, {Status.DRY})
        operator = Operator(name='climb-ladder', preconditions=["On(Robot, Floor)"], postconditions=[])
        new_state = initial_state.apply_operator(operator)
        self.assertEqual(new_state.robot_position, RobotPosition.ON_LADDER)
        self.assertEqual(new_state.ceiling_status, {Status.PAINTED})
        self.assertEqual(new_state.ladder_status, {Status.DRY})

    def test_apply_operator_climb_ladder_failure(self):
        initial_state = RobotPaintingState(RobotPosition.ON_LADDER, {Status.PAINTED}, {Status.DRY})
        operator = Operator(name='climb-ladder', preconditions=["On(Robot, Floor)"], postconditions=[])

        with self.assertRaises(ValueError) as context:
            initial_state.apply_operator(operator)

        self.assertTrue("Precondition 'On(Robot, Floor)' is not met." in str(context.exception))

    def test_apply_operator_paint_ceiling_success(self):
        initial_state = RobotPaintingState(RobotPosition.ON_LADDER, {Status.DRY}, {Status.DRY})
        operator = Operator(name='paint-ceiling', preconditions=["On(Robot, Ladder)", "Dry(Ceiling)"],
                            postconditions=[])
        new_state = initial_state.apply_operator(operator)
        self.assertEqual(new_state.robot_position, RobotPosition.ON_LADDER)
        self.assertEqual(new_state.ceiling_status, {Status.PAINTED, Status.NOT_DRY})
        self.assertEqual(new_state.ladder_status, {Status.DRY})

    def test_apply_operator_paint_ceiling_failure_due_to_position(self):
        initial_state = RobotPaintingState(RobotPosition.ON_FLOOR, {Status.DRY}, {Status.DRY})
        operator = Operator(name='paint-ceiling', preconditions=["On(Robot, Ladder)", "Dry(Ceiling)"],
                            postconditions=[])

        with self.assertRaises(ValueError) as context:
            initial_state.apply_operator(operator)

        self.assertTrue("Precondition 'On(Robot, Ladder)' is not met." in str(context.exception))

    def test_apply_operator_paint_ceiling_failure_due_to_status(self):
        initial_state = RobotPaintingState(RobotPosition.ON_LADDER, {Status.NOT_DRY}, {Status.DRY})
        operator = Operator(name='paint-ceiling', preconditions=["On(Robot, Ladder)", "Dry(Ceiling)"],
                            postconditions=[])

        with self.assertRaises(ValueError) as context:
            initial_state.apply_operator(operator)

        self.assertTrue("Precondition 'Dry(Ceiling)' is not met." in str(context.exception))

    def test_apply_operator_unknown_precondition(self):
        initial_state = RobotPaintingState(RobotPosition.ON_LADDER, {Status.DRY}, {Status.DRY})
        operator = Operator(name='paint-ceiling', preconditions=["On(Robot, Roof)"], postconditions=[])

        with self.assertRaises(ValueError) as context:
            initial_state.apply_operator(operator)

        self.assertTrue("Unknown or unsupported precondition: On(Robot, Roof)" in str(context.exception))

        # Assert that the ceiling has been painted and is not dry
        self.assertEqual(new_state.robot_position, RobotPosition.ON_LADDER)
        self.assertEqual(new_state.ceiling_status, {Status.PAINTED, Status.NOT_DRY})
        self.assertEqual(new_state.ladder_status, {Status.DRY})

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