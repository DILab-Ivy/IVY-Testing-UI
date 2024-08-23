from typing import Set
from skills.planning.states.state import State
from enum import Enum, auto

class RobotPosition(Enum):
    ON_FLOOR = auto()
    ON_LADDER = auto()


class Status(Enum):
    PAINTED = auto()
    DRY = auto()
    NOT_DRY = auto()

class RobotPaintingState(State):
    def __init__(self, robot_position: RobotPosition, ceiling_status: Set[Status], ladder_status: Set[Status]):
        self.robot_position = robot_position
        self.ceiling_status = ceiling_status
        self.ladder_status = ladder_status

    def is_goal_state(self, goal_state: 'RobotPaintingState') -> bool:
        """Check if current state matches the goal state."""
        return (self.robot_position == goal_state.robot_position and
                self.ceiling_status == goal_state.ceiling_status and
                self.ladder_status == goal_state.ladder_status)

    def apply_operator(self, operator: 'Operator') -> 'RobotPaintingState':
        """Apply an operator to the current state to produce a new state."""
        new_robot_position = self.robot_position
        new_ceiling_status = self.ceiling_status.copy()
        new_ladder_status = self.ladder_status.copy()

        if operator.name == "climb-ladder":
            new_robot_position = RobotPosition.ON_LADDER
        elif operator.name == "descend-ladder":
            new_robot_position = RobotPosition.ON_FLOOR
        elif operator.name == "paint-ceiling":
            new_ceiling_status = {Status.PAINTED, Status.NOT_DRY}
        elif operator.name == "paint-ladder":
            new_ladder_status = {Status.PAINTED, Status.NOT_DRY}

        return RobotPaintingState(new_robot_position, new_ceiling_status, new_ladder_status)

    def format_state(self) -> str:
        """Format the current state for easy reporting."""
        conditions = []

        # Robot position condition
        if self.robot_position == RobotPosition.ON_FLOOR:
            conditions.append("On(Robot, Floor)")
        elif self.robot_position == RobotPosition.ON_LADDER:
            conditions.append("On(Robot, Ladder)")

        # Ceiling status conditions
        if Status.PAINTED in self.ceiling_status:
            conditions.append("Painted(Ceiling)")
        if Status.DRY in self.ceiling_status:
            conditions.append("Dry(Ceiling)")
        if Status.NOT_DRY in self.ceiling_status:
            conditions.append("¬Dry(Ceiling)")

        # Ladder status conditions
        if Status.PAINTED in self.ladder_status:
            conditions.append("Painted(Ladder)")
        if Status.DRY in self.ladder_status:
            conditions.append("Dry(Ladder)")
        if Status.NOT_DRY in self.ladder_status:
            conditions.append("¬Dry(Ladder)")

        return " ^ ".join(conditions)
