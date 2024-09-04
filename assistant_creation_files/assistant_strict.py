import json

from openai import OpenAI

client = OpenAI()
tmk = {
    "model": "Method",
    "methods": [
        {
            "name": "find_path_between_two_states",
            "description": "Finds a sequence of moves and state to move between current state and goal state. The state representation [num_guards_left_bank, num_guards_right_bank, num_prisoners_left_bank, num_prisoners_right_bank, boat_location]",
            "inputs": "The current state of the problem and the goal state of the problem",
            "outputs": "Sequence of moves and state to go from current state to goal state",
            "sub-methods": {
                "name": "get_next_states",
                "description": "Returns a set of valid next state and moves to get to those state from the given current state",
                "inputs": "The current state of the problem",
                "outputs": "Valid next state and moves to get to those state",
                "transitions": {
                    "validate_state": {
                        "description": "checks if given state is legal of not given problem constraints",
                        "type": "operation"
                    }
                }
            }
        }
    ]
}
tmk_str = json.dumps(tmk)
assistant = client.beta.assistants.create(
    name="GPP bot v19 - multi function handling w strict = True",
    instructions=f"You are a helpful tutor who helps students understand the guards and prisoners problem. This is the guards and prisoners problem: In the guards and prisoners problem, m guards and n prisoners must cross a river using a boat which can carry at most two people, under the constraint that, for both banks, if there are guards present on the bank, they cannot be outnumbered by prisoners (if they were, the prisoners would overpower the guards). The boat cannot cross the river by itself with no people on board. Initially, all m guards and n prisoners are on the left side of the bank. We use the following notation to denote the situation: [3, 0, 3, 0, 0]. This means that there are [3 Guards on the left, 0 guards on the right, 3 prisoners on the left, 0 prisoners on the right, boat on the left]. The last integer indicates the boat position: it is 0 when the boat is on the left bank and 1 when the boat is on the right bank. You will be given access to a function called get_next_states that you can pass state to in order to find out the next state. Do not try to figure out next state on your own. You will be given access to a function called validate_state that you should use when you are asked whether a certain state is valid or legal. You will be given access to a function called find_path_between_two_states that you should use to find a valid sequence of moves and state to move between a start_state and a goal_state. You should always use the functions to help you when asked questions relevant to them. Here is a TMK representation to help you understand the relationships between the functions you have access to: {tmk_str}. If you reference the functions to the user you can call them Methods, Sub-Methods and Transitions as appropriate based on this representation.",
    model="gpt-4o-2024-08-06",
    tools=[
        {
            "type": "function",
            "function": {
                "name": "get_next_states",
                "description": "get the next valid state possible after the current state for the guards and prisoners problem. returns a dict with both valid and invalid next state",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "state": {
                            "type": "list",
                            "description": "The city and state, e.g., San Francisco, CA"
                        }
                    },
                    "required": ["state"],
                    "additionalProperties": False
                },
                "strict": True
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_rain_probability",
                "description": "Get the probability of rain for a specific location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The city and state, e.g., San Francisco, CA"
                        }
                    },
                    "required": ["location"],
                    "additionalProperties": False
                },
                "strict": True
            }
        }
    ]
)

ASSISTANT_ID = assistant.id
print(ASSISTANT_ID)
client.beta.assistants._delete(ASSISTANT_ID)
