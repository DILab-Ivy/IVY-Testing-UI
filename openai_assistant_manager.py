from __future__ import annotations
from typing_extensions import override
import openai
from openai import AssistantEventHandler
from openai.types.beta import AssistantStreamEvent
from openai.types.beta.threads import Text, TextDelta
from openai.types.beta.threads.runs import RunStep, RunStepDelta
import ast
from skills.semantic_networks.gpp_solving_functions import find_path_between_two_states, validate_state, get_next_states, empty_args_error, handle_get_next_states, handle_validate_state, handle_find_path_between_two_states
from skills.planning.planning_solving_functions import create_plan, apply_operator

# OpenAI Response Function
def get_mage_response(question: str) -> str:
    print(f"user_question: {question}")
    client = openai.OpenAI()
    response = ""

    def update_response(new_value):
        nonlocal response
        response += new_value

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
            handlers = {
                "get_next_states": handle_get_next_states,
                "validate_state": handle_validate_state,
                "find_path_between_two_states": handle_find_path_between_two_states
            }

            tool_outputs = []

            for tool in data.required_action.submit_tool_outputs.tool_calls:
                print(f'tool.function.arguments: {tool.function.arguments}')
                # Fetch the handler function from the dictionary using the function name
                handler = handlers.get(tool.function.name)

                if handler:
                    print(f"{tool.function.name} function called")
                    handler(tool, tool_outputs)  # Call the handler function
                else:
                    print(f"Unknown function name: {tool.function.name}")

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

    # ASSISTANT_ID = "asst_Hh9KFq4TgDdijln6CyTZgIlz" #v15
    ASSISTANT_ID = "asst_bTejWDz2qFjzlsjvLgmAACez"  # V18 tmk_str referencing

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
