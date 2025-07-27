import aws_cdk as core
import aws_cdk.assertions as assertions

from multi_stacks.multi_stacks_stack import MultiStacksStack

# example tests. To run these tests, uncomment this file along with the example
# resource in multi_stacks/multi_stacks_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = MultiStacksStack(app, "multi-stacks")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
