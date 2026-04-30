import json
from pathlib import Path

DEFAULT_PROFILE = Path(__file__).parent / "profiles" / "default_profile.json"

def load_profile(path: str = None) -> dict:
    profile_path = Path(path) if path else DEFAULT_PROFILE
    with open(profile_path) as f:
        return json.load(f)

def score_job(job: dict, profile: dict) -> dict:
    title = job.get("job_title", "").lower()
    desc = job.get("job_description", "").lower()
    text = f"{title} {desc}"

    score = 0
    matched = []

    for tier_name in ["tier_1", "tier_2", "tier_3", "tier_4"]:
        for keyword, weight in profile.get(tier_name, {}).items():
            if keyword.lower() in text:
                score += weight
                matched.append(keyword)

    for keyword, bonus in profile.get("bonus_keywords", {}).items():
        if keyword.lower() in text:
            score += bonus

    for neg in profile.get("negative_keywords", []):
        if neg.lower() in text:
            score = max(0, score - 50)
            matched.append(f"DISQUALIFIER: {neg}")

    return {
        **job,
        "score": score,
        "matched_skills": matched,
    }
