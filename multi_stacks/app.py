#!/usr/bin/env python3

import os

import aws_cdk as cdk

from stacks.stack_data_pipeline.stack_data_pipeline import (
    DataPipelineStack,
    DataPipelineStackProps,
)
from stacks.stack_shared_resources.stack_shared_resources import (
    SharedResourcesStack,
    SharedResourcesStackProps,
)

# Environment configuration for the CDK app.
# This includes the account and region.
# In this configuration account and region are
# taken from environmental variables with the AWS
# CLI configured AWS profile.
app_env = cdk.Environment(
    account=os.getenv("CDK_DEFAULT_ACCOUNT"),
    region=os.getenv("CDK_DEFAULT_REGION"),
)

# Description for the stack. This description gets
# passed in to every stack to create a unique identifier.
desc = "Home energy coach application from Hands-on AWS CDK Book"

# The CDK app.
# This is the top level class and all stacks and constructs are
# defined within this app construct. There can only be one app
# within this file, but you can have multiple apps within the
# bin directory.
app = cdk.App()

# SharedResourcesStack constructor.
# We are instantiating a new instance of
# the SharedResourcesStack class and passing in the props below
shared_resources_stack = SharedResourcesStack(
    app,
    "SharedResourcesStack",
    props=SharedResourcesStackProps(admin_email_address="edi7709@gmail.com"),
    env=app_env,
    description=desc,
)

data_pipeline_stack_props = DataPipelineStackProps(
    raw_data_landing_bucket=shared_resources_stack.raw_data_upload_bucket,
    sns_topic_raw_upload=shared_resources_stack.sns_topic_raw_upload,
    sns_topic_calculator_summary=shared_resources_stack.sns_topic_calculator_summary,
    calculated_energy_table=shared_resources_stack.calculated_energy_table,
)

# DataPipelineStack constructor.
# We are instantiating a new instance of
# the DataPipelineStack class and passing in the props below
data_pipeline_stack = DataPipelineStack(
    app,
    "DataPipelineStack",
    env=app_env,
    description=desc,
    props=data_pipeline_stack_props,
)

app.synth()
