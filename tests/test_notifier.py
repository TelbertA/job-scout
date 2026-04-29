import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from unittest.mock import patch, MagicMock
from notifier import post_to_discord, _score_color


def test_score_color_green():
    assert _score_color(55) == 0x00FF00


def test_score_color_orange():
    assert _score_color(35) == 0xFFAA00


def test_score_color_default():
    assert _score_color(5) == 0x5865F2


def test_post_to_discord_skips_when_no_webhook():
    # DISCORD_WEBHOOK_URL is "" in conftest — should not call requests
    with patch("notifier.requests.post") as mock_post:
        post_to_discord([{"score": 20, "job_title": "DevOps"}], "2026-04-29")
    mock_post.assert_not_called()


def test_post_to_discord_calls_webhook():
    jobs = [{
        "job_id": "1", "job_title": "DevSecOps", "employer_name": "Acme",
        "job_apply_link": "https://example.com", "score": 45,
        "matched_skills": ["docker", "aws"], "job_city": "Remote",
        "job_employment_type": "FULLTIME", "job_publisher": "LinkedIn",
        "job_min_salary": None, "job_max_salary": None,
    }]
    mock_resp = MagicMock()
    mock_resp.raise_for_status.return_value = None

    with patch("notifier.DISCORD_WEBHOOK_URL", "https://discord.com/api/webhooks/fake"):
        with patch("notifier.requests.post", return_value=mock_resp) as mock_post:
            post_to_discord(jobs, "2026-04-29")

    mock_post.assert_called_once()
