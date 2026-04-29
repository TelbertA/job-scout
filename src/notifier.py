import logging
import requests
from config import DISCORD_WEBHOOK_URL

logger = logging.getLogger(__name__)

MAX_JOBS_PER_MESSAGE = 10
SCORE_COLOR_MAP = [
    (50, 0x00FF00),   # green  - excellent match
    (30, 0xFFAA00),   # orange - strong match
    (0,  0x5865F2),   # blurple - standard
]

def _score_color(score: int) -> int:
    for threshold, color in SCORE_COLOR_MAP:
        if score >= threshold:
            return color
    return 0x5865F2

def _build_embed(job: dict) -> dict:
    salary = ""
    if job.get("job_min_salary") and job.get("job_max_salary"):
        lo = int(job["job_min_salary"])
        hi = int(job["job_max_salary"])
        salary = f"\n**Salary:** ${lo:,} - ${hi:,}"

    skills_preview = ", ".join(job.get("matched_skills", [])[:8])

    return {
        "title": f"{job.get('job_title', 'Unknown Title')} @ {job.get('employer_name', 'Unknown')}",
        "url": job.get("job_apply_link", ""),
        "color": _score_color(job["score"]),
        "fields": [
            {"name": "Score", "value": str(job["score"]), "inline": True},
            {"name": "Location", "value": job.get("job_city", "Remote") or "Remote", "inline": True},
            {"name": "Type", "value": job.get("job_employment_type", "N/A"), "inline": True},
            {"name": "Matched Skills", "value": skills_preview or "N/A", "inline": False},
        ],
        "description": salary,
        "footer": {"text": f"via {job.get('job_publisher', 'JSearch')}"},
    }

def post_to_discord(jobs: list[dict], date_str: str) -> None:
    if not DISCORD_WEBHOOK_URL:
        logger.warning("DISCORD_WEBHOOK_URL not set — skipping notification")
        return
    if not jobs:
        logger.info("No qualified jobs to post")
        return

    top_jobs = sorted(jobs, key=lambda j: j["score"], reverse=True)[:MAX_JOBS_PER_MESSAGE]

    payload = {
        "content": f"**Job Scout Report — {date_str}** | {len(jobs)} qualified jobs found",
        "embeds": [_build_embed(job) for job in top_jobs],
    }

    try:
        resp = requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=10)
        resp.raise_for_status()
        logger.info("Posted %d jobs to Discord", len(top_jobs))
    except requests.exceptions.RequestException as e:
        logger.error("Discord webhook error: %s", e)
