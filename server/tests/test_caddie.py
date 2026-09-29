import json
import unittest
from unittest.mock import patch

from app.services.caddie import explain_recommendation


RECOMMENDATION = {
    "club_name": "8 iron",
    "carry_yards": 132,
    "target_yards": 125,
    "target_name": "Pin",
    "rationale": "The measured distance is within this club's carry range.",
}


class CaddieExplanationTests(unittest.TestCase):
    @patch.dict("os.environ", {}, clear=True)
    def test_falls_back_to_supplied_recommendation_without_api_key(self):
        explanation, source = explain_recommendation("Which club?", RECOMMENDATION)

        self.assertEqual(source, "rules")
        self.assertIn("8 iron", explanation)
        self.assertIn("125 yard", explanation)

    @patch("app.services.caddie.urlopen")
    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-key", "OPENAI_MODEL": "test-model"})
    def test_uses_responses_api_text_when_configured(self, urlopen):
        class Response:
            def __enter__(self):
                return self

            def __exit__(self, *_):
                return None

            def read(self):
                return json.dumps({"output": [{"type": "message", "content": [
                    {"type": "output_text", "text": "Take the 8 iron toward the pin."}
                ]}]}).encode()

        urlopen.return_value = Response()

        explanation, source = explain_recommendation("Which club?", RECOMMENDATION)

        self.assertEqual(source, "openai")
        self.assertEqual(explanation, "Take the 8 iron toward the pin.")
        request = urlopen.call_args.args[0]
        request_data = json.loads(request.data)
        self.assertEqual(request_data["model"], "test-model")
        self.assertFalse(request_data["store"])
        self.assertEqual(request.get_header("Authorization"), "Bearer test-key")


if __name__ == "__main__":
    unittest.main()
