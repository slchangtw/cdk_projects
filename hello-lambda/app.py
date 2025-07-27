import aws_cdk as cdk

from lib.cdk_hello_world_stack import CdkHelloWorldStack, Environment

app = cdk.App()

# Get environment from context (defaults to 'test' if not specified)
env = app.node.try_get_context("env") or "test"

# Validate environment - only allow 'test' and 'prod'
valid_environments = [e.value for e in Environment]
if env not in valid_environments:
    raise ValueError(f"Environment must be one of {valid_environments}, got: {env}")

CdkHelloWorldStack(
    app,
    f"HelloWorldStack-{env}",
    env=env,
)
app.synth()
