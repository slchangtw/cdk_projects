import os


def lambda_handler(event, context):
    environment = os.environ.get("ENVIRONMENT", "unknown")
    animal = os.environ.get("ANIMAL", "unknown")

    return {
        "status_code": 200,
        "message": f"Hello, World! Running in {environment} environment with {animal}",
    }
