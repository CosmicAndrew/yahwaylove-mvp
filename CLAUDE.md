# CLAUDE.md — YAHWAYLOVE MVP
> Claude Code auto-reads this file on startup. Contains full project context, architecture, and working instructions.

---

## Identity & Mission

**YAHWAYLOVE LLC** — Faith-First AI Marketing Agency  
Owner: Andrew Rocha | rocha@yahwaylove.com | (561) 305-0404  
Location: Fort Worth, TX  
Tagline: *"Faith. AI. Kingdom Growth."*  
Competition: **Perplexity Billion Dollar Build** (Apr 14 – Jun 2, 2026) — up to $1M seed + $1M compute credits

---

## Repository

```
GitHub:  https://github.com/CosmicAndrew/yahwaylove-mvp
Branch:  main
Latest:  9bf1c65 — real logo SVG + business model audit fixes
```

Clone:
```bash
git clone https://github.com/CosmicAndrew/yahwaylove-mvp.git
cd yahwaylove-mvp
```

---

## Design System

| Token | Value |
|---|---|
| Navy (bg) | `#0a0f2e` |
| Gold (accent) | `#c9a227` |
| Cream (text/bg) | `#faf8f3` |
| Font | Playfair Display (headings) + Inter (body) |

### Logo
- File: `logo.svg` (repo root)
- Circular badge — YAH/WAY pill-stroke letters, cream cross bearing ANDREW/JESUS/HAILEY
- Colors: face `#c4a882`, letterforms `#5c3318`, ring `#7a5533`, cross `#e8d4bc`
- Uses `<clipPath id="bc"><circle cx="100" cy="100" r="89"/></clipPath>`
- Nav: 32px | Footer: 28px | Hero variants: 36px

---

## Site Structure (`/yahwaylove/`)

```
index.html              Homepage — hero, Canopy OS agent grid, Platform Vision (TAM), tools bar, CTA
pages/
  sprint.html           $500 Faith Content Sprint — Ministry DNA Scanner, Content Ideas Board, Free Post form
  pricing.html          Full offer ladder (Tier 0–3)
  training.html         AI Training Camp ($97 Self-Study, Group $297, 1-on-1 $497, Team $2,500)
  agents.html           Agent team profiles (Director, Aria, Content, Herald, Voice, Funnel, Build, Pulse, Scout, Editor)
  services.html         Service descriptions
  about.html            Andrew Rocha bio + mission
  contact.html          Contact form (Formspree xwpbbzvy → rocha@yahwaylove.com)
  portfolio.html        Case studies / social proof
  funnel.html           Lead funnel page
css/
  tokens.css            Design tokens
  base.css              Reset + base styles
  components.css        Reusable UI components
js/
  main.js               Dark mode toggle, nav scroll, animations
logo.svg                Real YAHWAYLOVE logo (SVG)
AGENT_ARCHITECTURE.md   Full 10-agent technical blueprint
BUSINESS_AUDIT.md       405-line deliverability + scalability audit
SYSTEM.md               Canopy OS agent identity + routing table
company.yaml            Offer ladder, budget governance, API keys status, tool inventory
agents/
  voice_profiler.py     Taste Interviewer (claude-opus-4-7)
  content_agent.py      10-post generator (claude-sonnet-4-6)
  editor_agent.py       Theology + tone QA (claude-opus-4-7)
  sprint_runner.py      End-to-end orchestrator (--distribute, --batch-scout, --free-sample flags)
  scout_agent.py        Grok multi-agent SCOUT (Harper + Benjamin sub-agents)
  tools/
    blotato_tools.py    Multi-platform distribution — schedule_sprint_batch()
    remotion_tools.py   5 video templates (explainer, testimonial, dataviz, demo, avatar)
    higgsfield_tools.py Higgsfield CLI video generation (replaces/extends MuAPI)
  definitions/
    scout.md            Canopy agent definition for SCOUT
  .env.example          All API keys documented
  README.md             Agent usage docs
vercel.json             Vercel deployment config
```

---

## Agent Architecture (10 Agents — Canopy OS)

| Agent | Model | Role |
|---|---|---|
| Director | claude-opus-4-7 | Orchestrator — routes tasks, manages state |
| Aria | claude-sonnet-4-6 | Client-facing voice assistant |
| Content | claude-sonnet-4-6 | 10-post generator per Sprint |
| Herald | claude-sonnet-4-6 | Email/DM outreach writer |
| Voice | claude-opus-4-7 | Ministry voice profiler (taste interviewer) |
| Funnel | claude-sonnet-4-6 | Lead nurture sequences |
| Build | claude-sonnet-4-6 | Landing page copy generator |
| Pulse | claude-sonnet-4-6 | Analytics interpreter |
| Scout | Grok (api.x.ai) | Harper (prospect research) + Benjamin (trend intel) |
| Editor | claude-opus-4-7 | Theology accuracy + tone QA |

Run agents from `agents/` directory:
```bash
cd agents
python sprint_runner.py --free-sample          # 1 post (outbound GTM)
python sprint_runner.py --distribute           # full 10-post sprint + Blotato schedule
python sprint_runner.py --batch-scout          # SCOUT prospect research
python scout_agent.py --run "church name"      # single prospect scan
```

---

## Offer Ladder

### Tier 0 — Free Sample Close
- SCOUT + CONTENT generates 1 free post
- Email-first outreach (NOT LinkedIn DM — account ban risk)
- Cap: 10–15/week

### Tier 1 — Faith Content Sprint: $500 flat
- 10 AI-written faith posts in 48 hours
- Entry: `/sprint` page → Free Post form → Formspree `xwpbbzvy` → rocha@yahwaylove.com
- Andrew time: 3–4 hrs | Hard cost: $9–20 | Gross margin: 96–98%
- Cap 4 simultaneous clients until automation built
- Raise to $750 after 10 clients

### Tier 2 — Monthly Retainer
- Kingdom Starter: $2,500/mo (15–20 hrs/mo, 88–95% margin) ← START HERE
- Kingdom Builder: $4,500/mo (30–40 hrs/mo)
- Kingdom Dominator: $8,500/mo (Enterprise — hold until case studies)
- Target: 3–5 retainer clients max; 4 clients = $10K MRR

### Tier 3 — AI Training Camp
- Group Workshop: $297/person (immediate revenue — just Zoom + Claude)
- Self-Study: $97 (record workshop → product)
- 1-on-1: $497 (raise to $697–997 after results)
- Team Training: $2,500

---

## API Keys Status

| Key | Status | Notes |
|---|---|---|
| `ANTHROPIC_API_KEY` | ⏳ Pending | **CRITICAL** — needed for ALL agents |
| `MUAPI_PRODUCTION_KEY` | ✅ Live ($20 credit) | Now also integrates Higgsfield CLI |
| `HIGGSFIELD_API_KEY` | ✅ Live | Higgsfield CLI video generation |
| `VERCEL_TOKEN` | ✅ Live | Auto-deploy on git push |
| `GITHUB_TOKEN` | ✅ Live | |
| `FORMSPREE_ID` | ✅ Live | `xwpbbzvy` → rocha@yahwaylove.com |
| `BLOTATO_API_KEY` | ⏳ Pending | blotato.com, free trial 5K credits |
| `GROK_API_KEY` | ⏳ Pending | SuperGrok $30/mo, api.x.ai |
| `SHIPCLAW_TOKEN` | ⏳ Pending | shipclaw.org |
| Meta, HubSpot, Twilio, VAPI, Supabase | ⏳ Pending | Retainer tier only |

---

## Tool Stack

| Tool | Purpose | Status |
|---|---|---|
| Claude (Anthropic) | Core LLM for all content agents | Pending API key |
| Blotato | Multi-platform auto-distribution (33M views/mo) | Pending key |
| Grok SCOUT | Prospect research (Harper + Benjamin agents) | Pending key |
| Remotion | Programmatic video (5 templates) | Integrated |
| Higgsfield CLI | AI video generation (replaces/extends MuAPI) | ✅ Live |
| Canopy OS | Agent orchestration protocol | Built |
| ShipClaw | Outreach automation | Pending key |
| Formspree | Form submissions → email | ✅ Live |
| Vercel | Production hosting | ✅ Live |

---

## Business Model Audit — Key Findings

Full audit: `BUSINESS_AUDIT.md`

### Top 5 Risks
1. LinkedIn cold DMs → account suspension — use email only
2. Meta religious ad targeting (Special Ad Category restrictions since Jan 2022)
3. Theology accuracy liability → mandatory client review before publishing
4. Single-operator bottleneck → hire VA at $5K MRR
5. Anthropic API pricing dependency → build model-agnostic prompts

### Path to $1B
- Services = proof of concept; SaaS pivot required at Month 18
- **Faith Marketing OS** ($199–499/mo self-serve) — target Month 18
- TAM: 370K US congregations, $155B industry, $1.5–10B platform TAM
- Moat: denomination voice playbooks + faith sector trust + first-mover
- Acquisition targets: Ministry Brands, Blackbaud, Pushpay (90K+ churches, zero AI marketing)

---

## 30-Day Revenue Targets

| Metric | Target |
|---|---|
| Sprint sales | 15–20 |
| Retainer clients | 2–3 |
| Team Trainings | 2 |
| Group Workshops | 1–2 |
| Total 8-week revenue | $15,000–$25,000 |
| MRR at competition end | $5,000–$10,000 |

### Week 1 Priorities
1. Get `ANTHROPIC_API_KEY` — unlocks all agents
2. Send 10–15 cold emails (NOT LinkedIn) with free sample post
3. Record first Group Workshop (Zoom + Claude = done)
4. Sign up for Blotato free trial (5K credits)

---

## Google Labs Mirrors Built

| Google Labs | YAHWAYLOVE Mirror | Location |
|---|---|---|
| Pomelli (URL → brand DNA) | Ministry DNA Scanner | `/sprint` page |
| Mixboard (AI concepting) | Content Ideation Board (6 idea cards) | `/sprint` page |
| Opal (AI mini-app builder) | Ministry AI Builder | Mapped, not yet built |
| Stitch (NL → UI) | Brand Preview after scan | Partial in DNA scanner |

**Ministry DNA Scanner** is fully client-side JS — no API key needed for demo.

---

## Working Notes for Claude Code

- All Python agents use `os.chdir(Path(__file__).parent)` — run from `agents/` directory
- DNA Scanner is client-side JS only — works without any API keys
- Vercel auto-deploys on push to `main`
- Formspree form ID `xwpbbzvy` is hardcoded in `contact.html` and `sprint.html`
- `--free-sample` flag on `sprint_runner.py` generates 1 post for outbound GTM
- Blotato schedules at 2-day spacing, 9am CT (14:00 UTC) by default
- Grok API endpoint: `https://api.x.ai/v1/chat/completions` (OpenAI-compatible interface)
- Higgsfield CLI replaces standalone MuAPI usage for video generation
- Never use `yahwaylove.com` as the live URL — that is a DIFFERENT business
- Live preview: https://www.perplexity.ai/computer/a/yahwaylove-G9Vg.ulrQtKX3rvdv3JVww
