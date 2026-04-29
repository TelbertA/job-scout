import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from scoring import score_job, load_profile

PROFILE = load_profile()


def test_devsecops_job_scores_high():
    job = {
        "job_title": "DevSecOps Engineer",
        "job_description": (
            "CI/CD pipeline GitHub Actions Docker Kubernetes Python "
            "AWS Lambda Terraform SAST secrets detection"
        ),
    }
    result = score_job(job, PROFILE)
    assert result["score"] >= 30


def test_irrelevant_job_scores_zero():
    job = {
        "job_title": "Physical Security Guard",
        "job_description": "CCTV armed unarmed loss prevention 15+ years",
    }
    result = score_job(job, PROFILE)
    assert result["score"] == 0


def test_devops_with_bonus():
    job = {
        "job_title": "DevOps Engineer",
        "job_description": "Python AWS Docker CI/CD Terraform 3-5 years",
    }
    result = score_job(job, PROFILE)
    assert result["score"] >= 25


def test_empty_job_scores_zero():
    job = {"job_title": "", "job_description": ""}
    result = score_job(job, PROFILE)
    assert result["score"] == 0


def test_matched_skills_populated():
    job = {
        "job_title": "Cloud Engineer",
        "job_description": "AWS Lambda Python CloudFormation",
    }
    result = score_job(job, PROFILE)
    assert len(result["matched_skills"]) > 0


def test_original_job_fields_preserved():
    job = {
        "job_id": "abc123",
        "job_title": "Platform Engineer",
        "job_description": "kubernetes docker aws",
    }
    result = score_job(job, PROFILE)
    assert result["job_id"] == "abc123"
    assert "score" in result
    assert "matched_skills" in result
