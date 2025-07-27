# Hello World Lambda using CDK

This repository demonstrates a simple Hello World Lambda function deployed using AWS Cloud Development Kit (CDK). The Lambda function returns different environment variables depending on whether it's deployed to the test or production environment.

## Setup

1. Install the Dependencies.
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Deploy the stack to test or production environment.
```bash
cdk deploy
cdk deploy -c env=prod
```

## Clean up the AWS Resources

1. Destroy the stack.
```bash
cdk destroy
```
