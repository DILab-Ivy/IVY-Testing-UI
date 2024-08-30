from skills.planning.planner.planner import Planner


class BlockWorldPlanner(Planner):
    def _get_json_filepath(self) -> str:
        """Provide the JSON file path for BlockWorldPlanner's operator."""
        return 'blockworld_operators.json'

    def build_partial_plan(self, start_state, goal_state):
        print(f"Generating plan for Block World from {start_state} to {goal_state}")
        return ["move A to B", "move B to C"]

    def reorder_partial_plans(self, plans):
        print(f"Reordering plan to avoid obstacles: {plans}")
        return ["move C to A", "move B to C"]


    def generate_complete_plan(self, start_state, goal_state, obstacles):
        print("BlockWorldPlanner: Custom complete plan logic")

        # Use the loaded operator for additional logic (if needed)
        print(f"Operators available for planning: {self.operators}")

        # Step 1: Generate an initial plan
        plan = self.build_partial_plan(start_state, goal_state)

        # Step 2: Reorder the plan to avoid obstacles
        reordered_plan = self.reorder_partial_plans(obstacles)

        # Step 3: Complete the reordered plan
        complete_plan = self.complete_plan(reordered_plan)

        return complete_plan