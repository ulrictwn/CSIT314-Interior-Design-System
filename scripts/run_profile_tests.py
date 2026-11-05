"""One local/CI command for verbose tests, coverage, JUnit and visual reports."""
import os
from pathlib import Path
import subprocess
import sys
import shutil


def main():
    root = Path(__file__).resolve().parents[1]
    os.chdir(root)
    reports = root / 'reports'
    reports.mkdir(exist_ok=True)
    # A failed new run must not display a stale report from an earlier passing run.
    for filename in ('tests.xml', 'test-results.html', 'summary.md', 'coverage.xml'):
        (reports / filename).unlink(missing_ok=True)
    shutil.rmtree(reports / 'coverage', ignore_errors=True)
    command = [sys.executable, '-m', 'pytest', 'tests', '-vv',
        '--cov=boundary', '--cov=control', '--cov=entity', '--cov=infrastructure', '--cov=app',
        '--cov-report=term-missing', '--cov-report=xml:reports/coverage.xml',
        '--cov-report=html:reports/coverage', '--junitxml=reports/tests.xml',
        '--html=reports/test-results.html', '--self-contained-html']
    result = subprocess.run(command, check=False)
    summary = subprocess.run([sys.executable, 'scripts/profile_test_report.py',
        '--label', 'PostgreSQL' if os.getenv('TEST_DATABASE_URL') else 'Local SQLite',
        '--run-result', 'success' if result.returncode == 0 else 'failure'], check=False)
    print('\nOpen reports/test-results.html for each result; reports/coverage/index.html for coverage.', flush=True)
    return result.returncode if result.returncode else summary.returncode


if __name__ == '__main__':
    raise SystemExit(main())
