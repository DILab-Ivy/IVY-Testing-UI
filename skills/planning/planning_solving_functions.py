# Dispatcher function
from skills.planning.planners.blockworld_planner import BlockWorldPlanner
from skills.planning.planners.planner import Planner
from skills.planning.planners.robot_painting_planner import RobotPaintingPlanner


def get_planner(problem_type: str) -> Planner:
    """Function to load planner for appropriate problem instance"""
    if problem_type == 'blockworld':
        return BlockWorldPlanner()
    elif problem_type == 'robot':
        return RobotPaintingPlanner()
    else:
        raise ValueError("Unknown problem type. Please choose 'blockworld' or 'robot'.")

# Wrapper functions that use the planner
def generate_plan(problem_type: str, start_state, goal_state):
    planner = get_planner(problem_type)
    return planner.generate_plan(start_state, goal_state)

def reorder_to_avoid(problem_type: str, obstacles):
    planner = get_planner(problem_type)
    return planner.reorder_to_avoid(obstacles)

def complete_plan(problem_type: str, partial_plan):
    planner = get_planner(problem_type)
    return planner.complete_plan(partial_plan)

def generate_complete_plan(problem_type: str, start_state, goal_state, obstacles):
    planner = get_planner(problem_type)
    return planner.generate_complete_plan(start_state, goal_state, obstacles)