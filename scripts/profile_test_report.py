"""Render actual JUnit results by sprint and story; never invent passes."""
import argparse
from collections import Counter
import os
from pathlib import Path
import re
import xml.etree.ElementTree as ET


def cell(value):
    return str(value).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('|', '&#124;').replace('\n', ' ')


def render(xml_path, label, run_result):
    title = f'## Sprint 1–5 tests — {cell(label)}\n\n'
    if not xml_path.is_file():
        return title + '**No test results were produced.** Check dependency installation and the Run sprint 1-5 tests log. This is not a passing run.\n', False
    try:
        root = ET.parse(xml_path).getroot()
    except ET.ParseError:
        return title + '**The test results XML is invalid.** Check the test log.\n', False
    rows = []
    for case in root.iter('testcase'):
        name = case.get('name', 'Unnamed test')
        classname = case.get('classname', '')
        sprint_match = re.search(r'sprint_(\d+)', classname + ' ' + name)
        story_match = re.search(r'test_story_(\d+)_', classname + ' ' + name)
        sprint = int(sprint_match.group(1)) if sprint_match else 0
        story = int(story_match.group(1)) if story_match else 0
        identifier = re.search(r'TC\d+', name)
        case_id = identifier.group() if identifier else f'US{story:02}' if story else 'Collection/setup'
        state = ('ERROR' if case.find('error') is not None else
                 'FAILED' if case.find('failure') is not None else
                 'SKIPPED' if case.find('skipped') is not None else 'PASSED')
        rows.append(dict(sprint=sprint, story=story, case_id=case_id, name=name,
                         state=state, seconds=case.get('time', '0')))
    rows.sort(key=lambda row: (row['sprint'], row['story'], row['case_id'], row['name']))
    totals = Counter(row['state'] for row in rows)
    succeeded = run_result == 'success' and rows and not (totals['FAILED'] or totals['ERROR'])
    status = ('**Test command succeeded.**' if succeeded else
              f'**Test command did not succeed ({cell(run_result)}).** Check the job log, even if some cases passed.')
    lines = [title.rstrip(), '', status, '',
             f"{len(rows)} results · {totals['PASSED']} passed · {totals['FAILED']} failed · {totals['ERROR']} errors · {totals['SKIPPED']} skipped", '',
             '| Sprint | Stories | Passed | Failed / error | Skipped |',
             '| --- | --- | ---: | ---: | ---: |']
    for sprint, stories in [(1, '1–5'), (2, '6–17'), (3, '18–29'), (4, '30–38'), (5, '39–48')]:
        counts = Counter(row['state'] for row in rows if row['sprint'] == sprint)
        lines.append(f"| Sprint {sprint} | {stories} | {counts['PASSED']} | {counts['FAILED'] + counts['ERROR']} | {counts['SKIPPED']} |")
    if any(row['sprint'] == 0 for row in rows):
        counts = Counter(row['state'] for row in rows if row['sprint'] == 0)
        lines.append(f"| Collection/setup | — | {counts['PASSED']} | {counts['FAILED'] + counts['ERROR']} | {counts['SKIPPED']} |")
    lines += ['', '### Every test result', '',
              '| ID | Sprint | Story | Test case | Result | Seconds |',
              '| --- | --- | --- | --- | --- | ---: |']
    icons = {'PASSED': '✅', 'FAILED': '❌', 'ERROR': '❌', 'SKIPPED': '⏭️'}
    for row in rows:
        values = [row['case_id'], f"Sprint {row['sprint']}" if row['sprint'] else 'Setup',
                  str(row['story']) if row['story'] else '—', row['name'],
                  icons[row['state']] + ' ' + row['state'], row['seconds']]
        lines.append('| ' + ' | '.join(map(cell, values)) + ' |')
    lines += ['', 'Sprint 1 uses the Word document’s TC01–TC22 checks. Sprints 2–5 have one test per story, numbered TC23–TC65.', '',
              'Open `test-results.html` for filters and assertion details, or `coverage/index.html` for executed code lines. Skipped tests are not passes. Coverage is separate from test success.', '']
    return '\n'.join(lines), bool(rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--label', default='Local SQLite')
    parser.add_argument('--run-result', default='unknown')
    parser.add_argument('--xml', type=Path, default=Path('reports/tests.xml'))
    parser.add_argument('--github', action='store_true')
    args = parser.parse_args()
    result, valid = render(args.xml, args.label, args.run_result)
    destination = Path('reports/summary.md')
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(result, encoding='utf-8')
    if args.github and os.getenv('GITHUB_STEP_SUMMARY'):
        with open(os.environ['GITHUB_STEP_SUMMARY'], 'a', encoding='utf-8') as stream:
            stream.write(result)
    print(f'Per-test summary: {destination}')
    return 0 if valid else 1


if __name__ == '__main__':
    raise SystemExit(main())
