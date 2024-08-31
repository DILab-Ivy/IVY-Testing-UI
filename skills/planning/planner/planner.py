import os
from abc import ABC, abstractmethod
from collections import defaultdict, deque
from typing import List, Dict
import json

from skills.planning.plan import Plan
from skills.planning.operator.operator import Operator
from skills.planning.state.state import State


class Planner(ABC):
    def __init__(self):
        self.operators = self._generate_operators()
        self.partial_plans = []
        self.complete_plan = []

    @abstractmethod
    def _generate_operators(self) -> Dict[str, 'Operator']:
        """Private method to load operator specific to the planner."""
        pass

    @abstractmethod
    def _get_json_filepath(self) -> str:
        """Abstract method to get the JSON file path for the operator."""
        pass

    def build_partial_plan(self, start_state: State, goal_condition: str, add_to_complete=False) -> str:
        """Generate a plan from start_state to a goal_state satisfying a single goal condition"""
        partial_plan = Plan(start_state, goal_condition, self.operators)
        if add_to_complete:
            self.complete_plan.append(partial_plan)
        else:
            self.partial_plans.append(partial_plan)
        return partial_plan

    @abstractmethod
    def reorder_partial_plans_list(self) -> None:
        """Reorder partial plans list to avoid conflicts."""
        pass # TODO: just going to implement Robot shortcut for now - some implementation ideas are commented out below and could be used for more advanced implementations
        # TODO: set up instance specific implementations of this method -
        #  Blockworld has a shortcut where you can always prioritize Table involving operators first and then work upwards
        #  - but you could also look for way to handle this generally

        # TODO: figure out a better way to implement this in general - below will work for robot, but BW needs a custom implementation
        #  and below has issues that will break it will more complex planning instances
        # print('here')
        # final_plan_order = []
        # for i, plan in enumerate(self.partial_plans):
        #     for op in plan.operator_steps:
        #         # TODO: currently only set up to handle one conflict check condition, but could be refactored to handle multiple
        #         conflict_check_precondition = op.precondition_for_conflict_check
        #         for j, other_plan in enumerate(self.partial_plans):
        #             if i == j:
        #                 continue
        #             for state in other_plan.state_steps:
        #                 if state.check_if_state_clobbers_operator(conflict_check_precondition):
        #                    # if j is less than i that means the plan at index j is currently scheduled to be executed first
        #                    # since the j plan was just found to clobber the i plan, the i plan must be inserted in front of it in the list
        #                     if j < i:
        #                         final_plan_order.append(op)
        #                         final_plan_order.append(other_plan)

    #     """Reorder partial plans list to avoid conflicts."""
    #     # Step 1: Initialize the graph
    #     graph = defaultdict(list)  # Adjacency list representation of the graph
    #     in_degree = {plan: 0 for plan in self.partial_plans}  # Track the number of incoming edges (dependencies)
    #
    #     # Step 2: Detect conflicts and build the graph
    #     for i, plan in enumerate(self.partial_plans):
    #         for j, other_plan in enumerate(self.partial_plans):
    #             if i == j:
    #                 continue
    #
    #             # Check if there is a conflict between plan and other_plan
    #             if self._has_conflict(plan, other_plan):
    #                 # If there is a conflict, plan must be executed before other_plan
    #                 graph[plan].append(other_plan)
    #                 in_degree[other_plan] += 1
    #
    #     # Step 3: Topological sort to find the order of plans
    #     sorted_plans = self._topological_sort(graph, in_degree)
    #
    #     # Step 4: Reorder the partial_plans list based on the sorted order
    #     self.partial_plans = sorted_plans
    #
    # def _has_conflict(self, plan_a: Plan, plan_b: Plan) -> bool:
    #     """Check if there is a conflict between plan_a and plan_b."""
    #     for op in plan_a.operator_steps:
    #         conflict_precondition = op.precondition_for_conflict_check
    #         for state in plan_b.state_steps:
    #             if state.check_if_state_clobbers_operator(conflict_precondition):
    #                 return True
    #     return False
    #
    # def _topological_sort(self, graph: Dict[Plan, List[Plan]], in_degree: Dict[Plan, int]) -> List[Plan]:
    #     """Perform a topological sort on the graph to determine the order of plans."""
    #     queue = deque([plan for plan in self.partial_plans if in_degree[plan] == 0])
    #     sorted_plans = []
    #
    #     while queue:
    #         current_plan = queue.popleft()
    #         sorted_plans.append(current_plan)
    #
    #         for neighbor in graph[current_plan]:
    #             in_degree[neighbor] -= 1
    #             if in_degree[neighbor] == 0:
    #                 queue.append(neighbor)
    #
    #     if len(sorted_plans) != len(self.partial_plans):
    #         raise ValueError("Cycle detected in the plan dependency graph, indicating conflicting plans.")

    # def add_plan_to_top_of_list(self, plans: List[Plan]) -> None:
    #     """Reorder actions to avoid obstacles."""
    #     pass

    def slice_partial_plan(self, plan: Plan, start_operator_index: int) -> Plan:
        """Slices a partial plan down to certain steps and operators based on provided index"""
        # TODO: implement slice_partial_plan
        pass

    def build_complete_plan(self, start_state: State, goal_conditions: List[str]) -> List[Plan]:
        """
        Generate a complete plan using the generate_plan, reorder_to_avoid,
        and complete_plan methods.
        """
        # Step 1) Build out partial plans for all goal conditions (subgoals)
        for goal in goal_conditions:
            self.build_partial_plan(start_state, goal)

        # Step 2) Order plans to avoid conflicts
        self.reorder_partial_plans_list()

        # Step 3) Construct final plan
        self.complete_plan = []
        while len(self.partial_plans) > 0:
            curr_plan = self.partial_plans.pop(0)
            # TODO: optimize final plan representation for agent to understand complete plan
            #  and the plans that make it up, why they are ordered the way they are, highlight conflicts
            #  and highlight where two subgoal plans are connected together with extra operators
            self.complete_plan.append(curr_plan)
            if len(self.partial_plans) == 0:
                break

            # check if curr plan end state matches next plan's goal state, if so then that plan can be skipped
            while curr_plan.get_final_state().check_if_state_matches_goal_condition(
                    self.partial_plans[0].primary_goal):
                self.partial_plans.pop(0)

            # next, loop through the next plan's operators backwards until pre-condition found that matches curr_state
            next_plan = self.partial_plans.pop(0)
            next_plan_operator_steps_reversed = next_plan.operator_steps
            next_plan_operator_steps_reversed.reverse()
            for i, op in enumerate(next_plan_operator_steps_reversed):
                curr_plan_final_state = curr_plan.get_final_state()
                op_precondition = op.precondition_for_reverse_search
                if curr_plan_final_state.check_if_state_matches_goal_condition(
                        op_precondition):
                    # # TODO: implement slicing functionality so that work done on previous plan building can be used
                    # # slice plan so that we only include the operators and states we need to move from current state to next plan's goal condition
                    # sliced_plan = self.slice_partial_plan(next_plan, i * -1)
                    # complete_plan.append(sliced_plan)
                    # break
                    print('opportunity for more efficient plan found: implement self.slice_partial_plan in order to use it')
                else:
                    # if the beginning of the next plan is reached without finding a connection to our current state, then a connecting plan needs to be constructed
                    if i == len(next_plan_operator_steps_reversed) - 1:
                        self.partial_plans.insert(0, next_plan)
                        self.build_partial_plan(start_state=curr_plan_final_state,
                                                goal_condition=next_plan.operator_steps[0].precondition_for_reverse_search,
                                                add_to_complete=True)
        return self.complete_plan
