import copy
import json
import tempfile
import unittest
from pathlib import Path

from src import app as app_module


class RegistrationPersistenceTests(unittest.TestCase):
    def setUp(self):
        self.original_activities = copy.deepcopy(app_module.activities)
        self.original_registrations_file = app_module.REGISTRATIONS_FILE
        self.temp_dir = tempfile.TemporaryDirectory()
        app_module.REGISTRATIONS_FILE = Path(self.temp_dir.name) / "registrations.json"

    def tearDown(self):
        app_module.activities.clear()
        app_module.activities.update(self.original_activities)
        app_module.REGISTRATIONS_FILE = self.original_registrations_file
        self.temp_dir.cleanup()

    def test_missing_store_keeps_default_participants(self):
        expected = copy.deepcopy(app_module.activities["Chess Club"]["participants"])

        app_module.load_registrations()

        self.assertEqual(app_module.activities["Chess Club"]["participants"], expected)

    def test_signup_and_unregister_survive_reload(self):
        activity_name = "Chess Club"
        email = "new-student@mergington.edu"
        original_participants = app_module.activities[activity_name]["participants"].copy()

        app_module.signup_for_activity(activity_name, email)
        self.assertIn(email, app_module.activities[activity_name]["participants"])

        app_module.activities[activity_name]["participants"] = original_participants
        app_module.load_registrations()
        self.assertIn(email, app_module.get_activities()[activity_name]["participants"])

        app_module.unregister_from_activity(activity_name, email)
        app_module.activities[activity_name]["participants"] = original_participants
        app_module.load_registrations()
        self.assertNotIn(email, app_module.get_activities()[activity_name]["participants"])

    def test_invalid_store_raises_value_error(self):
        app_module.REGISTRATIONS_FILE.write_text(json.dumps(["not", "a", "mapping"]))

        with self.assertRaises(ValueError):
            app_module.load_registrations()


if __name__ == "__main__":
    unittest.main()
