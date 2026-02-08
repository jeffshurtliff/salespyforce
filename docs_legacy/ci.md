# Continuous Integration (CI) Notes

This repository uses **GitHub Actions** for continuous integration (CI) to ensure code quality, 
security, and compatibility across supported Python versions.

The workflow file is located at:
```
.github/workflows/ci.yml
```
It automatically runs on all pushes and pull requests.

---

## CI Overview

Each CI run performs the following steps:

1. **Matrix Testing**  
   Tests on multiple Python versions (currently 3.7–3.12) across Ubuntu and macOS.

2. **Dependency Installation**  
   Installs Poetry via `pipx`, restores cached dependencies, and runs:
   ```bash
   poetry install --with dev
   ```

3. **Static Analysis (Linting)**  
   Uses **flake8** to detect syntax errors, undefined names, and complexity issues.

4. **Unit Tests & Coverage**  
   Runs **pytest** with **pytest-cov** to generate coverage data.  
   Coverage results are uploaded to Codecov for centralized tracking.

5. **Security Scan (Bandit)**  
   Runs **Bandit** on the `src/` directory and uploads results in **SARIF** format,  
   which populates GitHub’s “Code Scanning Alerts” under the **Security** tab.

6. **Build Artifacts**  
   Builds both the source distribution and wheel via:
   ```bash
   poetry build
   ```

---

## Running the CI Steps Locally

You can replicate most of the workflow locally using Poetry.

### 1. Install dependencies
```bash
poetry install --with dev
```

### 2. Run lint checks
```bash
poetry run flake8 .
```

### 3. Run tests with coverage
```bash
poetry run pytest --cov=salespyforce --cov-report=term-missing
```

### 4. Run Bandit security scan
```bash
poetry run bandit -r src
```

### 5. Build distribution files
```bash
poetry build
```
The build output will appear under the `dist/` directory.

---

## Maintaining the CI

- **Workflow file:** `.github/workflows/ci.yml`
- **Primary configuration:** `pyproject.toml`
- **No `setup.py` required** — all build metadata is defined in `pyproject.toml`.
- **Python support:** 3.7 and above.
- **Dependency management:** Fully handled by Poetry.

---

## Secrets Used

| Secret Name | Purpose |
|--------------|----------|
| `HELPER_DECRYPT_PASSPHRASE` | Decrypts helper config file in CI |
| `CODECOV_TOKEN` | (Optional) Authenticates coverage uploads to Codecov |
| `PYPI_TOKEN` | (Optional) Used for publishing releases to PyPI |

---

## Notes for Contributors

- Use `poetry run <command>` to ensure the correct environment is used.
- Run tests locally before pushing; GitHub Actions enforces the same steps.
- When adding new dependencies, modify `pyproject.toml` (not `requirements.txt`), then regenerate it via:
  ```bash
  poetry export -f requirements.txt --output requirements.txt --without-hashes
  ```

---

_Last updated: {{date}}_
