from __future__ import annotations
from typing import List


def find_path_between_two_states(start_state: List[int], goal_state: List[int]):
    """
    BFS to find sequence of legal moves to get from start_state to goal_state
    """
    explored = set()
    frontier = [[("start", start_state)]]
    while len(frontier) > 0:
        next_seq_to_explore = frontier.pop(0)
        curr_state = next_seq_to_explore[-1][1]
        # prev_move = next_seq_to_explore[-1][0]
        if tuple(curr_state) in explored:
            continue
        else:
            explored.add(tuple(curr_state))
            if curr_state == goal_state:
                print(f"Sequence between {start_state} and {goal_state} found: {next_seq_to_explore}")
                return next_seq_to_explore
            else:
                result_dict = get_next_states(curr_state=curr_state)
                valid_states = result_dict["valid"]
                moves = result_dict["moves"]
                if len(valid_states) > 0:
                    for i, state in enumerate(valid_states):
                        curr_sequence = next_seq_to_explore.copy()
                        curr_sequence.append((moves[i], state))
                        frontier.append(curr_sequence)

    return f"No sequence of legal moves found between {start_state} and {goal_state}"


def validate_state(curr_state: List[int], num_guards: int = 3, num_prisoners: int = 3) -> bool:
    """
    Check if the state is valid and print reasons
    """
    # Check if the number of guards are valid
    guard_l_valid = 0 <= curr_state[0] <= num_guards
    guard_r_valid = 0 <= curr_state[1] <= num_guards
    guard_total_valid = (curr_state[0] + curr_state[1]) == num_guards
    if not guard_l_valid or not guard_r_valid or not guard_total_valid:
        log = f"Invalid state: {curr_state} - Number of guards are not between 0 and {num_guards}"
        print(log)
        return False, log

    # Check if the number of prisoners are valid
    pris_l_valid = 0 <= curr_state[2] <= num_prisoners
    pris_r_valid = 0 <= curr_state[3] <= num_prisoners
    pris_total_valid = (curr_state[2] + curr_state[3]) == num_prisoners
    if not pris_l_valid or not pris_r_valid or not pris_total_valid:
        log = f"Invalid state: {curr_state} - Number of prisoners are not between 0 and {num_prisoners}"
        print(log)
        return False, log

    # Check the left side
    # Check if guards are present, and if so, check if there are more prisoners than guards
    if curr_state[0] > 0 and curr_state[0] < curr_state[2]:
        log = f"Invalid state: {curr_state} - Prisoners outnumber guards on left side"
        print(log)
        return False, log

    # Check the right side
    # Check if guards are present, and if so, check if there are more prisoners than guards
    if curr_state[1] > 0 and curr_state[1] < curr_state[3]:
        log = f"Invalid state: {curr_state} - Prisoners outnumber guards on right side"
        print(log)
        return False, log

    # If we get here, the state is valid
    log = f"Valid state: {curr_state} - This state is valid"
    return True, log


def get_next_states(
        curr_state: List[int]) -> List[List[int]]:
    """
    Curr state is in format [Guards Left, Guards Right, Prisoners Left, Prisoners Right, Boat Position]

    Returns a dict with both valid and invalid states
    """

    def move_1_guard(curr_state: List[int]) -> List[int]:
        """
        Move 1 guard to the other side
        """
        if curr_state[4] == 0:
            # If the boat is on the left side
            return [
                curr_state[0] - 1,
                curr_state[1] + 1,
                curr_state[2],
                curr_state[3],
                1 if curr_state[4] == 0 else 0,
            ]
        else:
            # If the boat is on the right side
            return [
                curr_state[0] + 1,
                curr_state[1] - 1,
                curr_state[2],
                curr_state[3],
                1 if curr_state[4] == 0 else 0,
            ]

    def move_1_prisoner(curr_state: List[int]) -> List[int]:
        """
        Move 1 prisoner to the other side
        """
        if curr_state[4] == 0:
            # If the boat is on the left side
            return [
                curr_state[0],
                curr_state[1],
                curr_state[2] - 1,
                curr_state[3] + 1,
                1 if curr_state[4] == 0 else 0,
            ]
        else:
            # If the boat is on the right side
            return [
                curr_state[0],
                curr_state[1],
                curr_state[2] + 1,
                curr_state[3] - 1,
                1 if curr_state[4] == 0 else 0,
            ]

    def move_2_guards(curr_state: List[int]) -> List[int]:
        """
        Move 2 guards to the other side
        """
        if curr_state[4] == 0:
            # If the boat is on the left side
            return [
                curr_state[0] - 2,
                curr_state[1] + 2,
                curr_state[2],
                curr_state[3],
                1 if curr_state[4] == 0 else 0,
            ]
        else:
            # If the boat is on the right side
            return [
                curr_state[0] + 2,
                curr_state[1] - 2,
                curr_state[2],
                curr_state[3],
                1 if curr_state[4] == 0 else 0,
            ]

    def move_2_prisoners(curr_state: List[int]) -> List[int]:
        """
        Move 2 prisoners to the other side
        """
        if curr_state[4] == 0:
            # If the boat is on the left side
            return [
                curr_state[0],
                curr_state[1],
                curr_state[2] - 2,
                curr_state[3] + 2,
                1 if curr_state[4] == 0 else 0,
            ]
        else:
            # If the boat is on the right side
            return [
                curr_state[0],
                curr_state[1],
                curr_state[2] + 2,
                curr_state[3] - 2,
                1 if curr_state[4] == 0 else 0,
            ]

    def move_1_guard_1_prisoner(curr_state: List[int]) -> List[int]:
        """
        Move 1 guard and 1 prisoner to the other side
        """
        if curr_state[4] == 0:
            # If the boat is on the left side
            return [
                curr_state[0] - 1,
                curr_state[1] + 1,
                curr_state[2] - 1,
                curr_state[3] + 1,
                1 if curr_state[4] == 0 else 0,
            ]
        else:
            # If the boat is on the right side
            return [
                curr_state[0] + 1,
                curr_state[1] - 1,
                curr_state[2] + 1,
                curr_state[3] - 1,
                1 if curr_state[4] == 0 else 0,
            ]

    curr_state = curr_state.copy()
    valid_states = []
    invalid_states = []
    valid_moves = []
    log = ""

    # Check if the current state is valid
    curr_valid, curr_log = validate_state(curr_state)
    if not curr_valid:
        log = log + " " + curr_log
        return {"valid": valid_states, "moves": valid_moves, "invalid": invalid_states, "log": log}

    # Check each possible move
    for move in [
        move_1_guard,
        move_1_prisoner,
        move_2_guards,
        move_2_prisoners,
        move_1_guard_1_prisoner,
    ]:
        new_state = move(curr_state)
        valid, valid_log = validate_state(new_state)
        log = log + " " + valid_log
        if valid:
            # If the new state is valid, add it to the list of valid states
            valid_states.append(new_state)
            valid_moves.append(move.__name__)
        else:
            # If the new state is invalid, add it to the list of invalid states
            invalid_states.append(new_state)

    # Return the valid and invalid states
    result = {"valid": valid_states, "moves": valid_moves, "invalid": invalid_states, "log": log}
    print(f"result: {result}")
    return result
