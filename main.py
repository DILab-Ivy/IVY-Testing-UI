import os
import pathlib
import time
from datetime import datetime

import gradio as gr
import httpx
import boto3

if not os.getenv("MCM_URL"):
    raise ValueError("Please set the MCM_URL environment variable")

#Initializes a CSV logger and sets the path for logging flagged responses
# csv_logger = gr.CSVLogger()
# csv_path = pathlib.Path("flagged/log.csv")

#Encoded variables, TODO: need to integrate with a login interface
username = "Dummy Username"
session_id = '0'

#Initialize DynamoDB
dynamodb = boto3.resource('dynamodb')
login_table = dynamodb.Table('UserLogin')
chat_history_table = dynamodb.Table('ChatHistory')

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

    #Not integrated yet: Save Login data to dynamoDB
    def log_user_login(user_id, session_id):
        timestamp = time.time()
        dt = datetime.fromtimestamp(timestamp)
        timestamp = dt.strftime('%b-%d-%Y_%H:%M')
        login_data = {
            'Username': user_id,
            'SessionId': session_id,
            'Timestamp': timestamp
        }
        login_table.put_item(Item=login_data)

    def log_chat_history(user_id, session_id, question, response, reaction):
        timestamp = time.time()
        dt = datetime.fromtimestamp(timestamp)
        timestamp = dt.strftime('%b-%d-%Y_%H:%M')
        
        chat_data = {
            'Username': user_id,
            'SessionId': session_id,
            'Timestamp': timestamp,
            'Question': question,
            'Response': response,
            'Reaction': reaction
        }

        # Check if item exists and update or put item
        existing_item = chat_history_table.get_item(
            Key={
                'Username': user_id,
                'Timestamp': timestamp,
            }
        )
        
        if 'Item' in existing_item:
            update_chat_history(user_id, session_id, question, response, reaction)
            print("Chat data updated successfully")
        else:
            chat_history_table.put_item(Item=chat_data)
            print("Chat data logged successfully")

    def update_chat_history(user_id, session_id, question, response, reaction):
        timestamp = time.time()
        dt = datetime.fromtimestamp(timestamp)
        formatted_timestamp = dt.strftime('%b-%d-%Y_%H:%M')
        
        # Update item in DynamoDB
        response = chat_history_table.update_item(
            Key={
                'Username': user_id,
                'Timestamp': formatted_timestamp,
            },
            UpdateExpression='SET Reaction = :reaction',
            ExpressionAttributeValues={
                ':reaction': reaction
            },
            ReturnValues='UPDATED_NEW'
        )


    def update_user_message(user_message, history):
        return "", history + [[user_message, None]]

    def get_response_from_ivy(history):
        history[-1][1] = ""
        response = get_mcm_response(history[-1][0])
        for character in response:
            history[-1][1] += character
            time.sleep(0.008)
            yield history
        # Log to DynamoDB every interaction here
        log_chat_history(username, session_id, history[-1][0], history[-1][1], 'no_reaction')

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
        log_chat_history(username, session_id, question, response, 'liked')
        gr.Info("Saved successfully!")

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
        log_chat_history(username, session_id, question, response, 'disliked')
        gr.Info("Saved successfully!")


    def chat_liked_or_disliked(history, data: gr.LikeData):
        question = history[data.index[0]][0]
        response = history[data.index[0]][1]
        if data.liked:
            log_commended_response([[question, response]])
        else:
            log_flagged_response([[question, response]])

    #Additional Loggers and User Info using CSV Logger
    # commended_csv_logger = gr.CSVLogger()
    # flagged_csv_logger = gr.CSVLogger()
    # flagged_csv_path = pathlib.Path("flagged/log.csv")

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