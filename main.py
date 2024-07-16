import os
import pathlib

import gradio as gr
import httpx
import openai
from typing import List

# Ensure environment variable is set
if not os.getenv("MCM_URL"):
    raise ValueError("Please set the MCM_URL environment variable")

# Initialize CSV Logger
csv_logger = gr.CSVLogger()
csv_path = pathlib.Path("flagged/log.csv")

# MCM Response Function
def get_mcm_response(question: str) -> str:
    response = httpx.post(
        mcm_url.value,
        json={
            "question": question,
            "api_key": mcm_api_key.value,
            "Episodic_Knowledge": {},
        },
        timeout=timeout_secs.value,
    )
    return response.json()["response"]

# OpenAI Response Function
def get_openai_response(question: str) -> str:
    client = openai.OpenAI()
    ASSISTANT_ID = "asst_iMCg2aqO343Sik6YWP3BDADq"

    class EventHandler(openai.AssistantEventHandler):
        def on_event(self, event: openai.types.beta.AssistantStreamEvent) -> None:
            pass

        def on_text_delta(self, delta: openai.types.beta.TextDelta, snapshot: openai.types.beta.threads.Text) -> None:
            pass

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
        assistant_id=ASSISTANT_ID,
        event_handler=EventHandler(),
    ) as stream:
        response = ""
        for delta in stream.text_deltas:
            response += delta.value
        return response

with gr.Blocks() as demo:
    # Title
    gr.Markdown("# Ivy Chatbot UI")

    # Settings
    with gr.Accordion("Settings", open=False):
        # MCM Settings
        with gr.Group("MCM Settings"):
            with gr.Row():
                # MCM URL
                mcm_url = gr.Textbox(
                    value=os.getenv("MCM_URL")
                    or "http://localhost:8001/ivy/ask_question",  # Default URL
                    label="MCM URL",
                    interactive=True,
                )
                # MCM API Key
                mcm_api_key = gr.Textbox(
                    value="123456789",
                    label="MCM API Key",
                    interactive=True,
                )

        with gr.Group("General Settings"):
            timeout_secs = gr.Slider(
                label="Timeout (seconds)",
                minimum=5,
                maximum=300,
                step=5,
                value=60,
                interactive=True,
            )

    # Chatbot Selection
    chatbot_selector = gr.Dropdown(
        choices=["MCM", "OpenAI"],
        value="MCM",
        label="Select Chatbot"
    )

    # Question Input
    question = gr.TextArea(
        label="Question", placeholder="Please type your question here..."
    )

    with gr.Row():
        # Output
        output = gr.TextArea(
            label="Output",
            placeholder="Answer will appear here...",
            show_copy_button=True,
        )

    with gr.Row():
        # Submit Button
        submit_button = gr.Button(value="Submit", variant="primary")
        # Clear Button
        clear_button = gr.Button(value="Clear", variant="stop")

    with gr.Row():
        # Flag
        flag_btn = gr.Button(value="Save For Review", variant="secondary")
        # Download
        download_btn = gr.DownloadButton(
            label="Download Logs", value=csv_path, visible=True
        )

    csv_logger.setup([question, output], "flagged")

    # Callbacks
    def on_submit_click(question, chatbot):
        if chatbot == "MCM":
            return get_mcm_response(question)
        elif chatbot == "OpenAI":
            return get_openai_response(question)
        return "Invalid selection"

    def on_clear_click():
        return "", ""

    def on_flag_click(*args):
        if not args[0] and not args[1]:
            gr.Warning("No data to save!")
            return

        csv_logger.flag(args)
        gr.Info("Saved successfully!")

    submit_button.click(on_submit_click, inputs=[question, chatbot_selector], outputs=[output])
    clear_button.click(on_clear_click, outputs=[question, output])
    flag_btn.click(
        on_flag_click,
        [question, output],
        None,
        preprocess=False,
    )

demo.launch()
