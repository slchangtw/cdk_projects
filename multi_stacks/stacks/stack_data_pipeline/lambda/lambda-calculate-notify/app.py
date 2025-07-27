import json
import os
from datetime import datetime

import boto3

# Initialize DynamoDB client
dynamodb = boto3.client("dynamodb")


def lambda_handler(event, context):
    """
    Lambda function to calculate energy usage statistics and store in DynamoDB
    """
    try:
        # Parse the event to get the data
        # Assuming the event contains the CSV data as a list of dictionaries
        if "body" in event:
            # If data comes from API Gateway
            data = json.loads(event["body"])
        else:
            # If data comes directly from S3 event
            data = event.get("data", [])

        # Initialize variables
        total_kwh = 0
        counts = {
            "electricVehicleCharging": {"true": 0, "false": 0},
            "hotWaterHeater": {"true": 0, "false": 0},
            "poolPump": {"true": 0, "false": 0},
            "heatPump": {"true": 0, "false": 0},
        }

        # Calculate energy statistics from the provided data
        for row in data:
            # Calculate daily KWH from the four time periods
            daily_kwh = row["6am"] + row["12pm"] + row["6pm"] + row["12am"]
            total_kwh += daily_kwh
            row["totalKWH"] = daily_kwh

            # Count boolean values for each energy source
            for key in counts:
                bool_value = str(row[key]).lower()
                if bool_value in counts[key]:
                    counts[key][bool_value] += 1

        # Calculate percentage counts for each energy source
        data_length = len(data)
        percentage_counts = {
            "electricVehicleCharging": {
                "true": (counts["electricVehicleCharging"]["true"] / data_length) * 100,
                "false": (counts["electricVehicleCharging"]["false"] / data_length)
                * 100,
            },
            "hotWaterHeater": {
                "true": (counts["hotWaterHeater"]["true"] / data_length) * 100,
                "false": (counts["hotWaterHeater"]["false"] / data_length) * 100,
            },
            "poolPump": {
                "true": (counts["poolPump"]["true"] / data_length) * 100,
                "false": (counts["poolPump"]["false"] / data_length) * 100,
            },
            "heatPump": {
                "true": (counts["heatPump"]["true"] / data_length) * 100,
                "false": (counts["heatPump"]["false"] / data_length) * 100,
            },
        }

        # DynamoDB item preparation
        current_timestamp = datetime.now().isoformat()
        dynamo_item = {
            "TableName": os.environ.get("CALCULATED_ENERGY_TABLE_NAME"),
            "Item": {
                "primaryKey": {"S": "1"},
                "timestamp": {"S": current_timestamp},
                "data": {
                    "S": json.dumps(
                        {
                            "total_kwh": total_kwh,
                            "counts": counts,
                            "percentage_counts": percentage_counts,
                            "data": data,
                        }
                    )
                },
            },
        }

        # Store data in DynamoDB
        dynamodb.put_item(**dynamo_item)
        print("Successfully stored processed data in DynamoDB.")

        # Prepare response
        response = {
            "statusCode": 200,
            "body": json.dumps(
                {
                    "message": "Energy calculation completed successfully",
                    "total_kwh": total_kwh,
                    "counts": counts,
                    "percentage_counts": percentage_counts,
                    "timestamp": current_timestamp,
                }
            ),
        }

        return response

    except Exception as e:
        print(f"Error processing energy calculation: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Internal server error", "message": str(e)}),
        }
