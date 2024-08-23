# Concrete implementation for Robot Painting
from skills.planning.planners.planner import Planner


class RobotPaintingPlanner(Planner):
    def _get_json_filepath(self) -> str:
        """Provide the JSON file path for RobotPaintingPlanner's operators."""
        return 'skills/planning/data/robotpainting_operators.json'

    def generate_plan(self, start_state, goal_state):
        print(f"Generating plan for Robot Painting from {start_state} to {goal_state}")
        return ["paint ladder", "paint ceiling"]

    def reorder_to_avoid(self, obstacles):
        print(f"Reordering plan to avoid obstacles: {obstacles}")
        return ["paint ceiling", "move ladder", "paint ladder"]

    def complete_plan(self, partial_plan):
        print(f"Completing the partial plan: {partial_plan}")
        return partial_plan + ["clean up"]

    def generate_complete_plan(self, start_state, goal_state, obstacles):
        print("RobotPaintingPlanner: Custom complete plan logic")

        # Use the loaded operators for additional logic (if needed)
        print(f"Operators available for planning: {self.operators}")

        # Step 1: Generate an initial plan
        plan = self.generate_plan(start_state, goal_state)

        # Step 2: Reorder the plan to avoid obstacles
        reordered_plan = self.reorder_to_avoid(obstacles)

        # Step 3: Complete the reordered plan
        complete_plan = self.complete_plan(reordered_plan)

        return complete_plan