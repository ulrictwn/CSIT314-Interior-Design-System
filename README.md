# Nestora – Online Interior Design Platform

CSIT314 Software Development Methodologies group project by team **Fugglers**.

Nestora connects homeowners with interior designers. It implements all 48 user stories across four portals:

| Portal | What it does | User stories |
| --- | --- | --- |
| User Admin | Create, view, update, suspend and search user profiles and user accounts | US1–US12 |
| Interior Designer | Manage a company profile and new and past Interior Design Projects (IDPs); see each project's view and shortlist counts | US13–US29, US37–US38 |
| Customer | Search and view IDPs, save them to a shortlist, and search and view the shortlist | US30–US36 |
| Platform Manager | Manage IDP categories and generate daily, weekly and monthly reports | US39–US48 |

## Design

The code follows the Boundary–Control–Entity (BCE) pattern, with one boundary, one controller and one entity method per user story action:

- **`boundary/`** – pages that receive input, strip ordinary text and display results or errors.
- **`control/`** – controllers that pass each request to the entity in a single line.
- **`entity/`** – entities that validate all input and read and write the database (`entity/validation.py` holds the shared field rules).
- **`templates/`** and **`static/`** – the HTML screens and styles.
- **`infrastructure/`** – app set-up: database connection, login protection for each portal, and command-line commands.

## Technology

Python 3.12, Flask, SQLAlchemy, PostgreSQL (SQLite for tests), pytest and GitHub Actions.

## Setting up

Run these from the project folder. On Windows, use `.venv\Scripts\python.exe` instead of `.venv/bin/python`.

1. Create a virtual environment and install the dependencies:
   ```bash
   python -m venv .venv
   .venv/bin/python -m pip install -r requirements-dev.txt
   ```
2. Configure the database in `.env`. In the Codespace, `python scripts/setup_env.py` adds any missing settings. Without PostgreSQL, you can use SQLite instead:
   ```
   DATABASE_URL=sqlite:///nestora.db
   SECRET_KEY=any-long-random-text
   ```
3. Create the database tables:
   ```bash
   .venv/bin/python -m flask --app app upgrade-db
   ```
4. Either create the first User Admin yourself, or load the test data (next section):
   ```bash
   .venv/bin/python -m flask --app app bootstrap-admin
   ```
5. Start the website:
   ```bash
   .venv/bin/python -m flask --app app run --host=0.0.0.0 --port=5000
   ```
   Staff sign in at `/login` and choose their role (User Admin, Interior Designer or Platform Manager). Customers sign in at `/customer/login`.

Accounts created by a User Admin start with the default password `password`. To set a different password from the terminal:

```bash
.venv/bin/python -m flask --app app reset-password --username <username>
```

## Test data

The `test data` folder fills an empty database with realistic Singapore sample data: 100 user profiles, 220 user accounts, 100 company profiles, 100 IDP categories, 300 projects, 300 shortlist entries, 100 reports and about 7,700 activity events.

```bash
.venv/bin/python "test data/create_data.py"
```

Every sample account's password is `password`, for example `customer001`, `designer001`, `manager01` and `admin01`. See [test data/README.md](test%20data/README.md) for listing and clearing the data.

## Tests

The automated tests are in `tests/sprint_1/` to `tests/sprint_5/`, with one file per user story: 22 tests for Sprint 1 (TC01–TC22) and one test for each later story (TC23–TC65), 65 in total. Each test uses its own temporary database.

```bash
.venv/bin/python -m pytest -v
```

To also produce the HTML test report and coverage report in `reports/`:

```bash
.venv/bin/python scripts/run_profile_tests.py
```

## CI/CD

The GitHub Actions workflow `.github/workflows/profile-ci.yml` runs on every push and pull request. It runs all 65 tests twice, once on SQLite and once on PostgreSQL, and uploads the test reports as artifacts. When tests pass on the `main` branch, it also packages the tested source code as a downloadable artifact.