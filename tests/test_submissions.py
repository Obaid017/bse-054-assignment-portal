import json
import os
import tempfile
import unittest

from app import create_app

VALID = {
    "name": "Obaid Ullah Khan",
    "reg_no": "FA23-BSE-054",
    "title": "Lab Assignment 2",
    "url": "https://github.com/Obaid017/bse-054-docker-assignment",
}


class SubmissionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.data_file = os.path.join(self.tmp.name, "submissions.json")
        app = create_app(self.data_file)
        app.config["TESTING"] = True
        self.client = app.test_client()

    def tearDown(self):
        self.tmp.cleanup()

    def test_valid_submission_is_saved_and_listed(self):
        resp = self.client.post("/submit", data=VALID, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"Lab Assignment 2", resp.data)  # appears in the list
        with open(self.data_file, encoding="utf-8") as f:
            saved = json.load(f)
        self.assertEqual(len(saved), 1)
        self.assertEqual(saved[0]["reg_no"], "FA23-BSE-054")

    def test_missing_registration_number_is_rejected(self):
        data = {**VALID, "reg_no": ""}
        resp = self.client.post("/submit", data=data)
        self.assertEqual(resp.status_code, 400)
        self.assertIn(b"Registration number is required.", resp.data)
        self.assertFalse(os.path.exists(self.data_file))

    def test_invalid_url_is_rejected_and_not_saved(self):
        data = {**VALID, "url": "not-a-valid-url"}
        resp = self.client.post("/submit", data=data)
        self.assertEqual(resp.status_code, 400)
        self.assertIn(b"Submission URL is invalid", resp.data)
        self.assertFalse(os.path.exists(self.data_file))


if __name__ == "__main__":
    unittest.main()
