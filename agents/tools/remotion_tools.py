"""
Remotion Video Tools — YAHWAYLOVE CONTENT Agent
Generates faith ministry video content from text using Remotion templates.

Install: npx skills add remotion-dev/skills
Docs: https://remotion.dev

5 Production Templates:
  1. Education Explainer (30s) — faith concepts, scripture breakdowns
  2. Product Demo (25s) — ministry website / app showcase
  3. Google Reviews Testimonial (20s) — social proof from congregation
  4. Avatar + Overlays (variable) — Andrew's talking-head enhancement
  5. Data Viz Dashboard (15s) — ministry growth metrics

Usage (Python → Node subprocess):
  python remotion_tools.py --template testimonial --data testimonials.json
  python remotion_tools.py --template explainer --topic "Grace through faith"
"""

import os
import json
import subprocess
import tempfile
from pathlib import Path
from typing import Optional


REMOTION_TEMPLATES = {
    "explainer": {
        "name": "Education Explainer",
        "duration": "30s",
        "use_case": "Explain faith concepts, scripture, AI tools for ministry",
        "scenes": 5,
        "input_fields": ["title", "subtitle", "key_points", "scripture", "cta"]
    },
    "demo": {
        "name": "Product Demo",
        "duration": "25s",
        "use_case": "Showcase client ministry website or app",
        "scenes": 4,
        "input_fields": ["website_url", "headline", "features", "cta"]
    },
    "testimonial": {
        "name": "Google Reviews Testimonial",
        "duration": "20s",
        "use_case": "Social proof from congregation members",
        "scenes": 3,
        "input_fields": ["reviewer_name", "review_text", "stars", "church_name"]
    },
    "avatar": {
        "name": "Avatar + Animated Overlays",
        "duration": "variable",
        "use_case": "Enhance Andrew's talking-head content with overlays",
        "scenes": 1,
        "input_fields": ["video_file", "transcript", "name_overlay", "church_overlay"]
    },
    "dataviz": {
        "name": "Data Viz Dashboard",
        "duration": "15s",
        "use_case": "Ministry growth metrics, analytics reports",
        "scenes": 4,
        "input_fields": ["title", "kpis", "chart_data", "period"]
    }
}


def list_templates() -> None:
    """Display available Remotion templates"""
    print("\n🎬 YAHWAYLOVE Remotion Templates")
    print("=" * 50)
    for key, tmpl in REMOTION_TEMPLATES.items():
        print(f"\n[{key}] {tmpl['name']} ({tmpl['duration']})")
        print(f"  Use case: {tmpl['use_case']}")
        print(f"  Inputs: {', '.join(tmpl['input_fields'])}")


def generate_explainer_video(
    title: str,
    key_points: list,
    scripture: str = None,
    cta: str = "Visit yahwaylove.com",
    output_path: str = None
) -> dict:
    """
    Generate a 30s education explainer video.
    Ideal for: scripture breakdowns, faith concepts, ministry announcements.
    
    Args:
        title: Main topic title (e.g., "Grace Through Faith")
        key_points: 3-5 bullet points for the explainer
        scripture: Optional scripture reference (e.g., "Ephesians 2:8-9")
        cta: Call to action text for final scene
        output_path: Where to save the video file
    
    Returns:
        dict with output_path, duration, template_used
    """
    if not _check_remotion_installed():
        return _mock_video_result("explainer", title, output_path)
    
    props = {
        "title": title,
        "keyPoints": key_points[:5],  # Max 5 points
        "scripture": scripture or "",
        "cta": cta,
        "theme": "yahwaylove",  # Navy + gold design
        "brandColors": {
            "primary": "#0a0f2e",
            "accent": "#c9a227",
            "light": "#faf8f3"
        }
    }
    
    return _render_template("explainer", props, output_path)


def generate_testimonial_video(
    reviews: list,
    church_name: str,
    output_path: str = None
) -> dict:
    """
    Generate a 20s testimonial reel from congregation reviews.
    
    Args:
        reviews: List of dicts with reviewer_name, review_text, stars (1-5)
        church_name: The ministry name
        output_path: Output file path
    
    Returns:
        dict with output_path, duration, template_used
    """
    if not _check_remotion_installed():
        return _mock_video_result("testimonial", church_name, output_path)
    
    # Use top 3 reviews
    top_reviews = sorted(reviews, key=lambda r: r.get("stars", 0), reverse=True)[:3]
    
    props = {
        "reviews": top_reviews,
        "churchName": church_name,
        "theme": "yahwaylove",
        "accentColor": "#c9a227"
    }
    
    return _render_template("testimonial", props, output_path)


def generate_dataviz_video(
    title: str,
    kpis: dict,
    period: str = "Last 30 Days",
    output_path: str = None
) -> dict:
    """
    Generate a 15s animated KPI dashboard video.
    
    Args:
        title: Dashboard title (e.g., "April Ministry Growth")
        kpis: Dict of metric_name: value pairs
              e.g., {"New Members": 24, "Avg Reach": "12.4K", "Engagement Rate": "8.2%"}
        period: Time period label
        output_path: Output file path
    
    Returns:
        dict with output_path, duration, template_used
    """
    if not _check_remotion_installed():
        return _mock_video_result("dataviz", title, output_path)
    
    props = {
        "title": title,
        "kpis": kpis,
        "period": period,
        "theme": "glass",  # Glass-morphism aesthetic
        "accentColor": "#c9a227"
    }
    
    return _render_template("dataviz", props, output_path)


def _check_remotion_installed() -> bool:
    """Check if Remotion CLI is available"""
    try:
        result = subprocess.run(
            ["npx", "remotion", "--version"],
            capture_output=True, text=True, timeout=10
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def _render_template(template: str, props: dict, output_path: str = None) -> dict:
    """
    Render a Remotion template via CLI.
    Requires: npx remotion CLI + template packages installed.
    """
    import datetime
    
    if not output_path:
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = Path("../outputs/videos")
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = str(output_dir / f"{template}_{ts}.mp4")
    
    # Write props to temp file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(props, f)
        props_file = f.name
    
    try:
        cmd = [
            "npx", "remotion", "render",
            f"yahwaylove-{template}",  # Template composition name
            output_path,
            f"--props={props_file}",
            "--log=error"
        ]
        
        print(f"🎬 Rendering {REMOTION_TEMPLATES[template]['name']}...")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print(f"✅ Video rendered: {output_path}")
            return {
                "status": "success",
                "output_path": output_path,
                "template": template,
                "duration": REMOTION_TEMPLATES[template]["duration"]
            }
        else:
            print(f"⚠️  Remotion error: {result.stderr}")
            return _mock_video_result(template, str(props), output_path)
    
    except subprocess.TimeoutExpired:
        print("⚠️  Remotion render timed out (>5 min)")
        return _mock_video_result(template, str(props), output_path)
    finally:
        Path(props_file).unlink(missing_ok=True)


def _mock_video_result(template: str, title: str, output_path: str) -> dict:
    """Mock result when Remotion not installed"""
    tmpl = REMOTION_TEMPLATES.get(template, {})
    return {
        "status": "mock",
        "template": template,
        "template_name": tmpl.get("name", template),
        "duration": tmpl.get("duration", "?"),
        "title": title,
        "output_path": output_path or f"[would render to outputs/videos/{template}.mp4]",
        "note": "Install Remotion to enable video: npx skills add remotion-dev/skills",
        "docs": "https://remotion.dev"
    }


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Remotion Video Generator — YAHWAYLOVE")
    parser.add_argument("--list", action="store_true", help="List available templates")
    parser.add_argument("--template", type=str, help="Template to use")
    parser.add_argument("--topic", type=str, help="Topic for explainer template")
    args = parser.parse_args()
    
    if args.list:
        list_templates()
    elif args.template == "explainer" and args.topic:
        result = generate_explainer_video(
            title=args.topic,
            key_points=[
                f"Understanding {args.topic}",
                "What scripture says",
                "Practical application",
                "Prayer for today"
            ]
        )
        print(json.dumps(result, indent=2))
    else:
        parser.print_help()
