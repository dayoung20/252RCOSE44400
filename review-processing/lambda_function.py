import boto3  
from textblob import TextBlob  
import datetime
import json
import os

# DynamoDB
dynamodb = boto3.resource("dynamodb")

# Environment variable should be set in Lambda console
TABLE_NAME = os.environ.get("TABLE_NAME", "")
table = dynamodb.Table(TABLE_NAME)

# SES
ses = boto3.client("ses", region_name="us-east-1")

# Sender / Receiver email (must be verified in SES sandbox)
SENDER_EMAIL = os.environ.get("SENDER_EMAIL", "")
RECEIVER_EMAIL = os.environ.get("RECIPIENT_EMAIL", "")


def lambda_handler(event, context):
    try:
        # 1. Parse the incoming request body
        # API Gateway may pass the body as a JSON string, so we need to parse it safely.
        if isinstance(event.get("body"), str):
            body = json.loads(event["body"])
        else:
            # In case of direct invocation or test, event itself may be the body.
            body = event

        user_name = body.get("user_name", "Anonymous")
        review_text = body.get("review", "")
        timestamp = datetime.datetime.now().isoformat()

        # 2. Perform Sentiment Analysis using TextBlob
        # Polarity score ranges from -1.0 (Negative) to 1.0 (Positive)
        blob = TextBlob(review_text)
        polarity = blob.sentiment.polarity

        # Determine sentiment category based on polarity thresholds
        if polarity > 0.1:
            sentiment = "Positive"
        elif polarity < -0.1:
            sentiment = "Negative"
        else:
            sentiment = "Neutral"

        # 3. Save the result to DynamoDB
        # Storing the exact polarity score is useful for future data analysis.
        table.put_item(
            Item={
                "user_name": user_name,
                "review": review_text,
                "sentiment": sentiment,
                # Convert float to string for DynamoDB compatibility
                "polarity_score": str(polarity),
                "timestamp": timestamp,
            }
        )

        # 4. Send Email Notification via SES
        # SES: In Sandbox mode, both the sender and recipient emails must be verified.
        if sentiment == "Positive" and SENDER_EMAIL and RECEIVER_EMAIL:
            ses.send_email(
                Source=SENDER_EMAIL,
                Destination={"ToAddresses": [RECEIVER_EMAIL]},
                Message={
                    "Subject": {"Data": f"[{sentiment}] Review from {user_name}"},
                    "Body": {
                        "Text": {
                            "Data": (
                                f"User: {user_name}\n"
                                f"Sentiment: {sentiment}\n"
                                f"Score: {polarity:.2f}\n\n"
                                f"Review:\n{review_text}"
                            )
                        }
                    },
                },
            )

        # 5. Return HTTP response
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(
                {
                    "message": "Review processed",
                    "user_name": user_name,
                    "sentiment": sentiment,
                    "polarity_score": round(polarity, 2),
                }
            ),
        }

    except Exception as e:
        # Log the error for debugging (CloudWatch Logs)
        print(f"Error: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps("Internal Server Error"),
        }
