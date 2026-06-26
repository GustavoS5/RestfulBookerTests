# Restful-Booker API Test Framework

API test automation project for the public
[Restful-Booker](https://restful-booker.herokuapp.com/) practice API.

The goal of this project is to show a clean, maintainable API testing approach
using Playwright's request client, pytest, typed Pydantic models, reusable test
fixtures, and Allure reporting.

## Tech stack

- Python 3.13
- Playwright Python Sync API
- pytest
- Pydantic v2
- Faker
- Ruff
- mypy
- pre-commit
- Allure
- GitHub Actions

## What is covered

- Health check: `GET /ping`
- Authentication: valid and invalid `POST /auth`
- Booking CRUD:
  - list bookings
  - create booking
  - read booking
  - full update booking
  - partial update booking
  - delete booking
- Query filtering by name and booking dates
- Unauthorized booking mutations
- Missing booking scenarios
- Invalid payload behavior
- Documented Restful-Booker quirks

## Project structure

```text
src/restful_booker/
├── clients/          # API clients; return raw Playwright APIResponse objects
├── config/           # environment-driven settings
├── models/           # Pydantic request/response schemas
└── utils/            # test data factories

tests/
├── auth/             # authentication tests
├── booking/          # booking resource tests
├── health/           # API availability smoke test
└── conftest.py       # shared fixtures
```

## Design choices

- Clients do not assert. They only perform requests and return raw responses.
- Tests own expectations: status codes, response body validation, and behavior.
- Pydantic models validate response contracts and request payloads.
- `managed_booking` creates a fresh booking per test and cleans it up afterward.
- Negative tests document the real behavior of Restful-Booker, including quirks.
- Allure attachments are added from the base client for request/response context.

## Setup

Install dependencies:

```bash
uv sync
```

Optional: create a local `.env` file.

```bash
cp .env.example .env
```

Default values target the public Restful-Booker instance:

```env
API_BASE_URL=https://restful-booker.herokuapp.com
API_USERNAME=admin
API_PASSWORD=password123
```

## Running tests

Run the full suite:

```bash
uv run pytest
```

Run a specific area:

```bash
uv run pytest tests/booking
```

Run by marker:

```bash
uv run pytest -m smoke
uv run pytest -m auth
uv run pytest -m crud
uv run pytest -m negative
```

Run one test by name:

```bash
uv run pytest -k test_should_create_booking
```

## Code quality

```bash
uv run ruff check .
uv run ruff format .
uv run mypy
uv run pre-commit run --all-files
```

Install pre-commit hooks:

```bash
uv run pre-commit install
```

Pre-commit runs Ruff and basic file hygiene checks. CI also runs mypy and the
test suite.

## Allure report

Published report:

<https://gustavos5.github.io/RestfulBookerTests/>

Generate local Allure results:

```bash
uv run pytest --alluredir=allure-results --clean-alluredir
```

Open the report:

```bash
allure serve allure-results
```

## CI

GitHub Actions runs on pull requests and pushes to `main`.

The workflow:

1. Installs dependencies with `uv`.
2. Runs Ruff linting and formatting checks.
3. Runs mypy.
4. Runs the pytest suite.
5. Uploads Allure results.
6. Publishes the Allure report to GitHub Pages after successful `main` runs.

## Restful-Booker quirks documented by tests

- `GET /ping` returns `201`.
- Invalid auth credentials return `200` with a failure body.
- Successful booking creation returns `200`, not `201`.
- Successful booking deletion returns `201`, not `204`.
- Mutating a missing booking returns `405`.
- Partial update accepts some invalid field types instead of rejecting them.

## Purpose

This repository is a portfolio project focused on API automation design,
readability, test isolation, typed validation, and CI-ready execution.
