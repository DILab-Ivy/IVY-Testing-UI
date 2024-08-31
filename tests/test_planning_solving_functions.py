import unittest
from unittest.mock import patch, MagicMock
from skills.planning.planning_solving_functions import get_planner, get_state_object, build_partial_plan, reorder_plans_to_avoid_conflicts, build_complete_plan
from skills.planning.planner.instances.robot_painting_planner import RobotPaintingPlanner
from skills.planning.state.instances.robot_painting_state import RobotPaintingState
from skills.planning.planner.instances.blockworld_planner import BlockWorldPlanner
from skills.planning.operator.operator import Operator


class TestDispatcherFunctions(unittest.TestCase):

    def test_get_planner_robot(self):
        planner = get_planner('robot')
        self.assertIsInstance(planner, RobotPaintingPlanner)
        self.assertIsInstance(planner.operators['climb-ladder'], Operator)

    # def test_get_planner_blockworld(self):
    #     planner = get_planner('blockworld')
    #     self.assertIsInstance(planner, BlockWorldPlanner)

    def test_get_planner_unknown(self):
        with self.assertRaises(ValueError) as context:
            get_planner('unknown')
        self.assertEqual(str(context.exception), "Unknown problem type. Please choose 'blockworld' or 'robot'.")

    def test_get_state_object_robot(self):
        state_conditions_list = ['On(Robot, Floor)', 'Dry(Ceiling)', 'Dry(Ladder)']
        state = get_state_object('robot', state_conditions_list)
        self.assertIsInstance(state, RobotPaintingState)

    # def test_get_state_object_blockworld(self):
    #     state_conditions_list = ['On(A,B)', 'On(B,Table)']
    #     state = get_state_object('blockworld', state_conditions_list)
    #     self.assertIsInstance(state, BlockWorldState)

    def test_get_state_object_unknown(self):
        with self.assertRaises(ValueError) as context:
            get_state_object('unknown', '[{"condition": "on", "object": "block"}]')
        self.assertEqual(str(context.exception), "Unknown problem type. Please choose 'blockworld' or 'robot'.")

    @patch('dispatcher.RobotPaintingPlanner.generate_partial_plan')
    @patch('dispatcher.RobotPaintingState.from_conditions_list')
    def test_generate_plan(self, mock_from_conditions_list, mock_generate_partial_plan):
        mock_state = MagicMock(spec=RobotPaintingState)
        mock_from_conditions_list.return_value = mock_state
        mock_generate_partial_plan.return_value = ['paint wall']

        start_state_conditions = '[{"condition": "clean", "object": "wall"}]'
        goal_state_conditions = '[{"condition": "painted", "object": "wall"}]'

        plan = build_partial_plan('robot', start_state_conditions, goal_state_conditions)

        mock_from_conditions_list.assert_called_with(start_state_conditions)
        mock_from_conditions_list.assert_called_with(goal_state_conditions)
        mock_generate_partial_plan.assert_called_with(mock_state, mock_state)
        self.assertEqual(plan, ['paint wall'])

    @patch('dispatcher.RobotPaintingPlanner.reorder_partial_plans')
    def test_reorder_to_avoid(self, mock_reorder_partial_plans):
        mock_reorder_partial_plans.return_value = [['plan1', 'plan2']]
        plans = [['plan1'], ['plan2']]

        reordered_plans = reorder_plans_to_avoid_conflicts('robot', plans)

        mock_reorder_partial_plans.assert_called_with(plans)
        self.assertEqual(reordered_plans, [['plan1', 'plan2']])

    @patch('dispatcher.RobotPaintingPlanner.generate_complete_plan')
    @patch('dispatcher.RobotPaintingState.from_conditions_list')
    def test_generate_complete_plan(self, mock_from_conditions_list, mock_generate_complete_plan):
        mock_state = MagicMock(spec=RobotPaintingState)
        mock_from_conditions_list.return_value = mock_state
        mock_generate_complete_plan.return_value = ['complete plan']

        start_state_conditions = '[{"condition": "clean", "object": "wall"}]'
        goal_state_conditions = '[{"condition": "painted", "object": "wall"}]'

        complete_plan = build_complete_plan('robot', start_state_conditions, goal_state_conditions)

        mock_from_conditions_list.assert_called_with(start_state_conditions)
        mock_from_conditions_list.assert_called_with(goal_state_conditions)
        mock_generate_complete_plan.assert_called_with(mock_state, mock_state)
        self.assertEqual(complete_plan, ['complete plan'])
