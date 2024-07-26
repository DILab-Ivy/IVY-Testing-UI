from __future__ import annotations
from typing_extensions import override
import openai
from openai import AssistantEventHandler
from openai.types.beta import AssistantStreamEvent
from openai.types.beta.threads import Text, TextDelta
from openai.types.beta.threads.runs import RunStep, RunStepDelta
import ast
from typing import List


# OpenAI Response Function
def get_mage_gpp_response(question: str) -> str:
    print(f"user_question: {question}")
    client = openai.OpenAI()
    response = ""

    def update_response(new_value):
        nonlocal response
        response += new_value

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
        log = ""

        # Check if the current state is valid
        curr_valid, curr_log = validate_state(curr_state)
        if not curr_valid:
            log = log + " " + curr_log
            return {"valid": valid_states, "invalid": invalid_states, "log":log}

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
            else:
                # If the new state is invalid, add it to the list of invalid states
                invalid_states.append(new_state)

        # Return the valid and invalid states
        result = {"valid": valid_states, "invalid": invalid_states, "log": log}
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
            # for char in delta.value:
            #     yield char
            print(delta.value, end="", flush=True)
            # print(delta.value, end="", flush=True)
            # # TODO: set up streaming directly to gradio vs building out response
            update_response(delta.value)
            # # yield delta.value

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

        def handle_requires_action(self, data, run_id, tool_id=None):
            def empty_args_error(tool):
                missing_arg_error_message = "Error: MissingArguments - No arguments provided. Please resubmit request with the required arguments."
                print(missing_arg_error_message)
                tool_outputs.append({"tool_call_id": tool.id, "output": missing_arg_error_message})


            tool_outputs = []

            for tool in data.required_action.submit_tool_outputs.tool_calls:
                print(f'tool.function.arguments: {tool.function.arguments}')
                if tool.function.name == "get_next_states":
                    print("get_next_states function called")
                    if len(tool.function.arguments) < 3:
                        empty_args_error(tool)
                        continue
                    # tool_outputs.append({"tool_call_id": tool.id, "output": "57"})
                    args = ast.literal_eval(tool.function.arguments)
                    try:
                        curr_state = args["state"]
                    except KeyError:
                        error_message = "Error: InvalidParameterName - Please resubmit with the required 'state' parameter"
                        print(error_message)
                        tool_outputs.append({"tool_call_id": tool.id, "output": error_message})
                        continue
                        # # TODO: if the above isn't working well or you don't want to re-call function constantly then you can simply grab the first provided argument
                        # args_values_list = list(args.values())
                        # curr_state = args_values_list[0]
                    function_output = get_next_states(curr_state)
                    function_output = str(function_output)
                    print(f"function_output: {function_output}")
                    tool_outputs.append({"tool_call_id": tool.id, "output": function_output})
                elif tool.function.name == "validate_state":
                    print("validate_state function called")
                    if len(tool.function.arguments) < 3:
                        empty_args_error(tool)
                        continue
                    # tool_outputs.append({"tool_call_id": tool.id, "output": "57"})
                    args = ast.literal_eval(tool.function.arguments)
                    try:
                        curr_state = args["state"]
                    except KeyError:
                        error_message = "Error: InvalidParameterName - Please resubmit with the required 'state' parameter"
                        print(error_message)
                        tool_outputs.append({"tool_call_id": tool.id, "output": error_message})
                        continue
                        # args_values_list = list(args.values())
                        # curr_state = args_values_list[0]
                    function_output, log = validate_state(curr_state)
                    function_output = str(function_output)
                    function_output = function_output + " " + log
                    print(f"function_output: {function_output}")
                    tool_outputs.append({"tool_call_id": tool.id, "output": function_output})

            # Submit all tool_outputs at the same time
            self.submit_tool_outputs(tool_outputs)

        def submit_tool_outputs(self, tool_outputs):
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

    ## Below can be used to create a new OAI assistant and define its interactions with functions
    # assistant = client.beta.assistants.create(
    #     name='GPP bot v11 - multi function handling',
    #     instructions="You are a helpful tutor who helps students understand the guards and prisoners problem. This is the guards and prisoners problem: In the guards and prisoners problem, m guards and n prisoners must cross a river using a boat which can carry at most two people, under the constraint that, for both banks, if there are guards present on the bank, they cannot be outnumbered by prisoners (if they were, the prisoners would overpower the guards). The boat cannot cross the river by itself with no people on board. Initially, all m guards and n prisoners are on the left side of the bank. We use the following notation to denote the situation: [3, 0, 3, 0, 0]. This means that there are [3 Guards on the left, 0 guards on the right, 3 prisoners on the left, 0 prisoners on the right, boat on the left]. You will be given access to a function called get_next_states that you can pass states to in order to find out the next states. Do not try to figure out next states on your own. You will be given access to a function called validate_state that you should use when you are asked whether a certain state is valid or legal. You should always use the functions to help you when asked questions relevant to them",
    #     model="gpt-4o",
    #     tools=[
    #         {
    #             "type": "function",
    #             "function": {
    #               "name": "get_next_states",
    #               "description": "get the next valid states possible after the current state for the guards and prisoners problem. returns a dict with both valid and invalid next states",
    #               "parameters": {
    #                 "type": "object",
    #                 "properties": {
    #                   "state": {
    #                     "type": "object",
    #                     "description": "the current state from which the next states will be generated. 'state' is a List[int] in the format [Guards Left, Guards Right, Prisoners Left, Prisoners Right, Boat Position] all integers and the Boat Position == 0 when the boat is on the left bank and Boat Position == 1 when the boat is on the right bank in the current state. eg 3 guards and 2 prisoners on the left bank and 0 guards and 1 prisoner on the right bank with the boat on the right bank would look like this [3,0,2,1,1]"
    #                   }
    #                 },
    #                 "required": [
    #                   "state"
    #                 ]
    #               }
    #             }
    #         },
    #         {
    #             "type": "function",
    #             "function": {
    #                 "name": "validate_state",
    #                 "description": "checks if a state in the guards and prisoners is valid or not and returns True if the state is valid and False if it isn't",
    #                 "parameters": {
    #                     "type": "object",
    #                     "properties": {
    #                         "state": {
    #                             "type": "object",
    #                             "description": "the current state that the function will check for validity. state is a List[int] in the format [Guards Left, Guards Right, Prisoners Left, Prisoners Right, Boat Position] all integers and the Boat Position == 0 when the boat is on the left bank and Boat Position == 1 when the boat is on the right bank in the current state. eg 3 guards and 2 prisoners on the left bank and 0 guards and 1 prisoner on the right bank with the boat on the right bank would look like this [3,0,2,1,1]"
    #                         }
    #                     },
    #                     "required": [
    #                         "state"
    #                     ]
    #                 }
    #             }
    #         },
    #     ]
    # )
    # ASSISTANT_ID = assistant.id
    # print(ASSISTANT_ID)
    # ASSISTANT_ID = "asst_KuvzrM2XDMLGAke8qknm1Xmt" #V10
    ASSISTANT_ID = "asst_2r1rHMIpTsnB9lJR1dYPGZOm"

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
        stream.until_done()
        # print()

    return response