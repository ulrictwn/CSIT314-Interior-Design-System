"""Render actual JUnit results as a per-case GitHub summary; never invent passes."""
import argparse
from collections import Counter
import os
from pathlib import Path
import re
import xml.etree.ElementTree as ET


def cell(value):
    return str(value).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('|', '&#124;').replace('\n', ' ')


def render(xml_path, label, run_result):
    if not xml_path.is_file():
        return f'## BCE story tests — {cell(label)}\n\n**No test results were produced.** Check dependency installation and the Run stories 1-48 tests log. This is not a passing run.\n', False
    try:
        root = ET.parse(xml_path).getroot()
    except ET.ParseError:
        return f'## BCE story tests — {cell(label)}\n\n**The test results XML is invalid.** Check the test log.\n', False
    rows = []
    for case in root.iter('testcase'):
        name = case.get('name', 'Unnamed test')
        identifiers = re.findall(r'TC\d+(?:\.\d+)*', name)
        # A name may contain parent TC01 followed by parameter [TC01.4].
        # Prefer the most specific ID so the summary keeps the sub-check.
        case_id = max(identifiers, key=lambda item: item.count('.')) if identifiers else 'Collection/setup'
        classname = case.get('classname', '')
        story_match = re.search(r'test_story_(\d+)_', classname)
        group = f'Story {story_match.group(1)}' if story_match else 'BCE & database'
        state = 'ERROR' if case.find('error') is not None else 'FAILED' if case.find('failure') is not None else 'SKIPPED' if case.find('skipped') is not None else 'PASSED'
        icon = {'PASSED': '✅', 'FAILED': '❌', 'ERROR': '❌', 'SKIPPED': '⏭️'}[state]
        rows.append((group, case_id, name, icon + ' ' + state, case.get('time', '0'), state))
    rows.sort(key=lambda r: (tuple(map(int, re.findall(r'\d+', r[1]))) or (9999,), r[2]))
    totals = Counter(r[5] for r in rows)
    status = '**Test command succeeded.**' if run_result == 'success' and rows and not (totals['FAILED'] or totals['ERROR']) else f'**Test command did not succeed ({cell(run_result)}).** Check the job log, even if some individual cases passed.'
    lines = [f'## BCE story tests — {cell(label)}', '', status, '',
        f"{len(rows)} results · {totals['PASSED']} passed · {totals['FAILED']} failed · {totals['ERROR']} errors · {totals['SKIPPED']} skipped", '',
        '| Area | Passed | Failed / error | Skipped |', '| --- | ---: | ---: | ---: |']
    for group in [f'Story {number}' for number in range(1, 13)] + ['Security & database']:
        counts = Counter(r[5] for r in rows if r[0] == group)
        lines.append(f"| {group} | {counts['PASSED']} | {counts['FAILED'] + counts['ERROR']} | {counts['SKIPPED']} |")
    lines += ['', '### Every test result', '', '| ID | Area | Test case | Result | Seconds |', '| --- | --- | --- | --- | ---: |']
    for group, case_id, name, state, seconds, _ in rows:
        lines.append('| ' + ' | '.join(map(cell, [case_id, group, name, state, seconds])) + ' |')
    lines += ['', 'Download the job’s report artifact and open `test-results.html` for filters and assertion details, or `coverage/index.html` for executed code lines.', '',
              'Parameterized tests have one row per input. Skipped tests are not passes. Coverage is a separate measurement from test success.', '']
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
