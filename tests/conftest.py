import os

# Set env vars before any src imports so config.py reads these instead of SSM
os.environ.setdefault("AWS_DEFAULT_REGION", "us-east-1")
os.environ.setdefault("DYNAMODB_TABLE", "test-job-scout")
os.environ.setdefault("S3_BUCKET", "test-reports")
os.environ.setdefault("RAPIDAPI_KEY", "test-key")
os.environ.setdefault("DISCORD_WEBHOOK_URL", "")
