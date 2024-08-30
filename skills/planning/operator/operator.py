import json
from typing import List, Dict
from abc import ABC, abstractmethod


class Operator:
    def __init__(self, name: str, preconditions: List[str], postconditions: List[str]):
        self.name = name
        self.preconditions = preconditions
        self.postconditions = postconditions
        self.dynamic = False #TODO: Blockworld will need dynamic Operators that can update based on context, Robot won't need these
        self.precondition_for_reverse_search = self._get_precondition_for_reverse_search()
        # self.precondition_for_conflict_check = self._get_precondition_for_conflict_check()

    def __repr__(self):
        return f"Operator(name={self.name}, preconditions={self.preconditions}, postconditions={self.postconditions})"

    @abstractmethod
    def _get_precondition_for_reverse_search(self) -> str:
        """Abstract method to get the JSON file path for the operator."""
        pass

    # @abstractmethod
    # def _get_precondition_for_conflict_check(self) -> str:
    #     """Abstract method to get the JSON file path for the operator."""
    #     pass