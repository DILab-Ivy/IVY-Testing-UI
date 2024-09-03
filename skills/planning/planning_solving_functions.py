import copy
import json
from typing import List
import ast

from skills.planning.planner.instances.blockworld_planner import BlockWorldPlanner
from skills.planning.planner.planner import Planner
from skills.planning.planner.instances.robot_painting_planner import RobotPaintingPlanner
from skills.planning.state.instances.robot_painting_state import RobotPaintingState
from skills.planning.state.state import State

# Valid conditions list
VALID_CONDITIONS = [
    'Dry(Ladder)', '¬Dry(Ladder)', 'Dry(Ceiling)', '¬Dry(Ceiling)',
    'Painted(Ladder)', 'Painted(Ceiling)', 'On(Robot, Floor)', 'On(Robot, Ladder)'
]


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

def apply_operator(start_state_conditions, operator, problem_type: str = 'robot'):
    # TODO: test questions: "what happens if i'm starting with the robot on the floor and the ladder painted and i try to climb the ladder?"

    #TODO: build error handling to check that all required conditions for each problem type and input are included and in correct format

    # Initialize Planner based on problem_type
    planner = _get_planner(problem_type)

    try:
        # Convert conditions string from agent into appropriate State instances based on problem type
        start_state = _get_state_object(problem_type, start_state_conditions)
    except ValueError as error_message:
        return f"Error: The start state conditions are invalid: {error_message}"

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
    # Initialize Planner based on problem_type
    try:
        planner = _get_planner(problem_type)
        try:
            # Convert conditions string from agent into appropriate State instances based on problem type
            start_state = _get_state_object(problem_type, start_state_conditions)
        except ValueError as error_message:
            return f"Error: The start state conditions are invalid: {error_message}"

        goal_conditions = goal_state_conditions

        # Try to build the complete plan using the planner
        try:
            complete_plan = planner.build_complete_plan(start_state, goal_conditions)
        except ValueError as error_message:
            return f"Error: The plan could not be created due to an issue: {error_message}"

    except ValueError as error_message:
        return f"Error: {error_message}"

    return str(complete_plan)

def empty_args_error(tool, tool_outputs):
    missing_arg_error_message = "Error: MissingArguments - No arguments provided. Please resubmit request with the required arguments."
    print(missing_arg_error_message)
    tool_outputs.append({"tool_call_id": tool.id, "output": missing_arg_error_message})

def handle_apply_operator(tool, tool_outputs):
    if len(tool.function.arguments) < 3:
        empty_args_error(tool, tool_outputs)
        return

    args = ast.literal_eval(tool.function.arguments)
    try:
        start_conditions = args["start_conditions"]
        operator_name = args["operator"]

        # Validate the input format
        if not isinstance(start_conditions, list) or not all(isinstance(cond, str) for cond in start_conditions):
            raise ValueError("Invalid format for 'start_conditions'. It must be a list of strings.")
        if not isinstance(operator_name, str):
            raise ValueError("Invalid format for 'operator'. It must be a string.")

        # Ensure start_conditions only contain valid conditions
        invalid_conditions = [cond for cond in start_conditions if cond not in VALID_CONDITIONS]
        if invalid_conditions:
            raise ValueError(
                f"Invalid condition(s) detected: {invalid_conditions}. Please use conditions from the list: {VALID_CONDITIONS}.")

        # Ensure exactly one "On(Robot, {location})" condition
        robot_conditions = [cond for cond in start_conditions if cond.startswith("On(Robot, ")]
        if len(robot_conditions) != 1 or not any(location in robot_conditions[0] for location in ["Floor", "Ladder"]):
            raise ValueError(
                "Exactly one valid 'On(Robot, {location})' condition must be provided, where location is either 'Floor' or 'Ladder'.")

        # Check ladder conditions, default to "Dry(Ladder)" if not provided
        ladder_conditions = [cond for cond in start_conditions if "Ladder" in cond]
        if not ladder_conditions:
            start_conditions.append("Dry(Ladder)")
        elif "Dry(Ladder)" in ladder_conditions and (
                "Painted(Ladder)" in ladder_conditions or "¬Dry(Ladder)" in ladder_conditions):
            raise ValueError(
                "Invalid ladder conditions: 'Dry(Ladder)' cannot be combined with 'Painted(Ladder)' or '¬Dry(Ladder)'.")

        # Check ceiling conditions, default to "Dry(Ceiling)" if not provided
        ceiling_conditions = [cond for cond in start_conditions if "Ceiling" in cond]
        if not ceiling_conditions:
            start_conditions.append("Dry(Ceiling)")
        elif "Dry(Ceiling)" in ceiling_conditions and (
                "Painted(Ceiling)" in ceiling_conditions or "¬Dry(Ceiling)" in ceiling_conditions):
            raise ValueError(
                "Invalid ceiling conditions: 'Dry(Ceiling)' cannot be combined with 'Painted(Ceiling)' or '¬Dry(Ceiling)'.")

        # Check if operator exists in planner.operators
        planner = RobotPaintingPlanner()  # Assuming the planner is always RobotPaintingPlanner
        if operator_name not in planner.operators.keys():
            raise ValueError(f"Invalid operator '{operator_name}'. Must be one of: {list(planner.operators.keys())}")

    except KeyError:
        error_message = "Error: InvalidParameterName - Please resubmit with the required 'start_conditions' and 'operator' parameters."
        print(error_message)
        tool_outputs.append({"tool_call_id": tool.id, "output": error_message})
        return
    except ValueError as error_message:
        tool_outputs.append({"tool_call_id": tool.id, "output": str(error_message)})
        return

    function_output = apply_operator(start_conditions, operator_name, problem_type='robot')
    function_output = f"{function_output}"
    print(f"function_output: {function_output}")
    tool_outputs.append({"tool_call_id": tool.id, "output": function_output})

# TODO: merge with main functions or separate out duplicate code
def handle_create_plan(tool, tool_outputs):
    if len(tool.function.arguments) < 3:
        empty_args_error(tool, tool_outputs)
        return

    args = ast.literal_eval(tool.function.arguments)
    try:
        start_conditions = args["start_conditions"]
        goal_conditions = args["goal_conditions"]

        # Validate the input format
        if not isinstance(start_conditions, list) or not all(isinstance(cond, str) for cond in start_conditions):
            raise ValueError("Invalid format for 'start_conditions'. It must be a list of strings.")

        if not isinstance(goal_conditions, list) or not all(isinstance(cond, str) for cond in goal_conditions):
            raise ValueError("Invalid format for 'goal_conditions'. It must be a list of strings.")

        # Ensure start_conditions and goal_conditions only contain valid conditions
        invalid_start_conditions = [cond for cond in start_conditions if cond not in VALID_CONDITIONS]
        invalid_goal_conditions = [cond for cond in goal_conditions if cond not in VALID_CONDITIONS]
        if invalid_start_conditions:
            raise ValueError(
                f"Invalid start condition(s) detected: {invalid_start_conditions}. Please use conditions from the list: {VALID_CONDITIONS}.")
        if invalid_goal_conditions:
            raise ValueError(
                f"Invalid goal condition(s) detected: {invalid_goal_conditions}. Please use conditions from the list: {VALID_CONDITIONS}.")

        # Ensure exactly one "On(Robot, {location})" condition
        robot_conditions = [cond for cond in start_conditions if cond.startswith("On(Robot, ")]
        if len(robot_conditions) != 1 or not any(
                location in robot_conditions[0] for location in ["Floor", "Ladder"]):
            raise ValueError(
                "Exactly one valid 'On(Robot, {location})' condition must be provided, where location is either 'Floor' or 'Ladder'.")

        # Check ladder conditions, default to "Dry(Ladder)" if not provided
        ladder_conditions = [cond for cond in start_conditions if "Ladder" in cond]
        if not ladder_conditions:
            start_conditions.append("Dry(Ladder)")
        elif "Dry(Ladder)" in ladder_conditions and (
                "Painted(Ladder)" in ladder_conditions or "¬Dry(Ladder)" in ladder_conditions):
            raise ValueError(
                "Invalid ladder conditions: 'Dry(Ladder)' cannot be combined with 'Painted(Ladder)' or '¬Dry(Ladder)'.")

        # Check ceiling conditions, default to "Dry(Ceiling)" if not provided
        ceiling_conditions = [cond for cond in start_conditions if "Ceiling" in cond]
        if not ceiling_conditions:
            start_conditions.append("Dry(Ceiling)")
        elif "Dry(Ceiling)" in ceiling_conditions and (
                "Painted(Ceiling)" in ceiling_conditions or "¬Dry(Ceiling)" in ceiling_conditions):
            raise ValueError(
                "Invalid ceiling conditions: 'Dry(Ceiling)' cannot be combined with 'Painted(Ceiling)' or '¬Dry(Ceiling)'.")

        # Check if goal_conditions include "Painted(Ceiling)" or "Painted(Ladder)"
        if not any(cond in goal_conditions for cond in ["Painted(Ceiling)", "Painted(Ladder)"]):
            raise ValueError("Goal conditions must include at least 'Painted(Ceiling)' or 'Painted(Ladder)'.")

    except KeyError:
        error_message = "Error: InvalidParameterName - Please resubmit with the required 'start_conditions' and 'goal_conditions' parameters"
        print(error_message)
        tool_outputs.append({"tool_call_id": tool.id, "output": error_message})
        return
    except ValueError as error_message:
        tool_outputs.append({"tool_call_id": tool.id, "output": str(error_message)})
        return

    function_output = create_plan(start_conditions, goal_conditions, problem_type='robot')
    function_output = f"{function_output}"
    print(f"function_output: {function_output}")
    tool_outputs.append({"tool_call_id": tool.id, "output": function_output})




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