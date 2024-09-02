import copy
import json
from typing import List

from skills.planning.planner.instances.blockworld_planner import BlockWorldPlanner
from skills.planning.planner.planner import Planner
from skills.planning.planner.instances.robot_painting_planner import RobotPaintingPlanner
from skills.planning.state.instances.robot_painting_state import RobotPaintingState
from skills.planning.state.state import State


def _get_planner(problem_type: str) -> Planner:
    """Function to load planner for appropriate problem instance"""
    if problem_type == 'robot':
        return RobotPaintingPlanner()
    elif problem_type == 'blockworld':
        # return BlockWorldPlanner()
        raise ValueError("Blockworld planner not implemented")
    else:
        raise ValueError("Unknown problem type. Please choose 'blockworld' or 'robot'.")

def _get_state_object(problem_type: str, state_conditions_list: str) -> State:
    """Function to load State object for appropriate problem instance"""
    if problem_type == 'robot':
        return RobotPaintingState.from_conditions_list(state_conditions_list)
    elif problem_type == 'blockworld':
        # return BlockWorldPlanner()
        raise ValueError("Blockworld State creation not implemented")
    else:
        raise ValueError("Unknown problem type. Please choose 'blockworld' or 'robot'.")

def apply_operator(start_state_conditions, operator, problem_type: str = 'robot'):
    #TODO: build error handling to check that all required conditions for each problem type and input are included and in correct format

    # Initialize Planner based on problem_type
    planner = _get_planner(problem_type)

    # Convert conditions string from agent into appropriate State instances based on problem type
    start_state = _get_state_object(problem_type, start_state_conditions)
    result_state = copy.deepcopy(start_state)

    for i, op in enumerate.planner.operators:
        if operator == op:
            result_state.apply_operator(op)
            break
        if i == (len(planner.operators) -1):
            # raise ValueError(f"Operator not valid for {problem_type}. Please resubmit a valid operator from this list in the correct format: {str(planner.operators)}")
            return f"Error: Operator not valid for {problem_type} problem instance. Please resubmit a valid operator from this list in the correct format: {str(planner.operators)}"

    return f"The result of applying {operator} to {start_state.__repr__()} is {result_state.__repr__()}"




def create_plan(start_state_conditions, goal_state_conditions, problem_type: str = 'robot'):
    #TODO: build error handling to check that all required conditions for each problem type and input are included and in correct format

    # Initialize Planner based on problem_type
    planner = _get_planner(problem_type)

    # TODO: set up conditions for function call - basically handle converting agent inputs for robot and blockworld here to correct format for function
    # Convert conditions string from agent into appropriate State instances based on problem type
    start_state = _get_state_object(problem_type, start_state_conditions)
    goal_conditions = goal_state_conditions
    # goal_state = get_state_object(problem_type, goal_state_conditions)

    return str(planner.build_complete_plan(start_state, goal_conditions))

# Wrapper functions that use the planner
# def build_partial_plan(problem_type: str, start_state_conditions: str, goal_state_conditions: str):
#     pass
#     # # Initialize Planner based on problem_type
#     # planner = get_planner(problem_type)
#     #
#     # # Convert conditions string from agent into appropriate State instances based on problem type
#     # start_state = get_state_object(problem_type, start_state_conditions)
#     # goal_state = get_state_object(problem_type, goal_state_conditions)
#
#     # return planner.build_partial_plan(start_state, goal_state)

# def reorder_plans_to_avoid_conflicts(problem_type: str, plans: List[List[str]]):
#     # planner = get_planner(problem_type)
#     # return planner.reorder_partial_plans(plans)
#     pass