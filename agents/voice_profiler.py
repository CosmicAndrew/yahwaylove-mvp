"""
voice_profiler.py — YAHWAYLOVE Taste Interviewer
=================================================
Generates a pastor.md voice profile file from a set of intake answers.
The pastor.md file is the single source of truth for CONTENT agent.

Usage:
    python voice_profiler.py --input intake.json --output pastor.md
    python voice_profiler.py --interactive          # CLI interview mode
    python voice_profiler.py --from-form form.json  # from Formspree webhook payload

Requirements:
    pip install openai python-dotenv
    DEEPSEEK_API_KEY or OPENAI_API_KEY in agents/.env
"""

import argparse
import json
import os
import sys
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

# ── System prompt for the Taste Interviewer ──────────────────────────────────

TASTE_INTERVIEWER_SYSTEM = """
You are the YAHWAYLOVE Taste Interviewer — an AI that builds precise voice profile
documents for faith leaders so the CONTENT agent can write in their exact voice.

Your job is to analyze the intake answers and produce a structured pastor.md file.
The file must be specific enough that another AI can impersonate this person's writing
style without ever having read their content.

You must capture:
1. VOICE FINGERPRINT — their unique writing patterns, vocabulary, sentence length
2. THEOLOGY — their doctrinal convictions, Scripture translation preference, how they
   use the Bible (proof-texting vs. narrative vs. typological)
3. AUDIENCE — who they speak to, what those people struggle with, the cultural context
4. TONE DIALS — where they sit on each axis:
   - Encouraging ←──────────────→ Prophetically challenging
   - Conversational ←──────────→ Theologically precise
   - Story-driven ←────────────→ Principle-driven
   - Humor-forward ←───────────→ Gravitas-forward
5. CONTENT PATTERNS — their go-to hooks, recurring themes, how they close a post
6. AVOID LIST — things they would never say, topics they stay away from, phrases
   that would sound fake coming from them

Output ONLY the markdown pastor.md file. No preamble. No explanation.
Start directly with the frontmatter block.
"""

TASTE_INTERVIEWER_PROMPT = """
Build a complete pastor.md voice profile from these intake answers:

{intake_data}

The pastor.md must follow this exact structure:

---
name: [Full name]
church: [Church name]
location: [City, State]
generated: [Today's date]
sprint_id: [Auto-generate: SPRINT-YYYY-MM-DD-[INITIALS]]
---

# Voice Profile: [Name]

## Voice Fingerprint
[3-5 bullet points describing their exact writing style — sentence length, rhythm,
vocabulary level, use of contractions, capitalization quirks, paragraph length]

## Theology
- Translation: [KJV / ESV / NIV / NLT / NKJV / Mix]
- Tradition: [Baptist / Pentecostal / Non-denominational / etc.]
- Bible usage: [How they integrate Scripture — quote-heavy, paraphrase, narrative]
- Core themes: [3-5 recurring theological ideas they return to]
- Would never say: [Theological statements or framings they'd reject]

## Audience
- Primary: [Who they're speaking to — demographics, spiritual maturity level]
- Pain points: [What their people struggle with most]
- Cultural context: [What cultural references land naturally]
- Platform: [Where they post most — Facebook, Instagram, LinkedIn, X]

## Tone Dials
[Rate each 1-10, with 1=left side, 10=right side]
- Encouraging (1) ←→ Prophetically challenging (10): [score]/10
- Conversational (1) ←→ Theologically precise (10): [score]/10
- Story-driven (1) ←→ Principle-driven (10): [score]/10
- Humor-forward (1) ←→ Gravitas-forward (10): [score]/10

## Content Patterns
- Hook style: [How they typically open — question, statement, story beat, Scripture]
- Structure: [How they build a post — problem/tension/resolution, list, etc.]
- Closing move: [How they end — invitation, declaration, question, prayer]
- Recurring metaphors: [Images or analogies they return to]
- Signature phrases: [2-3 phrases that sound distinctly like them]

## Avoid List
- [Phrase or topic 1 — reason]
- [Phrase or topic 2 — reason]
- [Phrase or topic 3 — reason]

## Sample Post Prompt
[A single paragraph prompt that, when given to an LLM, would produce a post that
sounds exactly like this person. Should reference their specific style, theology,
and audience in concrete terms.]
"""

# ── Interactive CLI interview ─────────────────────────────────────────────────

INTERVIEW_QUESTIONS = [
    ("name", "Pastor's full name"),
    ("church", "Church or ministry name"),
    ("location", "City, State"),
    ("email", "Email address (for delivery)"),
    ("platform", "Primary posting platform (Facebook / Instagram / LinkedIn / X / All)"),
    ("topic", "What topic or Scripture passage would you post about this week?"),
    ("style", "Describe your posting style in your own words"),
    ("audience", "Who is your primary audience? What do they struggle with?"),
    ("theology", "What Bible translation do you prefer? What's your tradition?"),
    ("example_post", "Paste or describe one of your best-performing posts (optional)"),
    ("avoid", "Anything you'd never say or topics you stay away from?"),
]


def run_interactive_interview() -> dict:
    """Walk Andrew or a team member through the intake questions in the terminal."""
    print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("  YAHWAYLOVE — Voice Profile Interview")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
    intake = {}
    for key, question in INTERVIEW_QUESTIONS:
        value = input(f"  {question}:\n  > ").strip()
        intake[key] = value
        print()
    return intake


def parse_formspree_payload(payload: dict) -> dict:
    """
    Map Formspree form field names to internal intake keys.
    Matches the field names in pages/sprint.html.
    """
    return {
        "name": payload.get("name", ""),
        "church": payload.get("church", ""),
        "email": payload.get("email", ""),
        "topic": payload.get("topic", ""),
        "style": payload.get("style", ""),
        "platform": payload.get("platform", "Instagram/Facebook"),
        "audience": payload.get("audience", ""),
        "theology": payload.get("theology", ""),
        "example_post": payload.get("example_post", ""),
        "avoid": payload.get("avoid", ""),
        "location": payload.get("location", ""),
    }


# ── Core: build voice profile via configured LLM route ───────────────────────

def build_voice_profile(intake: dict) -> str:
    """
    Send intake answers to the configured LLM and get back a complete pastor.md string.
    """
    intake_text = "\n".join(
        f"**{k.replace('_', ' ').title()}:** {v}" for k, v in intake.items() if v
    )

    today = datetime.now().strftime("%Y-%m-%d")
    initials = "".join(w[0].upper() for w in intake.get("name", "XX").split()[:2])
    sprint_id = f"SPRINT-{today}-{initials}"

    prompt = TASTE_INTERVIEWER_PROMPT.format(
        intake_data=intake_text,
    ).replace("[Auto-generate: SPRINT-YYYY-MM-DD-[INITIALS]]", sprint_id)

    print("  ⟳  Building voice profile via DeepSeek/GPT-5.5...")

    return generate_text(
        system=TASTE_INTERVIEWER_SYSTEM,
        prompt=prompt,
        max_tokens=4096,
    )


def save_profile(profile_md: str, output_path: str, intake: dict) -> None:
    """Save the pastor.md file and print a summary."""
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(profile_md)

    name = intake.get("name", "Pastor")
    print(f"\n  ✓  Voice profile saved → {output_path}")
    print(f"  ✓  Ready for CONTENT agent: python content_agent.py --profile {output_path}")
    print(f"\n  Pastor: {name}")
    print(f"  Church: {intake.get('church', '')}")
    print(f"  Email:  {intake.get('email', '')}\n")


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="YAHWAYLOVE Voice Profiler")
    parser.add_argument("--interactive", action="store_true", help="Run CLI interview")
    parser.add_argument("--input", type=str, help="Path to intake JSON file")
    parser.add_argument("--from-form", type=str, help="Path to Formspree webhook JSON")
    parser.add_argument("--output", type=str, default="profiles/pastor.md",
                        help="Output path for pastor.md (default: profiles/pastor.md)")
    args = parser.parse_args()

    try:
        require_llm_credentials()
    except LLMConfigError as exc:
        print(f"\n  ✗  {exc}\n")
        sys.exit(1)

    # Gather intake
    if args.interactive:
        intake = run_interactive_interview()
    elif args.from_form:
        with open(args.from_form, encoding="utf-8") as f:
            raw = json.load(f)
        intake = parse_formspree_payload(raw)
    elif args.input:
        with open(args.input, encoding="utf-8") as f:
            intake = json.load(f)
    else:
        parser.print_help()
        sys.exit(1)

    # Build profile
    profile_md = build_voice_profile(intake)

    # Auto-name output file from pastor's name if default path used
    if args.output == "profiles/pastor.md" and intake.get("name"):
        safe_name = intake["name"].lower().replace(" ", "_")
        args.output = f"profiles/{safe_name}.md"

    save_profile(profile_md, args.output, intake)


if __name__ == "__main__":
    main()
