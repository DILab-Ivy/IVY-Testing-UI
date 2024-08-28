from typing import Set, List
from skills.planning.state.state import State
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

    @classmethod
    def from_conditions_list(cls, conditions: List[str]) -> 'RobotPaintingState':
        """
        Create a RobotPaintingState object from a list of conditions.

        :param conditions: List of conditions provided by the user.
        :return: RobotPaintingState object if the format is correct.
        :raises ValueError: If the conditions list is not in the correct format.
        """
        robot_position = None
        ceiling_status = set()
        ladder_status = set()

        # Process each condition
        for condition in conditions:
            condition = condition.strip()

            # Check for the robot position condition
            if condition.startswith("On(Robot, "):
                if robot_position is not None:
                    raise ValueError("There can be only one 'On(Robot, ...)' condition.")
                if condition == "On(Robot, Floor)":
                    robot_position = RobotPosition.ON_FLOOR
                elif condition == "On(Robot, Ladder)":
                    robot_position = RobotPosition.ON_LADDER
                else:
                    raise ValueError(
                        "Invalid 'On(Robot, ...)' condition. Must be 'On(Robot, Floor)' or 'On(Robot, Ladder)'.")

            # Check for ceiling status conditions
            elif condition.startswith("Dry(Ceiling)"):
                ceiling_status.add(Status.DRY)
            elif condition.startswith("¬Dry(Ceiling)"):
                ceiling_status.add(Status.NOT_DRY)
            elif condition.startswith("Painted(Ceiling)"):
                ceiling_status.add(Status.PAINTED)

            # Check for ladder status conditions
            elif condition.startswith("Dry(Ladder)"):
                ladder_status.add(Status.DRY)
            elif condition.startswith("¬Dry(Ladder)"):
                ladder_status.add(Status.NOT_DRY)
            elif condition.startswith("Painted(Ladder)"):
                ladder_status.add(Status.PAINTED)

            else:
                raise ValueError(f"Unknown condition '{condition}'.")

        # Validate that we have one robot position and at least one status for ceiling and ladder
        if robot_position is None:
            raise ValueError(
                "Missing 'On(Robot, ...)' condition. Must specify robot position (e.g., 'On(Robot, Floor)').")

        if not ceiling_status:
            raise ValueError(
                "Missing ceiling status condition. Must specify at least one ceiling condition (e.g., 'Dry(Ceiling)').")

        if not ladder_status:
            raise ValueError(
                "Missing ladder status condition. Must specify at least one ladder condition (e.g., 'Dry(Ladder)').")

        # Create and return the RobotPaintingState object
        return cls(robot_position, ceiling_status, ladder_status)

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

    def check_if_state_clobbers_operator(self, operator: 'Operator') -> 'State':
        """Check if State conditions clobber Operator preconditions"""
        pass

    def check_if_state_matches_operator(self, operator: 'Operator') -> 'State':
        """Check if State conditions match provided Operator preconditions"""
        pass

    def return_eligible_goal_conditions(self) -> List[str]:
        """Returns list of conditions that are eligible for partial order plan"""
        # return ['Painted(Ceiling)', 'Painted(Ladder)'] # example from robot instance - basically we don't also need to search for ¬Dry(Ceiling) etc too
        pass

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
