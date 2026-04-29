import logging
import time
import boto3
from botocore.exceptions import ClientError
from config import DYNAMODB_TABLE

logger = logging.getLogger(__name__)

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(DYNAMODB_TABLE)

TTL_DAYS = 90
TTL_SECONDS = TTL_DAYS * 24 * 60 * 60

def _ttl_timestamp() -> int:
    return int(time.time()) + TTL_SECONDS

def is_seen(job_id: str) -> bool:
    try:
        resp = table.get_item(Key={"job_id": job_id})
        return "Item" in resp
    except ClientError as e:
        logger.error("DynamoDB get_item error: %s", e)
        return False

def filter_new_jobs(jobs: list[dict]) -> list[dict]:
    return [j for j in jobs if not is_seen(j.get("job_id", ""))]

def mark_seen(jobs: list[dict]) -> None:
    with table.batch_writer() as batch:
        for job in jobs:
            job_id = job.get("job_id")
            if not job_id:
                continue
            try:
                batch.put_item(Item={
                    "job_id": job_id,
                    "job_title": job.get("job_title", ""),
                    "employer_name": job.get("employer_name", ""),
                    "ttl": _ttl_timestamp(),
                })
            except ClientError as e:
                logger.error("DynamoDB put_item error for %s: %s", job_id, e)
