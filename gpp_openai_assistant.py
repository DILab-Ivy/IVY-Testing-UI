from __future__ import annotations

from typing_extensions import override

import openai
from openai import AssistantEventHandler
from openai.types.beta import AssistantStreamEvent
from openai.types.beta.threads import Text, TextDelta
from openai.types.beta.threads.runs import RunStep, RunStepDelta
import ast
from typing import List


client = openai.OpenAI()

def validate_state(curr_state: List[int], num_guards: int = 3, num_prisoners: int = 3) -> bool:
    """
    Check if the state is valid and print reasons
    """
    # Check if the number of guards are valid
    guard_l_valid = 0 <= curr_state[0] <= num_guards
    guard_r_valid = 0 <= curr_state[1] <= num_guards
    if not guard_l_valid or not guard_r_valid:
        print(
            f"Invalid state: {curr_state} - Number of guards are not between 0 and {num_guards}"
        )
        return False

    # Check if the number of prisoners are valid
    if not (0 <= curr_state[2] <= num_prisoners) or not (
            0 <= curr_state[3] <= num_prisoners
    ):
        print(
            f"Invalid state: {curr_state} - Number of prisoners are not between 0 and {num_prisoners}"
        )
        return False

    # Check the left side
    # Check if guards are present, and if so, check if there are more prisoners than guards
    if curr_state[0] > 0 and curr_state[0] < curr_state[2]:
        print(
            f"Invalid state: {curr_state} - Prisoners outnumber guards on left side"
        )
        return False

    # Check the right side
    # Check if guards are present, and if so, check if there are more prisoners than guards
    if curr_state[1] > 0 and curr_state[1] < curr_state[3]:
        print(
            f"Invalid state: {curr_state} - Prisoners outnumber guards on right side"
        )
        return False

    # If we get here, the state is valid
    return True

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

    # Check if the current state is valid
    if not validate_state(curr_state):
        return {"valid": valid_states, "invalid": invalid_states}

    # Check each possible move
    for move in [
        move_1_guard,
        move_1_prisoner,
        move_2_guards,
        move_2_prisoners,
        move_1_guard_1_prisoner,
    ]:
        new_state = move(curr_state)
        valid = validate_state(new_state)
        if valid:
            # If the new state is valid, add it to the list of valid states
            valid_states.append(new_state)
        else:
            # If the new state is invalid, add it to the list of invalid states
            invalid_states.append(new_state)

    # Return the valid and invalid states
    result = {"valid": valid_states, "invalid": invalid_states}
    print(f"result: {result}")
    return result


class EventHandler(AssistantEventHandler):
    @override
    def on_event(self, event: AssistantStreamEvent) -> None:
        if event.event == "thread.run.step.created":
            details = event.data.step_details
            if details.type == "tool_calls":
                print("Generating code to interpret:\n\n```py")
        elif event.event == 'thread.run.requires_action':
            print('requires action')
            run_id = event.data.id  # Retrieve the run ID from the event data
            self.handle_requires_action(event.data, run_id)
        elif event.event == "thread.message.created":
            print("\nResponse:\n")

    @override
    def on_text_delta(self, delta: TextDelta, snapshot: Text) -> None:
        print(delta.value, end="", flush=True)

    @override
    def on_run_step_done(self, run_step: RunStep) -> None:
        details = run_step.step_details
        if details.type == "tool_calls":
            for tool in details.tool_calls:
                if tool.type == "code_interpreter":
                    print("\n```\nExecuting code...")

    @override
    def on_run_step_delta(self, delta: RunStepDelta, snapshot: RunStep) -> None:
        details = delta.step_details
        if details is not None and details.type == "tool_calls":
            for tool in details.tool_calls or []:
                if tool.type == "code_interpreter" and tool.code_interpreter and tool.code_interpreter.input:
                    print(tool.code_interpreter.input, end="", flush=True)

    def handle_requires_action(self, data, run_id):
        tool_outputs = []

        # TODO: get this properly formatted for new function
        for tool in data.required_action.submit_tool_outputs.tool_calls:
            if tool.function.name == "get_next_states":
                # tool_outputs.append({"tool_call_id": tool.id, "output": "57"})
                args = ast.literal_eval(tool.function.arguments)
                curr_state = args["state"]
                function_output = get_next_states(curr_state)
                function_output = str(function_output)
                tool_outputs.append({"tool_call_id": tool.id, "output": function_output})
            elif tool.function.name == "validate_state":
                # tool_outputs.append({"tool_call_id": tool.id, "output": "57"})
                args = ast.literal_eval(tool.function.arguments)
                curr_state = args["state"]
                function_output = validate_state(curr_state)
                function_output = str(function_output)
                tool_outputs.append({"tool_call_id": tool.id, "output": function_output})

        # Submit all tool_outputs at the same time
        self.submit_tool_outputs(tool_outputs, run_id)

    def submit_tool_outputs(self, tool_outputs, run_id):
        # client = openai.OpenAI()
        # Use the submit_tool_outputs_stream helper
        with client.beta.threads.runs.submit_tool_outputs_stream(
                thread_id=self.current_run.thread_id,
                run_id=self.current_run.id,
                tool_outputs=tool_outputs,
                event_handler=EventHandler(),
        ) as stream:
            print('tool output submitted')
            for text in stream.text_deltas:
                pass
                # print(text, end="", flush=True)
            print()

# OpenAI Response Function
def get_openai_gpp_response(question: str) -> str:
    ASSISTANT_ID = "asst_iMCg2aqO343Sik6YWP3BDADq"

    # Load the existing assistant
    assistant = client.beta.assistants.retrieve(ASSISTANT_ID)

    thread = client.beta.threads.create(
        messages=[
            {
                "role": "user",
                "content": question,
            },
        ]
    )

    with client.beta.threads.runs.stream(
        thread_id=thread.id,
        assistant_id=assistant.id,
        event_handler=EventHandler(),
    ) as stream:
        response = ""
        for delta in stream.text_deltas:
            response += delta
        return response