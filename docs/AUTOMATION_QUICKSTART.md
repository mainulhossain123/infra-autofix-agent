# Quick Start: GitHub Actions Automation

## What Was Added

Your infra-autofix-agent now has a **complete CI/CD pipeline** with 7 automated workflows:

### 🔄 **Continuous Integration** 
Every push/PR automatically:
- Runs Python tests with pytest
- Lints code with flake8
- Builds frontend with npm
- Tests all Docker images
- Generates coverage reports

### 🐳 **Docker Publishing**
Automatically builds multi-platform images and publishes to GitHub Container Registry on:
- Every push to `main`
- Version tags (e.g., `v1.0.0`)
- Manual trigger

### 🔒 **Security Scanning**
Weekly and on-demand scans:
- CodeQL for code vulnerabilities
- Trivy for container security
- Safety for Python dependencies

### 🚀 **Deployment**
Manual deployment to:
- AWS ECS (with task definitions)
- Remote VM via SSH + Docker Compose

### ⚡ **Performance Testing**
Weekly Locust load tests measuring:
- API response times
- Throughput (requests/sec)
- Error rates under load

### 📦 **Automated Updates**
Dependabot creates PRs for:
- Python packages (weekly)
- npm packages (weekly)
- Docker base images (weekly)
- GitHub Actions (monthly)

### 🧹 **Cleanup**
Automatic housekeeping:
- Removes old container images (30+ days)
- Cleans workflow artifacts
- Reduces storage costs

---

## Getting Started

### 1. Enable Workflows
Once you push these files to GitHub:

```powershell
git add .github/
git add docs/github-actions.md
git add tests/locustfile.py
git add README.md
git commit -m "feat: add GitHub Actions CI/CD automation"
git push origin main
```

Workflows will start automatically!

### 2. View Workflows
Go to: `https://github.com/mainulhossain123/infra-autofix-agent/actions`

### 3. Pull Published Images
After first successful build:

```powershell
docker pull ghcr.io/mainulhossain123/infra-autofix-agent-app:latest
docker pull ghcr.io/mainulhossain123/infra-autofix-agent-bot:latest
docker pull ghcr.io/mainulhossain123/infra-autofix-agent-frontend:latest
```

### 4. Create a Release
To trigger release workflow:

```powershell
git tag v1.0.0
git push origin v1.0.0
```

This will:
- Create GitHub release with changelog
- Build & tag Docker images with version
- Optionally trigger deployment

---

## Configuration

### Required GitHub Secrets (for deployment)

Go to: Settings → Secrets and variables → Actions

**For AWS ECS:**
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_REGION` (e.g., `us-east-1`)
- `ECS_CLUSTER_NAME`

**For VM deployment:**
- `DEPLOY_HOST` (server IP/hostname)
- `DEPLOY_USER` (SSH username)
- `DEPLOY_SSH_KEY` (private key)
- `DEPLOY_PORT` (optional, default: 22)

### Enable GitHub Container Registry

1. Go to Settings → Actions → General
2. Set "Workflow permissions": **Read and write permissions**
3. Enable: **Allow GitHub Actions to create and approve pull requests**

### Make Packages Public (optional)

After first workflow run:
1. Go to your profile → Packages
2. Select `infra-autofix-agent-*` packages
3. Package settings → Change visibility → Public

---

## What Happens Next

### On Every Push/PR:
✅ Tests run automatically  
✅ Code is linted  
✅ Docker builds are validated  
✅ Security scans detect vulnerabilities  
✅ Status checks show on PR  

### On Push to Main:
✅ Docker images built and pushed to GHCR  
✅ Tagged with `latest` and git SHA  
✅ Available for deployment  

### Weekly (Automated):
✅ Security scans run  
✅ Performance tests execute  
✅ Dependabot checks for updates  
✅ Old artifacts cleaned up  

### On Version Tag:
✅ GitHub release created  
✅ Versioned Docker images published  
✅ Changelog auto-generated  
✅ Deployment can be triggered  

---

## Usage Examples

### Manual Deployment
1. Go to Actions → "Deploy to Cloud"
2. Click "Run workflow"
3. Select:
   - Environment: `staging` or `production`
   - Version: `latest` or `v1.0.0`
4. Click "Run workflow"

### View Security Issues
1. Go to Security tab
2. Click "Code scanning"
3. Review CodeQL and Trivy findings

### Check Performance
1. Go to Actions → "Performance Testing"
2. Click latest run
3. Download HTML report from artifacts

### View Coverage
1. CI workflow uploads to Codecov
2. Or download coverage.xml from artifacts

---

## Monitoring

### Status Badges
Already added to README.md:
- [![CI Pipeline](badge)](link)
- [![Security Scanning](badge)](link)
- [![Docker Publish](badge)](link)

### Notifications
Configure in Settings → Notifications → Actions:
- Email on workflow failure
- Slack/Discord webhooks (add to workflows)

---

## Cost Optimization

### Free Tier (Public Repos)
- ✅ Unlimited GitHub Actions minutes
- ✅ Unlimited GitHub Packages storage
- ✅ All features included

### Private Repos
- 2,000 free minutes/month
- 500MB free storage
- Use caching to reduce build time
- Self-hosted runners for unlimited builds

### Current Optimizations
✅ Layer caching for Docker builds  
✅ npm/pip dependency caching  
✅ Parallel matrix builds  
✅ Automatic cleanup workflows  

---

## Troubleshooting

### Workflow Fails on First Run
**Issue**: Missing secrets  
**Solution**: Add required secrets in Settings → Secrets

### Docker Images Not Public
**Issue**: Can't pull images  
**Solution**: Change package visibility to public

### Tests Fail
**Issue**: Environment differences  
**Solution**: Check test logs, adjust test database config

### Rate Limiting
**Issue**: Too many requests  
**Solution**: GitHub Actions has high limits, but add delays if needed

---

## Next Steps

### Recommended Enhancements
1. **Add integration tests**: Playwright for frontend
2. **Database migrations**: Automated with Alembic
3. **Monitoring integration**: Datadog, New Relic
4. **Slack notifications**: Add to deploy.yml
5. **Canary deployments**: Gradual rollout
6. **Infrastructure as Code**: Terraform workflows

### Branch Protection
Enable for `main` branch:
1. Settings → Branches → Add rule
2. Require status checks: `test-backend`, `test-frontend`, `docker-build`
3. Require pull request reviews
4. Require conversation resolution

### Auto-merge Dependabot
Install Kodiak or Mergify to auto-merge:
- Patch version updates
- When CI passes
- When security approved

---

## Support

📚 **Full Documentation**: [docs/github-actions.md](docs/github-actions.md)  
🐛 **Report Issues**: Use bug report template  
💡 **Feature Requests**: Use feature request template  
📖 **GitHub Actions Docs**: https://docs.github.com/actions  

---

**You're all set!** 🎉

Your project now has production-ready automation. Push these changes and watch the magic happen!
