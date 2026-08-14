import boto3
import json
import os
from functools import lru_cache
from dotenv import load_dotenv


@lru_cache(maxsize=1)
def get_secrets() -> dict:
    if os.environ.get("SECRET_ARN"):
        client = boto3.client(
            "secretsmanager", region_name=os.environ["APP_AWS_REGION"])
        secret = client.get_secret_value(SecretId=os.environ["SECRET_ARN"])
        return json.loads(secret["SecretString"])

    load_dotenv()
    return {
        "NEBIUS_API_KEY": os.getenv("NEBIUS_API_KEY"),
        "TAVILY_API_KEY": os.getenv("TAVILY_API_KEY"),
    }
