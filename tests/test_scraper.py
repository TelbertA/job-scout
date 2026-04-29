import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from unittest.mock import patch, MagicMock
from scraper import search_jobs, search_all_jobs


def _mock_response(jobs: list) -> MagicMock:
    mock = MagicMock()
    mock.json.return_value = {"data": jobs}
    mock.raise_for_status.return_value = None
    return mock


def test_search_jobs_returns_data():
    fake_jobs = [{"job_id": "1", "job_title": "DevSecOps Engineer"}]
    with patch("scraper.requests.get", return_value=_mock_response(fake_jobs)):
        result = search_jobs("DevSecOps Engineer remote")
    assert result == fake_jobs


def test_search_jobs_returns_empty_on_error():
    import requests as req
    with patch("scraper.requests.get", side_effect=req.exceptions.RequestException("timeout")):
        result = search_jobs("DevSecOps Engineer remote")
    assert result == []


def test_search_all_jobs_deduplicates():
    fake_job = {"job_id": "dup-1", "job_title": "DevSecOps Engineer"}
    with patch("scraper.requests.get", return_value=_mock_response([fake_job])):
        with patch("scraper.time.sleep"):
            result = search_all_jobs()
    # Same job_id appears in every query combo — should only appear once
    ids = [j["job_id"] for j in result]
    assert ids.count("dup-1") == 1
