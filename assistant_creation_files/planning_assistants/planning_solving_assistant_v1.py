from __future__ import annotations
import openai
import json

client = openai.OpenAI()

# Define the Tool Method Knowledge (TMK) representation for the Robot Painting Problem
tmk = {
  "model": "Method",
  "methods": [
    {
      "name": "create_plan",
      "description": "Generates a plan to achieve the goal state from the start state in the Robot Painting Problem.",
      "inputs": "The initial conditions (start state) and desired outcomes (goal state) for the painting robot.",
      "outputs": "A sequence of actions that the robot should perform to achieve the goal state.",
      "sub-methods": {
        "name": "apply_operator",
        "description": "Applies an operator to the current state to simulate the next state in the Robot Painting Problem.",
        "inputs": "The current state and the operator to apply.",
        "outputs": "The resulting state after applying the operator.",
      }
    }
  ]
}
tmk_str = json.dumps(tmk)

# Creating a new OpenAI assistant and defining its interactions with functions for the Robot Painting Problem
assistant = client.beta.assistants.create(
    name='Planning bot v1 - multi function handling for robot problem',
    instructions=f"You are a helpful tutor who helps students understand and solve the Robot Painting Problem. In this problem, a robot must paint a ceiling and a ladder while adhering to specific constraints on movement and painting order. You have access to two functions: 'apply_operator' and 'create_plan'. You will use these functions to help students find solutions to the problem by simulating the actions of the robot and generating plans to achieve specific goals. Do not attempt to solve the problem on your own; always use the functions provided to simulate the robot's actions or generate plans. Here is a TMK representation to help you understand the relationships between the functions you have access to: {tmk_str}.",
    model="gpt-4o",
    tools=[
        {
            "type": "function",
            "function": {
              "name": "apply_operator",
              "description": "Applies an operator to the current state to simulate the next state in the Robot Painting Problem. This function returns the resulting state after applying the operator.",
              "parameters": {
                "type": "object",
                "properties": {
                  "start_conditions": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": "The current state of the robot and the painting surfaces. This is a list of strings representing the conditions, such as 'On(Robot, Floor)', 'Painted(Ceiling)', 'Dry(Ladder)', etc."
                  },
                  "operator": {
                    "type": "string",
                    "description": "The operator to apply, which represents an action the robot can perform, such as 'climb-ladder' or 'paint-ceiling'."
                  }
                },
                "required": [
                  "start_conditions",
                  "operator"
                ]
              }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "create_plan",
                "description": "Generates a plan to achieve the goal state from the start state in the Robot Painting Problem. This function returns a sequence of actions that the robot should perform to achieve the goal state.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "start_conditions": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            },
                            "description": "The initial state of the robot and the painting surfaces. This is a list of strings representing the conditions, such as 'On(Robot, Floor)', 'Painted(Ceiling)', 'Dry(Ladder)', etc."
                        },
                        "goal_conditions": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            },
                            "description": "The desired goal state that the robot should achieve. This is a list of strings representing the conditions, such as 'Painted(Ceiling)', 'Painted(Ladder)'."
                        }
                    },
                    "required": [
                        "start_conditions",
                        "goal_conditions"
                    ]
                }
            }
        }
    ]
)

ASSISTANT_ID = assistant.id
print(ASSISTANT_ID)