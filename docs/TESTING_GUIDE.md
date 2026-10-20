# Run and visually inspect the tests

## In Codespaces

From the folder containing app.py:

```bash
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python scripts/run_profile_tests.py
```

Every executed test prints a PASSED/FAILED/ERROR status. The runner covers all twelve stories; its historical filename is retained. TC01.1–TC01.4 remain separate visible sub-checks. TC08 and TC09 are omitted.

The runner replaces stale reports at the start. Open `reports/summary.md` with **Open Preview** to see the result table. For interactive filters, download `reports/test-results.html` and open it in your browser. It is self-contained. Alternatively serve the report folder:

```bash
.venv/bin/python -m http.server 8000 --bind 0.0.0.0 --directory reports
```

Open forwarded port **8000** and select `test-results.html`. Stop the server with Ctrl+C when finished. `coverage/index.html` shows which code lines ran; it is not a list of test passes.

To run only one story, use its pytest marker, for example:

```bash
.venv/bin/python -m pytest tests/profiles -m story6 -vv
```

Run the report command again afterward if you want a fresh complete report. A successful subset run does not update the earlier complete HTML report.

## In GitHub

1. Merge the package files into your working branch, commit, and push that branch. Keep `.env` and database data out of Git.
2. Open the repository's **Actions** tab and select **User Admin Stories 1-12 CI and Delivery**.
3. Select the run for your commit. The **Summary** contains SQLite and PostgreSQL tables with one row per executed test, its ID, area and outcome.
4. Select **User Admin tests (SQLite)** or **User Admin tests (PostgreSQL)**, then **Run stories 1-12 tests** to inspect verbose assertion output.
5. Under the run's **Artifacts**, download `profile-reports-SQLite` or `profile-reports-PostgreSQL`. Extract and open `test-results.html`. Use the status filters to inspect passing or failing cases.

A green job means the job succeeded; individual rows provide evidence for each test. Dependency or setup failures can prevent test results from being produced. The summary explicitly reports missing results rather than claiming a pass. Actual results exist only after the workflow runs on your repository.

After both database jobs succeed on the default branch, **Deliver tested source package** uploads `nestora-user-admin-tested-source`. It packages tracked application files, tests and docs. It does not deploy a running website.

## Test database isolation

Local tests use a new temporary SQLite database for each test. They do not read your app's database settings. The PostgreSQL CI service uses only the disposable `nestora_test` database, with an isolated schema per test that is removed afterward. The fixture refuses other database names. Never point TEST_DATABASE_URL at your application database.

If you intentionally run against your own disposable test PostgreSQL service, create `nestora_test` first and set TEST_DATABASE_URL to its postgresql+psycopg URL using private credentials in your local environment. Otherwise leave TEST_DATABASE_URL unset for local SQLite tests.

## Common problems

- ModuleNotFoundError: use `.venv/bin/python` for both installation and execution, then reinstall from `requirements-dev.txt`.
- Missing app `.env`: restore your Codespace configuration; the tests have their own settings and do not create your application database.
- Permission failure in the browser: sign in with the administrator created by `bootstrap-admin`; the former development preview is no longer a production login.
- A failure after editing shared fixtures: account tests depend on the updated `tests/profiles/conftest.py`. Review the source and assertion output rather than deleting a failing test solely to make CI green.
