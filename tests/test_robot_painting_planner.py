import unittest
from unittest.mock import patch, MagicMock
from skills.planning.planner.instances.robot_painting_planner import RobotPaintingPlanner
from skills.planning.state.instances.robot_painting_state import RobotPaintingState, RobotPosition, Status

class TestRobotPaintingPlanner(unittest.TestCase):

    @patch('skills.planning.planner.instances.robot_painting_planner.PLANNING_DATA_DIR')
    def test_get_json_filepath(self, mock_planning_data_dir):
        mock_planning_data_dir.__truediv__.return_value = '/mock/path/robot_painting_operators.json'
        planner = RobotPaintingPlanner()
        expected_path = '/mock/path/robot_painting_operators.json'
        self.assertEqual(planner._get_json_filepath(), expected_path)

    def test_generate_partial_plan(self):
        planner = RobotPaintingPlanner()
        start_state = MagicMock(spec=RobotPaintingState)
        goal_condition = "Painted(Ceiling)"
        partial_plan = planner.generate_partial_plan(start_state, goal_condition)
        self.assertEqual(partial_plan, ["paint ladder", "paint ceiling"])

    def test_reorder_partial_plans(self):
        planner = RobotPaintingPlanner()
        plans = {"goal1": ["paint ladder"], "goal2": ["paint ceiling"]}
        reordered_plan = planner.reorder_partial_plans(plans)
        self.assertEqual(reordered_plan, ["paint ceiling", "move ladder", "paint ladder"])

    @patch('skills.planning.planner.instances.robot_painting_planner.RobotPaintingPlanner.generate_partial_plan')
    @patch('skills.planning.planner.instances.robot_painting_planner.RobotPaintingPlanner.reorder_partial_plans')
    def test_generate_complete_plan(self, mock_reorder_partial_plans, mock_generate_partial_plan):
        planner = RobotPaintingPlanner()

        # Setup mock behaviors
        start_state = MagicMock(spec=RobotPaintingState)
        goal_state = MagicMock(spec=RobotPaintingState)
        goal_state.return_eligible_goal_conditions.return_value = ["Painted(Ceiling)", "Painted(Ladder)"]

        mock_generate_partial_plan.side_effect = [
            ["paint ladder"],
            ["paint ceiling"]
        ]
        mock_reorder_partial_plans.return_value = ["paint ceiling", "move ladder", "paint ladder"]

        complete_plan = planner.generate_complete_plan(start_state, goal_state)
        self.assertEqual(complete_plan, ["paint ceiling", "move ladder", "paint ladder"])

        # Ensure that generate_partial_plan was called with correct parameters
        mock_generate_partial_plan.assert_any_call(start_state, "Painted(Ceiling)")
        mock_generate_partial_plan.assert_any_call(start_state, "Painted(Ladder)")

        # Ensure that reorder_partial_plans was called with correct parameters
        expected_partial_plans = {
            "Painted(Ceiling)": ["paint ladder"],
            "Painted(Ladder)": ["paint ceiling"]
        }
        mock_reorder_partial_plans.assert_called_once_with(expected_partial_plans)
