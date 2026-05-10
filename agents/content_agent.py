"""
content_agent.py — YAHWAYLOVE CONTENT Agent
============================================
Generates 10 faith posts in a pastor's exact voice using their pastor.md profile.
All output goes to EDITOR agent for theology + tone QA before delivery.

Usage:
    python content_agent.py --profile profiles/pastor_name.md
    python content_agent.py --profile profiles/pastor_name.md --count 10 --topic "faith over fear"
    python content_agent.py --profile profiles/pastor_name.md --free-sample  # generates 1 post only

Output:
    posts/[sprint_id]/raw_posts.md       — all 10 posts, unreviewed
    posts/[sprint_id]/intake_summary.md  — what was used as input

Requirements:
    pip install openai python-dotenv
    DEEPSEEK_API_KEY or OPENAI_API_KEY in agents/.env
"""

import argparse
import os
import sys
import re
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

try:
    from .llm_client import LLMConfigError, generate_text, require_llm_credentials
except ImportError:
    from llm_client import LLMConfigError, generate_text, require_llm_credentials

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

load_dotenv()

# ── Post type definitions ─────────────────────────────────────────────────────

POST_TYPES = [
    {
        "id": "scripture_reflection",
        "name": "Scripture Reflection",
        "description": "A single verse or passage unpacked with personal insight and application.",
        "length": "150–200 words",
    },
    {
        "id": "personal_story",
        "name": "Personal Story",
        "description": "A specific real-life moment that illustrates a spiritual truth.",
        "length": "180–220 words",
    },
    {
        "id": "theological_truth",
        "name": "Theological Truth",
        "description": "A doctrinal point made accessible — 'here's what this actually means for you.'",
        "length": "150–200 words",
    },
    {
        "id": "monday_momentum",
        "name": "Monday Momentum",
        "description": "Week-opener: a declaration or commissioning post to start the week with purpose.",
        "length": "100–150 words",
    },
    {
        "id": "mid_week_check",
        "name": "Mid-Week Check-In",
        "description": "Wednesday encouragement — acknowledges the grind, points to grace.",
        "length": "120–160 words",
    },
    {
        "id": "sermon_teaser",
        "name": "Sunday Sermon Teaser",
        "description": "Builds anticipation for Sunday's message without giving it away.",
        "length": "100–140 words",
    },
    {
        "id": "question_post",
        "name": "Engagement Question",
        "description": "Opens with a question that invites real responses from the congregation.",
        "length": "80–120 words",
    },
    {
        "id": "behind_the_scenes",
        "name": "Behind the Scenes",
        "description": "Humanizing post — what pastoral life actually looks like day to day.",
        "length": "150–180 words",
    },
    {
        "id": "prophetic_word",
        "name": "Prophetic Declaration",
        "description": "A bold, faith-forward declaration spoken over the reader's situation.",
        "length": "120–160 words",
    },
    {
        "id": "gratitude_testimony",
        "name": "Gratitude / Testimony",
        "description": "Celebrating what God has done — builds faith by recounting His faithfulness.",
        "length": "150–200 words",
    },
]

# ── System prompt ─────────────────────────────────────────────────────────────

CONTENT_SYSTEM = """
You are CONTENT, the post generation agent for YAHWAYLOVE LLC.

Your single job: write social media posts that sound EXACTLY like the faith leader
described in the voice profile you've been given. The reader should not be able to
tell the difference between this post and something the pastor wrote themselves.

CRITICAL RULES:
1. Read the voice profile completely before writing anything.
2. Match their sentence length, rhythm, vocabulary level, and theological framing.
3. Never use phrases on their Avoid List.
4. Scripture references must be real and contextually accurate — verify internally.
5. Do not be generic. Every post must feel specific to this person and their congregation.
6. Do not use hashtags unless the profile specifies they use them.
7. Respect their Tone Dial scores — a 3/10 prophetic voice should not thunder.
8. Each post must stand alone — no "as I mentioned before" references.
9. End each post in a way consistent with their Closing Move pattern.
10. Output posts in clean markdown — one post per section, with a type label.

You are writing for real ministry. Write like it matters. It does.
"""

SINGLE_POST_PROMPT = """
Voice Profile:
{profile}

---

Write a {post_type_name} post ({description}, {length}).

{topic_line}

Requirements:
- Sound exactly like this pastor based on their voice profile
- Match their tone dial scores precisely
- Use their preferred Scripture translation if including a verse
- Follow their hook style and closing move
- Do NOT use any phrases from their Avoid List
- Appropriate for {platform}

Output only the post text. No label, no preamble, no quotation marks.
"""

BATCH_PROMPT = """
Voice Profile:
{profile}

---

Write all 10 posts below. Each post must sound exactly like this pastor.

For each post:
- Match the voice profile precisely — tone dials, vocabulary, Scripture usage, closing moves
- Make it feel written specifically for this pastor's congregation
- Do NOT use any phrases from their Avoid List
- Keep each post self-contained

{topic_line}

Platform: {platform}

---

Write all 10 posts in this exact format — one after another, separated by ---:

## Post 1 — Scripture Reflection
[post text]

---

## Post 2 — Personal Story
[post text]

---

## Post 3 — Theological Truth
[post text]

---

## Post 4 — Monday Momentum
[post text]

---

## Post 5 — Mid-Week Check-In
[post text]

---

## Post 6 — Sunday Sermon Teaser
[post text]

---

## Post 7 — Engagement Question
[post text]

---

## Post 8 — Behind the Scenes
[post text]

---

## Post 9 — Prophetic Declaration
[post text]

---

## Post 10 — Gratitude / Testimony
[post text]
"""

# ── Helpers ───────────────────────────────────────────────────────────────────

def load_profile(profile_path: str) -> str:
    """Load pastor.md file and return as string."""
    with open(profile_path, encoding="utf-8") as f:
        return f.read()


def extract_sprint_id(profile: str) -> str:
    """Pull sprint_id from profile frontmatter."""
    match = re.search(r"sprint_id:\s*(.+)", profile)
    if match:
        return match.group(1).strip()
    return f"SPRINT-{datetime.now().strftime('%Y%m%d-%H%M%S')}"


def extract_name(profile: str) -> str:
    """Pull pastor name from profile frontmatter."""
    match = re.search(r"^name:\s*(.+)", profile, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return "Pastor"


def extract_platform(profile: str) -> str:
    """Pull primary platform from profile."""
    match = re.search(r"Platform:\s*(.+)", profile)
    if match:
        return match.group(1).strip()
    return "Facebook/Instagram"


def generate_posts(
    profile: str,
    topic: str = "",
    count: int = 10,
    free_sample: bool = False,
) -> str:
    """
    Generate posts using the configured LLM provider route.
    free_sample=True → generates only 1 post (Post 1: Scripture Reflection).
    """
    platform = extract_platform(profile)

    if free_sample or count == 1:
        post_type = POST_TYPES[0]
        topic_line = (
            f"Topic/theme to center on: {topic}"
            if topic
            else "Choose a theme that fits this pastor's current season and audience pain points."
        )
        prompt = SINGLE_POST_PROMPT.format(
            profile=profile,
            post_type_name=post_type["name"],
            description=post_type["description"],
            length=post_type["length"],
            topic_line=topic_line,
            platform=platform,
        )
        print(f"  ⟳  Generating free sample post...")
    else:
        topic_line = (
            f"Global topic/theme: {topic}"
            if topic
            else "Choose themes that fit this pastor's stated season, audience pain points, and recurring theological ideas from their profile."
        )
        prompt = BATCH_PROMPT.format(
            profile=profile,
            topic_line=topic_line,
            platform=platform,
        )
        print(f"  ⟳  Generating {count} posts via DeepSeek/GPT-5.5...")

    return generate_text(
        system=CONTENT_SYSTEM,
        prompt=prompt,
        max_tokens=8096,
    )


def save_posts(
    posts_text: str,
    profile: str,
    sprint_id: str,
    topic: str,
    free_sample: bool,
) -> str:
    """
    Save raw posts to posts/[sprint_id]/raw_posts.md.
    Returns the output directory path.
    """
    output_dir = Path(f"posts/{sprint_id}")
    output_dir.mkdir(parents=True, exist_ok=True)

    pastor_name = extract_name(profile)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    # Build the raw posts file
    file_type = "free_sample" if free_sample else "raw_posts"
    posts_file = output_dir / f"{file_type}.md"

    header = f"""# YAHWAYLOVE — {'Free Sample Post' if free_sample else '10 Posts'} for {pastor_name}
**Sprint ID:** {sprint_id}
**Generated:** {timestamp}
**Topic:** {topic or 'Auto-selected from profile'}
**Status:** RAW — Pending EDITOR review
**Next step:** python editor_agent.py --sprint {sprint_id}

---

"""
    with open(posts_file, "w", encoding="utf-8") as f:
        f.write(header + posts_text)

    # Save intake summary
    summary_file = output_dir / "intake_summary.md"
    with open(summary_file, "w", encoding="utf-8") as f:
        f.write(f"""# Sprint Intake Summary
**Sprint ID:** {sprint_id}
**Pastor:** {pastor_name}
**Generated:** {timestamp}
**Topic:** {topic or 'Auto-selected'}
**Mode:** {'Free Sample (1 post)' if free_sample else '10-post Sprint'}

## Profile Used
```
{profile[:800]}...
```
""")

    return str(output_dir)


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="YAHWAYLOVE CONTENT Agent")
    parser.add_argument("--profile", required=True, help="Path to pastor.md voice profile")
    parser.add_argument("--topic", default="", help="Optional topic or Scripture to center posts on")
    parser.add_argument("--count", type=int, default=10, help="Number of posts to generate (default: 10)")
    parser.add_argument("--free-sample", action="store_true", help="Generate 1 free sample post only")
    args = parser.parse_args()

    try:
        require_llm_credentials()
    except LLMConfigError as exc:
        print(f"\n  ✗  {exc}\n")
        sys.exit(1)

    if not os.path.exists(args.profile):
        print(f"\n  ✗  Profile not found: {args.profile}\n")
        sys.exit(1)

    print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("  YAHWAYLOVE — CONTENT Agent")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

    # Load profile
    profile = load_profile(args.profile)
    sprint_id = extract_sprint_id(profile)
    pastor_name = extract_name(profile)

    print(f"  Profile:   {pastor_name}")
    print(f"  Sprint ID: {sprint_id}")
    print(f"  Mode:      {'Free Sample (1 post)' if args.free_sample else f'{args.count} posts'}")
    if args.topic:
        print(f"  Topic:     {args.topic}")
    print()

    # Generate
    posts = generate_posts(
        profile=profile,
        topic=args.topic,
        count=args.count,
        free_sample=args.free_sample,
    )

    # Save
    output_dir = save_posts(
        posts_text=posts,
        profile=profile,
        sprint_id=sprint_id,
        topic=args.topic,
        free_sample=args.free_sample,
    )

    print(f"\n  ✓  Posts saved → {output_dir}/")
    print(f"  ✓  Next step: python editor_agent.py --sprint {sprint_id}")
    print()


if __name__ == "__main__":
    main()
