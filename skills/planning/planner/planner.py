import os
from abc import ABC, abstractmethod
from typing import List, Dict
import json

from skills.planning.plan import Plan
from skills.planning.operator.operator import Operator
from skills.planning.state.state import State


class Planner(ABC):
    def __init__(self):
        self.operators = self._generate_operators()
        self.partial_plans = []

    @abstractmethod
    def _generate_operators(self) -> Dict[str, 'Operator']:
        """Private method to load operator specific to the planner."""
        pass

    @abstractmethod
    def _get_json_filepath(self) -> str:
        """Abstract method to get the JSON file path for the operator."""
        pass

    def build_partial_plan(self, start_state: State, goal_condition: str) -> str:
        """Generate a plan from start_state to a goal_state satisfying a single goal condition"""
        partial_plan = Plan(start_state, goal_condition, self.operators)
        self.partial_plans.append(partial_plan)
        return partial_plan

    def reorder_partial_plans_list(self, plans: List[Plan]) -> None:
        """Reorder partial plans list to avoid conflicts."""
        pass

    def add_plan_to_top_of_list(self, plans: List[Plan]) -> None:
        """Reorder actions to avoid obstacles."""
        pass

    def slice_partial_plan(self, plan: Plan, start_operator_index: int) -> Plan:
        """Slices a partial plan down to certain steps and operators based on provided index"""
        pass

    def generate_complete_plan(self, start_state: State, goal_state: State) -> str:
        """
        Generate a complete plan using the generate_plan, reorder_to_avoid,
        and complete_plan methods.
        """
        pass