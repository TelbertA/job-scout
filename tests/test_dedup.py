import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import boto3
import pytest
from moto import mock_aws
from dedup import is_seen, filter_new_jobs, mark_seen


@pytest.fixture(autouse=True)
def ddb_table():
    with mock_aws():
        client = boto3.client("dynamodb", region_name="us-east-1")
        client.create_table(
            TableName="test-job-scout",
            AttributeDefinitions=[{"AttributeName": "job_id", "AttributeType": "S"}],
            KeySchema=[{"AttributeName": "job_id", "KeyType": "HASH"}],
            BillingMode="PAY_PER_REQUEST",
        )
        yield


def test_new_job_not_seen():
    assert is_seen("brand-new-id") is False


def test_mark_seen_then_is_seen():
    jobs = [{"job_id": "job-001", "job_title": "DevSecOps", "employer_name": "Acme"}]
    mark_seen(jobs)
    assert is_seen("job-001") is True


def test_filter_new_jobs_excludes_seen():
    jobs = [
        {"job_id": "old-job", "job_title": "Old", "employer_name": "X"},
        {"job_id": "new-job", "job_title": "New", "employer_name": "Y"},
    ]
    mark_seen([jobs[0]])
    result = filter_new_jobs(jobs)
    assert len(result) == 1
    assert result[0]["job_id"] == "new-job"


def test_filter_new_jobs_empty_input():
    assert filter_new_jobs([]) == []
