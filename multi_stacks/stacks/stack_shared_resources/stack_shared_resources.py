from aws_cdk import CfnOutput, RemovalPolicy, Stack
from aws_cdk import aws_dynamodb as dynamodb
from constructs import Construct


class SharedResourcesStackProps:
    """Properties for the SharedResourcesStack"""

    def __init__(self, stage: str):
        self.stage = stage


class SharedResourcesStack(Stack):
    """
    The stack class extends the base CDK Stack
    """

    calculated_energy_table: dynamodb.Table

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        props: SharedResourcesStackProps,
        **kwargs,
    ):
        """
        Constructor for the stack
        Args:
            scope: The CDK application scope
            construct_id: Stack ID
            props: Stack properties including adminEmailAddress
        """
        super().__init__(scope, construct_id, **kwargs)

        # Create DynamoDB table for calculated energy data
        self.calculated_energy_table = dynamodb.Table(
            self,
            "CalculatedEnergyTable",
            partition_key=dynamodb.Attribute(
                name="customerId", type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="timestamp", type=dynamodb.AttributeType.STRING
            ),
            removal_policy=RemovalPolicy.DESTROY,
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            time_to_live_attribute=dynamodb.Attribute(
                name="ttl", type=dynamodb.AttributeType.NUMBER
            ),
            point_in_time_recovery=True,
        )

        # Add a global secondary index to the table
        self.calculated_energy_table.add_global_secondary_index(
            index_name="customerId-timestamp-index",
            partition_key=dynamodb.Attribute(
                name="customerId", type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="timestamp", type=dynamodb.AttributeType.STRING
            ),
        )

        # Output the table name
        CfnOutput(
            self,
            "CalculatedEnergyTableName",
            value=self.calculated_energy_table.table_name,
        )
