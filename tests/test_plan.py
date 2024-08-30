import unittest
from typing import Dict, List, Set

from skills.planning.operator.instances import RobotPaintingOperator
from skills.planning.planner.instances import RobotPaintingPlanner
from skills.planning.state.instances import RobotPaintingState
from skills.planning.state.instances.robot_painting_state import RobotPosition, Status
from skills.planning.plan import Plan


class TestPlan(unittest.TestCase):
    def setUp(self):
        # Set up the real states and operators for the robot painting scenario

        # Initialize the start state with the robot on the floor, ceiling dry, and ladder dry
        self.start_state = RobotPaintingState(
            robot_position=RobotPosition.ON_FLOOR,
            ceiling_status={Status.DRY},
            ladder_status={Status.DRY}
        )
        self.planner = RobotPaintingPlanner()
        self.operators = self.planner.operators

    def test_plan_with_goal_painted_ceiling(self):
        # Test creating a plan with the goal condition "Painted(Ceiling)"
        plan = Plan(self.start_state, "Painted(Ceiling)", self.operators)
        plan_string = str(plan)
        expected_plan_string = "Plan(goal=Painted(Ceiling), operator_steps=[Operator(name=climb-ladder, preconditions=['On(Robot, Floor)', 'Dry(Ladder)'], postconditions=['On(Robot, Ladder)']), Operator(name=paint-ceiling, preconditions=['On(Robot, Ladder)'], postconditions=['Painted(Ceiling)', '¬Dry(Ceiling)'])], state_steps=[On(Robot, Floor) ^ Dry(Ceiling) ^ Dry(Ladder), On(Robot, Ladder) ^ Dry(Ceiling) ^ Dry(Ladder), On(Robot, Ladder) ^ Painted(Ceiling) ^ ¬Dry(Ceiling) ^ Dry(Ladder)])"
        self.assertEqual(plan.primary_goal, "Painted(Ceiling)")
        self.assertIn(plan_string, expected_plan_string)
        # # Check if the last state matches the expected goal state format
        # self.assertEqual(plan.state_steps[-1].format_state(), "On(Robot, Ladder) ^ Painted(Ceiling) ^ ¬Dry(Ceiling) ^ Dry(Ladder)")

    def test_plan_with_goal_painted_ladder(self):
        # Test creating a plan with the goal condition "Painted(Ladder)"
        plan = Plan(self.start_state, "Painted(Ladder)", self.operators)
        plan_string = str(plan)
        expected_plan_string = "Plan(goal=Painted(Ladder), operator_steps=[Operator(name=paint-ladder, preconditions=['On(Robot, Floor)'], postconditions=['Painted(Ladder)', '¬Dry(Ladder)'])], state_steps=[On(Robot, Floor) ^ Dry(Ceiling) ^ Dry(Ladder), On(Robot, Floor) ^ Dry(Ceiling) ^ Painted(Ladder) ^ ¬Dry(Ladder)])"
        self.assertEqual(plan.primary_goal, "Painted(Ladder)")
        self.assertIn(plan_string, expected_plan_string)

    def test_plan_with_goal_painted_ladder_alternate_start_state(self):
        self.start_state = RobotPaintingState(
            robot_position=RobotPosition.ON_LADDER,
            ceiling_status={Status.DRY},
            ladder_status={Status.DRY}
        )
        # Test creating a plan with the goal condition "Painted(Ladder)"
        plan = Plan(self.start_state, "Painted(Ladder)", self.operators)
        plan_string = str(plan)
        expected_plan_string = "Plan(goal=Painted(Ladder), operator_steps=[Operator(name=descend-ladder, preconditions=['On(Robot, Ladder)', 'Dry(Ladder)'], postconditions=['On(Robot, Floor)']), Operator(name=paint-ladder, preconditions=['On(Robot, Floor)'], postconditions=['Painted(Ladder)', '¬Dry(Ladder)'])], state_steps=[On(Robot, Ladder) ^ Dry(Ceiling) ^ Dry(Ladder), On(Robot, Floor) ^ Dry(Ceiling) ^ Dry(Ladder), On(Robot, Floor) ^ Dry(Ceiling) ^ Painted(Ladder) ^ ¬Dry(Ladder)])"
        self.assertEqual(plan.primary_goal, "Painted(Ladder)")
        self.assertIn(plan_string, expected_plan_string)

    def test_plan_with_goal_painted_ceiling_impossible_start_state(self):
        self.start_state = RobotPaintingState(
            robot_position=RobotPosition.ON_FLOOR,
            ceiling_status={Status.DRY},
            ladder_status={Status.PAINTED}
        )

        # Make sure that error is thrown since plan isn't possible
        # TODO: note, the operator list is being built and the error is being thrown
        #  when the state list is created through error handling in
        #  State.apply_operator this could maybe be handled in a better fashion
        with self.assertRaises(ValueError):
            Plan(self.start_state, "Painted(Ceiling)", self.operators)

    # def test_plan_with_goal_painted_floor(self):
    #     # Test creating a plan with the goal condition "Painted(Floor)"
    #     plan = Plan(self.start_state, "Painted(Floor)", self.operators)
    #     self.assertEqual(plan.primary_goal, "Painted(Floor)")
    #     self.assertIn(self.operator_paint_floor, plan.operator_steps)
    #     # Check if the last state matches the expected goal state format
    #     self.assertEqual(plan.state_steps[-1].format_state(), "On(Robot, Floor) ^ Painted(Floor) ^ Dry(Ceiling) ^ Dry(Ladder)")

    # def test_no_operator_found(self):
    #     # Test raising a LookupError when no operator matches the goal condition
    #     with self.assertRaises(LookupError):
    #         Plan(self.start_state, "UnreachableGoal", self.operators)