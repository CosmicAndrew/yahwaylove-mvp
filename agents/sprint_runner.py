"""
sprint_runner.py — YAHWAYLOVE Faith Content Sprint Orchestrator
===============================================================
End-to-end pipeline: intake form → voice profile → 10 posts → EDITOR review
→ Blotato distribution → delivery doc.

This is the single command Andrew runs after receiving a Formspree submission.

Usage:
    # Full pipeline from a form submission JSON:
    python sprint_runner.py --form form_payload.json

    # Full pipeline + auto-schedule to Blotato:
    python sprint_runner.py --form form_payload.json --distribute

    # Full pipeline from an existing profile:
    python sprint_runner.py --profile profiles/john_smith.md --topic "fear vs faith"

    # Free sample only (for the Free Sample Close):
    python sprint_runner.py --form form_payload.json --free-sample

    # Batch free samples from SCOUT prospect list:
    python sprint_runner.py --batch-scout ../raw/prospect_list.json --free-sample

    # Just run the editor pass on an existing sprint:
    python sprint_runner.py --sprint SPRINT-2026-04-19-JS --editor-only

    # After review — package delivery doc:
    python sprint_runner.py --sprint SPRINT-2026-04-19-JS --deliver

    # Distribute approved posts via Blotato:
    python sprint_runner.py --sprint SPRINT-2026-04-19-JS --distribute

Requirements:
    pip install anthropic python-dotenv requests
    ANTHROPIC_API_KEY in agents/.env
    BLOTATO_API_KEY in agents/.env (optional — for distribution)
"""

import argparse
import json
import os
import re
import sys
import subprocess
from datetime import datetime, date, timedelta
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Import distribution tools
sys.path.insert(0, str(Path(__file__).parent / "tools"))
try:
    from blotato_tools import schedule_sprint_batch
    BLOTATO_AVAILABLE = True
except ImportError:
    BLOTATO_AVAILABLE = False

try:
    from remotion_tools import generate_explainer_video, generate_testimonial_video
    REMOTION_AVAILABLE = True
except ImportError:
    REMOTION_AVAILABLE = False


# ── Pipeline steps ────────────────────────────────────────────────────────────

def step(num: int, total: int, label: str) -> None:
    print(f"\n  [{num}/{total}] {label}")
    print(f"  {'─' * 44}")


def run_step(cmd: list, label: str) -> int:
    """Run a subprocess step and stream its output."""
    result = subprocess.run(cmd, capture_output=False)
    return result.returncode


def load_json(path: str) -> dict:
    with open(path) as f:
        return json.load(f)


def find_profile_for_sprint(sprint_id: str) -> str | None:
    """Try to locate the pastor.md that was used for this sprint."""
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


def extract_posts_from_sprint(sprint_id: str) -> list:
    """Extract individual post texts from reviewed_posts.md"""
    reviewed = Path(f"posts/{sprint_id}/reviewed_posts.md")
    if not reviewed.exists():
        return []

    content = reviewed.read_text()

    # Split by post markers (## Post N: or --- separators)
    posts = []
    post_blocks = re.split(r"(?:^## Post \d+|^---)", content, flags=re.MULTILINE)
    for block in post_blocks:
        block = block.strip()
        if len(block) > 50:  # Filter out headers/empty blocks
            posts.append(block)

    return posts


def distribute_sprint(sprint_id: str, platforms: list = None, start_date: str = None) -> list:
    """
    Distribute an approved sprint via Blotato.

    Args:
        sprint_id: Sprint ID (e.g., SPRINT-2026-04-19-JS)
        platforms: List of platforms (default: linkedin, facebook)
        start_date: ISO date for first post (default: tomorrow)

    Returns:
        List of Blotato schedule confirmations
    """
    if not BLOTATO_AVAILABLE:
        print("  ⚠️  Blotato tools not available — check tools/blotato_tools.py")
        return []

    posts = extract_posts_from_sprint(sprint_id)
    if not posts:
        print(f"  ⚠️  No posts found in {sprint_id} — run editor pass first")
        return []

    # Get client name from intake summary
    summary = Path(f"posts/{sprint_id}/intake_summary.md")
    client_name = "Ministry"
    if summary.exists():
        content = summary.read_text()
        name_match = re.search(r"\*\*Pastor:\*\*\s*(.+)", content)
        if name_match:
            client_name = name_match.group(1).strip()

    if not start_date:
        start_date = (date.today() + timedelta(days=1)).isoformat()

    print(f"\n  📤 Distributing via Blotato — {client_name}")
    results = schedule_sprint_batch(
        posts=posts,
        client_name=client_name,
        platforms=platforms or ["linkedin", "facebook"],
        start_date=start_date
    )

    # Save distribution log
    sprint_dir = Path(f"posts/{sprint_id}")
    log_path = sprint_dir / "blotato_schedule.json"
    with open(log_path, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\n  💾 Distribution log → {log_path}")
    return results


def build_delivery_doc(sprint_id: str, blotato_results: list = None) -> str:
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

    # Extract pastor name from intake summary
    pastor_name = "Pastor"
    if summary.exists():
        content = summary.read_text()
        name_match = re.search(r"\*\*Pastor:\*\*\s*(.+)", content)
        if name_match:
            pastor_name = name_match.group(1).strip()

    reviewed_content = reviewed.read_text()
    timestamp = datetime.now().strftime("%B %d, %Y")

    # Build distribution section
    distribution_section = ""
    if blotato_results:
        scheduled_platforms = set()
        for r in blotato_results:
            scheduled_platforms.update(r.get("platforms", []))
        first_post = min(blotato_results, key=lambda x: x.get("scheduled_date", ""))
        last_post = max(blotato_results, key=lambda x: x.get("scheduled_date", ""))
        distribution_section = f"""
---

**✅ Distribution Scheduled via Blotato:**
Your posts are already queued for distribution across:
{', '.join(p.title() for p in scheduled_platforms)}

Schedule: {first_post.get('scheduled_date', '?')} → {last_post.get('scheduled_date', '?')}
(2-day spacing for optimal reach — posts go live at 9am CT)

"""
    else:
        distribution_section = """
---

**Want us to post these for you?**
Reply "Schedule them" and we'll distribute across Facebook, Instagram, and LinkedIn
automatically via Blotato — 2-day spacing, posted at peak engagement times.

"""

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
{distribution_section}
---

If you want to continue with a monthly plan (10 posts every month, plus Meta Ads,
web updates, and more), reply "Let's talk" and we'll schedule a 20-minute call.

Either way — these posts are yours. Use them however serves your ministry.

— Andrew Rocha
YAHWAYLOVE LLC | rocha@yahwaylove.com | (561) 305-0404 | Fort Worth, TX
yahwaylove.com/sprint

_Romans 3:23_
"""

    delivery_path = sprint_dir / "DELIVERY.md"
    with open(delivery_path, "w") as f:
        f.write(delivery_doc)

    return str(delivery_path)


def run_batch_scout(prospect_file: str, free_sample: bool = True) -> None:
    """
    Run free sample generation for top prospects from SCOUT output.
    Generates 1 post per high-priority prospect for the Free Sample Close.
    """
    if not os.path.exists(prospect_file):
        print(f"  ✗  Prospect file not found: {prospect_file}")
        sys.exit(1)

    with open(prospect_file) as f:
        prospects = json.load(f)

    # Filter HIGH priority prospects
    high_priority = [
        p for p in prospects
        if p.get("priority") == "HIGH" or p.get("score", 0) >= 7
    ][:10]  # Max 10 per batch

    print(f"\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"  YAHWAYLOVE — Batch Free Sample Close")
    print(f"  {len(high_priority)} high-priority prospects from SCOUT")
    print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    for i, prospect in enumerate(high_priority):
        print(f"\n  [{i+1}/{len(high_priority)}] {prospect.get('name')} — {prospect.get('church')}")

        # Build a minimal form.json from prospect data
        form_data = {
            "name": prospect.get("name", "Pastor"),
            "church": prospect.get("church", "Ministry"),
            "email": prospect.get("email", ""),
            "topic": prospect.get("recommended_topic", "faith and perseverance"),
            "style": prospect.get("voice_signals", {}).get("tone", "Conversational & warm"),
            "location": prospect.get("location", ""),
            "website": prospect.get("linkedin_url", ""),
            "niche": prospect.get("niche", "adult congregation"),
            "_scout_notes": prospect.get("sample_voice", "")
        }

        # Write temp form file
        form_path = f"_scout_form_{i+1}.json"
        with open(form_path, "w") as f:
            json.dump(form_data, f, indent=2)

        # Run pipeline (free sample mode)
        run_full_pipeline(
            form_path=form_path,
            free_sample=True
        )

        # Cleanup temp form
        Path(form_path).unlink(missing_ok=True)

        # Update prospect status
        prospect["status"] = "sample_generated"
        prospect["sample_date"] = date.today().isoformat()

    # Save updated prospect list
    with open(prospect_file, "w") as f:
        json.dump(prospects, f, indent=2)

    print(f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ✓  Batch Complete — {len(high_priority)} free samples generated
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Next: Send each sample via LinkedIn DM:
  "We wrote this for your church. Post it if you like it."

  Then follow up in 48 hours:
  "Did it resonate? The $500 Sprint delivers 9 more."
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")


# ── Full pipeline ─────────────────────────────────────────────────────────────

def run_full_pipeline(
    form_path: str | None = None,
    profile_path: str | None = None,
    topic: str = "",
    free_sample: bool = False,
    distribute: bool = False,
    platforms: list = None,
) -> None:
    """
    Run the complete Sprint pipeline:
    1. Build voice profile (if form provided)
    2. Generate posts via CONTENT agent
    3. Run EDITOR review
    4. Distribute via Blotato (if --distribute)
    5. Build delivery doc
    """
    total_steps = 4 if (profile_path or free_sample) else 5
    if distribute:
        total_steps += 1

    print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("  YAHWAYLOVE — Faith Content Sprint Runner")
    print(f"  Mode: {'Free Sample (1 post)' if free_sample else '10-post Sprint'}")
    if distribute:
        print(f"  + Blotato distribution: {', '.join(platforms or ['linkedin', 'facebook'])}")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    current_step = 1

    # Step 1: Voice Profile (skip if profile already provided)
    if form_path and not profile_path:
        step(current_step, total_steps, "Building Voice Profile")
        cmd = ["python", "voice_profiler.py", "--from-form", form_path]
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

    # Step 4: Blotato Distribution (optional)
    blotato_results = []
    if distribute and not free_sample:
        step(current_step, total_steps, "Distributing via Blotato")
        blotato_results = distribute_sprint(sprint_id, platforms=platforms)
        current_step += 1

    # Step 5: Build Delivery Doc
    step(current_step, total_steps, "Building Delivery Document")
    delivery_path = build_delivery_doc(sprint_id, blotato_results=blotato_results)
    print(f"\n  ✓  Delivery doc → {delivery_path}")

    # Final summary
    dist_note = ""
    if distribute and blotato_results:
        dist_note = f"\n  • Blotato schedule: posts/{sprint_id}/blotato_schedule.json"
    elif not distribute:
        dist_note = f"\n  • To distribute: python sprint_runner.py --sprint {sprint_id} --distribute"

    print(f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ✓  Sprint Complete — {sprint_id}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Files:
  • Voice profile:   {profile_path}
  • Raw posts:       posts/{sprint_id}/raw_posts.md
  • Editor report:   posts/{sprint_id}/editor_report.md
  • Reviewed posts:  posts/{sprint_id}/reviewed_posts.md
  • Delivery doc:    {delivery_path}{dist_note}

  Next:
  • Email DELIVERY.md to pastor
  • Follow up in 48 hours: "Did you like it?"
  • If yes → offer $500 Sprint upgrade or retainer

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="YAHWAYLOVE Sprint Runner — Faith Content Sprint Pipeline"
    )

    # Input source
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--form", type=str, help="Path to Formspree form JSON payload")
    source.add_argument("--profile", type=str, help="Path to existing pastor.md profile")
    source.add_argument("--batch-scout", type=str, help="Path to SCOUT prospect_list.json for batch free samples")

    # Options
    parser.add_argument("--topic", default="", help="Optional topic/Scripture focus")
    parser.add_argument("--free-sample", action="store_true", help="Generate 1 free sample post only")
    parser.add_argument("--distribute", action="store_true", help="Schedule approved posts via Blotato")
    parser.add_argument("--platforms", nargs="+", default=["linkedin", "facebook"],
                        help="Platforms for Blotato distribution (default: linkedin facebook)")
    parser.add_argument("--start-date", type=str, help="ISO date for first distributed post (YYYY-MM-DD)")

    # Special modes
    parser.add_argument("--sprint", type=str, help="Sprint ID — use with --editor-only, --deliver, or --distribute")
    parser.add_argument("--editor-only", action="store_true", help="Run EDITOR pass on existing sprint")
    parser.add_argument("--deliver", action="store_true", help="Build delivery doc for existing sprint")

    args = parser.parse_args()

    if not os.getenv("ANTHROPIC_API_KEY"):
        print("\n  ✗  ANTHROPIC_API_KEY not set in .env\n")
        print("  Add your Anthropic API key to agents/.env:")
        print("  ANTHROPIC_API_KEY=sk-ant-...\n")
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

    if args.distribute and args.sprint:
        results = distribute_sprint(
            args.sprint,
            platforms=args.platforms,
            start_date=args.start_date
        )
        if results:
            print(f"\n  ✓  {len(results)} posts scheduled via Blotato\n")
        return

    # Batch SCOUT mode
    if args.batch_scout:
        run_batch_scout(args.batch_scout, free_sample=True)
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
        distribute=args.distribute,
        platforms=args.platforms,
    )


if __name__ == "__main__":
    main()
