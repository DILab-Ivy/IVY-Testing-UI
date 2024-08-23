from abc import ABC, abstractmethod

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
    def format_state(self) -> str:
        """Format the current state for easy reporting."""
        pass

    def __repr__(self):
        return self.format_state()
