import os
import pathlib
import time
from datetime import datetime, timezone

import gradio as gr
import httpx
import boto3
import requests
import base64
import csv
import tempfile
import uvicorn

from fastapi import FastAPI
from starlette.responses import RedirectResponse

REQUIRED_ENV_VARS = ["COGNITO_LOCALHOST_CLIENT_SECRET", "COGNITO_PROD_CLIENT_SECRET"]
for env_var in REQUIRED_ENV_VARS:
    if not os.getenv(env_var):
        raise ValueError(f"Please set the {env_var} environment variable")

# If is_developer_view is True then there's additional functionalities available.
IS_DEVELOPER_VIEW = True
ON_LOCALHOST = False
MCM_URL = "https://classification.dilab-ivy.com/ivy/ask_question"
SKILL_NAME_TO_MCM_URL = {
    "Classification": "https://classification.dilab-ivy.com/ivy/ask_question",
    "Incremental Concept Learning": "https://icl.dilab-ivy.com/ivy/ask_question",
    "Means End Analysis": "https://mea.dilab-ivy.com/ivy/ask_question",
    "Semantic Networks": "https://gpp.dilab-ivy.com/ivy/ask_question",
}

COGNITO_DOMAIN = "https://ivy.auth.us-east-1.amazoncognito.com"
URL_CODE = ""
ACCESS_TOKEN = ""
REDIRECT_URL = (
    "http://localhost:8000/ask-ivy" if ON_LOCALHOST else "https://dev.dilab-ivy.com"
)
CLIENT_ID = (
    "60p8a9bvteiihrd8g89r5ggabi" if ON_LOCALHOST else "2d7ah9kttong2hdlt4olhtao4d"
)
CLIENT_SECRET = (
    os.getenv("COGNITO_LOCALHOST_CLIENT_SECRET")
    if ON_LOCALHOST
    else os.getenv("COGNITO_PROD_CLIENT_SECRET")
)
LOGIN_URL = (
    COGNITO_DOMAIN
    + f"/login?response_type=code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URL}"
)
GET_ACCESS_TOKEN_URL = COGNITO_DOMAIN + "/oauth2/token"
GET_USER_INFO_URL = COGNITO_DOMAIN + "/oauth2/userInfo"

USER_NAME = ""
USERNAME = ""
USER_EMAIL = ""


# Initialize DynamoDB
dynamodb = boto3.resource("dynamodb")
login_table = dynamodb.Table("UserLogin")
chat_history_table = dynamodb.Table("ChatHistory")

app = FastAPI()


@app.get("/")
def read_main():
    return RedirectResponse(url=LOGIN_URL)


def get_access_token_and_user_info(url_code):
    global URL_CODE
    URL_CODE = url_code
    access_token_data = {
        "grant_type": "authorization_code",
        "client_id": CLIENT_ID,
        "code": URL_CODE,
        "redirect_uri": REDIRECT_URL,
    }
    access_token_headers = {
        "Authorization": "Basic "
        + base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode("ascii")).decode(
            "ascii"
        ),
        "Content-Type": "application/x-www-form-urlencoded",
    }

    def get_user_info_header(access_token):
        return {
            "Authorization": "Bearer " + access_token,
            "Content-Type": "application/x-amz-json-1.1",
        }

    try:
        # Get Access Token
        response = requests.post(
            GET_ACCESS_TOKEN_URL, data=access_token_data, headers=access_token_headers
        )
        access_token = response.json()["access_token"]
        global ACCESS_TOKEN
        ACCESS_TOKEN = access_token

        # Get User Info
        response = requests.get(
            GET_USER_INFO_URL, headers=get_user_info_header(access_token)
        ).json()
        global USER_NAME
        global USERNAME
        global USER_EMAIL
        USER_NAME, USERNAME, USER_EMAIL = (
            response["name"],
            response["username"],
            response["email"],
        )
        return True
    except Exception as e:
        print(str(e))
        return False


# Sends a POST request to the MCM, Returns response
def get_mcm_response(question: str) -> str:
    response = httpx.post(
        MCM_URL,
        json={
            "question": question,
            "api_key": mcm_api_key.value,
            "Episodic_Knowledge": {},
        },
        timeout=timeout_secs.value,
    )
    return response.json()["response"]


# Gradio Interface Setup
with gr.Blocks() as ivy_main_page:
    # Title
    welcome_msg = gr.Markdown()
    # Settings
    with gr.Row():
        mcm_skill = gr.Dropdown(
            choices=SKILL_NAME_TO_MCM_URL.keys(),
            value="Classification",
            multiselect=False,
            label="Skill",
            interactive=True,
        )
        with gr.Accordion("Settings", open=False, visible=IS_DEVELOPER_VIEW):
            # MCM Settings
            with gr.Group("MCM Settings"):
                with gr.Row():
                    # MCM API Key
                    mcm_api_key = gr.Textbox(
                        value="123456789",
                        label="MCM API Key",
                        interactive=True,
                    )
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
        flag_btn = gr.Button(
            value="Flag last response", variant="secondary", visible=IS_DEVELOPER_VIEW
        )
        download_btn = gr.Button(
            value="Download Flagged Responses",
            variant="secondary",
            visible=IS_DEVELOPER_VIEW,
        )

    def on_page_load(request: gr.Request):
        if "code" not in dict(request.query_params):
            # (TODO): Redirect to login page
            return "Go back to login page"
        url_code = dict(request.query_params)["code"]
        if not get_access_token_and_user_info(url_code):
            # (TODO): Redirect to Login page or display Error page
            return "An Error Occurred"
        return f"# Welcome to Ivy Chatbot, {USER_NAME}"

    def log_user_login(user_id, session_id):
        timestamp = time.time()
        dt = datetime.fromtimestamp(timestamp)
        timestamp = dt.strftime("%b-%d-%Y_%H:%M")
        login_data = {
            "Username": user_id,
            "SessionId": session_id,
            "Timestamp": timestamp,
        }
        login_table.put_item(Item=login_data)

    def log_chat_history(user_id, session_id, question, response, reaction):
        timestamp = time.time()
        dt = datetime.fromtimestamp(timestamp)
        timestamp = dt.strftime("%b-%d-%Y_%H:%M")

        chat_data = {
            "Username": user_id,
            "SessionId": session_id,
            "Timestamp": timestamp,
            "Question": question,
            "Response": response,
            "Reaction": reaction,
        }

        # Check if item exists and update or put item
        existing_item = chat_history_table.get_item(
            Key={
                "Username": user_id,
                "Timestamp": timestamp,
            }
        )

        if "Item" in existing_item:
            update_chat_history(user_id, session_id, question, response, reaction)
            print("Chat data updated successfully")
        else:
            chat_history_table.put_item(Item=chat_data)
            print("Chat data logged successfully")

    def update_chat_history(user_id, session_id, question, response, reaction):
        timestamp = time.time()
        dt = datetime.fromtimestamp(timestamp)
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%S")

        # Update item in DynamoDB
        response = chat_history_table.update_item(
            Key={
                "Username": user_id,
                "Timestamp": timestamp,
            },
            UpdateExpression="SET Reaction = :reaction",
            ExpressionAttributeValues={":reaction": reaction},
            ReturnValues="UPDATED_NEW",
        )

    def update_user_message(user_message, history):
        return "", history + [[user_message, None]]

    def get_response_from_ivy(history):
        history[-1][1] = ""
        response = get_mcm_response(history[-1][0])
        for character in response:
            history[-1][1] += character
            time.sleep(0.005)
            yield history
        # Log to DynamoDB every interaction here
        log_chat_history(
            USERNAME, ACCESS_TOKEN, history[-1][0], history[-1][1], "no_reaction"
        )

    def log_commended_response(history):
        if len(history) == 0:
            return
        response = history[-1][1]
        question = history[-1][0]
        log_chat_history(USERNAME, ACCESS_TOKEN, question, response, "liked")
        gr.Info("Saved successfully!")

    def log_disliked_response(history):
        if len(history) == 0:
            return
        response = history[-1][1]
        question = history[-1][0]
        log_chat_history(USERNAME, ACCESS_TOKEN, question, response, "disliked")
        gr.Info("Saved successfully!")

    def log_flagged_response(history):
        if len(history) == 0:
            return
        response = history[-1][1]
        question = history[-1][0]
        log_chat_history(USERNAME, ACCESS_TOKEN, question, response, "flagged")
        gr.Info("Saved successfully!")

    def chat_liked_or_disliked(history, data: gr.LikeData):
        question = history[data.index[0]][0]
        response = history[data.index[0]][1]
        if data.liked:
            log_commended_response([[question, response]])
        else:
            log_disliked_response([[question, response]])

    def fetch_flagged_messages(user_id, session_id):
        response = chat_history_table.scan(
            FilterExpression=boto3.dynamodb.conditions.Attr("Username").eq(user_id)
            & boto3.dynamodb.conditions.Attr("SessionId").eq(session_id)
            & boto3.dynamodb.conditions.Attr("Reaction").eq("flagged")
        )
        return response.get("Items", [])

    def generate_csv(user_id, session_id):
        items = fetch_flagged_messages(user_id, session_id)
        if not items:
            return None

        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%S")
        temp_dir = tempfile.gettempdir()
        filepath = os.path.join(temp_dir, f"{user_id}_{timestamp}_flagged.csv")

        with open(filepath, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(
                [
                    "Username",
                    "SessionId",
                    "Timestamp",
                    "Question",
                    "Response",
                    "Reaction",
                ]
            )
            for item in items:
                writer.writerow(
                    [
                        item["Username"],
                        item["SessionId"],
                        item["Timestamp"],
                        item["Question"],
                        item["Response"],
                        item["Reaction"],
                    ]
                )

        return filepath

    def handle_download_click():
        filepath = generate_csv(USERNAME, ACCESS_TOKEN)
        return filepath if filepath else None

    def update_skill(skill_name):
        global MCM_URL
        MCM_URL = SKILL_NAME_TO_MCM_URL[skill_name]
        return []

    ivy_main_page.load(on_page_load, None, [welcome_msg])
    mcm_skill.change(update_skill, [mcm_skill], [chatbot])
    msg.submit(
        update_user_message, [msg, chatbot], [msg, chatbot], queue=False
    ).success(get_response_from_ivy, chatbot, chatbot)
    submit.click(
        update_user_message, [msg, chatbot], [msg, chatbot], queue=False
    ).success(get_response_from_ivy, chatbot, chatbot)
    chatbot.like(chat_liked_or_disliked, chatbot, None)
    clear.click(lambda: None, None, chatbot, queue=False)
    flag_btn.click(log_flagged_response, chatbot, None)
    download_btn.click(
        handle_download_click,
        inputs=[],
        outputs=[download_btn],
    )

# Launch the Application
ivy_main_page.queue()

with gr.Blocks() as evaluation_page:
    # Develop Evaluation page
    # Placeholder interface
    gr.Interface(lambda x: f"Hello {x}!", inputs="text", outputs="text")

app = gr.mount_gradio_app(app, ivy_main_page, path="/ask-ivy")
app = gr.mount_gradio_app(app, evaluation_page, path="/evaluation")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)
