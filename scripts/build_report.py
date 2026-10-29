"""Convert pytest's JUnit XML (report.xml) into test-report.json (+ summary.txt for email)."""
import json
import os
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

XML_PATH = "report.xml"
JSON_PATH = "test-report.json"
SUMMARY_PATH = "summary.txt"


def read_tests(path):
    tests = []
    if not os.path.exists(path):
        return tests
    root = ET.parse(path).getroot()
    for case in root.iter("testcase"):
        bad = case.find("failure")
        if bad is None:
            bad = case.find("error")
        if bad is not None:
            result = "failed"
            message = (bad.get("message") or bad.text or "").strip()[:500]
        elif case.find("skipped") is not None:
            result, message = "skipped", None
        else:
            result, message = "passed", None
        tests.append({"name": case.get("name"), "result": result, "failure_message": message})
    return tests


def main():
    tests = read_tests(XML_PATH)
    passed = sum(t["result"] == "passed" for t in tests)
    failed = sum(t["result"] == "failed" for t in tests)
    status = "passed" if tests and failed == 0 else "failed"

    report = {
        "repository": os.environ.get("GITHUB_REPOSITORY", "local"),
        "branch": os.environ.get("GITHUB_REF_NAME", "local"),
        "commit_sha": os.environ.get("GITHUB_SHA", "unknown"),
        "run_id": os.environ.get("GITHUB_RUN_ID", "local"),
        "run_number": os.environ.get("GITHUB_RUN_NUMBER", "0"),
        "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "summary": {"total": len(tests), "passed": passed, "failed": failed, "status": status},
        "tests": tests,
    }

    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    lines = [
        f"Repository : {report['repository']}",
        f"Branch     : {report['branch']}",
        f"Commit     : {report['commit_sha']}",
        f"Run ID     : {report['run_id']}",
        f"Result     : {status.upper()}",
        f"Tests      : total={len(tests)} passed={passed} failed={failed}",
        "",
    ]
    for t in tests:
        line = f"[{t['result'].upper()}] {t['name']}"
        if t["failure_message"]:
            line += f"  -> {t['failure_message']}"
        lines.append(line)
    with open(SUMMARY_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print(f"Report written: {JSON_PATH} (status={status}, passed={passed}, failed={failed})")


if __name__ == "__main__":
    main()
