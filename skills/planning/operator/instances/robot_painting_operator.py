from typing import List
from skills.planning import Operator

class RobotPaintingOperator(Operator):
    def __init__(self, name: str, preconditions: List[str], postconditions: List[str]):
        super().__init__(name, preconditions, postconditions)

    def _get_precondition_for_reverse_search(self) -> str:
        """Returns the 'On(Robot, ...)' precondition if it exists in the list of preconditions."""
        for precondition in self.preconditions:
            if precondition.startswith("On(Robot, "):
                return precondition
        return ""

    def _get_precondition_for_conflict_check(self) -> str:
        """Returns the first precondition related to 'Dry' or '¬Dry'."""
        for precondition in self.preconditions:
            if precondition.startswith("Dry"):
                return precondition
        return ""