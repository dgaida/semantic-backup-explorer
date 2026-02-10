# Contributing to Semantic Backup Explorer

## Development Setup

1. Fork and clone the repository.
2. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```
3. Install pre-commit hooks:
   ```bash
   pre-commit install
   ```

## Code Standards

- **Type Hints**: All code must have type hints (checked with `mypy --strict`).
- **Docstrings**: All public methods must have Google-style docstrings.
- **Test Coverage**: Test coverage must be ≥ 80%.
- **Style Guide**: Follow the Ruff style guide (automatically checked in CI).

## Testing

Run tests:
```bash
pytest                    # All tests
pytest --cov              # With coverage report
```

## Pull Request Process

1. Create a feature branch: `git checkout -b feature/my-feature`.
2. Write tests for your changes.
3. Ensure all tests pass and coverage is ≥ 80%.
4. Ensure `mypy` and `ruff` checks pass locally.
5. Update documentation if needed.
6. Submit a PR with a clear description of your changes.
