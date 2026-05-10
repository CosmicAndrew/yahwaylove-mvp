"""
Provider-neutral LLM client for local YAHWAYLOVE Sprint agents.

Default route:
1. DeepSeek V4 Pro
2. DeepSeek V4 Flash
3. OpenAI GPT-5.5
4. OpenRouter Claude Opus 4.7 only when premium escalation is enabled
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from dotenv import load_dotenv
from openai import OpenAI


AGENTS_DIR = Path(__file__).resolve().parent
load_dotenv(AGENTS_DIR / ".env", override=False)


class LLMConfigError(RuntimeError):
    """Raised when no configured provider can run the requested call."""


class LLMCallError(RuntimeError):
    """Raised when configured providers fail to return usable text."""


@dataclass(frozen=True)
class ProviderRoute:
    provider: str
    model: str


def generate_text(
    prompt: str,
    system: str | None = None,
    max_tokens: int = 1024,
    temperature: float | None = None,
    provider: str | None = None,
    model: str | None = None,
    allow_premium: bool = False,
) -> str:
    """
    Generate plain text using the configured provider route.

    The default route prefers DeepSeek, then OpenAI. OpenRouter Opus is only
    added when allow_premium=True or YAHWAYLOVE_ALLOW_OPUS=true.
    """
    routes = _build_routes(provider=provider, model=model, allow_premium=allow_premium)
    failures: list[str] = []

    for route in routes:
        try:
            return _run_provider(
                provider=route.provider,
                model=route.model,
                system=system,
                prompt=prompt,
                max_tokens=max_tokens,
                temperature=temperature,
            )
        except Exception as exc:
            failures.append(f"{route.provider}/{route.model}: {_redact_error(exc)}")

    raise LLMCallError("All configured LLM providers failed: " + "; ".join(failures))


def require_llm_credentials() -> None:
    if not (_env("DEEPSEEK_API_KEY") or _env("OPENAI_API_KEY")):
        raise LLMConfigError(
            "Set DEEPSEEK_API_KEY or OPENAI_API_KEY in agents/.env or the user environment."
        )


def configured_providers() -> list[str]:
    providers = []
    if _env("DEEPSEEK_API_KEY"):
        providers.append("deepseek")
    if _env("OPENAI_API_KEY"):
        providers.append("openai")
    if _env("OPENROUTER_API_KEY"):
        providers.append("openrouter")
    return providers


def _build_routes(
    provider: str | None,
    model: str | None,
    allow_premium: bool,
) -> list[ProviderRoute]:
    if provider:
        normalized = provider.strip().lower()
        if normalized not in {"deepseek", "openai", "openrouter"}:
            raise LLMConfigError(f"Unsupported LLM provider: {provider}")
        _require_provider_key(normalized)
        return [ProviderRoute(normalized, model or _default_model(normalized))]

    routes: list[ProviderRoute] = []
    if _env("DEEPSEEK_API_KEY"):
        routes.append(ProviderRoute("deepseek", _default_model("deepseek")))
        routes.append(ProviderRoute("deepseek", _deepseek_fallback_model()))
    if _env("OPENAI_API_KEY"):
        routes.append(ProviderRoute("openai", _default_model("openai")))

    premium_enabled = allow_premium or _truthy(_env("YAHWAYLOVE_ALLOW_OPUS"))
    if premium_enabled and _env("OPENROUTER_API_KEY"):
        routes.append(ProviderRoute("openrouter", _default_model("openrouter")))

    if not routes:
        raise LLMConfigError(
            "Set DEEPSEEK_API_KEY or OPENAI_API_KEY in agents/.env or the user environment."
        )
    return routes


def _run_provider(
    *,
    provider: str,
    model: str,
    system: str | None,
    prompt: str,
    max_tokens: int,
    temperature: float | None,
) -> str:
    if provider == "openai":
        return _run_openai_responses(
            model=model,
            system=system,
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=temperature,
        )
    if provider in {"deepseek", "openrouter"}:
        return _run_chat_completion(
            provider=provider,
            model=model,
            system=system,
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=temperature,
        )
    raise LLMConfigError(f"Unsupported LLM provider: {provider}")


def _run_chat_completion(
    *,
    provider: str,
    model: str,
    system: str | None,
    prompt: str,
    max_tokens: int,
    temperature: float | None,
) -> str:
    client = _openai_compatible_client(provider)
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    kwargs = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
    }
    if temperature is not None:
        kwargs["temperature"] = temperature

    response = client.chat.completions.create(**kwargs)
    return _extract_chat_completion_text(response)


def _run_openai_responses(
    *,
    model: str,
    system: str | None,
    prompt: str,
    max_tokens: int,
    temperature: float | None,
) -> str:
    client = OpenAI(api_key=_require_env("OPENAI_API_KEY"))
    kwargs = {
        "model": model,
        "input": prompt,
        "max_output_tokens": max_tokens,
    }
    if system:
        kwargs["instructions"] = system
    if temperature is not None:
        kwargs["temperature"] = temperature

    response = client.responses.create(**kwargs)
    return _extract_openai_response_text(response)


def _openai_compatible_client(provider: str) -> OpenAI:
    if provider == "deepseek":
        return OpenAI(
            api_key=_require_env("DEEPSEEK_API_KEY"),
            base_url=_env("DEEPSEEK_BASE_URL") or "https://api.deepseek.com",
        )
    if provider == "openrouter":
        return OpenAI(
            api_key=_require_env("OPENROUTER_API_KEY"),
            base_url=_env("OPENROUTER_BASE_URL") or "https://openrouter.ai/api/v1",
            default_headers={
                "HTTP-Referer": _env("OPENROUTER_SITE_URL") or "https://yahwaylove.com",
                "X-Title": _env("OPENROUTER_APP_NAME") or "YAHWAYLOVE Sprint Agents",
            },
        )
    raise LLMConfigError(f"Unsupported OpenAI-compatible provider: {provider}")


def _extract_chat_completion_text(response) -> str:
    choices = getattr(response, "choices", None) or []
    if not choices:
        raise LLMCallError("Chat completion returned no choices.")
    message = getattr(choices[0], "message", None)
    content = getattr(message, "content", None) if message else None
    if isinstance(content, list):
        text = "".join(
            part.get("text", "") if isinstance(part, dict) else getattr(part, "text", "")
            for part in content
        )
    else:
        text = content or ""
    text = text.strip()
    if not text:
        raise LLMCallError("Chat completion returned empty text.")
    return text


def _extract_openai_response_text(response) -> str:
    direct = getattr(response, "output_text", None)
    if direct:
        return direct.strip()

    pieces: list[str] = []
    for item in _iter(getattr(response, "output", None)):
        for content in _iter(getattr(item, "content", None)):
            content_type = getattr(content, "type", None)
            text = getattr(content, "text", None)
            if content_type in {None, "output_text"} and text:
                pieces.append(text)

    text = "\n".join(piece.strip() for piece in pieces if piece.strip()).strip()
    if not text:
        raise LLMCallError("OpenAI response returned empty text.")
    return text


def _iter(value) -> Iterable:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _default_model(provider: str) -> str:
    if provider == "deepseek":
        return _env("DEEPSEEK_MODEL") or _env("TIER2_MODEL") or "deepseek-v4-pro"
    if provider == "openai":
        return _env("OPENAI_MODEL") or "gpt-5.5"
    if provider == "openrouter":
        return _env("OPENROUTER_OPUS_MODEL") or "anthropic/claude-opus-4.7"
    raise LLMConfigError(f"Unsupported LLM provider: {provider}")


def _deepseek_fallback_model() -> str:
    return (
        _env("DEEPSEEK_FALLBACK_MODEL")
        or _env("TIER2_FALLBACK_MODEL")
        or "deepseek-v4-flash"
    )


def _require_provider_key(provider: str) -> None:
    key_name = {
        "deepseek": "DEEPSEEK_API_KEY",
        "openai": "OPENAI_API_KEY",
        "openrouter": "OPENROUTER_API_KEY",
    }[provider]
    _require_env(key_name)


def _require_env(name: str) -> str:
    value = _env(name)
    if not value:
        raise LLMConfigError(f"{name} is not set.")
    return value


def _env(name: str) -> str:
    return os.getenv(name, "").strip()


def _truthy(value: str) -> bool:
    return value.lower() in {"1", "true", "yes", "on"}


def _redact_error(exc: Exception) -> str:
    message = str(exc)
    for name in (
        "DEEPSEEK_API_KEY",
        "OPENAI_API_KEY",
        "OPENROUTER_API_KEY",
    ):
        value = _env(name)
        if value:
            message = message.replace(value, "[redacted]")
    return message or exc.__class__.__name__
