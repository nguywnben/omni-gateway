import sys
import unittest
from html.parser import HTMLParser
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from core.panel.root import _assemble_console_html


class FormControlParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.form_stack = []
        self.controls = []

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag == "form":
            self.form_stack.append(attributes)
        if tag in {"input", "button"}:
            self.controls.append(
                {
                    "tag": tag,
                    "attributes": attributes,
                    "form": self.form_stack[-1] if self.form_stack else None,
                }
            )

    def handle_endtag(self, tag):
        if tag == "form" and self.form_stack:
            self.form_stack.pop()


class FrontendPasswordFormTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        parser = FormControlParser()
        parser.feed(_assemble_console_html())
        cls.controls = parser.controls

    def find_control(self, control_id):
        return next(
            control for control in self.controls if control["attributes"].get("id") == control_id
        )

    def test_console_password_fields_are_scoped_to_the_admin_form(self):
        for control_id in (
            "currentConsolePassword",
            "newPanelPassword",
            "confirmPanelPassword",
            "updateAccessCredentialsBtn",
        ):
            control = self.find_control(control_id)
            self.assertIsNotNone(control["form"])
            self.assertIn("access-password-form", control["form"].get("class", "").split())

        identities = [
            control
            for control in self.controls
            if control["form"]
            and "access-password-form" in control["form"].get("class", "").split()
            and control["attributes"].get("autocomplete") == "username"
        ]
        self.assertEqual(len(identities), 1)
        self.assertEqual(identities[0]["attributes"].get("value"), "admin")
        self.assertEqual(
            self.find_control("updateAccessCredentialsBtn")["attributes"].get("type"),
            "submit",
        )

    def test_provider_user_agents_are_excluded_from_autofill(self):
        for control_id in ("antigravityUserAgent", "antigravityPayloadUserAgent"):
            control = self.find_control(control_id)
            self.assertEqual(control["attributes"].get("autocomplete"), "off")
            self.assertIsNone(control["form"])


if __name__ == "__main__":
    unittest.main()
