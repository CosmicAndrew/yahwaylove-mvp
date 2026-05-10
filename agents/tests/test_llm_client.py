import os
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from agents import llm_client


class LLMClientTests(unittest.TestCase):
    def test_default_routes_to_deepseek_primary_when_key_exists(self):
        with patch.dict(os.environ, {"DEEPSEEK_API_KEY": "key"}, clear=True):
            with patch.object(llm_client, "_run_provider", return_value="ok") as run:
                text = llm_client.generate_text(
                    system="system",
                    prompt="hello",
                    max_tokens=12,
                )

        self.assertEqual(text, "ok")
        self.assertEqual(run.call_args.kwargs["provider"], "deepseek")
        self.assertEqual(run.call_args.kwargs["model"], "deepseek-v4-pro")

    def test_missing_default_credentials_raises_clear_error(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(
                llm_client.LLMConfigError,
                "DEEPSEEK_API_KEY or OPENAI_API_KEY",
            ):
                llm_client.generate_text(prompt="hello")

    def test_deepseek_primary_falls_back_to_flash_before_openai(self):
        calls = []

        def fake_run(**kwargs):
            calls.append((kwargs["provider"], kwargs["model"]))
            if kwargs["model"] == "deepseek-v4-pro":
                raise llm_client.LLMCallError("primary failed")
            return "flash ok"

        with patch.dict(
            os.environ,
            {"DEEPSEEK_API_KEY": "deepseek", "OPENAI_API_KEY": "openai"},
            clear=True,
        ):
            with patch.object(llm_client, "_run_provider", side_effect=fake_run):
                text = llm_client.generate_text(prompt="hello")

        self.assertEqual(text, "flash ok")
        self.assertEqual(
            calls,
            [
                ("deepseek", "deepseek-v4-pro"),
                ("deepseek", "deepseek-v4-flash"),
            ],
        )

    def test_openrouter_opus_is_only_used_when_premium_is_allowed(self):
        calls = []

        def fake_run(**kwargs):
            calls.append((kwargs["provider"], kwargs["model"]))
            raise llm_client.LLMCallError("failed")

        with patch.dict(
            os.environ,
            {
                "DEEPSEEK_API_KEY": "deepseek",
                "OPENAI_API_KEY": "openai",
                "OPENROUTER_API_KEY": "openrouter",
            },
            clear=True,
        ):
            with patch.object(llm_client, "_run_provider", side_effect=fake_run):
                with self.assertRaises(llm_client.LLMCallError):
                    llm_client.generate_text(prompt="hello", allow_premium=True)

        self.assertEqual(
            calls,
            [
                ("deepseek", "deepseek-v4-pro"),
                ("deepseek", "deepseek-v4-flash"),
                ("openai", "gpt-5.5"),
                ("openrouter", "anthropic/claude-opus-4.7"),
            ],
        )

    def test_extracts_openai_responses_output_text(self):
        response = SimpleNamespace(output_text="direct text")
        self.assertEqual(
            llm_client._extract_openai_response_text(response),
            "direct text",
        )

    def test_extracts_openai_responses_nested_text(self):
        response = SimpleNamespace(
            output=[
                SimpleNamespace(
                    content=[
                        SimpleNamespace(type="output_text", text="nested text")
                    ]
                )
            ]
        )
        self.assertEqual(
            llm_client._extract_openai_response_text(response),
            "nested text",
        )


if __name__ == "__main__":
    unittest.main()
