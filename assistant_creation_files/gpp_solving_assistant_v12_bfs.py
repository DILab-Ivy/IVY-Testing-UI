from __future__ import annotations
import openai

client = openai.OpenAI()
# Below can be used to create a new OAI assistant and define its interactions with functions
assistant = client.beta.assistants.create(
    name='GPP bot v12 - multi function handling',
    instructions="You are a helpful tutor who helps students understand the guards and prisoners problem. This is the guards and prisoners problem: In the guards and prisoners problem, m guards and n prisoners must cross a river using a boat which can carry at most two people, under the constraint that, for both banks, if there are guards present on the bank, they cannot be outnumbered by prisoners (if they were, the prisoners would overpower the guards). The boat cannot cross the river by itself with no people on board. Initially, all m guards and n prisoners are on the left side of the bank. We use the following notation to denote the situation: [3, 0, 3, 0, 0]. This means that there are [3 Guards on the left, 0 guards on the right, 3 prisoners on the left, 0 prisoners on the right, boat on the left]. You will be given access to a function called get_next_states that you can pass states to in order to find out the next states. Do not try to figure out next states on your own. You will be given access to a function called validate_state that you should use when you are asked whether a certain state is valid or legal. You will be given access to a function called find_path_between_two_states that you should use to find a valid sequence of moves and states to move between a start_state and a goal_state. You should always use the functions to help you when asked questions relevant to them",
    model="gpt-4o",
    tools=[
        {
            "type": "function",
            "function": {
              "name": "get_next_states",
              "description": "get the next valid states possible after the current state for the guards and prisoners problem. returns a dict with both valid and invalid next states",
              "parameters": {
                "type": "object",
                "properties": {
                  "state": {
                    "type": "object",
                    "description": "the current state from which the next states will be generated. 'state' is a List[int] in the format [Guards Left, Guards Right, Prisoners Left, Prisoners Right, Boat Position] all integers and the Boat Position == 0 when the boat is on the left bank and Boat Position == 1 when the boat is on the right bank in the current state. eg 3 guards and 2 prisoners on the left bank and 0 guards and 1 prisoner on the right bank with the boat on the right bank would look like this [3,0,2,1,1]"
                  }
                },
                "required": [
                  "state"
                ]
              }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "validate_state",
                "description": "checks if a state in the guards and prisoners is valid or not and returns True if the state is valid and False if it isn't",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "state": {
                            "type": "object",
                            "description": "the current state that the function will check for validity. state is a List[int] in the format [Guards Left, Guards Right, Prisoners Left, Prisoners Right, Boat Position] all integers and the Boat Position == 0 when the boat is on the left bank and Boat Position == 1 when the boat is on the right bank in the current state. eg 3 guards and 2 prisoners on the left bank and 0 guards and 1 prisoner on the right bank with the boat on the right bank would look like this [3,0,2,1,1]"
                        }
                    },
                    "required": [
                        "state"
                    ]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "find_path_between_two_states",
                "description": "finds the optimal sequence of valid moves and states to move between a given start_state and goal_state for the guards and prisoners problem. this function will return a string of valid moves and states that can be used to move from the start_state to the goal_state in the fewest number of moves and preventing backtracking",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "start_state": {
                            "type": "object",
                            "description": "the start state that the function will use as its starting place to search for a valid sequence of moves to get to the goal state. start_state is a List[int] in the format [Guards Left, Guards Right, Prisoners Left, Prisoners Right, Boat Position] all integers and the Boat Position == 0 when the boat is on the left bank and Boat Position == 1 when the boat is on the right bank in the current state. eg 3 guards and 2 prisoners on the left bank and 0 guards and 1 prisoner on the right bank with the boat on the right bank would look like this [3,0,2,1,1]"
                        },
                        "goal_state": {
                            "type": "object",
                            "description": "The goal state is the state that the function will attempt to find a valid sequence of moves to reach from the start_state. goal_state is a List[int] in the format [Guards Left, Guards Right, Prisoners Left, Prisoners Right, Boat Position] all integers and the Boat Position == 0 when the boat is on the left bank and Boat Position == 1 when the boat is on the right bank in the current state. eg 3 guards and 2 prisoners on the left bank and 0 guards and 1 prisoner on the right bank with the boat on the right bank would look like this [3,0,2,1,1]"
                        }
                    },
                    "required": [
                        "start_state",
                        "goal_state"
                    ]
                }
            }
        }

    ]
)
ASSISTANT_ID = assistant.id
print(ASSISTANT_ID)