# Assignment Submission Portal

A small Flask web app where students submit their name, registration number, assignment title and a submission URL.
Every push is tested automatically with GitHub Actions, and the test report is sent to a receiver on my computer
which saves it as `test-report.json`.

## Project structure

| Path | Purpose |
|---|---|
| `app.py`, `templates/index.html` | The portal |
| `tests/test_submissions.py` | Automated tests (3 test cases) |
| `.github/workflows/ci.yml` | CI pipeline (tests, report delivery, email, Pages deploy) |
| `scripts/build_report.py` | Converts test results to `test-report.json` |
| `receiver/receiver.py` | Local HTTP receiver that saves the report |
| `docs/index.html` | Static demo published to GitHub Pages |

## 1. Run the application

```bash
python -m venv venv
venv\Scripts\activate          # Windows  (Linux/macOS: source venv/bin/activate)
pip install -r requirements.txt
python app.py
```

Open http://localhost:5000. Valid submissions are saved to `submissions.json`.

## 2. Run the tests

```bash
python -m pytest -v
```

## 3. Start the local report receiver

```bash
cd receiver
set REPORT_TOKEN=my-secret-token      # Windows CMD  (PowerShell: $env:REPORT_TOKEN="my-secret-token")
python receiver.py
```

The receiver listens on http://localhost:9000/report and writes every report it receives to
`receiver/test-report.json`. To reach it from GitHub Actions, expose it with a tunnel
(`ngrok http --url=<your-static-domain> 9000`) and store the public URL (ending in `/report`) in the
repository secret `REPORT_URL`; store the token in `REPORT_TOKEN`.

## Required GitHub secrets

`REPORT_URL`, `REPORT_TOKEN` (report delivery) and `MAIL_USERNAME`, `MAIL_PASSWORD`, `MAIL_TO` (email bonus).
