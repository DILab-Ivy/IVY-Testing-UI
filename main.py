import os
import pathlib

import gradio as gr
import httpx

if not os.getenv("MCM_URL"):
    raise ValueError("Please set the MCM_URL environment variable")

csv_logger = gr.CSVLogger()
csv_path = pathlib.Path("flagged/log.csv")


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
    def on_submit_click(question):
        return get_mcm_response(question)

    def on_clear_click():
        return "", ""

    def on_flag_click(*args):
        if not args[0] and not args[1]:
            gr.Warning("No data to save!")
            return

        csv_logger.flag(args)
        gr.Info("Saved successfully!")

    submit_button.click(on_submit_click, inputs=[question], outputs=[output])
    clear_button.click(on_clear_click, outputs=[question, output])
    flag_btn.click(
        on_flag_click,
        [question, output],
        None,
        preprocess=False,
    )

demo.launch()
