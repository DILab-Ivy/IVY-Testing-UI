from abc import ABC, abstractmethod
from typing import List, Dict

from skills.planning.states.state import State


class Planner(ABC):
    def __init__(self):
        self.operators = self._generate_operators()

    @abstractmethod
    def _generate_operators(self) -> Dict[str, 'Operator']:
        """Private method to load operators specific to the planner."""
        pass

    @abstractmethod
    def _get_json_filepath(self) -> str:
        """Abstract method to get the JSON file path for the operators."""
        pass

    @abstractmethod
    def generate_plan(self, start_state: State, goal_state: State):
        """Generate a plan from start_state to goal_state."""
        pass

    @abstractmethod
    def reorder_to_avoid(self, obstacles: List[str]):
        """Reorder actions to avoid obstacles."""
        pass

    @abstractmethod
    def complete_plan(self, partial_plan: List[str]):
        """Complete a partial plan."""
        pass

    @abstractmethod
    def generate_complete_plan(self, start_state: State, goal_state: State, obstacles: List[str]):
        """
        Generate a complete plan using the generate_plan, reorder_to_avoid,
        and complete_plan methods.
        """
        pass