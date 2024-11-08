import argparse
import csv
from datetime import datetime
import boto3
from boto3.dynamodb.conditions import Key
from dotenv import load_dotenv
import os
import logging


# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def initialize_dynamodb():
    global dynamodb, chat_table, video_table
    try:
        # Initialize DynamoDB resource
        dynamodb = boto3.resource('dynamodb', region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-1"))
        chat_table = dynamodb.Table('ChatHistory')
        video_table = dynamodb.Table('VideoLogs')
        logger.info("Successfully connected to DynamoDB.")
    except Exception as e:
        logger.error(f"Error initializing DynamoDB: {e}")


def get_unique_session_ids_for_date(specified_date):
    try:
        # Query VideoLogs for the specified date (filtering on timestamp)
        response = video_table.scan(
            FilterExpression=Key('timestamp').begins_with(specified_date)  # Filter by date (YYYY-MM-DD)
        )

        # Extract unique sessionIds from the response
        unique_session_ids = set(log['sessionId'] for log in response.get('Items', []))

        # Return as a sorted list
        return sorted(list(unique_session_ids))

    except Exception as e:
        logger.error(f"Error querying VideoLogs for date {specified_date}: {e}")
        return []


def get_chat_logs(session_id):
    try:
        chat_response = chat_table.query(
            IndexName="SessionIndex",
            KeyConditionExpression=Key("SessionId").eq(session_id)
        )
        # Only keep Question, Response, and standardized Timestamp fields
        chat_logs = [
            {
                "Timestamp": datetime.strptime(log["Timestamp"], "%Y-%m-%dT%H-%M-%S"),
                "Question": log.get("Question"),
                "Response": log.get("Response")
            }
            for log in chat_response.get('Items', [])
        ]
        return chat_logs
    except Exception as e:
        logger.error(f"Error querying ChatHistory: {e}")
        return []


def get_video_logs(session_id):
    try:
        video_response = video_table.query(
            IndexName="SessionIndex",
            KeyConditionExpression=Key("sessionId").eq(session_id)
        )
        # Only keep eventType, url, and standardized Timestamp fields
        video_logs = [
            {
                "Timestamp": datetime.strptime(log["timestamp"], "%Y-%m-%dT%H:%M:%S.%fZ"),
                "EventType": log.get("eventType"),
                "URL": log.get("url")
            }
            for log in video_response.get('Items', [])
        ]
        return video_logs
    except Exception as e:
        logger.error(f"Error querying VideoLogs: {e}")
        return []

# Function to combine logs and write to CSV
def export_user_journey_to_csv(session_id, filename=None):
    chat_logs = get_chat_logs(session_id)
    video_logs = get_video_logs(session_id)

    # Get the first 10 characters of the sessionId and first 5 characters of the userId
    session_id_prefix = session_id[:15]

    # Generate the filename using the prefixes
    if filename is None:
        filename = f"sessionId_{session_id_prefix}.csv"

    # Combine and sort logs by timestamp
    combined_logs = sorted(chat_logs + video_logs, key=lambda x: x["Timestamp"])

    # Write to CSV
    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Timestamp", "Chat Question", "Chat Response", "Video EventType", "Video URL"])

        for log in combined_logs:
            if "Question" in log:  # It's a chat log
                writer.writerow([log["Timestamp"], log["Question"], log["Response"], "", ""])
            elif "EventType" in log:  # It's a video log
                writer.writerow([log["Timestamp"], "", "", log["EventType"], log["URL"]])

    logger.info(f"User journey exported to {filename}")


# Main function to handle user inputs and process the data
def main():

    # Initialize argument parser
    parser = argparse.ArgumentParser(description="Export user journey from DynamoDB to CSV")
    parser.add_argument(
        '--env',
        type=str,
        required=True,
        help="Path to the environment file containing AWS credentials"
    )
    parser.add_argument(
        '--date',
        type=str,
        required=True,
        help="Date for filtering session logs (Format: YYYY-MM-DD)"
    )

    # Parse arguments
    args = parser.parse_args()

    # Load environment variables from the file
    load_dotenv(args.env)

    initialize_dynamodb()

    # Get unique session IDs from VideoLogs based on the specified date
    unique_session_ids = get_unique_session_ids_for_date(args.date)

    if not unique_session_ids:
        logger.warning(f"No session IDs found for the specified date: {args.date}")
        return

    # Process each session ID and export user journey
    # Export the user journey to CSV for each unique sessionId
    for session_id in unique_session_ids:
        export_user_journey_to_csv(session_id)


if __name__ == "__main__":
    main()


