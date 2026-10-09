import json
import logging
import os
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen


OPENAI_RESPONSES_URL = "https://api.openai.com/v1/responses"
GEMINI_GENERATE_CONTENT_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
logger = logging.getLogger(__name__)


def _generate_with_gemini(
    api_key: str,
    model: str,
    instructions: str,
    question: str,
    conversation: list[dict] | None,
    max_output_tokens: int,
) -> str:
    contents = [
        {
            "role": "model" if message["role"] == "assistant" else "user",
            "parts": [{"text": message["content"]}],
        }
        for message in (conversation or [])
    ]
    contents.append({"role": "user", "parts": [{"text": question}]})
    request_body = json.dumps({
        "systemInstruction": {"parts": [{"text": instructions}]},
        "contents": contents,
        "generationConfig": {"maxOutputTokens": max_output_tokens},
    }).encode()
    fallback_model = os.getenv("GOOGLE_FALLBACK_MODEL", "gemini-3.1-flash-lite")
    models = [model]
    if fallback_model and fallback_model != model:
        models.append(fallback_model)

    for index, request_model in enumerate(models):
        request = Request(
            GEMINI_GENERATE_CONTENT_URL.format(model=quote(request_model, safe="")),
            data=request_body,
            headers={"x-goog-api-key": api_key, "Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urlopen(request, timeout=25.0) as response:
                payload = json.loads(response.read())
        except HTTPError as error:
            try:
                error_payload = json.loads(error.read())
                api_message = error_payload.get("error", {}).get("message")
            except (ValueError, AttributeError):
                api_message = None
            if error.code == 503 and index + 1 < len(models):
                logger.warning(
                    "Gemini model %s returned HTTP 503; retrying with %s",
                    request_model,
                    models[index + 1],
                )
                continue
            logger.warning(
                "Gemini API rejected the request (HTTP %s): %s",
                error.code,
                api_message or error.reason,
            )
            raise RuntimeError(
                f"Gemini API returned HTTP {error.code}: {api_message or 'request rejected'}"
            ) from error
        except (URLError, TimeoutError, OSError, ValueError) as error:
            logger.warning("Gemini API request failed: %s", type(error).__name__)
            raise RuntimeError("Unable to reach or read a response from the Gemini API.") from error

        candidates = payload.get("candidates", [])
        truncated = any(
            candidate.get("finishReason") == "MAX_TOKENS"
            for candidate in candidates
        )
        if truncated:
            if index + 1 < len(models):
                logger.warning(
                    "Gemini model %s hit its output token limit; retrying with %s",
                    request_model,
                    models[index + 1],
                )
                continue
            raise RuntimeError("The AI service stopped before finishing its answer. Please try again.")

        text = "".join(
            part.get("text", "")
            for candidate in candidates
            for part in candidate.get("content", {}).get("parts", [])
            if part.get("text")
        ).strip()
        if not text:
            raise RuntimeError("The AI service returned no answer. Please try again in a moment.")
        return text

    raise RuntimeError("The AI service returned no answer. Please try again in a moment.")


def _configured_provider() -> tuple[str, str, str] | None:
    google_api_key = os.getenv("GOOGLE_API_KEY")
    if google_api_key:
        return google_api_key, os.getenv("GOOGLE_MODEL", "gemini-3.5-flash-lite"), "gemini"
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if openai_api_key:
        return openai_api_key, os.getenv("OPENAI_MODEL", "gpt-6-astra"), "openai"
    return None


def fallback_explanation(question: str, recommendation: dict, weather: dict | None = None) -> str:
    explanation = (
        f"For your question, start with the measured {recommendation['target_yards']} yard shot to "
        f"{recommendation['target_name']}. The distance-based suggestion is {recommendation['club_name']} "
        f"({recommendation['carry_yards']} yards of carry). {recommendation['rationale']}"
    )
    wind = (weather or {}).get("wind_speed_mph")
    if wind is not None:
        explanation += f" Current local wind is {round(wind)} mph; the club suggestion does not adjust for wind."
    return explanation


def explain_recommendation(
    question: str,
    recommendation: dict,
    weather: dict | None = None,
    conversation: list[dict] | None = None,
) -> tuple[str, str]:
    provider = _configured_provider()
    if not provider:
        return fallback_explanation(question, recommendation, weather), "rules"
    api_key, model, provider_name = provider

    context = {
        "question": question,
        "recommendation": recommendation,
        "conditions": weather,
        "conversation": conversation or [],
    }
    instructions = (
        "You are a concise golf caddie explaining a recommendation that has already been calculated. "
        "Do not change the recommended club, target, distance, or risk. Use only the supplied data. "
        "If course or weather facts are missing, say so. Do not claim to know a golfer's tendencies "
        "or course features that are not included. Keep the reply to two short sentences."
    )
    if provider_name == "gemini":
        try:
            explanation = _generate_with_gemini(
                api_key, model, instructions, json.dumps(context), None, 180
            )
            return explanation, provider_name
        except Exception as error:
            logger.warning("Gemini caddie explanation failed: %s", type(error).__name__)
            return fallback_explanation(question, recommendation, weather), "rules"

    request_body = json.dumps({
        "model": model,
        "store": False,
        "max_output_tokens": 180,
        "instructions": instructions,
        "input": json.dumps(context),
    }).encode()
    request = Request(
        OPENAI_RESPONSES_URL,
        data=request_body,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=12.0) as response:
            payload = json.loads(response.read())
        for item in payload.get("output", []):
            if item.get("type") != "message":
                continue
            for content in item.get("content", []):
                if content.get("type") == "output_text" and content.get("text"):
                    return content["text"].strip(), provider_name
    except Exception:
        # Preserve the usable structured recommendation if the explanation service is down.
        return fallback_explanation(question, recommendation, weather), "rules"
    return fallback_explanation(question, recommendation, weather), "rules"


def answer_general_question(question: str, conversation: list[dict] | None = None) -> tuple[str, str]:
    provider = _configured_provider()
    if not provider:
        raise RuntimeError(
            "General golf Q&A is unavailable because no AI API key is configured. "
            "You can still ask for shot advice during an active round."
        )
    api_key, model, provider_name = provider

    instructions = (
        "You are a helpful, concise golf assistant. Answer general questions about golf, including "
        "rules, strategy, practice, and equipment. Do not assume the user is currently playing a "
        "round or invent personal, course, or weather details. Use the conversation only to resolve "
        "follow-up questions. If a rules answer may depend on the governing body or local rules, say so. "
        "Keep the answer to a few clear sentences, and always finish the final sentence."
    )
    if provider_name == "gemini":
        try:
            answer = _generate_with_gemini(
                api_key, model, instructions, question, conversation, 250
            )
        except Exception as error:
            raise RuntimeError(str(error)) from error
        return answer, provider_name

    request_body = json.dumps({
        "model": model,
        "store": False,
        "max_output_tokens": 300,
        "instructions": instructions,
        "input": json.dumps({
            "question": question,
            "conversation": conversation or [],
        }),
    }).encode()
    request = Request(
        OPENAI_RESPONSES_URL,
        data=request_body,
        headers={"Authorization": f"******", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=12.0) as response:
            payload = json.loads(response.read())
    except (URLError, TimeoutError, OSError, ValueError) as error:
        raise RuntimeError("I couldn't reach the AI service just now. Please try again in a moment.") from error

    for item in payload.get("output", []):
        if item.get("type") != "message":
            continue
        for content in item.get("content", []):
            if content.get("type") == "output_text" and content.get("text"):
                return content["text"].strip(), provider_name

    raise RuntimeError("The AI service returned no answer. Please try again in a moment.")
