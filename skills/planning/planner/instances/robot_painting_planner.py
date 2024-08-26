# Concrete implementation for Robot Painting
from skills.planning.planner.planner import Planner
from config import PLANNING_DATA_DIR


class RobotPaintingPlanner(Planner):
    def _get_json_filepath(self) -> str:
        """Provide the JSON file path for RobotPaintingPlanner's operator."""
        robot_planning_operators_path = PLANNING_DATA_DIR / 'robotpainting_operators.json'
        return robot_planning_operators_path

    def generate_plan(self, start_state, goal_state):
        print(f"Generating plan for Robot Painting from {start_state} to {goal_state}")
        return ["paint ladder", "paint ceiling"]

    def reorder_to_avoid(self, plans):
        print(f"Reordering plan to avoid obstacles: {plans}")
        return ["paint ceiling", "move ladder", "paint ladder"]

    def complete_plan(self, partial_plan):
        print(f"Completing the partial plan: {partial_plan}")
        return partial_plan + ["clean up"]

    def generate_complete_plan(self, start_state, goal_state):
        print("RobotPaintingPlanner: Custom complete plan logic")

        # Use the loaded operator for additional logic (if needed)
        print(f"Operators available for planning: {self.operators}")

        # Step 1: Generate an initial plan
        plans = self.generate_plan(start_state, goal_state)

        # Step 2: Reorder the plan to avoid obstacles
        reordered_plan = self.reorder_to_avoid(plans)

        # Step 3: Complete the reordered plan
        complete_plan = self.complete_plan(reordered_plan)

        return complete_plan