import os
from dataclasses import dataclass

from aws_cdk import CfnOutput, Duration, RemovalPolicy, Stack
from aws_cdk import aws_dynamodb as dynamodb
from aws_cdk import aws_lambda as lambda_
from aws_cdk import aws_s3 as s3
from aws_cdk import aws_s3_notifications as s3n
from aws_cdk import aws_sns as sns
from aws_cdk import aws_sns_subscriptions as subscriptions
from constructs import Construct


@dataclass
class DataPipelineStackProps:
    """Properties for the DataPipelineStack"""

    def __init__(
        self,
        calculated_energy_table: dynamodb.Table,
    ):
        self.calculated_energy_table = calculated_energy_table


class DataPipelineStack(Stack):
    """
    The stack class extends the base CDK Stack
    """

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        props: DataPipelineStackProps,
        **kwargs,
    ):
        """
        Constructor for the stack
        Args:
            scope: The CDK application scope
            construct_id: Stack ID
            props: Data pipeline stack properties
        """
        super().__init__(scope, construct_id, **kwargs)

        # Create raw landing bucket for S3
        self.raw_data_upload_bucket = s3.Bucket(
            self,
            "RawDataUploadBucket",
            bucket_name="home-energy-coach-raw-data-upload",
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
            lifecycle_rules=[s3.LifecycleRule(expiration=Duration.days(1))],
        )

        # Create S3 bucket to store transformed JSON
        self.json_transformed_bucket = s3.Bucket(
            self,
            "JsonTransformedBucket",
            bucket_name="home-energy-coach-json-transformed",
            versioned=True,
            removal_policy=RemovalPolicy.DESTROY,
        )

        # Create SNS Notification topic for raw data upload
        self.sns_topic_raw_upload = sns.Topic(
            self,
            "SnsTopicRawUpload",
            display_name="Home Energy Coach SNS Topic",
            topic_name="home-energy-coach-raw-upload",
        )

        # Add email subscription to SNS topic for raw upload
        self.sns_topic_raw_upload.add_subscription(
            subscriptions.EmailSubscription(props.admin_email_address)
        )

        # Create SNS Notification topic for calculator summary
        self.sns_topic_calculator_summary = sns.Topic(
            self,
            "SnsTopicCalculatorSummary",
            display_name="Home Energy Coach SNS Topic for calculator summary",
            topic_name="home-energy-coach-calculator-summary",
        )

        # Add email subscription to SNS topic for calculator summary
        self.sns_topic_calculator_summary.add_subscription(
            subscriptions.EmailSubscription(props.admin_email_address)
        )

        # Create Lambda function to transform CSV to JSON
        transform_to_json_lambda_function = lambda_.Function(
            self,
            "TransformToJsonLambdaFunction",
            function_name="transform-to-json",
            runtime=lambda_.Runtime.PYTHON_3_13,
            handler="app.lambda_handler",
            code=lambda_.Code.from_asset(
                os.path.join(
                    os.path.dirname(__file__), "./lambda/lambda-transform-to-json"
                )
            ),
            environment={
                "TRANSFORMED_BUCKET": self.json_transformed_bucket.bucket_name,
            },
            description="Lambda function transforms CSV to JSON and saves to S3 bucket",
        )

        # Create Lambda function to calculate energy usage and notify
        calculate_and_notify_lambda_function = lambda_.Function(
            self,
            "CalculateAndNotifyLambdaFunction",
            function_name="calculate-and-notify",
            runtime=lambda_.Runtime.PYTHON_3_13,
            handler="app.lambda_handler",
            code=lambda_.Code.from_asset(
                os.path.join(
                    os.path.dirname(__file__), "./lambda/lambda-calculate-notify"
                )
            ),
            environment={
                "SNS_TOPIC_CALCULATOR_SUMMARY": self.sns_topic_calculator_summary.topic_arn,
                "CALCULATED_ENERGY_TABLE_NAME": props.calculated_energy_table.table_name,
            },
            description="Lambda function calculates total energy usage and sends a summary notification via SNS",
        )

        self.processed_data_bucket = s3.Bucket(
            self,
            "ProcessedDataBucket",
            bucket_name="home-energy-coach-processed-data",
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
        )

        # Grant permissions for Lambda functions
        self.raw_data_upload_bucket.grant_read(transform_to_json_lambda_function)
        self.json_transformed_bucket.grant_write(transform_to_json_lambda_function)
        self.json_transformed_bucket.grant_read(calculate_and_notify_lambda_function)
        props.calculated_energy_table.grant_write_data(
            calculate_and_notify_lambda_function
        )

        # Add event notification to trigger CSV transformation on .csv files
        self.raw_data_upload_bucket.add_event_notification(
            s3.EventType.OBJECT_CREATED,
            s3n.SnsDestination(self.sns_topic_raw_upload),
            s3.NotificationKeyFilter(suffix=".csv"),
        )

        # Add event notification to trigger calculation on .json files
        self.json_transformed_bucket.add_event_notification(
            s3.EventType.OBJECT_CREATED,
            s3n.LambdaDestination(calculate_and_notify_lambda_function),
            s3.NotificationKeyFilter(suffix=".json"),
        )

        # Output S3 bucket names for reference
        CfnOutput(
            self,
            "RawDataLandingBucketName",
            value=self.raw_data_landing_bucket.bucket_name,
        )

        CfnOutput(
            self,
            "JsonTransformedBucketName",
            value=self.json_transformed_bucket.bucket_name,
        )

        ## Add SNS topic outputs
        CfnOutput(
            self,
            "SnsTopicRawUploadName",
            value=self.sns_topic_raw_upload.topic_name,
        )

        CfnOutput(
            self,
            "SnsTopicCalculatorSummaryName",
            value=self.sns_topic_calculator_summary.topic_name,
        )
