# Tests and CI/delivery for user stories 1–5

This adds tests to **Nestora-User-Profiles-Stories-1-5.zip**, the corrected profile-only source package. It does not add later user stories or change application behavior. There are **44 named test scenarios, executed as 64 tests** because some scenarios repeat with different inputs. Every input variant has its own report row.

## 1. Add the files

Copy these additions into the repository root alongside `app.py`: `.github/`, `tests/profiles/`, the three new scripts, `requirements-dev.txt`, `pytest.ini`, and these docs. Merge folders rather than deleting existing files. The workflow must end up at **`.github/workflows/profile-ci.yml`**, not inside another project subfolder.

The included `LOCAL_CHECK_RESULTS` folder is a snapshot of the SQLite checks performed while preparing this package. Open its HTML report immediately if you want an example. It is not evidence of your latest commit passing, and it is not a GitHub Actions run. Do not commit this example folder.

If you already have a `pytest.ini`, merge the settings. This suite and its workflow explicitly target `tests/profiles`; old preview-only tests elsewhere are retained but are not run by this workflow. Do not delete a separate workflow or another person's tests without reviewing them. Earlier prototype tests that expect ignored permissions or non-persistent POST behavior describe the old preview, not these working profile features.

Append the following lines to your existing `.gitignore`:

```gitignore
.pytest_cache/
.coverage
.coverage.*
reports/
dist/
LOCAL_CHECK_RESULTS/
```

## 2. Install and run in Codespaces

Run from the project root using the same virtual environment as Flask:

```bash
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python scripts/run_profile_tests.py
```

The application can remain running in another terminal. These tests use separate disposable databases and do not modify the application's database or `.env`. CSRF stays enabled, and submissions include real tokens. The test setup overrides the application connection before importing `app.py`, so your normal `DATABASE_URL` is not used for test data.

The terminal prints each full test name followed by **PASSED** or **FAILED**, then the final totals. A failure makes the command exit with a nonzero status; the workflow does not suppress that failure.

## 3. View individual local results in a browser

After running the tests:

- `reports/test-results.html`: one result row for every test input, with names, outcomes, timings, and failure details. Filter to **Passed** or **Failed** and expand a row for available logs. This is the test pass/fail report.
- `reports/summary.md`: a Markdown table grouped by story and then a row for every test. Open the file in VS Code and choose **Open Preview** or press **Ctrl+Shift+V**.
- `reports/coverage/index.html`: the percentage of Python lines executed, with per-file views. Coverage is not the number of passing tests and does not prove every behavior is correct.
- `reports/tests.xml`: machine-readable JUnit results used to build the summary.

To open the HTML from Codespaces, either download it and open it in your computer's browser, or start a separate server that exposes **only the report folder**:

```bash
.venv/bin/python -m http.server 8001 --directory reports
```

Open port **8001** in the **Ports** tab, keep its visibility **Private**, and select `test-results.html`. Open `/coverage/` on that same forwarded address for the coverage report. Stop the report server with Ctrl+C when finished. Port 5000 can continue serving your actual application.

## 4. Commit and push the additions

Review changed files with Source Control in VS Code. Stage the new test/configuration files, commit with a message such as `Add profile tests and CI reports`, then use **Sync Changes / Push**. Generated reports, `.env`, and database files should not be staged.

The workflow triggers on pushes, pull requests and manual runs. If an existing workflow also triggers, GitHub may show both; identify this one by its name **User Profiles CI and Delivery**. No GitHub repository files have been edited or pushed by this downloaded package itself.

## 5. Find EVERY result in GitHub

1. Open the repository in GitHub.
2. Click **Actions** in the top navigation.
3. Choose **User Profiles CI and Delivery** on the left.
4. Open the run whose branch and commit match the changes you pushed.
5. On the run's **Summary**, look for **Profile tests — SQLite** and **Profile tests — PostgreSQL**. Each has story totals and a table titled **Every test result**, including `TC01` through `TC44` and the parameter variants. Use the browser's Ctrl+F to find a case ID.
6. A green check beside a job means that job succeeded overall. To see the literal result of each test, open **Profile tests (SQLite)** or **Profile tests (PostgreSQL)** → **Run profile tests**. Expand the log and find each `test_TC... PASSED` line. Failed tests show the assertion difference/traceback.
7. For the visual HTML report, return to the run summary, find **Artifacts**, and download **profile-reports-SQLite** or **profile-reports-PostgreSQL**. Extract the download and open `test-results.html` in your local browser. Open `coverage/index.html` from the same download to inspect coverage. Artifact downloads are ZIP files, not live HTML websites.

Reports are uploaded even when the test step fails. If installation or collection fails before results can be produced, the summary says no results were produced or lists errors; it does not claim a pass. The pipeline does not continue to deliver source after a failed test job.

The two database jobs run the same 64 tests. SQLite provides a quick compatibility check; PostgreSQL 17 verifies the real database dialect, including native array storage. PostgreSQL runs on a disposable GitHub service container with a database named `nestora_test`; a separate schema is created and removed for every test. These disposable CI credentials are not your application credentials. No GitHub Secrets are needed for this workflow.

## 6. CI and CD meaning in this setup

**Continuous integration:** every push/PR installs the dependencies, runs the profile tests on SQLite and PostgreSQL, and publishes results. A failed test marks the job red.

**Continuous delivery:** after both database jobs pass on a push to your repository's default branch, the workflow creates a source ZIP artifact named **nestora-profiles-tested-source**. Download it from that run's Artifacts section. Pull requests and non-default branches run tests but do not deliver this package. A failed test blocks delivery.

This is tested-source delivery, not production deployment. A hosting destination and deployment configuration have not been selected. Codespaces remains your development environment; this workflow does not deploy to it or GitHub Pages. Uploaded artifacts are retained for 14 days, subject to repository policy.

## Focused runs

```bash
# Only story 1, with every result printed:
.venv/bin/python -m pytest tests/profiles -m story1 -vv

# Only cases whose names contain TC22 (assignment guard variants):
.venv/bin/python -m pytest tests/profiles -k TC22 -vv
```

These focused commands print results but do not regenerate the full HTML report. Use `scripts/run_profile_tests.py` when you want fresh complete reports. You do not need to enable development preview in `.env` for the test suite; the fixtures configure their own app instances.

## Limits of these checks

The tests exercise Flask forms/routes, controllers, database persistence, rendering, access control and migrations. They do not drive a real browser or prove CSS/JavaScript layout behavior. The Cancel checks confirm that the link navigates without saving; they do not automate typing and clicking in a browser. The named test cases are mapped in `TEST_CASES.md`.

During preparation, all 64 tests passed locally on SQLite with approximately 86% Python line coverage. The generated PostgreSQL CI job must run in your repository before a PostgreSQL pass can be claimed. A passing historical report does not certify later code changes.

## Reference documentation

- GitHub Python testing: https://docs.github.com/en/actions/tutorials/build-and-test-code/python
- GitHub job summaries: https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-commands#adding-a-job-summary
- GitHub PostgreSQL service containers: https://docs.github.com/en/actions/tutorials/use-containerized-services/create-postgresql-service-containers
- GitHub workflow artifacts: https://docs.github.com/en/actions/concepts/workflows-and-actions/workflow-artifacts
- pytest HTML reports: https://pytest-html.readthedocs.io/en/stable/user_guide.html
