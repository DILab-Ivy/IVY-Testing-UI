from abc import ABC, abstractmethod
from typing import List


class State(ABC):
    @abstractmethod
    def is_goal_state(self, goal_state: 'State') -> bool:
        """Check if current state matches the goal state."""
        pass

    @abstractmethod
    def apply_operator(self, operator: 'Operator') -> 'State':
        """Apply an operator to the current state to produce a new state."""
        pass

    @abstractmethod
    def reverse_operator(self, operator: 'Operator') -> 'State':
        """Reverse an operator on the current state to produce a new state"""
        pass

    @abstractmethod
    def check_if_state_clobbers_operator(self, operator: 'Operator') -> 'State':
        """Check if State conditions clobber Operator preconditions"""
        pass

    @abstractmethod
    def check_if_state_matches_operator(self, operator: 'Operator') -> 'State':
        """Check if State conditions match provided Operator preconditions"""
        pass

    @abstractmethod
    def return_eligible_goal_conditions(self) -> List[str]:
        """Returns list of conditions that are eligible for partial order plan"""
        # return ['Painted(Ceiling)', 'Painted(Ladder)'] # example from robot instance - basically we don't also need to search for ¬Dry(Ceiling) etc too
        pass

    @abstractmethod
    def format_state(self) -> str:
        """Format the current state for easy reporting."""
        pass

    def __repr__(self):
        return self.format_state()
