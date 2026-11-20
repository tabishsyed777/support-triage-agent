import io
import json
import unittest
from unittest.mock import patch

from support_triage_agent.agent import AgentError, openai_controller, run


class AgentTests(unittest.TestCase):
    def test_recovers_from_missing_prerequisites_in_alternate_order(self):
        actions = iter(["finish", "assess", "read_policy", "read_case", "assess", "finish"])
        result = run(lambda: 2, {"multiplier": 3},
                     lambda case, policy: case * policy["multiplier"],
                     lambda history: next(actions))
        self.assertEqual(result["decision"], 6)
        self.assertIn("error", result["trace"][0])
        self.assertIn("error", result["trace"][1])

    def test_budget_stops_repeated_actions(self):
        calls = []
        with self.assertRaisesRegex(AgentError, "2-step budget"):
            run(lambda: calls.append(True), {}, None, lambda history: "read_case", max_steps=2)
        self.assertEqual(calls, [True])

    def test_rejects_unknown_action(self):
        with self.assertRaisesRegex(AgentError, "unknown tool"):
            run(None, {}, None, lambda history: ["read_case"])

    @patch("support_triage_agent.agent.urlopen")
    def test_model_request_and_response(self, urlopen):
        message = {"content": '{"tool":"read_policy"}'}
        urlopen.return_value = io.BytesIO(json.dumps({"choices": [{"message": message}]}).encode())
        self.assertEqual(openai_controller("test-model", "fake-key")([]), "read_policy")
        request = urlopen.call_args.args[0]
        self.assertEqual(json.loads(request.data)["model"], "test-model")
        self.assertEqual(urlopen.call_args.kwargs["timeout"], 20)

    @patch("support_triage_agent.agent.urlopen", return_value=io.BytesIO(b'{"choices": []}'))
    def test_malformed_model_response(self, urlopen):
        with self.assertRaisesRegex(AgentError, "tool decision"):
            openai_controller("test-model", "fake-key")([])
