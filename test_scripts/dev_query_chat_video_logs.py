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
                "URL": log.get("url"),
                "eventData": log.get("eventData")  # Add eventData field
            }
            for log in video_response.get('Items', [])
        ]
        return video_logs
    except Exception as e:
        logger.error(f"Error querying VideoLogs: {e}")
        return []


#Extracts and formats fields from the eventData for CSV export
def parse_event_data(event_data):
    try:
        # Ensure event_data is a dictionary (we know it's a dict from the logs)
        if not isinstance(event_data, dict):
            logger.error(f"Unexpected eventData type: {type(event_data)}")
            return {}

        # Proceed only if the eventType is 'submission' and 'verb' is "answered"
        if event_data["verb"] == "answered":
            # Extract Activity Title directly from event_data
            activity_title = event_data["object"] if "object" in event_data else "N/A"

            # Extract and convert time spent (duration) from event_data
            duration_str = event_data["result"]["duration"] if "result" in event_data and "duration" in event_data["result"] else "PT0S"
            time_spent = float(duration_str.replace("PT", "").replace("S", ""))

            # Extract score details
            score_data = event_data["result"]["score"] if "result" in event_data and "score" in event_data["result"] else {}
            raw_score = int(score_data["raw"]) if "raw" in score_data else 0
            max_score = int(score_data["max"]) if "max" in score_data else 0
            scaled_score = float(score_data["scaled"]) if "scaled" in score_data else 0
            score_info = f"{raw_score} out of {max_score} ({scaled_score * 100:.2f}%)"

            # Extract completion status
            completion_status = event_data["result"]["completion"] if "result" in event_data and "completion" in event_data["result"] else False
            completion_text = f"The activity was {'completed' if completion_status else 'not completed'}."

            # Return the parsed data
            return {
                "Activity Title": activity_title,
                "Time Spent": f"{time_spent} seconds",
                "Score": score_info,
                "Completion Status": completion_text
            }
        else:
            logger.error(f"Event verb is not 'answered': {event_data['verb']}")
            return {}

    except KeyError as e:
        logger.error(f"KeyError encountered: {e} in eventData.")
        return {}
    except Exception as e:
        logger.error(f"Error parsing eventData: {e}")
        return {}
def export_user_journey_to_csv(session_id):
    chat_logs = get_chat_logs(session_id)
    video_logs = get_video_logs(session_id)

    # Get the first 10 characters of the sessionId and first 5 characters of the userId
    session_id_prefix = session_id[:15]

    # Generate the filename using the prefixes
    # if filename is None:
    filename = f"sessionId_{session_id_prefix}.csv"

    # Combine and sort logs by timestamp
    combined_logs = sorted(chat_logs + video_logs, key=lambda x: x["Timestamp"])

    # Write to CSV
    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([
            "Timestamp", "Chat Question", "Chat Response",
            "Video EventType", "Video URL",
            "Activity Question", "Time Spent", "Score", "Completion Status"
        ])

        for log in combined_logs:
            if "Question" in log:  # It's a chat log
                writer.writerow([
                    log["Timestamp"], log["Question"], log["Response"],
                    "", "", "", "", "", ""
                ])
            elif "EventType" in log:  # It's a video log
                # Default values for additional columns
                activity_title = time_spent = score = completion_status = ""

                if log["EventType"] == "submission" and "eventData" in log:
                    # Parse the eventData using the parse_event_data function
                    parsed_data = parse_event_data(log["eventData"])
                    activity_title = parsed_data.get("Activity Title", "")
                    time_spent = parsed_data.get("Time Spent", "")
                    score = parsed_data.get("Score", "")
                    completion_status = parsed_data.get("Completion Status", "")

                writer.writerow([
                    log["Timestamp"], "", "", log["EventType"], log["URL"],
                    activity_title, time_spent, score, completion_status
                ])

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


