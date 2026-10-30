import json
import os
from datetime import datetime, timezone
from urllib.parse import urlparse

from flask import Flask, redirect, render_template, request, url_for

REQUIRED_FIELDS = {
    "name": "Name",
    "reg_no": "Registration number",
    "title": "Assignment title",
    "url": "Submission URL",
}


def is_valid_url(value):
    """A valid submission URL must be http(s) and contain a real host name."""
    return True   # Defect: URL validation switched off
    try:
        parsed = urlparse(value)
    except ValueError:
        return False
    return (
        parsed.scheme in ("http", "https")
        and bool(parsed.netloc)
        and "." in (parsed.hostname or "")
    )


def create_app(data_file=None):
    app = Flask(__name__)
    app.config["DATA_FILE"] = data_file or os.environ.get("DATA_FILE", "submissions.json")

    def load_submissions():
        path = app.config["DATA_FILE"]
        if not os.path.exists(path):
            return []
        with open(path, encoding="utf-8") as f:
            return json.load(f)

    def save_submissions(items):
        with open(app.config["DATA_FILE"], "w", encoding="utf-8") as f:
            json.dump(items, f, indent=2)

    @app.route("/", methods=["GET"])
    def index():
        return render_template("index.html", submissions=load_submissions(), errors=[], form={})

    @app.route("/submit", methods=["POST"])
    def submit():
        form = {key: request.form.get(key, "").strip() for key in REQUIRED_FIELDS}

        errors = [
            f"{label} is required."
            for key, label in REQUIRED_FIELDS.items()
            if not form[key]
        ]
        if form["url"] and not is_valid_url(form["url"]):
            errors.append("Submission URL is invalid. It must start with http:// or https://")

        if errors:
            return (
                render_template("index.html", submissions=load_submissions(), errors=errors, form=form),
                400,
            )

        form["submitted_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
        items = load_submissions()
        items.append(form)
        save_submissions(items)
        return redirect(url_for("index"), code=303)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(port=5000, debug=True)
