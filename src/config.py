import os
import boto3

def _is_lambda() -> bool:
    return "AWS_LAMBDA_FUNCTION_NAME" in os.environ

def get_secret(name: str) -> str:
    if _is_lambda():
        ssm = boto3.client("ssm")
        resp = ssm.get_parameter(Name=name, WithDecryption=True)
        return resp["Parameter"]["Value"]
    # Local dev: derive env var name from SSM path (e.g. /job-scout/rapidapi-key -> RAPIDAPI_KEY)
    env_key = name.split("/")[-1].upper().replace("-", "_")
    return os.environ.get(env_key, "")

RAPIDAPI_KEY = get_secret("/job-scout/rapidapi-key")
DISCORD_WEBHOOK_URL = get_secret("/job-scout/discord-webhook")
DYNAMODB_TABLE = os.environ.get("DYNAMODB_TABLE", "job-scout-seen")
S3_BUCKET = os.environ.get("S3_BUCKET", "job-scout-reports")
MIN_SCORE = int(os.environ.get("MIN_SCORE", "10"))
TOP_N = int(os.environ.get("TOP_N", "10"))
