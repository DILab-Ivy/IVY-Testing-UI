from typing import List, Tuple, Dict
import copy

class Plan:
    def __init__(self, start_state: 'State', goal_condition: str, operators: Dict[str, 'Operator']):
        """
        Initialize a plan with a goal, a list of steps, and a priority score.

        :param goal_condition: The goal of the plan.
        :param steps: A list of steps, where each step is a tuple ('state', 'operator').
        :param priority: The priority score of the plan.
        """
        self.start_state = start_state
        self.primary_goal = goal_condition
        self.operator_steps = []
        self.state_steps = [start_state]
        # self.priority = priority
        goal_c = goal_condition
        curr_state = copy.deepcopy(start_state)
        while not curr_state.check_if_state_matches_operator(goal_c):
            for i, op in enumerate(operators):
                pass
                # if

    def __repr__(self):
        return f"Plan(goal={self.goal_condition}, operator_steps={self.operator_steps}, state_steps={self.state_steps})"

    # def __lt__(self, other: 'Plan') -> bool:
    #     """Less than operator for sorting plans by priority."""
    #     return self.priority < other.priority

    # def get_start_state(self) -> str:
    #     """Return the initial state of the plan."""
    #     return self.start_state
    #
    # def get_goal_condition(self) -> str:
    #     """Return the final state of the plan."""
    #     return self.goal_condition

    # def get_final_state(self) -> str:
    #     """Return the final state of the plan."""
    #     return self.steps[-1][0] if self.steps else None

    # def execute(self):
    #     """Simulate executing the plan by iterating over steps."""
    #     for state, operator in self.steps:
    #         print(f"Executing {operator} in state {state}")

    # def add_step(self, preceding_state: str, operator: str):
    #     """Add a step to the plan."""
    #     self.steps.append((preceding_state, operator))

    # def get_plan_summary(self) -> List[str]:
    #     """Return a summary of the plan from start to goal state."""
    #     summary = ["start"]
    #     for state, operator in self.steps:
    #         summary.append(f"{state} -> {operator}")
    #     summary.append("end")
    #     return summary
