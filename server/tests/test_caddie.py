import json
from io import BytesIO
import unittest
from urllib.error import HTTPError
from unittest.mock import patch

from app.services.caddie import answer_general_question, explain_recommendation


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
    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-key", "OPENAI_MODEL": "test-model"}, clear=True)
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


    @patch.dict("os.environ", {}, clear=True)
    def test_general_answer_explains_when_ai_is_not_configured(self):
        with self.assertRaisesRegex(RuntimeError, "no AI API key"):
            answer_general_question("What is match play?")

    @patch("app.services.caddie.urlopen")
    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-key", "OPENAI_MODEL": "test-model"}, clear=True)
    def test_answers_general_question_with_conversation(self, urlopen):
        class Response:
            def __enter__(self):
                return self

            def __exit__(self, *_):
                return None

            def read(self):
                return json.dumps({"output": [{"type": "message", "content": [
                    {"type": "output_text", "text": "A birdie is one under par."}
                ]}]}).encode()

        urlopen.return_value = Response()
        conversation = [
            {"role": "user", "content": "What is par?"},
            {"role": "assistant", "content": "Par is the expected number of strokes."},
        ]

        answer, source = answer_general_question("And a birdie?", conversation)

        self.assertEqual(source, "openai")
        self.assertEqual(answer, "A birdie is one under par.")
        request_data = json.loads(urlopen.call_args.args[0].data)
        self.assertEqual(request_data["model"], "test-model")
        self.assertEqual(json.loads(request_data["input"])["conversation"], conversation)

    @patch("app.services.caddie.urlopen")
    @patch.dict("os.environ", {"GOOGLE_API_KEY": "google-test-key", "GOOGLE_MODEL": "gemini-test"}, clear=True)
    def test_answers_general_question_with_gemini(self, urlopen):
        class Response:
            def __enter__(self):
                return self

            def __exit__(self, *_):
                return None

            def read(self):
                return json.dumps({"candidates": [{
                    "content": {"parts": [{"text": "A birdie is one under par."}]}
                }]}).encode()

        urlopen.return_value = Response()
        conversation = [
            {"role": "user", "content": "What is par?"},
            {"role": "assistant", "content": "Par is the expected number of strokes."},
        ]

        answer, source = answer_general_question("And a birdie?", conversation)

        self.assertEqual(source, "gemini")
        self.assertEqual(answer, "A birdie is one under par.")
        request = urlopen.call_args.args[0]
        self.assertIn("/models/gemini-test:generateContent", request.full_url)
        self.assertEqual(request.get_header("X-goog-api-key"), "google-test-key")
        request_data = json.loads(request.data)
        self.assertEqual(request_data["contents"][0]["role"], "user")
        self.assertEqual(request_data["contents"][1]["role"], "model")
        self.assertEqual(request_data["contents"][2]["role"], "user")
        self.assertEqual(request_data["contents"][2]["parts"][0]["text"], "And a birdie?")

    @patch("app.services.caddie.urlopen")
    @patch.dict(
        "os.environ",
        {
            "GOOGLE_API_KEY": "google-test-key",
            "GOOGLE_MODEL": "gemini-primary",
            "GOOGLE_FALLBACK_MODEL": "gemini-fallback",
        },
        clear=True,
    )
    def test_retries_gemini_503_using_fallback_model(self, urlopen):
        class Response:
            def __enter__(self):
                return self

            def __exit__(self, *_):
                return None

            def read(self):
                return json.dumps({"candidates": [{
                    "content": {"parts": [{"text": "Par is the expected score."}]}
                }]}).encode()

        busy_response = json.dumps({
            "error": {"message": "The model is currently experiencing high demand."}
        }).encode()
        urlopen.side_effect = [
            HTTPError("https://example.test", 503, "Service Unavailable", {}, BytesIO(busy_response)),
            Response(),
        ]

        answer, source = answer_general_question("What is par?")

        self.assertEqual(source, "gemini")
        self.assertEqual(answer, "Par is the expected score.")
        self.assertIn("/models/gemini-primary:generateContent", urlopen.call_args_list[0].args[0].full_url)
        self.assertIn("/models/gemini-fallback:generateContent", urlopen.call_args_list[1].args[0].full_url)

    @patch("app.services.caddie.urlopen")
    @patch.dict(
        "os.environ",
        {
            "GOOGLE_API_KEY": "google-test-key",
            "GOOGLE_MODEL": "gemini-primary",
            "GOOGLE_FALLBACK_MODEL": "gemini-fallback",
        },
        clear=True,
    )
    def test_retries_truncated_gemini_answer_on_fallback_model(self, urlopen):
        class Response:
            def __init__(self, payload):
                self.payload = payload

            def __enter__(self):
                return self

            def __exit__(self, *_):
                return None

            def read(self):
                return json.dumps(self.payload).encode()

        urlopen.side_effect = [
            Response({"candidates": [{
                "finishReason": "MAX_TOKENS",
                "content": {"parts": [{"text": "In match play, players compete hole-"}]},
            }]}),
            Response({"candidates": [{
                "finishReason": "STOP",
                "content": {"parts": [{
                    "text": "In match play, players compete to win each hole. The player who wins the most holes wins the match."
                }]},
            }]}),
        ]

        answer, source = answer_general_question("How does match play work?")

        self.assertEqual(source, "gemini")
        self.assertIn("wins the match.", answer)
        self.assertIn("/models/gemini-primary:generateContent", urlopen.call_args_list[0].args[0].full_url)
        self.assertIn("/models/gemini-fallback:generateContent", urlopen.call_args_list[1].args[0].full_url)

    @patch("app.services.caddie.urlopen")
    @patch.dict(
        "os.environ",
        {
            "GOOGLE_API_KEY": "google-test-key",
            "GOOGLE_MODEL": "gemini-only",
            "GOOGLE_FALLBACK_MODEL": "",
        },
        clear=True,
    )
    def test_does_not_return_gemini_answer_marked_truncated(self, urlopen):
        class Response:
            def __enter__(self):
                return self

            def __exit__(self, *_):
                return None

            def read(self):
                return json.dumps({"candidates": [{
                    "finishReason": "MAX_TOKENS",
                    "content": {"parts": [{"text": "In match play, players compete hole-"}]},
                }]}).encode()

        urlopen.return_value = Response()

        with self.assertRaisesRegex(RuntimeError, "stopped before finishing"):
            answer_general_question("How does match play work?")

    @patch("app.services.caddie.urlopen")
    @patch.dict(
        "os.environ",
        {"GOOGLE_API_KEY": "google-test-key", "GOOGLE_MODEL": "gemini-test"},
        clear=True,
    )
    def test_uses_gemini_to_explain_shot_recommendation(self, urlopen):
        class Response:
            def __enter__(self):
                return self

            def __exit__(self, *_):
                return None

            def read(self):
                return json.dumps({"candidates": [{
                    "content": {"parts": [{"text": "Take the 8 iron toward the pin."}]}
                }]}).encode()

        urlopen.return_value = Response()

        explanation, source = explain_recommendation("Which club?", RECOMMENDATION)

        self.assertEqual(source, "gemini")
        self.assertEqual(explanation, "Take the 8 iron toward the pin.")
        request_data = json.loads(urlopen.call_args.args[0].data)
        recommendation_context = json.loads(request_data["contents"][0]["parts"][0]["text"])
        self.assertEqual(recommendation_context["recommendation"], RECOMMENDATION)


if __name__ == "__main__":
    unittest.main()
