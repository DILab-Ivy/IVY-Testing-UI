# Example Planner function Usage
from skills.planning.operators.operator import Operator
from skills.planning.planning_solving_functions import generate_complete_plan
from skills.planning.states.robot_painting_state import RobotPosition, Status
from skills.planning.states.state import State

start_state = [["A", "B"], ["C"]]
goal_state = [["B"], ["A", "C"]]
obstacles = ["obstacle1", "obstacle2"]
partial_plan = ["move A to B"]

# Call generate_complete_plan for BlockWorldPlanner
print("BlockWorldPlanner:")
complete_plan_result = generate_complete_plan('blockworld', start_state, goal_state, obstacles)
print(complete_plan_result)  # Output: Complete plan for blockworld

# Call generate_complete_plan for RobotPaintingPlanner
print("\nRobotPaintingPlanner:")
complete_plan_result = generate_complete_plan('robot', start_state, goal_state, obstacles)
print(complete_plan_result)  # Output: Complete plan for robot



# Example State and Operator object usage
# Define the initial state, goal state, and an example intermediate state
initial_state = State(
    robot_position=RobotPosition.ON_FLOOR,
    ceiling_status={Status.DRY},
    ladder_status={Status.DRY}
)

goal_state = State(
    robot_position=RobotPosition.ON_FLOOR,
    ceiling_status={Status.PAINTED, Status.NOT_DRY},
    ladder_status={Status.PAINTED, Status.NOT_DRY}
)

# Example intermediate state after climbing the ladder
intermediate_state = initial_state.apply_operator(Operator(
    name="climb-ladder",
    preconditions=["On(Robot, Floor)", "Dry(Ladder)"],
    postconditions=["On(Robot, Ladder)"]
))

print("Initial State:", initial_state)
print("Intermediate State after climbing ladder:", intermediate_state)
print("Is Intermediate State Goal State?", intermediate_state.is_goal_state(goal_state))
