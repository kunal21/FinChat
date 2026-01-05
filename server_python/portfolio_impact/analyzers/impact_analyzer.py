from __future__ import annotations

import json
from typing import Dict, Tuple

from openai import OpenAI


VALID_IMPACT_LEVELS = {"HIGH", "MEDIUM", "LOW"}
VALID_EFFECTS = {"positive", "negative", "neutral"}


def build_impact_prompt(clean_text: str, ticker: str) -> str:
    """
    Build LLM prompt for materiality analysis of a news article.

    Args:
        clean_text: Combined article text (title + description + content)
        ticker: Stock ticker to analyze impact for

    Returns:
        Formatted prompt string for LLM
    """
    return (
        f"You are a financial analyst assistant. Analyze the following news article "
        f"for its materiality and potential impact on {ticker}.\n\n"
        f"A news article is \"material\" if it:\n"
        f"1. Directly mentions {ticker} or the company\n"
        f"2. Discusses events that could reasonably affect {ticker}'s stock price\n"
        f"3. Contains information an investor holding {ticker} would want to know\n\n"
        "Respond with JSON only. Schema:\n"
        "{\n"
        '  "is_material": boolean,\n'
        '  "impact_level": "HIGH" | "MEDIUM" | "LOW",\n'
        '  "impact_summary": string (1-2 sentences explaining the impact),\n'
        '  "estimated_effect": "positive" | "negative" | "neutral",\n'
        '  "confidence": number (0.0 to 1.0)\n'
        "}\n\n"
        "Article:\n"
        f"{clean_text}\n\n"
        f"Ticker: {ticker}"
    )


def validate_impact_json(impact: Dict) -> Tuple[bool, str]:
    """
    Validate impact analysis JSON structure.

    Args:
        impact: Dictionary returned from LLM

    Returns:
        Tuple of (is_valid, error_message)
    """
    required_keys = {
        "is_material", "impact_level", "impact_summary",
        "estimated_effect", "confidence"
    }

    missing = required_keys.difference(impact.keys())
    if missing:
        return False, f"Missing keys: {sorted(missing)}"

    if not isinstance(impact["is_material"], bool):
        return False, "is_material must be boolean"

    if impact["impact_level"] not in VALID_IMPACT_LEVELS:
        return False, f"impact_level must be one of {VALID_IMPACT_LEVELS}"

    if impact["estimated_effect"] not in VALID_EFFECTS:
        return False, f"estimated_effect must be one of {VALID_EFFECTS}"

    if not isinstance(impact["confidence"], (int, float)) or not 0 <= impact["confidence"] <= 1:
        return False, "confidence must be between 0 and 1"

    if not isinstance(impact["impact_summary"], str) or not impact["impact_summary"].strip():
        return False, "impact_summary must be non-empty string"

    return True, ""


def analyze_impact(clean_text: str, ticker: str, api_key: str, model: str = "gpt-4o-mini") -> Dict:
    """
    Analyze article impact for a specific ticker using LLM.

    Args:
        clean_text: Combined article text (title + content)
        ticker: Stock ticker to analyze for
        api_key: OpenAI API key
        model: OpenAI model to use

    Returns:
        Dictionary with impact analysis containing:
        - is_material: bool
        - impact_level: "HIGH"|"MEDIUM"|"LOW"
        - impact_summary: str
        - estimated_effect: "positive"|"negative"|"neutral"
        - confidence: float

    Raises:
        Exception: If API call fails
    """
    client = OpenAI(api_key=api_key)
    prompt = build_impact_prompt(clean_text, ticker)

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
    except TypeError:
        # Fallback for older OpenAI versions without response_format support
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )

    content = response.choices[0].message.content or "{}"
    return json.loads(content)


def analyze_impact_with_retry(
    clean_text: str,
    ticker: str,
    api_key: str,
    model: str = "gpt-4o-mini",
    max_attempts: int = 2
) -> Dict:
    """
    Analyze article impact with retry logic for robustness.

    Args:
        clean_text: Combined article text
        ticker: Stock ticker symbol
        api_key: OpenAI API key
        model: OpenAI model to use
        max_attempts: Maximum number of retry attempts

    Returns:
        Validated impact analysis dictionary

    Raises:
        ValueError: If analysis fails after max_attempts
    """
    attempt = 0
    last_error = ""

    while attempt < max_attempts:
        try:
            result = analyze_impact(clean_text, ticker, api_key, model)
            ok, error = validate_impact_json(result)
            if ok:
                return result
            last_error = error
        except (json.JSONDecodeError, ValueError, KeyError) as exc:
            last_error = str(exc)
        attempt += 1

    raise ValueError(f"Impact analysis failed after {max_attempts} attempts: {last_error}")
