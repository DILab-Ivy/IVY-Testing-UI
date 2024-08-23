import os
import pathlib
import gradio as gr
import httpx
from openai_assistant_handling import get_mage_gpp_response


# TODO: merge with db handling branch

# Ensure environment variable is set
if not os.getenv("MCM_URL"):
    raise ValueError("Please set the MCM_URL environment variable")

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

# Gradio Interface Setup
with gr.Blocks() as demo:
    # Title
    gr.Markdown("# Ivy Virtual TA")
    # Settings
    with gr.Accordion("Settings", open=False):
        # MCM Settings
        with gr.Group("MCM Settings"):
            with gr.Row():
                # MCM URL
                mcm_url = gr.Textbox(
                    value=os.getenv("MCM_URL")
                          or "https://classification.dilab-ivy.com/ivy/ask_question",  # Default URL
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
        choices=["MCM", "MAGE - Episodic Query demo"],
        value="MAGE - Episodic Query demo",
        label="Select Agent",
        interactive=True
    )

    chatbot = gr.Chatbot(
        label="Your Conversation",
        show_copy_button=True,
        placeholder="Your conversations will appear here...",
    )

    msg = gr.Textbox(
        label="Question",
        placeholder="Please enter your question here...",
        show_copy_button=True,
        autofocus=True,
        show_label=True,
    )
    # with gr.Row():
    #     submit = gr.Button(value="Submit", variant="primary")
    #     clear = gr.Button(value="Clear", variant="stop")
    with gr.Row():
        flag_btn = gr.Button(value="Flag last response", variant="secondary")
        download_btn = gr.Button(
            value="Download Flagged Responses",
            variant="secondary",
            link="/file=flagged/log.csv",
        )


    def update_user_message(user_message, history):
        return "", history + [[user_message, None]]

    def get_response(history, chatbot_selector):
        if chatbot_selector == "MCM":
            history[-1][1] = ""
            response = get_mcm_response(history[-1][0])
            for character in response:
                history[-1][1] += character
                yield history
        elif chatbot_selector == "MAGE - Episodic Query demo":
            history[-1][1] = ""
            response_generator = get_mage_gpp_response(history[-1][0])
            for character in response_generator:
                history[-1][1] += character
                yield history

    def on_flag_click(*args):
        if not args[0] and not args[1]:
            gr.Warning("No data to save!")
            return

    msg.submit(
        update_user_message, [msg, chatbot], [msg, chatbot], queue=False
    ).success(get_response, [chatbot, chatbot_selector], chatbot)
    # submit.click(
    #     update_user_message, [msg, chatbot], [msg, chatbot], queue=False
    # ).success(get_response, chatbot, chatbot)

    # submit_button.click(on_submit_click, inputs=[msg, chatbot], outputs=[msg, chatbot])
    # clear.click(lambda: None, None, chatbot, queue=False)
    flag_btn.click(on_flag_click, chatbot, None)

#Launch the Application
demo.queue()
demo.launch(allowed_paths=["flagged/", "commended/"])
