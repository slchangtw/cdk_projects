import csv
import json
import os
from typing import Any

import boto3


def transform_csv_to_json(csv_path: str) -> list[dict[str, Any]]:
    """
    Transform CSV content to JSON format
    """
    data = []

    with open(csv_path, "r") as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            # Convert numeric values to appropriate types
            processed_row = {
                "date": row["date"],
                "6am": float(row["6am"]),
                "12pm": float(row["12pm"]),
                "6pm": float(row["6pm"]),
                "12am": float(row["12am"]),
                "electricVehicleCharging": row["electricVehicleCharging"].upper()
                == "TRUE",
                "hotWaterHeater": row["hotWaterHeater"].upper() == "TRUE",
                "poolPump": row["poolPump"].upper() == "TRUE",
                "heatPump": row["heatPump"].upper() == "TRUE",
            }
            data.append(processed_row)

    return data


def lambda_handler(event, context):
    """
    Lambda function to transform CSV data to JSON and upload to S3
    """
    try:
        # Get S3 bucket and key from the event
        s3_bucket = event["Records"][0]["s3"]["bucket"]["name"]
        s3_key = event["Records"][0]["s3"]["object"]["key"]

        # Only process CSV files
        if not s3_key.lower().endswith(".csv"):
            print(f"Skipping non-CSV file: {s3_key}")
            return {
                "statusCode": 200,
                "body": json.dumps({"message": "Skipped non-CSV file"}),
            }

        # Initialize S3 client
        s3_client = boto3.client("s3")

        # Read CSV file from S3
        response = s3_client.get_object(Bucket=s3_bucket, Key=s3_key)
        csv_content = response["Body"].read().decode("utf-8")

        # Transform CSV to JSON
        json_data = transform_csv_to_json(csv_content)

        # Create JSON filename
        json_filename = s3_key.replace(".csv", ".json")

        # Upload JSON to transformed bucket
        transformed_bucket = os.environ.get("TRANSFORMED_BUCKET")
        s3_client.put_object(
            Bucket=transformed_bucket,
            Key=json_filename,
            Body=json.dumps(json_data, indent=2),
            ContentType="application/json",
        )

        print(f"Successfully transformed {s3_key} to {json_filename}")

        return {
            "statusCode": 200,
            "body": json.dumps(
                {
                    "message": "CSV to JSON transformation completed successfully",
                    "sourceFile": s3_key,
                    "outputFile": json_filename,
                    "recordCount": len(json_data),
                }
            ),
        }

    except Exception as e:
        print(f"Error processing CSV transformation: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps(
                {"error": "CSV transformation error", "message": str(e)}
            ),
        }
