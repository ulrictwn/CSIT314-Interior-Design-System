# Sprint tests

The test suite follows `Nothinghere/CSIT314 Group Project Report (5).docx`:

| Folder | User stories | Tests |
| --- | --- | ---: |
| `tests/sprint_1/` | 1–5 | 22: the document's TC01–TC22 checks |
| `tests/sprint_2/` | 6–17 | 12: TC23–TC34, one per story |
| `tests/sprint_3/` | 18–29 | 12: TC35–TC46, one per story |
| `tests/sprint_4/` | 30–38 | 9: TC47–TC55, one per story |
| `tests/sprint_5/` | 39–48 | 10: TC56–TC65, one per story |
| Total | 1–48 | 65 |

Each story has its own `test_story_XX_*.py` file. Shared database and sample-data fixtures are in `tests/conftest.py`. Sprint 1 has a small form-reading fixture; Sprint 5 has known report activity. Tests create their own prerequisites and can run independently. Role-specific client fixtures arrange a signed-in account; login tests use an anonymous client.

## Run locally

From the folder containing `app.py`:

```bash
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python scripts/run_profile_tests.py
```

The existing runner name is retained. It runs all five sprint folders and generates fresh reports:

- `reports/summary.md`: results grouped by sprint and story, with TC01–TC22 for Sprint 1 and TC23–TC65 for later stories.
- `reports/test-results.html`: a self-contained report with status filters and assertion details.
- `reports/tests.xml`: JUnit results for CI.
- `reports/coverage/index.html`: executed code lines, separate from test success.

To run a sprint or story without generating reports:

```bash
.venv/bin/python -m pytest tests/sprint_1 -vv
.venv/bin/python -m pytest tests -m sprint3 -vv
.venv/bin/python -m pytest tests -m story6 -vv
```

After a subset run, run the complete report command again to refresh the report files. See [the case map](TEST_CASES.md) for exactly what each test checks.

## GitHub Actions

The **BCE Sprint 1-5 CI and Delivery** workflow runs the same suite on SQLite and PostgreSQL. Each job's Summary contains results grouped by sprint. Download `sprint-reports-SQLite` or `sprint-reports-PostgreSQL` and open `test-results.html` to inspect individual assertions. Missing results, setup errors, failed tests, and skipped tests are reported separately.

After both database jobs succeed on the default branch, the existing delivery job packages tracked application files, tests, and documentation. It does not deploy the website.

## Test database isolation

Every test uses a fresh temporary SQLite database by default. The fixture sets safe test settings before importing the application; it does not use the application's database credentials.

For PostgreSQL, `TEST_DATABASE_URL` must point to a dedicated database named `nestora_test` using `postgresql+psycopg`. Each test gets a unique `sprint_test_*` schema, which is removed afterward. The fixture refuses other database names. Leave `TEST_DATABASE_URL` unset for normal local SQLite tests.

## Scope

Sprint 1 preserves every check listed in the updated document, including TC08 and TC09. Story 3's ID heading says TC12–TC18, but its actual Checks list defines TC12–TC16; TC17–TC18 belong to Story 4. The executable tests follow those explicit Checks lists. T04–T07 are consistently named TC04–TC07 in code.

Sprints 2–5 each have one successful workflow test per story. Requests exercise the real boundary, controller, and entity, with checks of displayed results or stored changes. Later-story JSON requests use the same BCE handlers as the HTML forms. Logout tests begin with an existing browser login, and report tests use known activity and dates.

The broad migration, browser-layout, and method-contract suites remain excluded as requested. The latest access checks are asserted within existing login/logout, company deletion, project deletion, and shortlist story tests; direct entity rejection is also checked in existing profile/account cases. The earlier diagram transcription remains as a reference in `docs/bce_contracts.json`. This smaller suite covers the requested sprint scenarios; it is not the previous exhaustive regression suite.
