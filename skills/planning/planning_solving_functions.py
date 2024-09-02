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
        # TODO: build in handling that will take partial states and then complete them with default values -
        #  eg. On(Robot, Floor), Painted(Ceiling) passed in but nothing for ladder -> just set Dry(Ladder) as default
        return RobotPaintingState.from_conditions_list(state_conditions_list)
    elif problem_type == 'blockworld':
        # return BlockWorldPlanner()
        raise ValueError("Blockworld State creation not implemented")
    else:
        raise ValueError("Unknown problem type. Please choose 'blockworld' or 'robot'.")

    #### TODO: Tuesday Sept 2
# TODO: merge with main functions or separate out duplicate code
def handle_create_plan(tool, tool_outputs):
    """
    Handler function to create a plan from start state to goal state.
    """
    try:
        # Extract arguments from tool function
        args = tool.function.arguments

        # Assuming arguments are passed as strings (state_conditions and operator)
        start_state_conditions, goal_state_conditions, problem_type = args.get('start_state_conditions'), args.get(
            'goal_state_conditions'), args.get('problem_type', 'robot')

        # Initialize Planner based on problem_type
        planner = _get_planner(problem_type)

        # Convert conditions string from agent into appropriate State instances based on problem type
        start_state = _get_state_object(problem_type, start_state_conditions)
        goal_conditions = goal_state_conditions

        plan_result = str(planner.build_complete_plan(start_state, goal_conditions))

        tool_outputs.append({"tool_call_id": tool.id, "output": plan_result})

    except ValueError as e:
        tool_outputs.append({"tool_call_id": tool.id, "output": f"Error: {e}"})
    except Exception as e:
        tool_outputs.append({"tool_call_id": tool.id, "output": f"An unexpected error occurred: {e}"})


def handle_apply_operator(tool, tool_outputs):
    """
    Handler function for applying an operator to a given state.
    """
    try:
        # Extract arguments from tool function
        args = tool.function.arguments

        # Assuming arguments are passed as strings (state_conditions and operator)
        start_state_conditions, operator, problem_type = args.get('start_state_conditions'), args.get(
            'operator'), args.get('problem_type', 'robot')

        # Initialize Planner based on problem_type
        planner = _get_planner(problem_type)

        # Convert conditions string from agent into appropriate State instances based on problem type
        start_state = _get_state_object(problem_type, start_state_conditions)
        result_state = copy.deepcopy(start_state)

        # Iterate through operators to find the matching one
        for i, op in enumerate(planner.operators.keys()):
            if operator == op:
                try:
                    result_state.apply_operator(planner.operators[op])
                except ValueError as error_message:
                    tool_outputs.append({
                        "tool_call_id": tool.id,
                        "output": f"The provided operator '{operator}' cannot be applied to start state '{start_state}' for the following reason: {error_message}"
                    })
                    return
                break
            if i == (len(planner.operators) - 1):
                tool_outputs.append({
                    "tool_call_id": tool.id,
                    "output": f"Error: Operator not valid for {problem_type} problem instance. Please resubmit tool call with the operator parameter set to a valid option from this list in the correct format: {str(list(planner.operators.keys()))}"
                })
                return

        tool_outputs.append({
            "tool_call_id": tool.id,
            "output": f"The result of applying the '{operator}' operator to start state '{start_state.__repr__()}' is the resulting state '{result_state.__repr__()}'"
        })

    except ValueError as e:
        tool_outputs.append({"tool_call_id": tool.id, "output": f"Error: {e}"})
    except Exception as e:
        tool_outputs.append({"tool_call_id": tool.id, "output": f"An unexpected error occurred: {e}"})


def apply_operator(start_state_conditions, operator, problem_type: str = 'robot'):
    # TODO: test questions: "what happens if i'm starting with the robot on the floor and the ladder painted and i try to climb the ladder?"

    #TODO: build error handling to check that all required conditions for each problem type and input are included and in correct format

    # Initialize Planner based on problem_type
    planner = _get_planner(problem_type)

    # Convert conditions string from agent into appropriate State instances based on problem type
    start_state = _get_state_object(problem_type, start_state_conditions)
    result_state = copy.deepcopy(start_state)

    for i, op in enumerate(planner.operators.keys()):
        if operator == op:
            try:
                result_state.apply_operator(planner.operators[op])
            except ValueError as error_message:
                return f"The provided operator '{operator}' cannot be applied to start state '{start_state}' for the following reason: {error_message}"
            break
        if i == (len(planner.operators) -1):
            # raise ValueError(f"Operator not valid for {problem_type}. Please resubmit a valid operator from this list in the correct format: {str(planner.operators)}")
            return f"Error: Operator not valid for {problem_type} problem instance. Please resubmit tool call with the operator parameter set to a valid option from this list in the correct format: {str(list(planner.operators.keys()))}"

    return f"The result of applying the '{operator}' operator to start state '{start_state.__repr__()}' is the resulting state '{result_state.__repr__()}'"




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