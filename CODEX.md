# CODEX.md — YAHWAYLOVE MVP
> OpenAI Codex CLI reads this file for task context. Contains codebase map, implementation patterns, and task instructions.

---

## Project

**YAHWAYLOVE LLC** — Faith-First AI Marketing Agency  
**Repo:** https://github.com/CosmicAndrew/yahwaylove-mvp  
**Branch:** main | **Latest commit:** `9bf1c65`  
**Stack:** Vanilla HTML/CSS/JS (frontend) + Python agents (backend automation)  
**Hosting:** Vercel (auto-deploy on push to main)

---

## Codebase Patterns

### Frontend
- Pure HTML5 + CSS custom properties + vanilla JS — no build step required
- Design tokens in `css/tokens.css` — always use tokens, never hardcode colors
- Dark mode via `data-theme="dark"` on `<html>` — toggle in `js/main.js`
- All pages link to `../css/tokens.css`, `../css/base.css`, `../css/components.css` (except index.html which uses `css/` directly)
- Logo is inline SVG — copy from `logo.svg`, embed directly in `<nav>` and `<footer>`
- Formspree form ID: `xwpbbzvy` — used in `contact.html` and `sprint.html`

### Python Agents
- All agents live in `agents/` — always `cd agents` before running
- Each agent uses `os.chdir(Path(__file__).parent)` for relative path resolution
- Environment variables loaded via `python-dotenv` from `agents/.env`
- Copy `agents/.env.example` → `agents/.env` and fill keys before running
- Models: `claude-opus-4-7` (quality tasks), `claude-sonnet-4-6` (speed tasks)
- Grok Scout uses OpenAI-compatible interface at `https://api.x.ai/v1/chat/completions`
- Higgsfield CLI is the primary video generation tool (replaces standalone MuAPI for video)

### Key Design Tokens
```css
--color-navy:  #0a0f2e;   /* primary background */
--color-gold:  #c9a227;   /* accent, CTAs */
--color-cream: #faf8f3;   /* text on dark, light bg */
```

---

## Implementation Tasks

### 1. Add `higgsfield_tools.py` (Priority: HIGH)
MuAPI is now also integrated with Higgsfield CLI for video generation. Create `agents/tools/higgsfield_tools.py`:

```python
"""
Higgsfield CLI — AI video generation tool
Primary video generation interface (extends/replaces MuAPI standalone usage)
Endpoint: https://api.higgsfield.ai (check higgsfield.ai/docs for latest)
Auth: Bearer HIGGSFIELD_API_KEY
"""
import os, requests
from pathlib import Path

HIGGSFIELD_API_KEY = os.getenv("HIGGSFIELD_API_KEY")
BASE_URL = "https://api.higgsfield.ai"  # verify at higgsfield.ai/docs

def generate_ministry_video(prompt: str, style: str = "cinematic", duration: int = 15) -> dict:
    """Generate a ministry/church promotional video via Higgsfield CLI."""
    headers = {"Authorization": f"Bearer {HIGGSFIELD_API_KEY}", "Content-Type": "application/json"}
    payload = {"prompt": prompt, "style": style, "duration": duration}
    resp = requests.post(f"{BASE_URL}/v1/generate", json=payload, headers=headers)
    resp.raise_for_status()
    return resp.json()

def generate_sermon_highlight(transcript: str, duration: int = 30) -> dict:
    """Turn a sermon transcript snippet into a shareable highlight video."""
    prompt = f"Faith-focused highlight video. Sermon excerpt: {transcript[:500]}"
    return generate_ministry_video(prompt, style="testimonial", duration=duration)

def generate_scripture_reel(scripture: str, verse_ref: str) -> dict:
    """Generate an Instagram Reel-style scripture card video."""
    prompt = f"Scripture reel: '{scripture}' — {verse_ref}. Visual: warm, worshipful, clean typography."
    return generate_ministry_video(prompt, style="kinetic_text", duration=15)
```

Add `HIGGSFIELD_API_KEY=` to `agents/.env.example`.

---

### 2. Wire `ANTHROPIC_API_KEY` (Priority: CRITICAL)
Once the key is obtained, add to `agents/.env`:
```
ANTHROPIC_API_KEY=sk-ant-...
```
Test with:
```bash
cd agents
python -c "from anthropic import Anthropic; c = Anthropic(); print(c.messages.create(model='claude-sonnet-4-6', max_tokens=10, messages=[{'role':'user','content':'ping'}]).content)"
```

---

### 3. Ministry DNA Scanner Enhancement
File: `pages/sprint.html`  
The scanner is client-side JS — no API needed. Current flow: URL input → fake "scanning" animation → 6 content idea cards.

**Proposed upgrade:** After scan, show a "Brand Voice Preview" section with:
- Detected denomination style (Catholic/Evangelical/Pentecostal/Non-denom)
- Suggested content pillars (3 topics)
- Sample post preview (1 generated example using hardcoded templates)

This keeps it demo-ready with zero API dependency.

---

### 4. Blotato Distribution Integration
File: `agents/tools/blotato_tools.py`  
Key function: `schedule_sprint_batch(posts: list, start_date: str)`  
- Schedules 10 posts at 2-day intervals, 9am CT (14:00 UTC)
- Requires `BLOTATO_API_KEY` in `.env`
- Get free trial at blotato.com (5K credits)

---

### 5. Grok Scout Agent
File: `agents/scout_agent.py`  
Uses `api.x.ai` — OpenAI-compatible endpoint.  
Sub-agents:
- **Harper** → researches individual church/ministry prospects
- **Benjamin** → analyzes faith content trends on X/social

```bash
cd agents
python scout_agent.py --run "Grace Community Church Fort Worth"
python scout_agent.py --analyze
```

---

## Running the Full Sprint Pipeline

```bash
# Prerequisites
cd agents
cp .env.example .env
# Fill ANTHROPIC_API_KEY in .env

# Free sample (1 post — for outreach)
python sprint_runner.py --free-sample

# Full sprint (10 posts)
python sprint_runner.py

# Full sprint + auto-distribute via Blotato
python sprint_runner.py --distribute

# Full sprint + prospect research
python sprint_runner.py --batch-scout
```

---

## Frontend Dev Server

No build step needed. Open directly:
```bash
# macOS
open yahwaylove/index.html

# or serve locally
python -m http.server 8080 --directory yahwaylove
# then visit http://localhost:8080
```

---

## Deploy

Vercel auto-deploys on push to `main`. To force deploy:
```bash
git add -A && git commit -m "your message" && git push origin main
```

---

## Commit History

```
9bf1c65  feat: real logo SVG + business model audit fixes
b48435d  feat: better tools integration — Blotato, Grok SCOUT, Remotion, Canopy OS, ShipClaw
9b54933  feat: Ministry DNA Scanner + Content Ideation Board (Google Labs mirror)
4df21ed  feat: CONTENT agent stack — voice profiler, post generator, editor QA, sprint runner
dd9195c  tighten: training camp phases, 7 self-study tier, AGENT_ARCHITECTURE GTM overhaul
2dd90bb  feat: hero/sprint restructure
```

---

## Key External Endpoints

| Service | Endpoint | Auth |
|---|---|---|
| Anthropic | `https://api.anthropic.com/v1/messages` | `x-api-key: ANTHROPIC_API_KEY` |
| Grok/xAI | `https://api.x.ai/v1/chat/completions` | `Bearer GROK_API_KEY` |
| Blotato | `https://api.blotato.com` | `Bearer BLOTATO_API_KEY` |
| Higgsfield | `https://api.higgsfield.ai` | `Bearer HIGGSFIELD_API_KEY` |
| Formspree | `https://formspree.io/f/xwpbbzvy` | None (public form) |
| ShipClaw | `https://shipclaw.org` | `Bearer SHIPCLAW_TOKEN` |

---

## Do Not Touch

- `logo.svg` — finalized, do not regenerate
- `css/tokens.css` — color tokens are brand-locked
- Formspree ID `xwpbbzvy` — do not change
- `vercel.json` — do not modify deployment config
- `yahwaylove.com` — this is a DIFFERENT business, not Andrew's site
