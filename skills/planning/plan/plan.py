from typing import List, Tuple

class Plan:
    def __init__(self, goal: str, steps: List[Tuple[str, str]], priority: int):
        """
        Initialize a plan with a goal, a list of steps, and a priority score.

        :param goal: The goal of the plan.
        :param steps: A list of steps, where each step is a tuple ('state', 'operator').
        :param priority: The priority score of the plan.
        """
        self.goal = goal
        self.steps = steps  # List of tuples ('state', 'operator')
        self.priority = priority

    def __repr__(self):
        return f"Plan(goal={self.goal}, priority={self.priority}, steps={self.steps})"

    def __lt__(self, other: 'Plan') -> bool:
        """Less than operator for sorting plans by priority."""
        return self.priority < other.priority

    def get_initial_state(self) -> str:
        """Return the initial state of the plan."""
        return self.steps[0][0] if self.steps else None

    def get_final_state(self) -> str:
        """Return the final state of the plan."""
        return self.steps[-1][0] if self.steps else None

    def execute(self):
        """Simulate executing the plan by iterating over steps."""
        for state, operator in self.steps:
            print(f"Executing {operator} in state {state}")

    def add_step(self, state: str, operator: str):
        """Add a step to the plan."""
        self.steps.append((state, operator))

    def get_plan_summary(self) -> List[str]:
        """Return a summary of the plan from start to goal state."""
        summary = ["start"]
        for state, operator in self.steps:
            summary.append(f"{state} -> {operator}")
        summary.append("end")
        return summary
