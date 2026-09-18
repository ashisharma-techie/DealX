"""
llm_client.py
-------------
Thin, swappable wrapper around whichever LLM provider has a key configured.

Reads OPENAI_API_KEY or GEMINI_API_KEY from the environment (via a .env file
loaded with python-dotenv). OpenAI is tried first if both are set.

Public API:
    call_llm(system_prompt: str, user_prompt: str, json_mode: bool = False) -> str
        Returns the raw text response from whichever provider is configured.
        Raises LLMNotConfiguredError if neither key is present (callers - see
        spec_matcher.py - should catch this and fall back to a heuristic).
"""

from __future__ import annotations

import os

from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")


class LLMNotConfiguredError(RuntimeError):
    """Raised when neither OPENAI_API_KEY nor GEMINI_API_KEY is set."""


def provider_configured() -> str | None:
    if OPENAI_API_KEY:
        return "openai"
    if GEMINI_API_KEY:
        return "gemini"
    return None


def _call_openai(system_prompt: str, user_prompt: str, json_mode: bool) -> str:
    from openai import OpenAI

    client = OpenAI(api_key=OPENAI_API_KEY)
    kwargs = {}
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}

    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,
        **kwargs,
    )
    return response.choices[0].message.content


def _call_gemini(system_prompt: str, user_prompt: str, json_mode: bool) -> str:
    import google.generativeai as genai

    genai.configure(api_key=GEMINI_API_KEY)
    generation_config = {"temperature": 0.2}
    if json_mode:
        generation_config["response_mime_type"] = "application/json"

    model = genai.GenerativeModel(GEMINI_MODEL, system_instruction=system_prompt)
    response = model.generate_content(user_prompt, generation_config=generation_config)
    return response.text


def call_llm(system_prompt: str, user_prompt: str, json_mode: bool = False) -> str:
    """
    Calls whichever provider is configured. `json_mode=True` asks the
    provider to constrain its output to valid JSON (both OpenAI and Gemini
    support this natively) - spec_matcher.py relies on this.
    """
    provider = provider_configured()
    if provider == "openai":
        return _call_openai(system_prompt, user_prompt, json_mode)
    if provider == "gemini":
        return _call_gemini(system_prompt, user_prompt, json_mode)
    raise LLMNotConfiguredError(
        "No LLM API key found. Set OPENAI_API_KEY or GEMINI_API_KEY in ai-engine/.env "
        "(see .env.example). spec_matcher.py will fall back to a heuristic matcher "
        "if this is raised, so this is safe to hit during a demo without keys."
    )


if __name__ == "__main__":
    # Quick manual smoke test - requires a real key in .env.
    try:
        print(call_llm("You are terse.", "Say hello in 3 words."))
    except LLMNotConfiguredError as e:
        print(f"[not configured] {e}")
