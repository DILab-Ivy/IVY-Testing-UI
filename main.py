from dotenv import load_dotenv

load_dotenv()

import base64
import random
import sys
import time
from datetime import datetime, timezone

import gradio as gr
import hashlib
import httpx
import requests
import uvicorn
from fastapi import FastAPI
from starlette.responses import RedirectResponse

from chat_logging import *
from constants import (
    CLIENT_ID,
    CLIENT_SECRET,
    COGNITO_DOMAIN,
    EVALUATION_METRIC_DESCRIPTION,
    EVALUATION_URL,
    GET_ACCESS_TOKEN_URL,
    GET_USER_INFO_URL,
    IS_DEVELOPER_VIEW,
    LOGIN_URL,
    ON_LOCALHOST,
    REDIRECT_URL,
    SKILL_NAME_TO_MCM_URL,
)
from user_data import UserConfig

IVY_BACKEND = "MAGE"
IVY_SKILL = "Classification"
MCM_URL = "https://classification.dilab-ivy.com/ivy/ask_question"
MAGE_URL = "https://mage.dilab-ivy.com/ivy/ask_question"
EVALUATION_QUESTIONS = []
EVALUATION_QUESTION_NUM = 0
USE_TEST_EVAL_DB = False

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
        # Update Access token in constants/config file
        UserConfig.ACCESS_TOKEN = access_token

        # Get User Info
        response = requests.get(
            GET_USER_INFO_URL, headers=get_user_info_header(access_token)
        ).json()

        # Update User Info in constants/config file
        UserConfig.USERNAME = response["username"]
        UserConfig.USER_NAME = response["name"]

        # Log user login in DynamoDB
        log_user_login(UserConfig.USERNAME, UserConfig.ACCESS_TOKEN)

        return True
    except Exception as e:
        print(str(e))
        return False


def get_embed_response(
    question: str, backend="", skill="", api_key="", timeout=None
) -> str:
    print("Using Backend: ", backend)
    if backend == "MCM":
        return get_mcm_response(
            question, SKILL_NAME_TO_MCM_URL[skill], api_key, timeout
        )
    elif backend == "MAGE":
        return get_mage_response(question, MAGE_URL, api_key, skill, timeout)


def get_response(question: str) -> str:
    print("Using Backend: ", ivy_backend.value)
    if ivy_backend.value == "MCM":
        return get_mcm_response(question)
    elif ivy_backend.value == "MAGE":
        return get_mage_response(question)


def get_mcm_response(question: str, mcm_url="", api_key="", timeout=None) -> str:
    try:
        response = httpx.post(
            mcm_url or MCM_URL,
            json={
                "question": question,
                "api_key": api_key or mcm_api_key.value,
                "Episodic_Knowledge": {},
            },
            timeout=timeout or timeout_secs.value,
        )
        return response.json().get("response", "")
    except httpx.RequestError as e:
        print(f"HTTP request failed: {e}")
        return ""
    except Exception as e:
        print(f"An error occurred: {e}")
        return ""


def get_mage_response(
    question: str, mage_url="", api_key="", skill="", timeout=None
) -> str:
    try:
        response = httpx.post(
            mage_url or MAGE_URL,
            json={
                "question": question,
                "api_key": api_key or mcm_api_key.value,
                "skill": skill or IVY_SKILL,
            },
            timeout=timeout or timeout_secs.value,
        )
        return response.json().get("response", "")
    except httpx.RequestError as e:
        print(f"HTTP request failed: {e}")
        return ""
    except Exception as e:
        print(f"An error occurred: {e}")
        return ""


with gr.Blocks(css="footer {visibility: hidden}") as ivy_embed_page:
    session_settings = gr.State()
    lti_data = gr.State()
    # Title
    embed_welcome_msg = gr.Markdown()

    embed_message = gr.Markdown("## Ask your personal tutor!")
    embed_chat_area = gr.Chatbot(
        label="Your Conversation",
        show_copy_button=True,
        placeholder="Your conversations will appear here...",
    )
    embed_chatbox = gr.Textbox(
        label="Question",
        placeholder="Please enter your question here...",
        show_copy_button=True,
        autofocus=True,
        show_label=True,
    )
    embed_submit_btn = gr.Button(value="Submit", variant="primary")

    def on_page_load_ask_ivy_embed(request: gr.Request):
        backend, skill, mcm_api_key, timeout = "", "", "123456789", 60
        if "backend" in dict(request.query_params):
            backend = dict(request.query_params)["backend"]
        if backend not in ["MCM", "MAGE"]:
            backend = "MCM"

        if "skill" in dict(request.query_params):
            skill = dict(request.query_params)["skill"]
        if skill not in SKILL_NAME_TO_MCM_URL:
            raise Exception("skill url param not supported")

        if "mcm_api_key" in dict(request.query_params):
            mcm_api_key = dict(request.query_params)["mcm_api_key"]
        if "timeout" in dict(request.query_params):
            timeout = dict(request.query_params)["timeout"]

        session_settings = {
            "backend": backend,
            "skill": skill,
            "mcm_api_key": mcm_api_key,
            "timeout_secs": timeout,
        }

        lti_data_from_url_params = {
            "user_id": "",
            "full_name": "",
            "session_id": "",
            "user_role": "",
            "course_id": "",
        }
        if "user_id" in dict(request.query_params):
            lti_data_from_url_params["user_id"] = dict(request.query_params)["user_id"]
        if "full_name" in dict(request.query_params):
            lti_data_from_url_params["full_name"] = dict(request.query_params)[
                "full_name"
            ]
        if "session_id" in dict(request.query_params):
            session_id = dict(request.query_params)[
                "session_id"
            ]
            lti_data_from_url_params["session_id"] = hashlib.sha256(
                session_id.encode('utf-8')).hexdigest()
        if "user_role" in dict(request.query_params):
            lti_data_from_url_params["user_role"] = dict(request.query_params)[
                "user_role"
            ]
        if "course_id" in dict(request.query_params):
            lti_data_from_url_params["course_id"] = dict(request.query_params)[
                "course_id"
            ]
        return [gr.State(session_settings), gr.State(lti_data_from_url_params)]

    def update_user_message(user_message, history):
        return "", history + [[user_message, None]]

    def get_response_from_ivy(history, settings, lti_data):
        history[-1][1] = ""
        response = get_embed_response(
            history[-1][0],
            settings.value["backend"],
            settings.value["skill"],
            settings.value["mcm_api_key"],
            settings.value["timeout_secs"],
        )
        for character in response:
            history[-1][1] += character
            time.sleep(0.005)
            yield history
        # Log to DynamoDB every interaction here
        log_chat_history(
            lti_data.value["user_id"],
            lti_data.value["session_id"],
            history[-1][0],
            history[-1][1],
            "no_reaction",
            settings.value["backend"],
            settings.value["skill"]
        )

    ivy_embed_page.load(
        on_page_load_ask_ivy_embed,
        [],
        [session_settings, lti_data],
    )

    embed_chatbox.submit(
        update_user_message,
        [embed_chatbox, embed_chat_area],
        [embed_chatbox, embed_chat_area],
        queue=False,
    ).success(
        get_response_from_ivy,
        [embed_chat_area, session_settings, lti_data],
        embed_chat_area,
    )
    embed_submit_btn.click(
        update_user_message,
        [embed_chatbox, embed_chat_area],
        [embed_chatbox, embed_chat_area],
        queue=False,
    ).success(
        get_response_from_ivy,
        [embed_chat_area, session_settings, lti_data],
        embed_chat_area,
    )
    embed_chat_area.like(
        chat_liked_or_disliked, [embed_chat_area, lti_data, session_settings], None
    )

# Launch the Application
ivy_embed_page.queue()


# Gradio Interface Setup
with gr.Blocks(css="footer {visibility: hidden}") as ivy_main_page:
    # Title
    welcome_msg = gr.Markdown()
    # Settings
    with gr.Row():
        ivy_backend = gr.Dropdown(
            choices=["MCM", "MAGE"],
            value="MAGE",
            multiselect=False,
            label="Backend",
            interactive=True,
        )
        ivy_selected_skill = gr.Dropdown(
            choices=SKILL_NAME_TO_MCM_URL.keys(),
            value="Classification",
            multiselect=False,
            label="Skill",
            interactive=True,
        )
        with gr.Accordion(
            "Settings", open=False, visible=IS_DEVELOPER_VIEW
        ) as settings_ask_ivy:
            # MCM Settings
            with gr.Group("MCM Settings"):
                with gr.Row():
                    # MCM API Key
                    mcm_api_key = gr.Textbox(
                        value="123456789",
                        label="API Key",
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
        goto_eval_page_btn = gr.Button(value="Evaluate Ivy")

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
    with gr.Row(visible=IS_DEVELOPER_VIEW) as flag_download_button_grp_ask_ivy:
        flag_btn = gr.Button(value="Flag last response", variant="secondary")
        download_btn = gr.DownloadButton(
            value="Download Flagged Responses",
            variant="secondary",
        )

    def update_skill_ask_ivy(skill_name):
        global IVY_SKILL
        global MCM_URL
        IVY_SKILL = skill_name
        MCM_URL = SKILL_NAME_TO_MCM_URL[skill_name]
        return []

    def updte_ivy_backend(backend):
        global IVY_BACKEND
        print("Backend Updated: ", backend)
        IVY_BACKEND = backend
        return []

    def on_page_load_ask_ivy(skill_name, request: gr.Request):
        # Update visibility of certain components when Ivy is being embedded.
        embed_mode = False
        visibility_update = [gr.update(visible=True)] * 3
        if "embed" in dict(request.query_params):
            if dict(request.query_params)["embed"] == "true":
                embed_mode = True
                visibility_update = [gr.update(visible=False)] * 3

        display_msg = "# Welcome to Ivy!"
        if not embed_mode:
            # If session data not already available, get access tokens.
            if not UserConfig.ACCESS_TOKEN:
                if "code" not in dict(request.query_params):
                    # (TODO): Redirect to login page
                    display_msg = "Go back to login page"
                else:
                    url_code = dict(request.query_params)["code"]
                    if not get_access_token_and_user_info(url_code):
                        # (TODO): Redirect to Login page or display Error page
                        display_msg = "An Error Occurred"
                    else:
                        display_msg = (
                            f"# Welcome to Ivy Chatbot, {UserConfig.USER_NAME}"
                        )

        # Retrieve skill from query params if available.
        if "skill" in dict(request.query_params):
            skill_param = dict(request.query_params)["skill"]
            if skill_param in SKILL_NAME_TO_MCM_URL:
                skill_name = skill_param
        update_skill_ask_ivy(skill_name)

        updated_mcm_skill_ask_ivy = gr.Dropdown(
            choices=SKILL_NAME_TO_MCM_URL.keys(),
            value=skill_name,
            multiselect=False,
            label="Skill",
            interactive=True,
            visible=(not embed_mode),
        )
        return [display_msg, updated_mcm_skill_ask_ivy] + visibility_update

    def update_user_message(user_message, history):
        return "", history + [[user_message, None]]

    def get_response_from_ivy(history):
        history[-1][1] = ""
        response = get_response(history[-1][0])
        for character in response:
            history[-1][1] += character
            time.sleep(0.005)
            yield history
        # Log to DynamoDB every interaction here
        log_chat_history(
            UserConfig.USERNAME,
            UserConfig.ACCESS_TOKEN,
            history[-1][0],
            history[-1][1],
            "no_reaction",
            IVY_BACKEND,
            IVY_SKILL
        )

    def handle_download_click():
        filepath = generate_csv(UserConfig.USERNAME, UserConfig.ACCESS_TOKEN)
        return filepath if filepath else None

    ivy_main_page.load(
        on_page_load_ask_ivy,
        [ivy_selected_skill],
        [
            welcome_msg,
            ivy_selected_skill,
            settings_ask_ivy,
            clear,
            flag_download_button_grp_ask_ivy,
        ],
    )
    ivy_selected_skill.change(update_skill_ask_ivy, [ivy_selected_skill], [chatbot])
    ivy_backend.change(updte_ivy_backend, [ivy_backend], [])

    goto_eval_page_btn.click(
        None, None, None, js=f"() => window.open('{EVALUATION_URL}', '_blank')"
    )
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

try:
    evaluation_css = open("css/evaluation.css", "r").read()
except OSError:
    print("Could not open/read css file at css/evaluation.css")
    sys.exit()
with gr.Blocks(
    theme=gr.themes.Default(
        primary_hue=gr.themes.colors.teal, secondary_hue=gr.themes.colors.red
    ),
    css=evaluation_css,
) as evaluation_page:
    # Title
    welcome_msg = gr.Markdown()
    # Settings
    with gr.Row():
        mcm_skill_evaluation = gr.Dropdown(
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

    progress_bar = gr.HTML()

    with gr.Row():
        question_text = gr.Textbox(
            label="Evaluation Question",
            value="",
            interactive=True,
            scale=5,
        )
        submit_question_button = gr.Button(value="Submit", variant="primary")
        skip_question_button = gr.Button(value="Skip Question")

    with gr.Row():
        response_text1 = gr.Textbox(
            label="Evaluation Response 1",
            placeholder="Response from either MAGE / MCM will appear here..",
            value="",
            interactive=False,
            scale=1,
            lines=5,
        )
        response_text2 = gr.Textbox(
            label="Evaluation Response 2",
            placeholder="Response from either MAGE / MCM will appear here..",
            value="",
            interactive=False,
            scale=1,
            lines=5,
        )

    def get_metric_name(metric_name):
        return f"""
            <p>
                <div class="tooltip">{metric_name}
                <i class="fa fa-info-circle" style="font-size:10px;color:#007bff"></i>
                    <span class="tooltiptext" style="font-size:10px">{EVALUATION_METRIC_DESCRIPTION[metric_name]}</span>
                </div>
            </p>
        """

    metrics_evaluation_html = gr.HTML(
        f"""
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
    <div class='your-eval-container'>Enter your evaluations below</div> <br />
    <div class="eval-container">
        <table>
            <thead>
                <tr>
                    <th>Metrics</th>
                    <th>Strongly Disagree</th>
                    <th>Somewhat Disagree</th>
                    <th>Neutral</th>
                    <th>Somewhat Agree</th>
                    <th>Strongly Agree</th>
                </tr>
            </thead>
            <tbody>
                <tr style="background-color: #f9f9f9;">
                    <td>{get_metric_name("Correctness")}</td>
                    <td class="likert-label"><input type="radio" name="metric1" value="Strongly Disgree"></td>
                    <td class="likert-label"><input type="radio" name="metric1" value="Somewhat Disagree"></td>
                    <td class="likert-label"><input type="radio" name="metric1" value="Neutral"></td>
                    <td class="likert-label"><input type="radio" name="metric1" value="Somewhat Agree"></td>
                    <td class="likert-label"><input type="radio" name="metric1" value="Strongly Agree"></td>
                </tr>
                <tr style="background-color: #f0f0f0;">
                    <td>{get_metric_name("Completeness")}</td>
                    <td class="likert-label"><input type="radio" name="metric2" value="Strongly Disgree"></td>
                    <td class="likert-label"><input type="radio" name="metric2" value="Somewhat Disagree"></td>
                    <td class="likert-label"><input type="radio" name="metric2" value="Neutral"></td>
                    <td class="likert-label"><input type="radio" name="metric2" value="Somewhat Agree"></td>
                    <td class="likert-label"><input type="radio" name="metric2" value="Strongly Agree"></td>
                </tr>
                <tr style="background-color: #f9f9f9;">
                    <td>{get_metric_name("Confidence")}</td>
                    <td class="likert-label"><input type="radio" name="metric3" value="Strongly Disgree"></td>
                    <td class="likert-label"><input type="radio" name="metric3" value="Somewhat Disagree"></td>
                    <td class="likert-label"><input type="radio" name="metric3" value="Neutral"></td>
                    <td class="likert-label"><input type="radio" name="metric3" value="Somewhat Agree"></td>
                    <td class="likert-label"><input type="radio" name="metric3" value="Strongly Agree"></td>
                </tr>
                <tr style="background-color: #f0f0f0;">
                    <td>{get_metric_name("Comprehensibility")}</td>
                    <td class="likert-label"><input type="radio" name="metric4" value="Strongly Disgree"></td>
                    <td class="likert-label"><input type="radio" name="metric4" value="Somewhat Disagree"></td>
                    <td class="likert-label"><input type="radio" name="metric4" value="Neutral"></td>
                    <td class="likert-label"><input type="radio" name="metric4" value="Somewhat Agree"></td>
                    <td class="likert-label"><input type="radio" name="metric4" value="Strongly Agree"></td>
                </tr>
                <tr style="background-color: #f9f9f9;">
                    <td>{get_metric_name("Compactness")}</td>
                    <td class="likert-label"><input type="radio" name="metric5" value="Strongly Disgree"></td>
                    <td class="likert-label"><input type="radio" name="metric5" value="Somewhat Disagree"></td>
                    <td class="likert-label"><input type="radio" name="metric5" value="Neutral"></td>
                    <td class="likert-label"><input type="radio" name="metric5" value="Somewhat Agree"></td>
                    <td class="likert-label"><input type="radio" name="metric5" value="Strongly Agree"></td>
                </tr>
            </tbody>
        </table>
    </div><br />"""
    )

    with gr.Row():
        clear_button = gr.Button(value="Clear Rating", variant="stop")
        submit_rating_button = gr.Button(value="Next Question", variant="primary")

    def get_eval_dot_html(num, color_style):
        return f"""<div class="dot {color_style}">{num}</div>"""

    def create_progress_indicator(current_question):
        progress_html = """
        <div class="top-container">
            <div>
                <div class="progress-text">Evaluation Progress</div>
                <div class="dots">
                    %s
                </div>
            </div>
        </div>"""
        progress_dots_html = ""
        for i in range(len(EVALUATION_QUESTIONS)):
            if i < current_question:
                style = "green-dot"
            elif i > current_question:
                style = "red-dot"
            else:
                style = "yellow-dot"
            progress_dots_html += get_eval_dot_html(i + 1, style)
        progress_html = progress_html % progress_dots_html
        return progress_html

    def get_both_response(question: str):
        resp1 = get_mcm_response(question)
        resp2 = get_mage_response(question)

        resp1 += "\n\n\n\n\n\n\n (MCM)"
        resp2 += "\n\n\n\n\n\n\n (MAGE)"

        # Randomly shuffle the responses
        if random.randint(0, 1):
            return resp1, resp2

        return resp2, resp1

    # Update response 1 and response 2 textboxes
    submit_question_button.click(
        get_both_response,
        [question_text],
        [response_text1, response_text2],
    )

    def get_submit_rating_btn():
        if EVALUATION_QUESTION_NUM == len(EVALUATION_QUESTIONS) - 1:
            return gr.Button(
                value="Submit and Finish Evaluation",
                variant="primary",
                link="/post-eval",
            )
        else:
            return submit_rating_button

    def get_skip_question_btn():
        if EVALUATION_QUESTION_NUM == len(EVALUATION_QUESTIONS) - 1:
            return gr.Button(value="Skip Question", interactive=False)
        else:
            return skip_question_button

    def skip_eval_question():
        global EVALUATION_QUESTION_NUM
        EVALUATION_QUESTION_NUM += 1
        return [
            create_progress_indicator(EVALUATION_QUESTION_NUM),
            EVALUATION_QUESTIONS[EVALUATION_QUESTION_NUM][1],
            "",
            "",
            get_submit_rating_btn(),
            get_skip_question_btn(),
        ]

    skip_question_button.click(
        skip_eval_question,
        [],
        [
            progress_bar,
            question_text,
            response_text1,
            response_text2,
            submit_rating_button,
            skip_question_button,
        ],
    )

    clear_evaluation_rating_js = """
        function clear_selection() {
            selections = document.querySelectorAll('input[type="radio"]')
            selections.forEach(radio => {
                radio.checked = false;
            })
        }"""
    clear_button.click(
        None,
        inputs=[],
        outputs=[],
        js=clear_evaluation_rating_js,
    )

    def submit_rating_clear_update_question(response_concatenated_eval_ratings):
        global EVALUATION_QUESTION_NUM
        response_texts, concatenated_eval_ratings = (
            response_concatenated_eval_ratings.split("-response-eval-delim-")
        )
        response_text1, response_text2 = response_texts.split("-response-split-")

        log_evaluation_response(
            IVY_SKILL,
            EVALUATION_QUESTIONS[EVALUATION_QUESTION_NUM][1],
            EVALUATION_QUESTIONS[EVALUATION_QUESTION_NUM][0],
            response_text1,
            concatenated_eval_ratings.split(","),
            USE_TEST_EVAL_DB,
            IVY_BACKEND,
        )
        log_evaluation_response(
            IVY_SKILL,
            EVALUATION_QUESTIONS[EVALUATION_QUESTION_NUM][1],
            EVALUATION_QUESTIONS[EVALUATION_QUESTION_NUM][0],
            response_text2,
            concatenated_eval_ratings.split(","),
            USE_TEST_EVAL_DB,
            IVY_BACKEND,
        )

        EVALUATION_QUESTION_NUM += 1
        return [
            create_progress_indicator(EVALUATION_QUESTION_NUM),
            EVALUATION_QUESTIONS[EVALUATION_QUESTION_NUM][1],
            "",
            "",
            get_submit_rating_btn(),
            get_skip_question_btn(),
        ]

    submit_rating_button_js = """
        function fetch_ratings_and_clear(response_text1, response_text2) {
            metric1_value = document.querySelector('input[name="metric1"]:checked')?.value || 'None';
            metric2_value = document.querySelector('input[name="metric2"]:checked')?.value || 'None';
            metric3_value = document.querySelector('input[name="metric3"]:checked')?.value || 'None';
            metric4_value = document.querySelector('input[name="metric4"]:checked')?.value || 'None';
            metric5_value = document.querySelector('input[name="metric5"]:checked')?.value || 'None';

            document.querySelectorAll('input[type="radio"]').forEach(radio => {
                radio.checked = false;
            });

            return response_text1 + '-response-split-' + response_text2 + '-response-eval-delim-' + [metric1_value, metric2_value, metric3_value, metric4_value, metric5_value].join();
        }
        """

    submit_rating_button.click(
        submit_rating_clear_update_question,
        inputs=[response_text1, response_text2],
        outputs=[
            progress_bar,
            question_text,
            response_text1,
            response_text2,
            submit_rating_button,
            skip_question_button,
        ],
        js=submit_rating_button_js,
    )

    def update_eval_questions(skill_name):
        response = get_evaluation_questions(skill_name)
        response = response.get("Items", [])
        global EVALUATION_QUESTIONS
        EVALUATION_QUESTIONS = []
        global EVALUATION_QUESTION_NUM
        EVALUATION_QUESTION_NUM = 0
        for question_dict in response:
            EVALUATION_QUESTIONS.append(
                (question_dict["QuestionType"], question_dict["Question"])
            )
        random.shuffle(EVALUATION_QUESTIONS)

    def update_skill_evaluation(skill_name):
        global IVY_SKILL
        IVY_SKILL = skill_name
        global MCM_URL
        MCM_URL = SKILL_NAME_TO_MCM_URL[skill_name]
        update_eval_questions(skill_name)
        return [
            EVALUATION_QUESTIONS[EVALUATION_QUESTION_NUM][1],
            "",
            "",
            create_progress_indicator(EVALUATION_QUESTION_NUM),
        ]

    def on_page_load_evaluation(skill_name, request: gr.Request):
        if "eval_skill" in dict(request.query_params):
            skill_param = dict(request.query_params)["eval_skill"]
            if skill_param in SKILL_NAME_TO_MCM_URL:
                skill_name = skill_param
        update_skill_evaluation(skill_name)

        if "use_test_eval_db" in dict(request.query_params):
            global USE_TEST_EVAL_DB
            USE_TEST_EVAL_DB = dict(request.query_params)["use_test_eval_db"] == "true"

        first_question_to_display = update_skill_evaluation(skill_name)[0]
        return [
            create_progress_indicator(EVALUATION_QUESTION_NUM),
            first_question_to_display,
            skill_name,
        ]

    evaluation_page.load(
        on_page_load_evaluation,
        [mcm_skill_evaluation],
        [progress_bar, question_text, mcm_skill_evaluation],
    )
    mcm_skill_evaluation.change(
        update_skill_evaluation,
        [mcm_skill_evaluation],
        [question_text, response_text1, response_text2, progress_bar],
    )

with gr.Blocks(css="footer {visibility: hidden}") as post_eval_page:
    gr.HTML(
        f"<h1>Thank you for evaluating Ivy.</h1>You can close this window or go back to <a href='{EVALUATION_URL}' target='_self'>evaluation page</a> for evaluating another skill."
    )

app = gr.mount_gradio_app(
    app, ivy_embed_page, path="/ask-ivy-embed", root_path="/ask-ivy-embed"
)
app = gr.mount_gradio_app(app, ivy_main_page, path="/ask-ivy", root_path="/ask-ivy")
app = gr.mount_gradio_app(
    app, evaluation_page, path="/evaluation", root_path="/evaluation"
)
app = gr.mount_gradio_app(
    app, post_eval_page, path="/post-eval", root_path="/post-eval"
)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)
