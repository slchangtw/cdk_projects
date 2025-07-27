from enum import Enum

from aws_cdk import Stack
from aws_cdk import aws_lambda as _lambda
from constructs import Construct


class Environment(Enum):
    TEST = "test"
    PROD = "prod"


class CdkHelloWorldStack(Stack):
    # Environment-specific configurations
    ENV_CONFIG = {
        Environment.TEST.value: {
            "animal": "cat",
        },
        Environment.PROD.value: {
            "animal": "dog",
        },
    }

    def __init__(
        self, scope: Construct, construct_id: str, env: str = "test", **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Validate environment
        valid_environments = [e.value for e in Environment]
        if env not in valid_environments:
            raise ValueError(
                f"Environment must be one of {valid_environments}, got: {env}"
            )

        # Get environment-specific configuration
        env_config = self.ENV_CONFIG[env]

        # Create a Lambda function
        lambda_function = _lambda.Function(
            self,
            "HelloWorldLambda",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="app.lambda_handler",
            code=_lambda.Code.from_asset("lib/lambda"),
            function_name=f"hello-world-{env}",
            environment={
                "ENVIRONMENT": env,
                "STACK_NAME": construct_id,
                "ANIMAL": env_config["animal"],
            },
        )
