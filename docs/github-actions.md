# GitHub Actions Workflows Documentation

This project uses GitHub Actions for comprehensive CI/CD automation. All workflows are located in `.github/workflows/`.

## Workflows Overview

### 1. CI Pipeline (`ci.yml`)

**Trigger**: Push to `main`/`develop`, Pull Requests

**Purpose**: Automated testing and validation

**Jobs**:
- `test-backend`: Runs pytest on app and bot with PostgreSQL service, generates coverage reports
- `test-frontend`: Lints and builds the React app, uploads build artifacts
- `docker-build`: Tests Docker image builds for all services

**What it does**:
- ✅ Lints Python code with flake8
- ✅ Runs all tests with pytest
- ✅ Generates code coverage reports (uploads to Codecov)
- ✅ Verifies Docker images build successfully
- ✅ Uses GitHub Actions cache for faster builds

---

### 2. Docker Publish (`docker-publish.yml`)

**Trigger**: Push to `main`, version tags (`v*.*.*`), manual dispatch

**Purpose**: Build and publish Docker images to GitHub Container Registry

**Features**:
- Multi-platform builds (linux/amd64, linux/arm64)
- Semantic versioning from git tags
- Automatic `latest` tag on main branch
- Layer caching for faster builds
- Matrix strategy for parallel builds

**Image naming**:
- `ghcr.io/mainulhossain123/infra-autofix-agent-app:latest`
- `ghcr.io/mainulhossain123/infra-autofix-agent-bot:v1.0.0`
- `ghcr.io/mainulhossain123/infra-autofix-agent-frontend:main-abc1234`

---

### 3. Security Scanning (`security.yml`)

**Trigger**: Push, PRs, weekly schedule (Monday midnight)

**Purpose**: Automated security analysis

**Scanners**:
- **CodeQL**: Static code analysis for Python and JavaScript
- **Trivy**: Container vulnerability scanning (CRITICAL/HIGH severity)
- **Safety**: Python dependency security checks

**Reports**: Uploaded to GitHub Security tab (SARIF format)

---

### 4. Deployment (`deploy.yml`)

**Trigger**: Manual dispatch, version tags

**Purpose**: Deploy to cloud platforms

**Options**:
1. **AWS ECS Deployment**: Uses ECS task definitions, supports blue-green deployments
2. **VM Deployment**: SSH-based deployment using Docker Compose3. **Kubernetes**: For K8s deployments, see [Kubernetes Guide](kubernetes.md) - use ArgoCD, Flux, or kubectl apply
**Required Secrets**:
```
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
AWS_REGION
ECS_CLUSTER_NAME
DEPLOY_HOST
DEPLOY_USER
DEPLOY_SSH_KEY
```

**Usage**:
1. Go to Actions → Deploy to Cloud
2. Click "Run workflow"
3. Select environment (staging/production)
4. Enter version to deploy

---

### 5. Performance Testing (`performance.yml`)

**Trigger**: Manual dispatch, weekly schedule (Sunday 2 AM)

**Purpose**: Load testing with Locust

**Metrics**:
- Requests per second (RPS)
- Response times (p50, p95, p99)
- Error rates
- Concurrent users simulation

**Reports**: HTML reports uploaded as artifacts

---

### 6. Release (`release.yml`)

**Trigger**: Push version tags (`v*.*.*`)

**Purpose**: Create GitHub releases with changelogs

**Features**:
- Auto-generates changelog from commits
- Links to published Docker images
- Includes quick start instructions

**Example**:
```bash
git tag v1.2.0
git push origin v1.2.0
```

---

### 7. Cleanup (`cleanup.yml`)

**Trigger**: Weekly schedule (Sunday 3 AM), manual dispatch

**Purpose**: Housekeeping and storage management

**Actions**:
- Deletes container images older than 30 days (keeps 5 latest)
- Removes workflow run artifacts older than 30 days
- Keeps minimum 10 runs for history

---

## Dependabot Configuration

**File**: `.github/dependabot.yml`

**Updates**:
- Python packages (app + bot): Weekly on Monday
- npm packages (frontend): Weekly on Monday
- Docker base images: Weekly
- GitHub Actions versions: Monthly

**Auto-merging**: Can be configured with auto-merge apps like Kodiak or Mergify

---

## Setting Up Workflows

### Enable GitHub Actions
1. Go to repository Settings → Actions → General
2. Set "Workflow permissions" to "Read and write permissions"
3. Enable "Allow GitHub Actions to create and approve pull requests"

### Configure Secrets
1. Go to Settings → Secrets and variables → Actions
2. Add required secrets for deployment

### Enable GitHub Container Registry
1. Workflows will automatically push to `ghcr.io`
2. Make packages public: Settings → Packages → Package settings → Change visibility

### Branch Protection Rules
Recommended rules for `main` branch:
- ✅ Require status checks (CI Pipeline)
- ✅ Require pull request reviews
- ✅ Require conversation resolution
- ✅ Require linear history

---

## Local Testing

### Test Docker builds locally
```bash
docker build -t test-app ./app
docker build -t test-bot ./bot
docker build -t test-frontend ./frontend
```

### Test Locust load tests
```bash
pip install locust
locust -f tests/locustfile.py --host http://localhost:5000 --users 50 --spawn-rate 5
```

### Run security scans locally
```bash
# Trivy
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy image test-app:latest

# Safety
pip install safety
safety check -r app/requirements.txt
```

---

## Cost Optimization

- GitHub Actions minutes: Free for public repos, 2000 min/month for private
- Use caching to reduce build times
- Cleanup workflows reduce storage costs
- Self-hosted runners for unlimited builds (optional)

---

## Monitoring Workflows

**View workflow runs**: Actions tab in GitHub repo

**Badges**: Add to README for visibility
```markdown
[![CI](https://github.com/mainulhossain123/infra-autofix-agent/actions/workflows/ci.yml/badge.svg)](...)
```

**Notifications**: Settings → Notifications → Actions (email on failure)

---

## Best Practices

1. **Keep secrets secure**: Never commit secrets, use GitHub Secrets
2. **Use matrix strategies**: Parallelize builds for speed
3. **Cache dependencies**: Reduce workflow run times
4. **Pin action versions**: Use `@v4` not `@latest` for stability
5. **Test locally first**: Use `act` tool to run workflows locally
6. **Monitor costs**: Check Actions usage in Settings → Billing

---

## Troubleshooting

**Workflow fails on secrets**: Ensure all required secrets are configured

**Docker build timeout**: Increase timeout or optimize Dockerfile layers

**Rate limiting**: Use GitHub Actions cache and conditional runs

**Permission errors**: Check workflow permissions in Settings → Actions

---

## Future Enhancements

- [ ] Add integration tests with Playwright
- [ ] Implement canary deployments
- [ ] Add Slack/Discord notifications
- [ ] Database migration workflows
- [ ] Infrastructure as Code (Terraform) automation
- [ ] Auto-scaling based on metrics
