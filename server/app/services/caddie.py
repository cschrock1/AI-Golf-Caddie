import json
import os
from urllib.request import Request, urlopen


OPENAI_RESPONSES_URL = "https://api.openai.com/v1/responses"


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


def explain_recommendation(question: str, recommendation: dict, weather: dict | None = None) -> tuple[str, str]:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return fallback_explanation(question, recommendation, weather), "rules"

    context = {
        "question": question,
        "recommendation": recommendation,
        "conditions": weather,
    }
    request_body = json.dumps({
        "model": os.getenv("OPENAI_MODEL", "gpt-6-astra"),
        "store": False,
        "max_output_tokens": 180,
        "instructions": (
            "You are a concise golf caddie explaining a recommendation that has already been calculated. "
            "Do not change the recommended club, target, distance, or risk. Use only the supplied data. "
            "If course or weather facts are missing, say so. Do not claim to know a golfer's tendencies "
            "or course features that are not included. Keep the reply to two short sentences."
        ),
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
                    return content["text"].strip(), "openai"
    except Exception:
        # Preserve the usable structured recommendation if the explanation service is down.
        return fallback_explanation(question, recommendation, weather), "rules"

    return fallback_explanation(question, recommendation, weather), "rules"
