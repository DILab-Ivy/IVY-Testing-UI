#####################################################################################################################
# Description:
# The chat_logging.py module is responsible for handling all logging-related functionality for user login and chat history
# in the Ivy Chatbot application. It provides functions to log user login events, store chat interactions,
# update chat reactions, fetch flagged messages, and generate CSV files of flagged chats.
#####################################################################################################################

import time
from datetime import datetime, timezone
import boto3
import csv
import tempfile
import os
import gradio as gr

# Access user data file
from user_data import UserConfig


# Initialize DynamoDB
dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
login_table = dynamodb.Table("UserLogin")
chat_history_table = dynamodb.Table("ChatHistory")
evaluation_questions_table = dynamodb.Table("EvalQuestions")
evaluation_responses_table = dynamodb.Table("Evaluation")


####################################################################################
# Logging User Sign-in to UserLogin DB
####################################################################################
def log_user_login(user_id, session_id):
    timestamp = time.time()
    dt = datetime.fromtimestamp(timestamp)
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M")
    login_data = {
        "Username": user_id,
        "SessionId": session_id,
        "Timestamp": timestamp,
    }
    login_table.put_item(Item=login_data)


####################################################################################
# Logging and Updating Chat History to ChatHistory DB
####################################################################################


def log_chat_history(user_id, session_id, question, response, reaction):
    timestamp = time.time()
    dt = datetime.fromtimestamp(timestamp)
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M")

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
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M")

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


####################################################################################
# Handling Reaction to Responses
####################################################################################


def log_commended_response(history):
    if len(history) == 0:
        return
    response = history[-1][1]
    question = history[-1][0]
    log_chat_history(
        UserConfig.USERNAME, UserConfig.ACCESS_TOKEN, question, response, "liked"
    )
    gr.Info("Saved successfully!")


def log_disliked_response(history):
    if len(history) == 0:
        return
    response = history[-1][1]
    question = history[-1][0]
    log_chat_history(
        UserConfig.USERNAME, UserConfig.ACCESS_TOKEN, question, response, "disliked"
    )
    gr.Info("Saved successfully!")


def log_flagged_response(history):
    if len(history) == 0:
        return
    response = history[-1][1]
    question = history[-1][0]
    log_chat_history(
        UserConfig.USERNAME, UserConfig.ACCESS_TOKEN, question, response, "flagged"
    )
    gr.Info("Saved successfully!")


def chat_liked_or_disliked(history, data: gr.LikeData):
    question = history[data.index[0]][0]
    response = history[data.index[0]][1]
    if data.liked:
        log_commended_response([[question, response]])
    else:
        log_disliked_response([[question, response]])


####################################################################################
# Handling Flagged Responses
####################################################################################


def fetch_flagged_messages(user_id, session_id):
    response = chat_history_table.scan(
        FilterExpression=boto3.dynamodb.conditions.Attr("Username").eq(user_id)
        & boto3.dynamodb.conditions.Attr("SessionId").eq(session_id)
        & boto3.dynamodb.conditions.Attr("Reaction").eq("flagged")
    )
    return response.get("Items", [])


####################################################################################
# Generate CSV Files from fetched flagged message in DynamoDB
####################################################################################


def generate_csv(user_id, session_id):
    items = fetch_flagged_messages(user_id, session_id)
    if not items:
        return None

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M")
    temp_dir = tempfile.gettempdir()
    filepath = os.path.join(temp_dir, f"{user_id}_{timestamp}_flagged.csv")

    with open(filepath, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(
            [
                "Username",
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
                    item["Timestamp"],
                    item["Question"],
                    item["Response"],
                    item["Reaction"],
                ]
            )

    return filepath
