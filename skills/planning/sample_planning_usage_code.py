# Example Planner function Usage
from skills.planning.operator.operator import Operator
from skills.planning.planning_solving_functions import generate_complete_plan
from skills.planning.state.instances.robot_painting_state import RobotPosition, Status
from skills.planning.state.state import State

# # Example State and Operator object usage
# # Define the initial state, goal state, and an example intermediate state
# start_state = State(
#     robot_position=RobotPosition.ON_FLOOR,
#     ceiling_status={Status.DRY},
#     ladder_status={Status.DRY}
# )
#
# goal_state = State(
#     robot_position=RobotPosition.ON_FLOOR,
#     ceiling_status={Status.PAINTED, Status.NOT_DRY},
#     ladder_status={Status.PAINTED, Status.NOT_DRY}
# )
start_state = ['On(Robot, Floor)', 'Dry(Ceiling)', 'Dry(Ladder)']
# TODO: during State creation, have Painted conditions automatically add ¬Dry conditions and remove Dry conditions
goal_state = ['On(Robot, Floor)', 'Painted(Ceiling)', 'Painted(Ladder)']

# Call generate_complete_plan for RobotPaintingPlanner
print("\nRobotPaintingPlanner:")
complete_plan_result = generate_complete_plan('robot', start_state, goal_state)
print(complete_plan_result)  # Output: Complete plan for robot

# Example intermediate state after climbing the ladder
intermediate_state = start_state.apply_operator(Operator(
    name="climb-ladder",
    preconditions=["On(Robot, Floor)", "Dry(Ladder)"],
    postconditions=["On(Robot, Ladder)"]
))

print("Start State:", start_state)
print("Intermediate State after climbing ladder:", intermediate_state)
print("Is Intermediate State Goal State?", intermediate_state.is_goal_state(goal_state))
