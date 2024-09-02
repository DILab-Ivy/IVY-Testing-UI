from typing import Set, List, Callable, Dict
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
        self.condition_set = None

        # Clean up status on initialization
        self.sync_painted_dry_status()
        # Generate the initial condition set
        self.generate_condition_set()

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

        # Create the RobotPaintingState object
        state = cls(robot_position, ceiling_status, ladder_status)

        # Ensure the state is consistent
        state.sync_painted_dry_status()

        # Reset conditions set
        state.generate_condition_set()

        return state

    def sync_painted_dry_status(self):
        """Ensure that painted surfaces are also not dry and vice versa."""
        # Synchronize ceiling status
        if Status.PAINTED in self.ceiling_status or Status.NOT_DRY in self.ceiling_status:
            self.ceiling_status.discard(Status.DRY)  # Remove dry if it's painted or not dry
            self.ceiling_status.update({Status.PAINTED, Status.NOT_DRY})  # Ensure both painted and not dry are present

        # Synchronize ladder status
        if Status.PAINTED in self.ladder_status or Status.NOT_DRY in self.ladder_status:
            self.ladder_status.discard(Status.DRY)  # Remove dry if it's painted or not dry
            self.ladder_status.update({Status.PAINTED, Status.NOT_DRY})  # Ensure both painted and not dry are present

    def generate_condition_set(self):
        """Generate and store the set of string representations for all conditions in the state."""
        conditions = set()

        # Add the robot position condition
        if self.robot_position == RobotPosition.ON_FLOOR:
            conditions.add("On(Robot, Floor)")
        elif self.robot_position == RobotPosition.ON_LADDER:
            conditions.add("On(Robot, Ladder)")

        # Add ceiling status conditions
        if Status.PAINTED in self.ceiling_status:
            conditions.add("Painted(Ceiling)")
        if Status.DRY in self.ceiling_status:
            conditions.add("Dry(Ceiling)")
        if Status.NOT_DRY in self.ceiling_status:
            conditions.add("¬Dry(Ceiling)")

        # Add ladder status conditions
        if Status.PAINTED in self.ladder_status:
            conditions.add("Painted(Ladder)")
        if Status.DRY in self.ladder_status:
            conditions.add("Dry(Ladder)")
        if Status.NOT_DRY in self.ladder_status:
            conditions.add("¬Dry(Ladder)")

        # Update the condition set on the state
        self.condition_set = conditions

    # TODO: set this with Planner if appropriate so that the planner.operators can be used rather than duplicating precondition data definition here
    def get_condition_checks(self) -> Dict[str, Callable[[], bool]]:
        """Return a dictionary of condition checks specific to RobotPaintingState."""
        return {
            "On(Robot, Floor)": lambda: self.robot_position == RobotPosition.ON_FLOOR,
            "On(Robot, Ladder)": lambda: self.robot_position == RobotPosition.ON_LADDER,
            "Dry(Ceiling)": lambda: Status.DRY in self.ceiling_status,
            "¬Dry(Ceiling)": lambda: Status.NOT_DRY in self.ceiling_status,
            "Painted(Ceiling)": lambda: Status.PAINTED in self.ceiling_status,
            "Dry(Ladder)": lambda: Status.DRY in self.ladder_status,
            "¬Dry(Ladder)": lambda: Status.NOT_DRY in self.ladder_status,
            "Painted(Ladder)": lambda: Status.PAINTED in self.ladder_status
        }

    def is_goal_state(self, goal_state: 'RobotPaintingState') -> bool:
        """Check if current state matches the goal state."""
        return (self.robot_position == goal_state.robot_position and
                self.ceiling_status == goal_state.ceiling_status and
                self.ladder_status == goal_state.ladder_status)

    def apply_operator(self, operator: 'Operator') -> 'RobotPaintingState':
        """
        Apply an operator to the current state to produce a new state.
        Raises an error if the operator's preconditions are not met by the current state.
        """
        condition_checks = self.get_condition_checks()
        # Check if each precondition is met
        for precondition in operator.preconditions:
            if precondition not in condition_checks:
                raise ValueError(f"Unknown or unsupported precondition: {precondition}")

            if not condition_checks[precondition]():
                raise ValueError(f"Precondition '{precondition}' is not met.")

        # If all preconditions are met, apply the operator
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

        new_state = RobotPaintingState(new_robot_position, new_ceiling_status, new_ladder_status)
        new_state.sync_painted_dry_status()
        new_state.generate_condition_set()
        return new_state

    def check_if_state_clobbers_operator(self, operator_precondition: str) -> bool:
        """Check if the State conditions clobber the Operator preconditions."""

        # Check if the ladder is painted and not dry
        ladder_clobber_condition = Status.PAINTED in self.ladder_status or Status.NOT_DRY in self.ladder_status

        # Check for the specific operator and conditions
        if operator_precondition == "climb-ladder" and ladder_clobber_condition:
            return True  # The state clobbers the operator because the ladder is painted and not dry

        return False  # The state does not clobber the operator

    def check_if_state_matches_operator(self, operator: 'Operator') -> bool:
        """Check if State conditions match provided Operator preconditions using condition checks."""
        precondition = operator.precondition_for_reverse_search #ensuring just a single precondition for MVP simplicity # TODO: add multiple precondition handling
        if precondition in self.condition_set:
            return True
        return False

    def check_if_state_matches_goal_condition(self, goal_condition: str) -> bool:
        """Check if State conditions match provided Operator preconditions using condition checks."""
        # Check if the goal in condition set
        if goal_condition in self.condition_set:
            return True
        return False

    def return_eligible_goal_conditions(self) -> List[str]:
        """Returns list of conditions that are eligible for partial order plan"""
        return ['Painted(Ceiling)', 'Painted(Ladder)'] # example from robot instance - basically we don't also need to search for ¬Dry(Ceiling) etc too

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
