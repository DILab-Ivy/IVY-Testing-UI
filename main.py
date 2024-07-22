import os
import pathlib
import time

import gradio as gr
import httpx
import boto3

if not os.getenv("MCM_URL"):
    raise ValueError("Please set the MCM_URL environment variable")

#Initializes a CSV logger and sets the path for logging flagged responses
# csv_logger = gr.CSVLogger()
# csv_path = pathlib.Path("flagged/log.csv")

#Initialize DynamoDB
dynamodb = boto3.resource('dynamodb')
login_table = dynamodb.Table('User_Login')
chat_history_table = dynamodb.Table('Chat_History')

#Sends a POST request to the MCM, Returns response
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

#Save Login data to dynamoDB
def log_user_login(user_id, session_id):
    timestamp = int(time.time())
    login_data = {
        'user_id': user_id,
        'session_id': session_id,
        'timestamp': timestamp
    }
    login_table.put_item(Item=login_data)

#Additional Loggers and User Info using CSV Logger
# commended_csv_logger = gr.CSVLogger()
# flagged_csv_logger = gr.CSVLogger()
# flagged_csv_path = pathlib.Path("flagged/log.csv")
username = "Dummy Username"

#Gradio Interface Setup
with gr.Blocks() as demo:
    # Title
    gr.Markdown("# Ivy Chatbot")
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
    with gr.Row():
        submit = gr.Button(value="Submit", variant="primary")
        clear = gr.Button(value="Clear", variant="stop")
    with gr.Row():
        flag_btn = gr.Button(value="Flag last response", variant="secondary")
        download_btn = gr.Button(
            value="Download Flagged Responses",
            variant="secondary",
            link="/file=flagged/log.csv",
        )

#Function Definitions for Interaction
    def log_chat_history(user_id, session_id, question, response, reaction):
    timestamp = int(time.time())
    chat_data = {
        'user_id': user_id,
        'session_id': session_id,
        'timestamp': timestamp,
        'question': question,
        'response': response,
        'reaction': reaction
    }
    chat_history_table.put_item(Item=chat_data)

    def update_user_message(user_message, history):
        return "", history + [[user_message, None]]

    def get_response_from_ivy(history):
        history[-1][1] = ""
        response = get_mcm_response(history[-1][0])
        for character in response:
            history[-1][1] += character
            time.sleep(0.008)
            yield history

    # def log_commended_response(history):
    #     if len(history) == 0:
    #         return
    #     commended_csv_logger.flag(history[-1], username=username)
    #     gr.Info("Saved successfully!", duration=0.5)

    def log_commended_response(history):
        if len(history) == 0:
            return
        response = history[-1][1]
        question = history[-1][0]
        log_chat_history(username, 'session_id', question, response, 'liked')
        gr.Info("Saved successfully!", duration=0.5)

    # def log_flagged_response(history):
    #     if len(history) == 0:
    #         return
    #     flagged_csv_logger.flag(history[-1], username=username)
    #     gr.Info("Saved successfully!", duration=0.5)

    def log_flagged_response(history):
        if len(history) == 0:
            return
        response = history[-1][1]
        question = history[-1][0]
        log_chat_history(username, 'session_id', question, response, 'disliked')
        gr.Info("Saved successfully!", duration=0.5)


    def chat_liked_or_disliked(history, data: gr.LikeData):
        question = history[data.index[0]][0]
        response = history[data.index[0]][1]
        if data.liked:
            log_commended_response([[question, response]])
        else:
            log_flagged_response([[question, response]])

#Gradio Event Handling
    # commended_csv_logger.setup([msg, msg], "commended")
    # flagged_csv_logger.setup([msg, msg], "flagged")
    msg.submit(
        update_user_message, [msg, chatbot], [msg, chatbot], queue=False
    ).success(get_response_from_ivy, chatbot, chatbot)
    submit.click(
        update_user_message, [msg, chatbot], [msg, chatbot], queue=False
    ).success(get_response_from_ivy, chatbot, chatbot)
    chatbot.like(chat_liked_or_disliked, chatbot, None)
    clear.click(lambda: None, None, chatbot, queue=False)
    flag_btn.click(log_flagged_response, chatbot, None)

#Launch the Application
demo.queue()
demo.launch(allowed_paths=["flagged/", "commended/"])