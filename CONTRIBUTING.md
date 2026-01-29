# Contributing to infra-autofix-agent

Thank you for considering contributing to this project! This document outlines the process and guidelines.

## 🤝 How to Contribute

### Reporting Bugs

1. Check if the bug is already reported in [Issues](https://github.com/mainulhossain123/infra-autofix-agent/issues)
2. Use the bug report template
3. Include:
   - Clear description
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details
   - Logs/screenshots

### Suggesting Features

1. Check existing feature requests
2. Use the feature request template
3. Describe the problem it solves
4. Provide use cases and examples

### Pull Requests

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes
4. Write/update tests
5. Update documentation
6. Commit with clear messages: `feat: add anomaly detection`
7. Push and create a PR

## 📝 Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/infra-autofix-agent.git
cd infra-autofix-agent

# Install dependencies
cd app && pip install -r requirements.txt
cd ../bot && pip install -r requirements.txt
cd ../frontend && npm install

# Run with Docker
docker compose up --build -d
```

## 🧪 Testing

```bash
# Run Python tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov=bot

# Frontend tests
cd frontend && npm test
```

## 📐 Code Style

### Python
- Follow PEP 8
- Use `black` for formatting
- Use `flake8` for linting
- Type hints recommended

```bash
black app/ bot/
flake8 app/ bot/
```

### JavaScript/React
- Use Prettier for formatting
- Follow Airbnb style guide
- Use ESLint

```bash
npm run lint
npm run format
```

## 🔀 Git Workflow

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation only
- `style:` - Code style (formatting, no logic change)
- `refactor:` - Code refactoring
- `test:` - Adding tests
- `chore:` - Maintenance tasks

Examples:
```
feat(bot): add ML-based anomaly detection
fix(app): resolve memory leak in metrics collection
docs(observability): update Grafana dashboard guide
```

### Branch Naming

- `feature/description` - New features
- `fix/description` - Bug fixes
- `docs/description` - Documentation
- `refactor/description` - Refactoring

## 📋 PR Checklist

Before submitting:

- [ ] Code follows style guidelines
- [ ] Tests added/updated and passing
- [ ] Documentation updated
- [ ] Commit messages are clear
- [ ] No merge conflicts
- [ ] CI checks pass
- [ ] Breaking changes documented

## 🏗️ Project Structure

```
├── app/              # Flask backend
├── bot/              # Remediation bot
├── frontend/         # React dashboard
├── prometheus/       # Prometheus config
├── grafana/          # Grafana dashboards
├── loki/             # Loki logging config
├── docs/             # Documentation
├── tests/            # Test files
└── .github/          # GitHub Actions workflows
```

## 🔍 Code Review

PRs are reviewed for:
- Code quality and style
- Test coverage
- Performance impact
- Security considerations
- Documentation completeness

## 📖 Documentation

- Update README.md for user-facing changes
- Update relevant docs/ files
- Add inline comments for complex logic
- Include docstrings for functions/classes

## 🐛 Debugging

```bash
# View logs
docker compose logs -f app
docker compose logs -f bot

# Access containers
docker exec -it ar_app bash
docker exec -it ar_bot bash

# Check metrics
curl http://localhost:5000/metrics
curl http://localhost:8000/metrics
```

## 🎯 Areas for Contribution

- **Features**: Anomaly detection ML, Kubernetes support, more integrations
- **Testing**: Increase coverage, add E2E tests, chaos testing
- **Documentation**: Tutorials, examples, architecture diagrams
- **Performance**: Optimization, caching, query efficiency
- **Security**: Vulnerability fixes, authentication, RBAC

## 💬 Communication

- GitHub Issues - Bug reports and feature requests
- Pull Requests - Code contributions and discussions
- GitHub Discussions - General questions and ideas

## 📜 License

By contributing, you agree that your contributions will be licensed under the MIT License.

## 🙏 Recognition

Contributors are listed in releases and can be added to CONTRIBUTORS.md.

---

**Questions?** Open an issue or start a discussion. We're here to help!
