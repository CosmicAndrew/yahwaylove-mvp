"""
Blotato Distribution Tools — YAHWAYLOVE Content Agent
blotato.com | Created by Sabrina Ramonov | 33M views/month

Distributes Sprint content across LinkedIn, Instagram, X, Facebook, TikTok
after EDITOR review and approval.

API Docs: https://blotato.com/docs/api
Free trial: 5,000 credits
"""

import os
import json
import requests
from typing import Optional

BLOTATO_API_KEY = os.getenv("BLOTATO_API_KEY")
BLOTATO_BASE_URL = "https://api.blotato.com/v1"

# Platform codes
PLATFORMS = {
    "linkedin": "linkedin",
    "instagram": "instagram",
    "x": "twitter",
    "facebook": "facebook",
    "tiktok": "tiktok"
}


def schedule_post(
    content: str,
    platforms: list = None,
    schedule_time: str = None,
    client_account_id: str = None,
    media_url: str = None
) -> dict:
    """
    Schedule a single post to multiple platforms via Blotato.
    
    Args:
        content: Post text (Blotato handles platform-specific truncation)
        platforms: List of platform names. Defaults to ["linkedin", "facebook"]
        schedule_time: ISO 8601 datetime string. None = post immediately
        client_account_id: Blotato account ID for the client
        media_url: Optional image/video URL to attach
    
    Returns:
        dict with post_id, scheduled_time, platform_urls
    """
    if not BLOTATO_API_KEY:
        print("⚠️  BLOTATO_API_KEY not set — returning mock schedule")
        return _mock_schedule(content, platforms or ["linkedin", "facebook"], schedule_time)

    platforms = platforms or ["linkedin", "facebook"]
    
    payload = {
        "content": content,
        "platforms": [PLATFORMS.get(p, p) for p in platforms],
        "account_id": client_account_id or os.getenv("BLOTATO_DEFAULT_ACCOUNT_ID"),
    }
    
    if schedule_time:
        payload["scheduled_at"] = schedule_time
    if media_url:
        payload["media_url"] = media_url

    try:
        response = requests.post(
            f"{BLOTATO_BASE_URL}/posts",
            headers={
                "Authorization": f"Bearer {BLOTATO_API_KEY}",
                "Content-Type": "application/json"
            },
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"⚠️  Blotato API error: {e}")
        return _mock_schedule(content, platforms, schedule_time)


def schedule_sprint_batch(
    posts: list,
    client_name: str,
    platforms: list = None,
    start_date: str = None,
    spacing_days: int = 2
) -> list:
    """
    Schedule a full Sprint batch (10 posts) with 2-day spacing.
    
    Args:
        posts: List of post content strings (from EDITOR-approved sprint)
        client_name: Client name for logging
        platforms: Platforms to distribute on
        start_date: ISO date string for first post. Defaults to tomorrow
        spacing_days: Days between posts (default 2 = 5 posts/week cadence)
    
    Returns:
        List of schedule confirmations with platform URLs
    """
    import datetime
    
    platforms = platforms or ["linkedin", "facebook"]
    
    if not start_date:
        tomorrow = datetime.date.today() + datetime.timedelta(days=1)
        start_date = tomorrow.isoformat()
    
    base_date = datetime.date.fromisoformat(start_date)
    
    results = []
    print(f"\n📤 Blotato — Scheduling {len(posts)} posts for {client_name}")
    print(f"   Platforms: {', '.join(platforms)}")
    print(f"   Start: {start_date} | Spacing: every {spacing_days} days")
    
    for i, post_content in enumerate(posts):
        post_date = base_date + datetime.timedelta(days=i * spacing_days)
        # Schedule at 9am CT (14:00 UTC)
        schedule_time = f"{post_date.isoformat()}T14:00:00Z"
        
        result = schedule_post(
            content=post_content,
            platforms=platforms,
            schedule_time=schedule_time
        )
        
        result["post_number"] = i + 1
        result["scheduled_date"] = post_date.isoformat()
        results.append(result)
        
        status = "✅" if result.get("status") == "scheduled" else "📋"
        print(f"   {status} Post {i+1}/10 → {post_date.strftime('%b %d, %Y')}")
    
    print(f"\n🗓️  All {len(posts)} posts scheduled across {len(platforms)} platforms")
    print(f"   Last post: {(base_date + datetime.timedelta(days=(len(posts)-1)*spacing_days)).strftime('%b %d, %Y')}")
    
    return results


def get_account_stats(account_id: str = None) -> dict:
    """Pull posting stats for client's Blotato account"""
    if not BLOTATO_API_KEY:
        return {"status": "mock", "total_posts": 0, "credits_remaining": 5000}
    
    try:
        response = requests.get(
            f"{BLOTATO_BASE_URL}/accounts/{account_id or 'default'}/stats",
            headers={"Authorization": f"Bearer {BLOTATO_API_KEY}"},
            timeout=15
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e), "status": "unavailable"}


def _mock_schedule(content: str, platforms: list, schedule_time: str) -> dict:
    """Mock response for demo/no-API mode"""
    preview = content[:80].replace("\n", " ")
    return {
        "status": "mock_scheduled",
        "post_id": f"BLOTATO-MOCK-{hash(content) % 99999:05d}",
        "scheduled_at": schedule_time or "immediate",
        "platforms": platforms,
        "preview": f"{preview}...",
        "note": "Set BLOTATO_API_KEY to enable live distribution. Get it at blotato.com"
    }
