# Job Scout

Automated job discovery pipeline built as a DevSecOps portfolio project. Scrapes job postings via the JSearch API, scores each against a configurable skill profile, deduplicates in DynamoDB, stores HTML reports in S3, and posts top matches to Discord daily.

---

## Architecture

```
Developer Workstation
  │
  ├── Pre-commit hooks (detect-secrets, bandit, YAML checks)
  │
  ▼
GitHub (main branch, protected)
  │
  ├── PR → GitHub Actions CI
  │     ├── TruffleHog   (secrets detection)
  │     ├── Bandit       (Python SAST)
  │     ├── pip-audit    (dependency CVE scan)
  │     ├── cfn-lint     (IaC validation)
  │     ├── Trivy        (container vulnerability scan)
  │     └── pytest       (unit tests, 70%+ coverage)
  │
  └── Merge to main → GitHub Actions CD
        ├── OIDC auth to AWS (no stored credentials)
        ├── Docker build → push to ECR (scan-on-push)
        └── CloudFormation deploy
  │
  ▼
AWS (us-east-1)
  ├── EventBridge (cron: 12:00 UTC daily)
  │     └── triggers Lambda
  ├── Lambda (container image from ECR)
  │     ├── Reads secrets from SSM Parameter Store (KMS-encrypted)
  │     ├── Calls JSearch API → scores jobs → deduplicates
  │     ├── Posts top 20 matches to Discord
  │     └── Saves HTML report to S3
  ├── DynamoDB   (job_id dedup store, TTL 90 days, encrypted at rest)
  ├── S3         (HTML reports, SSE-S3, HTTPS-only policy)
  ├── ECR        (container registry, scan-on-push)
  └── SSM        (API keys as SecureString)
```

---

## Zero Trust Design

| Principle | Implementation |
|---|---|
| Verify explicitly | OIDC federation — GitHub Actions gets short-lived tokens, no stored AWS keys |
| Least privilege | IAM policies scoped to specific resource ARNs, no wildcards |
| Assume breach | Secrets in SSM (KMS-encrypted), DynamoDB TTL, S3 versioning |
| Encrypt everywhere | DynamoDB SSE, S3 SSE-S3, SSM SecureString, HTTPS-only bucket policy |
| Continuous validation | CI scans on every PR, ECR scan-on-push, CloudWatch logging |

---

## Project Structure

```
job-scout/
├── .github/workflows/
│   ├── ci.yml          # PR: 6 security gates + tests
│   └── cd.yml          # Merge: build → ECR → CloudFormation deploy
├── src/
│   ├── handler.py      # Lambda entry point
│   ├── scraper.py      # JSearch API client
│   ├── scoring.py      # Skill scoring engine
│   ├── dedup.py        # DynamoDB deduplication
│   ├── notifier.py     # Discord webhook
│   ├── report.py       # HTML report generator
│   └── config.py       # Centralized config + SSM reads
├── profiles/
│   └── default_profile.json   # Skill profile (customizable)
├── tests/              # Unit tests (pytest + moto)
├── k8s/                # Kubernetes CronJob manifest
├── Dockerfile          # Multi-stage build
└── template.yaml       # CloudFormation IaC
```

---

## Deploy Your Own

### Prerequisites
- AWS account with CLI configured
- Docker
- Python 3.12+
- RapidAPI account with JSearch subscription
- Discord webhook URL

### 1. Clone and configure

```bash
git clone https://github.com/TelbertA/job-scout.git
cd job-scout
cp profiles/default_profile.json profiles/my_profile.json
# Edit my_profile.json with your skills
```

### 2. Store secrets in SSM

```bash
aws ssm put-parameter --name "/job-scout/rapidapi-key" \
  --type SecureString --value "YOUR_KEY"

aws ssm put-parameter --name "/job-scout/discord-webhook" \
  --type SecureString --value "YOUR_WEBHOOK_URL"
```

### 3. Create ECR repository

```bash
aws ecr create-repository --repository-name job-scout \
  --image-scanning-configuration scanOnPush=true \
  --encryption-configuration encryptionType=AES256
```

### 4. Build and push the container

```bash
docker build --platform linux/amd64 --provenance=false -t job-scout:latest .
docker tag job-scout:latest <ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/job-scout:latest
docker push <ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/job-scout:latest
```

### 5. Deploy infrastructure

```bash
aws cloudformation deploy \
  --stack-name job-scout \
  --template-file template.yaml \
  --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM
```

### 6. Test

```bash
aws lambda invoke --function-name job-scout \
  --payload '{}' --cli-binary-format raw-in-base64-out \
  --invocation-type Event output.json
```

---

## Customizing Your Skill Profile

See [profiles/README.md](profiles/README.md) for how to create a profile tailored to your background.

---

## CI/CD Security Gates

Every pull request must pass all six gates before merging:

| Gate | Tool | What it checks |
|---|---|---|
| Secrets | TruffleHog | Leaked credentials in commits |
| SAST | Bandit | Insecure Python patterns |
| Dependencies | pip-audit | Known CVEs in packages |
| IaC | cfn-lint | CloudFormation misconfigurations |
| Container | Trivy | OS/library CVEs in Docker image |
| Tests | pytest | Logic correctness, 70%+ coverage |

---

## License

MIT
