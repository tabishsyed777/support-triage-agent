import unittest

from support_triage_agent.policy import POLICY, assess, validate


class PolicyTests(unittest.TestCase):
    def setUp(self):
        self.case = {
            "ticket_id": "T-123", "category": " ACCESS ",
            "users_affected": 10, "workaround": False,
        }

    def test_urgent_boundary(self):
        self.assertEqual(assess(self.case, POLICY)["priority"], "urgent")
        self.assertEqual(assess(dict(self.case, users_affected=9), POLICY)["priority"],
                         "elevated")

    def test_workaround_and_default_queue(self):
        result = assess(dict(self.case, category="other", workaround=True), POLICY)
        self.assertEqual(result["priority"], "normal")
        self.assertEqual(result["queue"], "general")

    def test_category_normalization(self):
        self.assertEqual(assess(self.case, POLICY)["queue"], "identity")

    def test_invalid_fields(self):
        for overrides in ({"users_affected": False}, {"users_affected": 0},
                          {"workaround": "false"}, {"category": " "}):
            with self.subTest(overrides=overrides), self.assertRaises(ValueError):
                validate(dict(self.case, **overrides))
