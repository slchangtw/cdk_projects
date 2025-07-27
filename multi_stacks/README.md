# Data Pipeline Stack

This CDK stack implements a serverless data processing pipeline for energy consumption data. It transforms CSV files to JSON format and calculates energy usage statistics.

## Architecture

The data pipeline consists of the following components:

### 1. S3 Buckets
- **Raw Data Landing Bucket**: Receives CSV files from external sources
- **JSON Transformed Bucket**: Stores processed JSON files

### 2. Lambda Functions
- **Transform to JSON Lambda**: Converts CSV data to JSON format
- **Calculate and Notify Lambda**: Processes JSON data and calculates energy statistics

### 3. Event-Driven Processing
- S3 event notifications trigger Lambda functions automatically
- CSV files trigger JSON transformation
- JSON files trigger energy calculation

## Data Flow

1. **File Upload**: CSV files are uploaded to the raw data landing bucket
2. **CSV Processing**: S3 event notification triggers the CSV-to-JSON transformation Lambda
3. **JSON Storage**: Transformed JSON files are stored in the dedicated bucket
4. **Energy Calculation**: When JSON files are created, the calculation Lambda processes them
5. **Results Storage**: Energy statistics are stored in DynamoDB
6. **Notification**: Results are sent via SNS topics

## Input Data Format

The pipeline expects CSV files with the following columns:

```csv
date,6am,12pm,6pm,12am,electricVehicleCharging,hotWaterHeater,poolPump,heatPump
1/1/2023,1.8,3.5,2.1,1.2,TRUE,TRUE,FALSE,FALSE
```

### Column Descriptions:
- `date`: Date of the energy reading
- `6am`, `12pm`, `6pm`, `12am`: Energy consumption in kWh for each time period
- `electricVehicleCharging`: Boolean indicating if electric vehicle charging was active
- `hotWaterHeater`: Boolean indicating if hot water heater was active
- `poolPump`: Boolean indicating if pool pump was active
- `heatPump`: Boolean indicating if heat pump was active

## Output Data

### JSON Transformation Output
The CSV-to-JSON Lambda produces JSON files with the following structure:

```json
[
  {
    "date": "1/1/2023",
    "6am": 1.8,
    "12pm": 3.5,
    "6pm": 2.1,
    "12am": 1.2,
    "electricVehicleCharging": true,
    "hotWaterHeater": true,
    "poolPump": false,
    "heatPump": false
  }
]
```

### Energy Calculation Output
The calculation Lambda stores results in DynamoDB with the following structure:

```json
{
  "totalKWH": 85.6,
  "counts": {
    "electricVehicleCharging": {"true": 6, "false": 4},
    "hotWaterHeater": {"true": 8, "false": 2},
    "poolPump": {"true": 3, "false": 7},
    "heatPump": {"true": 2, "false": 8}
  },
  "percentageCounts": {
    "electricVehicleCharging": {"true": 60.0, "false": 40.0},
    "hotWaterHeater": {"true": 80.0, "false": 20.0},
    "poolPump": {"true": 30.0, "false": 70.0},
    "heatPump": {"true": 20.0, "false": 80.0}
  }
}
```

## Environment Variables

### Transform to JSON Lambda
- `TRANSFORMED_BUCKET`: Name of the S3 bucket for storing JSON files
- `AWS_REGION`: AWS region for the Lambda function

### Calculate and Notify Lambda
- `SNS_TOPIC_CALCULATOR_SUMMARY`: ARN of the SNS topic for sending notifications
- `CALCULATED_ENERGY_TABLE_NAME`: Name of the DynamoDB table for storing results
- `AWS_REGION`: AWS region for the Lambda function

## Dependencies

The Lambda functions require the following Python packages:
- `boto3>=1.26.0`
- `botocore>=1.29.0`

## Usage

1. Deploy the stack using CDK:
   ```bash
   cdk deploy DataPipelineStack
   ```

2. Upload CSV files to the raw data landing bucket

3. Monitor the processing through CloudWatch logs

4. Check results in DynamoDB and SNS notifications

## Error Handling

- Lambda functions include comprehensive error handling
- Failed processing attempts are logged to CloudWatch
- S3 event notifications are filtered by file extension
- Invalid data formats are handled gracefully

## Security

- IAM permissions are granted on a least-privilege basis
- S3 buckets can be configured with encryption
- Lambda functions run in VPC if required
- Environment variables are used for configuration 