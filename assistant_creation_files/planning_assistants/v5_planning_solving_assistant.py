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
semantic_knowledge = {
  "conditions": {
    "On(Robot, Floor)": "Indicates that the robot is currently positioned on the floor.",
    "On(Robot, Ladder)": "Indicates that the robot is currently positioned on the ladder.",
    "Dry(Ladder)": "Indicates that the ladder is dry.",
    "¬Dry(Ladder)": "Indicates that the ladder is not dry. In this problem once an object is not dry, it can never be dry again. So this status is irreversible",
    "Painted(Ladder)": "Indicates that the ladder has been painted.",
    "Dry(Ceiling)": "Indicates that the ceiling is dry.",
    "¬Dry(Ceiling)": "Indicates that the ceiling is not dry. In this problem once an object is not dry, it can never be dry again. So this status is irreversible",
    "Painted(Ceiling)": "Indicates that the ceiling has been painted."
  },
  "operators": {
    "climb-ladder": {
      "preconditions": ["On(Robot, Floor)", "Dry(Ladder)"],
      "postconditions": ["On(Robot, Ladder)"],
      "description": "Allows the robot to climb the ladder, provided the ladder is dry and the robot is currently on the floor."
    },
    "descend-ladder": {
      "preconditions": ["On(Robot, Ladder)", "Dry(Ladder)"],
      "postconditions": ["On(Robot, Floor)"],
      "description": "Allows the robot to descend the ladder, provided the ladder is dry and the robot is currently on the ladder."
    },
    "paint-ceiling": {
      "preconditions": ["On(Robot, Ladder)"],
      "postconditions": ["Painted(Ceiling)", "¬Dry(Ceiling)"],
      "description": "Allows the robot to paint the ceiling if it is on the ladder, resulting in the ceiling becoming painted and not dry."
    },
    "paint-ladder": {
      "preconditions": ["On(Robot, Floor)"],
      "postconditions": ["Painted(Ladder)", "¬Dry(Ladder)"],
      "description": "Allows the robot to paint the ladder if it is on the floor, resulting in the ladder becoming painted and not dry."
    }
  }
}

tmk_str = json.dumps(tmk)
semantic_knowledge_str = json.dumps(semantic_knowledge)

# Creating a new OpenAI assistant and defining its interactions with functions for the Robot Painting Problem
assistant = client.beta.assistants.create(
    name='Planning bot v1 - multi function handling for robot problem',
    instructions=f"You are a helpful tutor who helps students understand and solve the Robot Painting Problem. In this problem, a robot must paint a ceiling and a ladder while adhering to specific constraints on movement and painting order. You have access to two functions: 'apply_operator' and 'create_plan'. You will use these functions to help students find solutions to the problem by simulating the actions of the robot and generating plans to achieve specific goals. Do not attempt to solve the problem on your own; always use the functions provided to simulate the robot's actions or generate plans. The function inputs sometimes require operators and conditions, you can find information on the valid operators and conditions here: {semantic_knowledge_str}. Make sure not to deviate from the provided operators and conditions. Here is a TMK representation to help you understand the relationships between the functions you have access to: {tmk_str}. If you reference these tools to the user then refer to the create_plan tool as an organizer and the apply_operator tool as an operator. Be as concise as possible. Just use a tool call and describe the output in a succinct manner. Always use the tool calls when they are relevant and never attempt to solve a problem on your own that can be solved with a tool call.",
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
