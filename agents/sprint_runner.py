"""
sprint_runner.py — YAHWAYLOVE Faith Content Sprint Orchestrator
===============================================================
End-to-end pipeline: intake form → voice profile → 10 posts → EDITOR review → delivery doc.

This is the single command Andrew runs after receiving a Formspree submission.

Usage:
    # Full pipeline from a form submission JSON:
    python sprint_runner.py --form form_payload.json

    # Full pipeline from an existing profile:
    python sprint_runner.py --profile profiles/john_smith.md --topic "fear vs faith"

    # Free sample only (for the Free Sample Close):
    python sprint_runner.py --form form_payload.json --free-sample

    # Just run the editor pass on an existing sprint:
    python sprint_runner.py --sprint SPRINT-2026-04-19-JS --editor-only

    # After review — package delivery doc:
    python sprint_runner.py --sprint SPRINT-2026-04-19-JS --deliver

Requirements:
    pip install anthropic python-dotenv
    ANTHROPIC_API_KEY in agents/.env
"""

import argparse
import json
import os
import re
import sys
import subprocess
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ── Pipeline steps ────────────────────────────────────────────────────────────

def step(num: int, total: int, label: str) -> None:
    print(f"\n  [{num}/{total}] {label}")
    print(f"  {'─' * 44}")


def run_step(cmd: list[str], label: str) -> int:
    """Run a subprocess step and stream its output."""
    result = subprocess.run(cmd, capture_output=False)
    return result.returncode


def load_json(path: str) -> dict:
    with open(path) as f:
        return json.load(f)


def find_profile_for_sprint(sprint_id: str) -> str | None:
    """Try to locate the pastor.md that was used for this sprint."""
    # Check intake_summary.md for profile hints
    summary = Path(f"posts/{sprint_id}/intake_summary.md")
    if not summary.exists():
        return None
    content = summary.read_text()
    name_match = re.search(r"\*\*Pastor:\*\*\s*(.+)", content)
    if not name_match:
        return None
    name = name_match.group(1).strip().lower().replace(" ", "_")
    profile_path = f"profiles/{name}.md"
    if os.path.exists(profile_path):
        return profile_path
    return None


def build_delivery_doc(sprint_id: str) -> str:
    """
    Package the reviewed_posts.md into a clean delivery document
    that Andrew can email directly to the pastor.
    """
    sprint_dir = Path(f"posts/{sprint_id}")
    reviewed = sprint_dir / "reviewed_posts.md"
    summary = sprint_dir / "intake_summary.md"

    if not reviewed.exists():
        print(f"\n  ✗  reviewed_posts.md not found. Run editor pass first.\n")
        sys.exit(1)

    # Extract pastor name and email from intake summary
    pastor_name = "Pastor"
    pastor_email = ""
    if summary.exists():
        content = summary.read_text()
        name_match = re.search(r"\*\*Pastor:\*\*\s*(.+)", content)
        if name_match:
            pastor_name = name_match.group(1).strip()

    reviewed_content = reviewed.read_text()
    timestamp = datetime.now().strftime("%B %d, %Y")

    delivery_doc = f"""# Faith Content Sprint — Delivery
**To:** {pastor_name}
**From:** Andrew Rocha | YAHWAYLOVE LLC
**Date:** {timestamp}
**Sprint ID:** {sprint_id}

---

{pastor_name},

Your 10 posts are ready. Each one was written in your voice, reviewed for
theological accuracy and tone, and is ready to post.

A few notes:
- Feel free to adjust any details — dates, specific names, local context
- Posts are ordered by type, not by posting day. Space them however works for your calendar.
- If anything doesn't feel like you, reply and we'll revise it at no charge.

---

{reviewed_content}

---

**Next steps:**
If you'd like YAHWAYLOVE to distribute these across your platforms automatically
(Facebook, Instagram, LinkedIn), reply "Schedule them" and we'll handle it via Blotato.

If you want to continue with a monthly plan (10 posts every month, plus Meta Ads,
web updates, and more), reply "Let's talk" and we'll schedule a 20-minute call.

Either way — these posts are yours. Use them however serves your ministry.

— Andrew Rocha
YAHWAYLOVE LLC | rocha@yahwaylove.com | (561) 305-0404 | Fort Worth, TX

_Romans 3:23_
"""

    delivery_path = sprint_dir / "DELIVERY.md"
    with open(delivery_path, "w") as f:
        f.write(delivery_doc)

    return str(delivery_path)


# ── Full pipeline ─────────────────────────────────────────────────────────────

def run_full_pipeline(
    form_path: str | None = None,
    profile_path: str | None = None,
    topic: str = "",
    free_sample: bool = False,
) -> None:
    """
    Run the complete Sprint pipeline:
    1. Build voice profile (if form provided)
    2. Generate posts via CONTENT agent
    3. Run EDITOR review
    4. Build delivery doc
    """
    total_steps = 3 if profile_path else 4

    print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("  YAHWAYLOVE — Faith Content Sprint Runner")
    print(f"  Mode: {'Free Sample (1 post)' if free_sample else '10-post Sprint'}")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    current_step = 1

    # Step 1: Voice Profile (skip if profile already provided)
    if form_path and not profile_path:
        step(current_step, total_steps, "Building Voice Profile")
        cmd = ["python", "voice_profiler.py", "--from-form", form_path]
        # Auto-name profile from form data
        form_data = load_json(form_path)
        name = form_data.get("name", "pastor").lower().replace(" ", "_")
        profile_path = f"profiles/{name}.md"
        cmd += ["--output", profile_path]
        returncode = run_step(cmd, "voice_profiler.py")
        if returncode != 0:
            print(f"\n  ✗  Voice profile build failed (exit {returncode})\n")
            sys.exit(1)
        current_step += 1

    if not profile_path or not os.path.exists(profile_path):
        print(f"\n  ✗  Profile not found: {profile_path}\n")
        sys.exit(1)

    # Step 2: Generate Posts
    step(current_step, total_steps, f"Generating {'1 Free Sample Post' if free_sample else '10 Posts'} (CONTENT Agent)")
    cmd = ["python", "content_agent.py", "--profile", profile_path]
    if topic:
        cmd += ["--topic", topic]
    if free_sample:
        cmd.append("--free-sample")
    returncode = run_step(cmd, "content_agent.py")
    if returncode != 0:
        print(f"\n  ✗  Content generation failed (exit {returncode})\n")
        sys.exit(1)
    current_step += 1

    # Determine sprint ID from the profile
    with open(profile_path) as f:
        profile_content = f.read()
    sprint_id_match = re.search(r"sprint_id:\s*(.+)", profile_content)
    sprint_id = sprint_id_match.group(1).strip() if sprint_id_match else "UNKNOWN"

    # Step 3: EDITOR Review
    step(current_step, total_steps, "Running EDITOR Review (Theology + Voice QA)")
    cmd = ["python", "editor_agent.py", "--sprint", sprint_id, "--profile", profile_path]
    returncode = run_step(cmd, "editor_agent.py")
    if returncode != 0:
        print(f"\n  ✗  Editor review failed (exit {returncode})\n")
        sys.exit(1)
    current_step += 1

    # Step 4: Build Delivery Doc
    step(current_step, total_steps, "Building Delivery Document")
    delivery_path = build_delivery_doc(sprint_id)
    print(f"\n  ✓  Delivery doc → {delivery_path}")

    # Final summary
    print(f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ✓  Sprint Complete — {sprint_id}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Files:
  • Voice profile:   {profile_path}
  • Raw posts:       posts/{sprint_id}/raw_posts.md
  • Editor report:   posts/{sprint_id}/editor_report.md
  • Reviewed posts:  posts/{sprint_id}/reviewed_posts.md
  • Delivery doc:    {delivery_path}

  Next:
  • Email DELIVERY.md to pastor
  • Follow up in 48 hours: "Did you like it?"
  • If yes → offer $500 Sprint upgrade or retainer

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="YAHWAYLOVE Sprint Runner")

    # Input source
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--form", type=str, help="Path to Formspree form JSON payload")
    source.add_argument("--profile", type=str, help="Path to existing pastor.md profile")

    # Options
    parser.add_argument("--topic", default="", help="Optional topic/Scripture focus")
    parser.add_argument("--free-sample", action="store_true", help="Generate 1 free sample post only")

    # Special modes
    parser.add_argument("--sprint", type=str, help="Sprint ID — use with --editor-only or --deliver")
    parser.add_argument("--editor-only", action="store_true", help="Run EDITOR pass on existing sprint")
    parser.add_argument("--deliver", action="store_true", help="Build delivery doc for existing sprint")

    args = parser.parse_args()

    if not os.getenv("ANTHROPIC_API_KEY"):
        print("\n  ✗  ANTHROPIC_API_KEY not set in .env\n")
        sys.exit(1)

    os.chdir(Path(__file__).parent)  # Always run from agents/ directory

    # Special modes
    if args.editor_only and args.sprint:
        profile_path = find_profile_for_sprint(args.sprint)
        cmd = ["python", "editor_agent.py", "--sprint", args.sprint]
        if profile_path:
            cmd += ["--profile", profile_path]
        subprocess.run(cmd)
        return

    if args.deliver and args.sprint:
        delivery_path = build_delivery_doc(args.sprint)
        print(f"\n  ✓  Delivery doc → {delivery_path}\n")
        return

    # Full pipeline
    if not args.form and not args.profile:
        parser.print_help()
        sys.exit(1)

    run_full_pipeline(
        form_path=args.form,
        profile_path=args.profile,
        topic=args.topic,
        free_sample=args.free_sample,
    )


if __name__ == "__main__":
    main()
