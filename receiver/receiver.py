"""Local HTTP receiver: saves the posted CI test report as test-report.json."""
import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = int(os.environ.get("PORT", "9000"))
TOKEN = os.environ.get("REPORT_TOKEN", "")
OUTPUT_FILE = os.environ.get("OUTPUT_FILE", "test-report.json")


class ReportHandler(BaseHTTPRequestHandler):
    def _reply(self, code, text):
        body = text.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        self._reply(200, "Report receiver is running. POST reports to /report\n")

    def do_POST(self):
        if self.path != "/report":
            return self._reply(404, "Not found\n")
        if TOKEN and self.headers.get("X-Report-Token") != TOKEN:
            return self._reply(401, "Invalid token\n")

        length = int(self.headers.get("Content-Length", 0))
        try:
            data = json.loads(self.rfile.read(length))
        except json.JSONDecodeError:
            return self._reply(400, "Body is not valid JSON\n")

        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        summary = data.get("summary", {})
        print(
            f"[receiver] saved {OUTPUT_FILE}: commit={str(data.get('commit_sha'))[:7]} "
            f"status={summary.get('status')} passed={summary.get('passed')} failed={summary.get('failed')}"
        )
        self._reply(200, "Report saved\n")


if __name__ == "__main__":
    print(f"[receiver] listening on http://localhost:{PORT}/report  (saving to {OUTPUT_FILE})")
    HTTPServer(("127.0.0.1", PORT), ReportHandler).serve_forever()
