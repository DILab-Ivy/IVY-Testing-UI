from skills.planning import Operator


class RobotPaintingOperator(Operator):
    def _get_precondition_for_reverse_search(self) -> str:
        return True