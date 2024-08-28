# Concrete implementation for Robot Painting
from typing import List, Dict

from skills.planning.planner.planner import Planner
from config import PLANNING_DATA_DIR
from skills.planning.state.state import State


class RobotPaintingPlanner(Planner):
    def _get_json_filepath(self) -> str:
        """Provide the JSON file path for RobotPaintingPlanner's operator."""
        robot_planning_operators_path = PLANNING_DATA_DIR / 'robot_painting_operators.json'
        return robot_planning_operators_path

    def generate_partial_plan(self, start_state: State, goal_condition: str) -> str:
        print(f"Generating plan for Robot Painting from {start_state} to goal_state satisfying {goal_condition}")
        return ["paint ladder", "paint ceiling"]

    def reorder_partial_plans(self, plans: Dict) -> List[str]:
        print(f"Reordering plan to avoid obstacles: {plans}")
        return ["paint ceiling", "move ladder", "paint ladder"]

    def generate_complete_plan(self, start_state: State, goal_state: State) -> str:
        print("RobotPaintingPlanner: Custom complete plan logic")

        # Use the loaded operator for additional logic (if needed)
        print(f"Operators available for planning: {self.operators}")

        goal_conditions = goal_state.return_eligible_goal_conditions()

        # Step 1: Generate an initial plan
        partial_plans_dict = dict() #dict of partial plans
        for goal_condition in goal_conditions:
            partial_plan = self.generate_partial_plan(start_state, goal_condition)
            partial_plans_dict[goal_condition] = partial_plan

        # Step 2: Reorder the plan to avoid conflicts
        reordered_plans = self.reorder_partial_plans(partial_plans_dict)

        # Step 3: Complete the reordered plan
        complete_plan = self.complete_plan(reordered_plans)

        return complete_plan