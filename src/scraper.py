import logging
import time
import requests
from config import RAPIDAPI_KEY

logger = logging.getLogger(__name__)

BASE_URL = "https://jsearch.p.rapidapi.com/search"
HEADERS = {
    "X-RapidAPI-Key": RAPIDAPI_KEY,
    "X-RapidAPI-Host": "jsearch.p.rapidapi.com",
}

TARGET_QUERIES = [
    "DevSecOps Engineer",
    "Cloud Security Engineer",
    "DevOps Engineer",
    "Platform Engineer",
    "Security Automation Engineer",
]

def search_jobs(query: str, date_posted: str = "week", page: int = 1) -> list[dict]:
    params = {
        "query": query,
        "page": str(page),
        "num_pages": "1",
        "date_posted": date_posted,
        "country": "us",
        "language": "en",
    }
    try:
        response = requests.get(BASE_URL, headers=HEADERS, params=params, timeout=10)
        response.raise_for_status()
        return response.json().get("data", [])
    except requests.exceptions.RequestException as e:
        logger.error("JSearch API error for query '%s': %s", query, e)
        return []

def search_all_jobs() -> list[dict]:
    seen_ids: set[str] = set()
    all_jobs: list[dict] = []

    for query in TARGET_QUERIES:
        logger.info("Searching: %s", query)
        jobs = search_jobs(query)
        for job in jobs:
            job_id = job.get("job_id")
            if job_id and job_id not in seen_ids:
                seen_ids.add(job_id)
                all_jobs.append(job)
        # Respect rate limits: 200 req/month free tier (5 calls/day = 150/month)
        time.sleep(0.5)

    logger.info("Total unique jobs from API: %d", len(all_jobs))
    return all_jobs
