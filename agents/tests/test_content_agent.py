import unittest
from unittest.mock import patch

from agents import content_agent


PROFILE = """
---
sprint_id: SPRINT-TEST
name: Smoke Test Pastor
---

## Platform Strategy
- Primary platform: LinkedIn

## Voice
Warm and pastoral.
"""


class ContentAgentTests(unittest.TestCase):
    def test_free_sample_prompt_formats_without_literal_brace_error(self):
        with patch.object(content_agent, "generate_text", return_value="sample post") as call:
            result = content_agent.generate_posts(
                profile=PROFILE,
                topic="Psalm 23",
                free_sample=True,
            )

        self.assertEqual(result, "sample post")
        self.assertIn("Topic/theme to center on: Psalm 23", call.call_args.kwargs["prompt"])

    def test_batch_prompt_formats_without_literal_brace_error(self):
        with patch.object(content_agent, "generate_text", return_value="batch posts") as call:
            result = content_agent.generate_posts(
                profile=PROFILE,
                topic="Psalm 23",
                count=10,
                free_sample=False,
            )

        self.assertEqual(result, "batch posts")
        self.assertIn("Global topic/theme: Psalm 23", call.call_args.kwargs["prompt"])


if __name__ == "__main__":
    unittest.main()
