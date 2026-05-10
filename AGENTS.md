# AGENTS.md — YAHWAYLOVE MVP
> OpenCode reads this file automatically. Contains agent definitions, tool permissions, task routing, and full project context.

---

## Project Identity

**YAHWAYLOVE LLC** — Faith-First AI Marketing Agency, Fort Worth TX  
Owner: Andrew Rocha | rocha@yahwaylove.com | (561) 305-0404  
Tagline: *"Faith. AI. Kingdom Growth."*  
Competition: Perplexity Billion Dollar Build (Apr 14 – Jun 2, 2026)

**Repo:** https://github.com/CosmicAndrew/yahwaylove-mvp (branch: `main`, latest: `9bf1c65`)

---

## Agent Roster — Canopy OS

> All agents run under the Canopy OS protocol defined in `SYSTEM.md`.  
> Orchestration entry point: `agents/sprint_runner.py`

### Director (Orchestrator)
- **Model:** claude-opus-4-7
- **Role:** Routes all inbound tasks to appropriate sub-agents, manages conversation state, enforces theology guardrails
- **Input:** Client intake form data, Ministry DNA scan results
- **Output:** Dispatches to Voice, Content, Scout, or Herald agents

### Voice (Taste Interviewer)
- **Model:** claude-opus-4-7
- **File:** `agents/voice_profiler.py`
- **Role:** Conducts 5-question brand voice interview, outputs `VoiceProfile` JSON
- **Output schema:**
  ```json
  { "tone": "", "theology": "", "platform": "", "audience": "", "avoidances": [] }
  ```

### Content (Post Generator)
- **Model:** claude-sonnet-4-6
- **File:** `agents/content_agent.py`
- **Role:** Generates 10 faith-contextualized social posts from VoiceProfile
- **Platforms:** Instagram, Facebook, LinkedIn, X, Threads
- **Output:** 10 posts in JSON array with `platform`, `copy`, `hashtags`, `cta` fields

### Editor (Theology + Tone QA)
- **Model:** claude-opus-4-7
- **File:** `agents/editor_agent.py`
- **Role:** Reviews all Content output for theology accuracy and brand tone before delivery
- **Hard rules:**
  - Flag any doctrinal claims not supported by scripture reference
  - Reject posts that use generic Christian clichés without substance
  - Ensure client review before any post goes live

### Scout (Prospect Research)
- **Model:** Grok (`https://api.x.ai/v1/chat/completions`)
- **File:** `agents/scout_agent.py`
- **Sub-agents:** Harper (prospect research) + Benjamin (trend intelligence)
- **Modes:**
  ```bash
  python scout_agent.py --run "church name"     # single prospect
  python scout_agent.py --analyze               # trend analysis
  python scout_agent.py --list                  # list tracked prospects
  ```

### Herald (Outreach Writer)
- **Model:** claude-sonnet-4-6
- **Role:** Writes cold email sequences for Tier 0 free sample outreach
- **CRITICAL:** Email only — NO LinkedIn DMs (account ban risk)
- **Cap:** 10–15 emails/week

### Funnel (Lead Nurture)
- **Model:** claude-sonnet-4-6
- **Role:** Writes email nurture sequences post-lead-capture

### Build (Landing Page Copy)
- **Model:** claude-sonnet-4-6
- **Role:** Generates church-specific landing page copy variants

### Pulse (Analytics)
- **Model:** claude-sonnet-4-6
- **Role:** Interprets engagement analytics, surfaces top-performing post patterns

### Aria (Client Assistant)
- **Model:** claude-sonnet-4-6
- **Role:** Client-facing voice interface, answers questions about deliverables

---

## Tool Permissions

| Tool | Agent(s) | Allowed Actions |
|---|---|---|
| `blotato_tools.py` | Content, Director | `schedule_sprint_batch()` — schedules 10-post distribution |
| `remotion_tools.py` | Content, Build | 5 video templates: explainer, testimonial, dataviz, demo, avatar |
| `higgsfield_tools.py` | Content, Build | Higgsfield CLI video generation (primary video tool — replaces MuAPI standalone) |
| `scout_agent.py` | Director | Prospect research via Grok api.x.ai |
| Formspree `xwpbbzvy` | Herald | Form submission intake only |
| GitHub API | Director | Read repo state, commit audit logs |

---

## Sprint Runner — Entry Point

```bash
cd agents
python sprint_runner.py --free-sample     # 1 post for outbound GTM
python sprint_runner.py                   # full 10-post Sprint
python sprint_runner.py --distribute      # Sprint + Blotato auto-distribution
python sprint_runner.py --batch-scout     # Sprint + SCOUT prospect scan
```

**Flags:**
- `--free-sample` → 1 post, no distribution (Tier 0 outreach)
- `--distribute` → calls `blotato_tools.schedule_sprint_batch()` after generation
- `--batch-scout` → runs Scout agent in parallel with content generation

---

## Environment Variables

```bash
# CRITICAL — get this first
ANTHROPIC_API_KEY=

# Live
MUAPI_PRODUCTION_KEY=           # $20 credit live
HIGGSFIELD_API_KEY=             # Higgsfield CLI — live (primary video)
VERCEL_TOKEN=                   # live
GITHUB_TOKEN=                   # live
FORMSPREE_ID=xwpbbzvy          # live → rocha@yahwaylove.com

# Pending
BLOTATO_API_KEY=                # blotato.com free trial — 5K credits
GROK_API_KEY=                   # api.x.ai — SuperGrok $30/mo
SHIPCLAW_TOKEN=                 # shipclaw.org

# Retainer tier only
META_ACCESS_TOKEN=
HUBSPOT_API_KEY=
TWILIO_AUTH_TOKEN=
VAPI_KEY=
SUPABASE_URL=
SUPABASE_ANON_KEY=
```

Copy `.env.example` in `agents/` for full documented template.

---

## File Tree

```
yahwaylove-mvp/
├── index.html                  Homepage
├── pages/
│   ├── sprint.html             $500 Sprint page (Ministry DNA Scanner)
│   ├── pricing.html            Full offer ladder
│   ├── training.html           AI Training Camp
│   ├── agents.html             Agent profiles
│   ├── services.html
│   ├── about.html
│   ├── contact.html
│   ├── portfolio.html
│   └── funnel.html
├── css/
│   ├── tokens.css
│   ├── base.css
│   └── components.css
├── js/main.js
├── logo.svg                    Real YAHWAYLOVE logo
├── agents/
│   ├── voice_profiler.py
│   ├── content_agent.py
│   ├── editor_agent.py
│   ├── sprint_runner.py        ← ENTRY POINT
│   ├── scout_agent.py
│   ├── tools/
│   │   ├── blotato_tools.py
│   │   ├── remotion_tools.py
│   │   └── higgsfield_tools.py
│   ├── definitions/scout.md
│   ├── .env.example
│   └── README.md
├── AGENT_ARCHITECTURE.md
├── BUSINESS_AUDIT.md
├── SYSTEM.md
├── company.yaml
├── CLAUDE.md
├── AGENTS.md                   ← THIS FILE
├── CODEX.md
├── CONTEXT.md
└── vercel.json
```

---

## Task Routing Guide

| User Request | Agent | Entry Point |
|---|---|---|
| "Write posts for my church" | Voice → Content → Editor | `sprint_runner.py` |
| "Research this prospect" | Scout (Harper) | `scout_agent.py --run` |
| "What's trending in faith content" | Scout (Benjamin) | `scout_agent.py --analyze` |
| "Schedule my posts" | Content + Blotato | `sprint_runner.py --distribute` |
| "Make a video" | Build + Higgsfield CLI | `higgsfield_tools.py` |
| "Write an outreach email" | Herald | Direct herald call |
| "Review my content" | Editor | Direct editor call |

---

## Critical Guardrails

1. **Theology review is non-negotiable** — Editor agent must approve ALL content before client delivery
2. **No LinkedIn cold DMs** — use email only for outreach
3. **Client reviews before posting** — contractual, not optional
4. **Cap simultaneous Sprint clients at 4** until `--distribute` automation is proven
5. **No Kingdom Dominator ($8,500) sales** until at least 2 retainer case studies documented
6. **Model-agnostic prompts** — don't hardcode Anthropic-specific syntax; must work on GPT-4o fallback
