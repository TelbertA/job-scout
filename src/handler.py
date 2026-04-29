import json
import logging
from datetime import date

import boto3

from scraper import search_all_jobs
from scoring import score_job, load_profile
from dedup import filter_new_jobs, mark_seen
from notifier import post_to_discord
from report import generate_html
from config import S3_BUCKET, MIN_SCORE

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3 = boto3.client("s3")

def lambda_handler(event, context):
    today = date.today().isoformat()
    profile = load_profile()

    logger.info("Starting Job Scout run for %s", today)

    raw_jobs = search_all_jobs()
    logger.info("Scraped %d total jobs", len(raw_jobs))

    new_jobs = filter_new_jobs(raw_jobs)
    logger.info("New (unseen): %d", len(new_jobs))

    scored = [score_job(job, profile) for job in new_jobs]
    scored.sort(key=lambda j: j["score"], reverse=True)
    qualified = [j for j in scored if j["score"] >= MIN_SCORE]
    logger.info("Qualified (score >= %d): %d", MIN_SCORE, len(qualified))

    mark_seen(qualified)

    post_to_discord(qualified, today)

    html = generate_html(qualified, today)
    s3.put_object(
        Bucket=S3_BUCKET,
        Key=f"reports/job_report_{today}.html",
        Body=html.encode("utf-8"),
        ContentType="text/html",
    )
    logger.info("Report saved to s3://%s/reports/job_report_%s.html", S3_BUCKET, today)

    result = {
        "statusCode": 200,
        "body": json.dumps({
            "date": today,
            "scraped": len(raw_jobs),
            "new": len(new_jobs),
            "qualified": len(qualified),
        }),
    }
    logger.info("Run complete: %s", result["body"])
    return result
