import json
import os
from functools import lru_cache

import boto3
from dotenv import load_dotenv


@lru_cache(maxsize=1)
def get_secrets() -> dict:
    if os.environ.get("SECRET_ARN"):
        client = boto3.client(
            "secretsmanager", region_name=os.environ["APP_AWS_REGION"]
        )
        secret = client.get_secret_value(SecretId=os.environ["SECRET_ARN"])
        secrets = json.loads(secret["SecretString"])
    else:
        load_dotenv()
        secrets = {
            "NEBIUS_API_KEY": os.getenv("NEBIUS_API_KEY"),
            "TAVILY_API_KEY": os.getenv("TAVILY_API_KEY"),
        }

    missing = [k for k in ("NEBIUS_API_KEY", "TAVILY_API_KEY")
               if not secrets.get(k)]
    if missing:
        raise RuntimeError(f"Missing required secrets: {', '.join(missing)}")

    return secrets


# import json
# import os
# from functools import lru_cache

# import boto3
# from dotenv import load_dotenv


# @lru_cache(maxsize=1)
# def get_secrets() -> dict:
#     if os.environ.get("SECRET_ARN"):
#         client = boto3.client(
#             "secretsmanager", region_name=os.environ["APP_AWS_REGION"]
#         )
#         secret = client.get_secret_value(SecretId=os.environ["SECRET_ARN"])
#         return json.loads(secret["SecretString"])

#     load_dotenv()
#     return {
#         "NEBIUS_API_KEY": os.getenv("NEBIUS_API_KEY"),
#         "TAVILY_API_KEY": os.getenv("TAVILY_API_KEY"),
#     }
