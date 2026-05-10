"""
SCOUT — YAHWAYLOVE Discovery Agent
Grok Multi-Agent Architecture: finds inconsistent faith posters for the Free Sample Close GTM

Usage:
  python scout_agent.py --analyze --prospect https://linkedin.com/in/pastorjames
  python scout_agent.py --run --limit 20 --niche "youth ministry"
  python scout_agent.py --list  # show current prospect list

Dependencies:
  pip install openai requests python-dotenv

API Keys needed:
  GROK_API_KEY — SuperGrok ($30/mo) for real-time search
  DEEPSEEK_API_KEY or OPENAI_API_KEY — for voice signal extraction + scoring
"""

import os
import json
import argparse
import datetime
import sys
from pathlib import Path

from dotenv import load_dotenv

try:
    from .llm_client import LLMConfigError, generate_text, require_llm_credentials
except ImportError:
    from llm_client import LLMConfigError, generate_text, require_llm_credentials

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Always run from agents/ directory
os.chdir(Path(__file__).parent)
load_dotenv()

GROK_API_KEY = os.getenv("GROK_API_KEY")

# ============================================
# GROK MULTI-AGENT SEARCH
# Harper (web search) + Benjamin (fact checker) + Grok (orchestrator)
# Pattern: Ruben Hassid, SuperGrok $30/mo
# ============================================

HARPER_SYSTEM = """
You are Harper, a web and social media intelligence specialist.
Your job: find faith leaders on LinkedIn and Facebook who post inconsistently (< 2x/week).

Search criteria:
- Faith leader: pastor, ministry director, church admin, faith-led business owner
- Public profile with > 500 followers
- Posts < 2x per week (< 8 posts in last 30 days)
- Last post within 30 days (still active)

Return a JSON array of prospects with: name, platform_url, estimated_followers, 
last_post_date, posts_last_30_days, sample_voice_notes, location, organization.
"""

BENJAMIN_SYSTEM = """
You are Benjamin, a fact-checker and data verifier.
Given a prospect found by Harper, verify:
1. The profile is real and active
2. The posting frequency claim is accurate
3. The contact information is current
4. The organization name matches the profile

Flag any prospect that looks like a bot, inactive account, or private profile.
Return: verified (true/false), confidence (0-10), notes.
"""

SCOUT_SCORING_PROMPT = """
Score this prospect for the YAHWAYLOVE Free Sample Close on a scale of 1-10.

Scoring criteria:
- 10: Large audience (>5K), very inconsistent (< 1 post/week), strong voice signals, warm niche
- 7-9: Medium audience (1K-5K), inconsistent, clear voice identifiable
- 4-6: Small audience (<1K) or hard-to-identify voice
- 1-3: Private profile, no clear faith angle, or abandoned account

Also extract voice signals from their public posts:
- Tone (formal/casual/warm/academic)
- Common phrases or pet words they use
- Scripture style (quotes directly vs. paraphrases)
- Signature sign-offs
- Content themes (hope, community, missions, family, etc.)

Return JSON: { "score": 8.5, "priority": "HIGH", "voice_signals": {...}, "recommended_topic": "..." }
"""


def analyze_prospect(linkedin_url: str) -> dict:
    """
    Analyze a single prospect from their public LinkedIn URL.
    Extracts voice signals and scores them for Free Sample Close priority.
    """
    try:
        require_llm_credentials()
    except LLMConfigError:
        print("⚠️  DEEPSEEK_API_KEY or OPENAI_API_KEY not set — returning mock analysis for demo")
        return _mock_prospect_analysis(linkedin_url)

    try:
        raw = generate_text(
            prompt=f"""Analyze this LinkedIn profile for the YAHWAYLOVE Free Sample Close:
URL: {linkedin_url}

Since you cannot browse URLs directly, provide a template analysis that Andrew can fill in
after visiting the profile manually. Structure it exactly as the SCOUT output format.

{SCOUT_SCORING_PROMPT}

Return valid JSON only.""",
            max_tokens=2048,
        )

        raw = raw.strip()
        # Extract JSON from response
        if "```json" in raw:
            raw = raw.split("```json")[1].split("```")[0].strip()
        elif "```" in raw:
            raw = raw.split("```")[1].split("```")[0].strip()

        analysis = json.loads(raw)
        analysis["linkedin_url"] = linkedin_url
        analysis["scout_date"] = datetime.date.today().isoformat()
        analysis["status"] = "pending_outreach"
        return analysis

    except Exception as e:
        print(f"⚠️  Analysis error: {e} — returning template")
        return _mock_prospect_analysis(linkedin_url)


def _mock_prospect_analysis(url: str) -> dict:
    """Template for manual Scout (no API keys needed)"""
    return {
        "prospect_id": f"P-{datetime.date.today().isoformat()}-MANUAL",
        "linkedin_url": url,
        "name": "[Fill in: Pastor Name]",
        "church": "[Fill in: Church/Organization]",
        "location": "[Fill in: City, State]",
        "followers": 0,
        "last_post_date": "[Fill in: YYYY-MM-DD]",
        "posts_last_30_days": 0,
        "score": 0,
        "priority": "[Fill in: HIGH/MEDIUM/LOW]",
        "voice_signals": {
            "tone": "[Fill in: formal/casual/warm/academic]",
            "common_phrases": ["[phrase 1]", "[phrase 2]"],
            "scripture_style": "[Fill in: direct quotes vs paraphrase]",
            "themes": ["[theme 1]", "[theme 2]"],
            "signature": "[Fill in: how they sign off]"
        },
        "recommended_topic": "[Fill in: based on their recent content themes]",
        "sample_voice": "[Fill in: 2-3 sentence description of their writing voice]",
        "niche": "[Fill in: youth/adult/missions/family/etc]",
        "scout_date": datetime.date.today().isoformat(),
        "status": "pending_outreach",
        "notes": "Manual SCOUT entry — fill in fields after visiting profile"
    }


def run_scout(limit: int = 10, niche: str = None) -> list:
    """
    Full automated SCOUT run using Grok multi-agent search.
    Requires GROK_API_KEY (SuperGrok $30/mo).
    Falls back to manual template list if not available.
    """
    if not GROK_API_KEY:
        print("⚠️  GROK_API_KEY not set")
        print("   Get SuperGrok at x.com/premium — $30/mo gives full API access")
        print("   Falling back to manual prospect template...")
        return _generate_manual_scout_template(limit)

    print(f"🔍 SCOUT running — Grok multi-agent search ({limit} prospects, niche: {niche or 'all faith'})")
    print("   Harper scanning LinkedIn + Facebook...")
    print("   Benjamin fact-checking...")

    # Grok API call (xAI API — same interface as OpenAI)
    import requests

    headers = {
        "Authorization": f"Bearer {GROK_API_KEY}",
        "Content-Type": "application/json"
    }

    niche_filter = f" specializing in {niche}" if niche else ""
    search_prompt = f"""
    Using Harper and Benjamin agents, find {limit} faith leaders{niche_filter} on LinkedIn 
    who post less than twice per week. They should have >500 followers and be active 
    within the last 30 days.

    For each prospect, provide:
    - Full name and title
    - Church/organization name
    - LinkedIn URL (if publicly discoverable)
    - Estimated follower count
    - Approximate posting frequency
    - Voice description (tone, themes, writing style from public posts)
    - Priority score (1-10) for YAHWAYLOVE Free Sample Close outreach

    Return as JSON array. Prioritize accounts where the voice is clearly identifiable
    from public posts — these are the best candidates for a personalized free sample.
    """

    payload = {
        "model": "grok-3",
        "messages": [
            {"role": "system", "content": HARPER_SYSTEM},
            {"role": "user", "content": search_prompt}
        ],
        "max_tokens": 4096,
        "temperature": 0.3
    }

    try:
        response = requests.post(
            "https://api.x.ai/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=60
        )
        response.raise_for_status()
        result = response.json()
        content = result["choices"][0]["message"]["content"]

        # Extract JSON
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()

        prospects = json.loads(content)
        print(f"✅ Found {len(prospects)} prospects via Grok multi-agent search")
        return prospects

    except Exception as e:
        print(f"⚠️  Grok search error: {e}")
        return _generate_manual_scout_template(limit)


def _generate_manual_scout_template(limit: int) -> list:
    """Generate blank prospect templates for manual SCOUT"""
    templates = []
    for i in range(min(limit, 10)):
        templates.append({
            "prospect_id": f"P-{datetime.date.today().isoformat()}-{i+1:03d}",
            "name": f"[Prospect {i+1}: Fill in name]",
            "church": "[Fill in organization]",
            "location": "[City, State]",
            "linkedin_url": "[Fill in LinkedIn URL]",
            "followers": 0,
            "last_post_date": "[YYYY-MM-DD]",
            "posts_last_30_days": 0,
            "score": 0,
            "priority": "PENDING",
            "voice_signals": {},
            "recommended_topic": "[Fill in after reviewing their content]",
            "scout_date": datetime.date.today().isoformat(),
            "status": "pending_review"
        })
    return templates


def save_prospects(prospects: list, output_path: str = None) -> str:
    """Save prospects to raw/prospect_list.json"""
    if not output_path:
        raw_dir = Path("../raw")
        raw_dir.mkdir(exist_ok=True)
        output_path = str(raw_dir / "prospect_list.json")

    # Load existing prospects if file exists
    existing = []
    if Path(output_path).exists():
        with open(output_path) as f:
            existing = json.load(f)

    # Merge, avoiding duplicates by URL
    existing_urls = {p.get("linkedin_url") for p in existing}
    new_prospects = [p for p in prospects if p.get("linkedin_url") not in existing_urls]

    all_prospects = existing + new_prospects

    # Sort by score descending
    all_prospects.sort(key=lambda x: x.get("score", 0), reverse=True)

    with open(output_path, "w") as f:
        json.dump(all_prospects, f, indent=2)

    print(f"💾 Saved {len(all_prospects)} prospects → {output_path}")
    print(f"   {len(new_prospects)} new | {len(existing)} existing")
    return output_path


def list_prospects(status_filter: str = None) -> None:
    """Display current prospect list"""
    prospect_file = Path("../raw/prospect_list.json")
    if not prospect_file.exists():
        print("No prospects found. Run: python scout_agent.py --run")
        return

    with open(prospect_file) as f:
        prospects = json.load(f)

    if status_filter:
        prospects = [p for p in prospects if p.get("status") == status_filter]

    print(f"\n{'='*60}")
    print(f"SCOUT — Prospect List ({len(prospects)} total)")
    print(f"{'='*60}")
    for p in prospects[:20]:  # Show top 20
        score = p.get("score", "?")
        priority = p.get("priority", "?")
        status = p.get("status", "?")
        print(f"\n[{priority}] Score: {score}/10 | {p.get('name', '?')}")
        print(f"  Church: {p.get('church', '?')}")
        print(f"  Location: {p.get('location', '?')}")
        print(f"  URL: {p.get('linkedin_url', '?')}")
        print(f"  Posts/30d: {p.get('posts_last_30_days', '?')} | Status: {status}")
        if p.get("recommended_topic"):
            print(f"  Topic: {p.get('recommended_topic')}")


# ============================================
# CLI
# ============================================

def main():
    parser = argparse.ArgumentParser(
        description="SCOUT — YAHWAYLOVE Discovery Agent (Grok Multi-Agent)"
    )
    parser.add_argument("--analyze", action="store_true", help="Analyze a single prospect")
    parser.add_argument("--prospect", type=str, help="LinkedIn URL to analyze")
    parser.add_argument("--run", action="store_true", help="Run full automated SCOUT")
    parser.add_argument("--limit", type=int, default=10, help="Max prospects to find")
    parser.add_argument("--niche", type=str, help="Focus niche (youth, missions, adult, etc.)")
    parser.add_argument("--list", action="store_true", help="List current prospects")
    parser.add_argument("--status", type=str, help="Filter by status (pending_outreach, contacted, converted)")
    args = parser.parse_args()

    if args.list:
        list_prospects(args.status)
        return

    if args.analyze:
        if not args.prospect:
            print("Error: --prospect [URL] required with --analyze")
            return
        print(f"\n🔍 Analyzing: {args.prospect}")
        analysis = analyze_prospect(args.prospect)
        print(json.dumps(analysis, indent=2))
        # Auto-save to prospect list
        save_prospects([analysis])
        print(f"\n→ Run content agent to generate free sample:")
        print(f"  python sprint_runner.py --prospect {args.prospect} --free-sample")
        return

    if args.run:
        print(f"\n🚀 SCOUT — Starting Grok multi-agent discovery run")
        print(f"   Limit: {args.limit} | Niche: {args.niche or 'all faith'}")
        prospects = run_scout(limit=args.limit, niche=args.niche)
        output = save_prospects(prospects)

        # Show top prospects
        high_priority = [p for p in prospects if p.get("priority") == "HIGH" or p.get("score", 0) >= 7]
        print(f"\n🎯 Top prospects for Free Sample Close: {len(high_priority)}")
        for p in high_priority[:5]:
            print(f"   [{p.get('score', '?')}/10] {p.get('name')} — {p.get('church')}")
        print(f"\n→ Next: generate free sample posts for top prospects:")
        print(f"  python sprint_runner.py --batch-scout {output} --free-sample")
        return

    parser.print_help()


if __name__ == "__main__":
    main()
