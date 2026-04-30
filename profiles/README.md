# Skill Profiles

Job Scout uses a JSON profile to score job postings against your background. Anyone can create their own profile and get personalized job matches without touching the scoring engine.

---

## Profile Structure

```json
{
  "name": "Your Name - Target Roles",
  "tier_1": { "keyword": points },
  "tier_2": { "keyword": points },
  "tier_3": { "keyword": points },
  "tier_4": { "keyword": points },
  "bonus_keywords": { "phrase": bonus_points },
  "negative_keywords": ["disqualifier phrase"]
}
```

### Tiers

| Tier | Points | Use for |
|---|---|---|
| tier_1 | 4 | Core skills that define your target role |
| tier_2 | 3 | Strong supporting skills you use regularly |
| tier_3 | 2 | Adjacent skills that round out a match |
| tier_4 | 1 | Certifications and soft signals |

### Bonus Keywords
Phrases that indicate a strong role match — added on top of tier scores. Use for job titles and experience ranges you're targeting.

### Negative Keywords
Any job containing these phrases gets a -50 penalty (floored at 0). Use for roles you are not qualified for or not interested in.

---

## How Scoring Works

The engine scans the job title and description for every keyword. Scores are additive — a job mentioning `docker`, `aws`, and `python` scores `4 + 4 + 4 = 12` from tier_1 alone. Bonus keywords stack on top. Any negative keyword match drives the score to 0.

Jobs scoring below 10 are filtered out before Discord and S3.

---

## Creating Your Profile

1. Copy the default profile:
```bash
cp profiles/default_profile.json profiles/my_profile.json
```

2. Edit `my_profile.json` — add your skills, remove irrelevant ones, set your target roles in `bonus_keywords`

3. Point the scoring engine to your profile by setting the `PROFILE_PATH` environment variable:
```bash
export PROFILE_PATH=profiles/my_profile.json
```

Or pass it directly when running locally:
```bash
python -c "from src.scoring import load_profile, score_job; p = load_profile('profiles/my_profile.json'); print(p['name'])"
```

---

## Tips

- **Be honest with tier_1** — only put skills you can speak to in an interview
- **Use exact strings** — matching is case-insensitive substring search, so `"ci/cd"` matches "CI/CD pipelines"
- **Tune negative_keywords aggressively** — "10+ years" and "principal engineer" are good defaults to keep
- **Check matched_skills in logs** — CloudWatch logs show exactly which keywords each job matched
