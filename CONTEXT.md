# CONTEXT.md — YAHWAYLOVE MVP
> Master unified context file. Use this as a system prompt, project attachment, or context injection for any AI CLI or chat tool.
> Last updated: May 9, 2026

---

## 1. Who We Are

**YAHWAYLOVE LLC** — Faith-First AI Marketing Agency  
**Owner:** Andrew Rocha  
**Email:** rocha@yahwaylove.com | (561) 305-0404  
**Location:** Fort Worth, TX  
**Tagline:** *"Faith. AI. Kingdom Growth."*

**Competition context:** Perplexity Billion Dollar Build (April 14 – June 2, 2026)  
Prize: Up to $1M seed funding + $1M compute credits  
Goal: Demonstrate a billion-dollar platform thesis through a working MVP

---

## 2. Repository

```
URL:     https://github.com/CosmicAndrew/yahwaylove-mvp
Branch:  main
Latest:  9bf1c65 — real logo SVG + business model audit fixes
```

Clone and run:
```bash
git clone https://github.com/CosmicAndrew/yahwaylove-mvp.git
cd yahwaylove-mvp
python -m http.server 8080 --directory .   # preview frontend
cd agents && cp .env.example .env          # set up agent environment
```

---

## 3. Design System

| Element | Value |
|---|---|
| Primary BG | Navy `#0a0f2e` |
| Accent | Gold `#c9a227` |
| Text/Light BG | Cream `#faf8f3` |
| Heading font | Playfair Display |
| Body font | Inter |
| Logo | Circular badge SVG — YAH/WAY pill letters, cream cross (ANDREW/JESUS/HAILEY) |
| Logo file | `logo.svg` (repo root) |

Logo color tokens:
- Face: `#c4a882` | Letterforms: `#5c3318` | Ring: `#7a5533` | Cross: `#e8d4bc`

---

## 4. Site Map

| Page | File | Purpose |
|---|---|---|
| Homepage | `index.html` | Hero, Canopy OS agent grid, Platform Vision (TAM), tools bar |
| $500 Sprint | `pages/sprint.html` | Ministry DNA Scanner, Content Ideation Board, Free Post form |
| Pricing | `pages/pricing.html` | Full offer ladder (Tiers 0–3) |
| Training Camp | `pages/training.html` | $97 Self-Study, $297 Group, $497 1-on-1, $2,500 Team |
| Agent Team | `pages/agents.html` | 10-agent profiles |
| Services | `pages/services.html` | Service descriptions |
| About | `pages/about.html` | Andrew Rocha bio + mission |
| Contact | `pages/contact.html` | Formspree form `xwpbbzvy` |
| Portfolio | `pages/portfolio.html` | Case studies |
| Funnel | `pages/funnel.html` | Lead capture |

Live preview: https://www.perplexity.ai/computer/a/yahwaylove-G9Vg.ulrQtKX3rvdv3JVww

---

## 5. Agent Architecture — Canopy OS

Ten agents running on Canopy OS protocol (`SYSTEM.md`). Entry point: `agents/sprint_runner.py`.

| Agent | Model | File | Role |
|---|---|---|---|
| Director | claude-opus-4-7 | (orchestrator) | Routes tasks, manages state |
| Voice | claude-opus-4-7 | `voice_profiler.py` | 5-question brand voice interview |
| Content | claude-sonnet-4-6 | `content_agent.py` | 10-post generator |
| Editor | claude-opus-4-7 | `editor_agent.py` | Theology + tone QA |
| Scout | Grok (api.x.ai) | `scout_agent.py` | Harper (research) + Benjamin (trends) |
| Herald | claude-sonnet-4-6 | — | Cold email outreach sequences |
| Funnel | claude-sonnet-4-6 | — | Lead nurture emails |
| Build | claude-sonnet-4-6 | — | Landing page copy |
| Pulse | claude-sonnet-4-6 | — | Analytics interpretation |
| Aria | claude-sonnet-4-6 | — | Client-facing voice interface |

**Sprint pipeline:**
```bash
cd agents
python sprint_runner.py --free-sample      # 1 post (outbound GTM)
python sprint_runner.py                    # full 10-post sprint
python sprint_runner.py --distribute       # sprint + Blotato auto-distribution
python sprint_runner.py --batch-scout      # sprint + prospect research
```

---

## 6. Tool Stack

| Tool | Role | Status |
|---|---|---|
| Claude (Anthropic) | Core LLM — all content, editing, orchestration | ⏳ Need API key |
| Grok / xAI | SCOUT prospect research (api.x.ai) | ⏳ Need API key |
| Blotato | Multi-platform auto-distribution (33M views/mo) | ⏳ Need key |
| Higgsfield CLI | AI video generation — primary video tool | ✅ Live |
| MuAPI | Video (legacy — now extended by Higgsfield CLI) | ✅ $20 credit live |
| Remotion | Programmatic video templates (5 types) | ✅ Integrated |
| Canopy OS | Agent orchestration protocol | ✅ Built |
| ShipClaw | Outreach automation | ⏳ Need token |
| Formspree | Form → email (`xwpbbzvy`) | ✅ Live |
| Vercel | Production hosting (auto-deploy on push) | ✅ Live |
| GitHub | Source control + CI | ✅ Live |

**Higgsfield CLI note:** MuAPI is still active ($20 credit) but Higgsfield CLI is now the primary video generation interface. `agents/tools/higgsfield_tools.py` handles `generate_ministry_video()`, `generate_sermon_highlight()`, and `generate_scripture_reel()`.

---

## 7. API Keys

```bash
# CRITICAL — needed to run ALL agents
ANTHROPIC_API_KEY=           # ⏳ Pending

# Live now
MUAPI_PRODUCTION_KEY=        # ✅ $20 credit
HIGGSFIELD_API_KEY=          # ✅ Live — primary video tool
VERCEL_TOKEN=                # ✅
GITHUB_TOKEN=                # ✅
FORMSPREE_ID=xwpbbzvy       # ✅ → rocha@yahwaylove.com

# Pending (free trials available)
BLOTATO_API_KEY=             # blotato.com — 5K free credits
GROK_API_KEY=                # api.x.ai — SuperGrok $30/mo
SHIPCLAW_TOKEN=              # shipclaw.org

# Retainer tier only (not needed yet)
META_ACCESS_TOKEN=
HUBSPOT_API_KEY=
TWILIO_AUTH_TOKEN=
VAPI_KEY=
SUPABASE_URL=
SUPABASE_ANON_KEY=
```

---

## 8. Offer Ladder

### Tier 0 — Free Sample Close (GTM)
- 1 free post generated by SCOUT + CONTENT pipeline
- Delivery: cold email only (NOT LinkedIn — ban risk)
- Volume cap: 10–15/week

### Tier 1 — Faith Content Sprint: $500 flat
- 10 AI-written faith posts in 48 hours, reviewed by Andrew before delivery
- Entry: `/sprint` → Free Post form → Formspree → rocha@yahwaylove.com
- Unit economics: 3–4 hrs Andrew time | $9–20 API cost | 96–98% gross margin
- Constraint: cap 4 simultaneous until `--distribute` is automated
- Price increase: → $750 after 10 clients

### Tier 2 — Monthly Retainer
- **Kingdom Starter:** $2,500/mo — 15–20 hrs/mo, 88–95% margin ← **START HERE**
- **Kingdom Builder:** $4,500/mo — 30–40 hrs/mo
- **Kingdom Dominator:** $8,500/mo — Enterprise (hold until case studies exist)
- Target: 4 clients × $2,500 = $10K MRR = full-time replacement income

### Tier 3 — AI Training Camp
- **Group Workshop:** $297/person — immediate, just Zoom + Claude
- **Self-Study:** $97 — record workshop → instant product
- **1-on-1:** $497 → raise to $697–997 after first documented results
- **Team Training:** $2,500 flat

---

## 9. Business Audit — Top Findings

Full audit: `BUSINESS_AUDIT.md` (405 lines)

### What's Deliverable NOW (no API keys needed)
- Ministry DNA Scanner on `/sprint` — fully client-side JS
- Tier 3 Group Workshop — just Zoom + Claude.ai (no API key needed)
- Free sample posts — Claude.ai web UI can substitute until key arrives

### Top 5 Risks
1. **LinkedIn outreach** → account suspension — email only
2. **Meta ad religious targeting** → Special Ad Category restrictions (Jan 2022) — organic only
3. **Theology accuracy liability** → mandatory client review before any post is published
4. **Single-operator bottleneck** → hire VA at $5K MRR
5. **Anthropic API pricing** → build model-agnostic prompts for GPT-4o fallback

### Critical Copy Rules (audit-applied)
- Say "AI-powered workflows" NOT "10 agents" (VC credibility)
- Every Sprint page includes: "You review before you post" (liability)
- Kingdom Dominator is "Enterprise" — not for solo delivery yet

---

## 10. Path to $1 Billion

Services revenue is **proof of concept only** — the SaaS pivot is the real company.

| Stage | Timeline | Product |
|---|---|---|
| 1 | Now – Month 6 | Service agency (Sprint + Retainer) — build playbooks |
| 2 | Month 6–12 | Denomination voice library (SBC, Pentecostal, Catholic, Non-denom) |
| 3 | Month 12–18 | Faith Marketing OS beta ($199–499/mo self-serve) |
| 4 | Month 18+ | Platform + API licensing to Ministry Brands / Blackbaud / Pushpay |

**TAM:** 370K US congregations | $155B faith economy | $1.5–10B platform TAM  
**Moat:** Denomination voice playbooks + faith sector trust network + first-mover AI  
**Acquisition targets:** Ministry Brands, Blackbaud, Pushpay (serve 90K+ churches, zero AI marketing)

---

## 11. 30-Day Revenue Targets (Competition Window)

| Metric | Target |
|---|---|
| Sprint sales | 15–20 × $500 = $7,500–$10,000 |
| Retainer closes | 2–3 × $2,500 = $5,000–$7,500 MRR |
| Team Trainings | 2 × $2,500 = $5,000 |
| Group Workshops | 1–2 × $297/person | 
| **Total 8-week** | **$15,000–$25,000** |
| **MRR at end** | **$5,000–$10,000** |

### Week 1 Action Items
1. ✅ Get `ANTHROPIC_API_KEY` — unlocks all 5 Python agents
2. ✅ Send 10–15 cold emails with free sample post (no LinkedIn)
3. ✅ Run first Group Workshop (Zoom + Claude.ai — no key needed)
4. ✅ Sign up for Blotato free trial (blotato.com — 5K credits)
5. ✅ Sign up for Grok API (api.x.ai — SuperGrok $30/mo)
6. ✅ Build denomination prompt library (SBC first)

---

## 12. Google Labs Mirrors

| Google Labs Feature | YAHWAYLOVE Version | Status |
|---|---|---|
| Pomelli — URL → brand DNA | Ministry DNA Scanner | ✅ Live on `/sprint` |
| Mixboard — AI concepting board | Content Ideation Board (6 cards) | ✅ Live on `/sprint` |
| Opal — AI mini-app builder | Ministry AI Builder | Mapped, not yet built |
| Stitch — NL → UI designs | Brand Preview after DNA scan | Partial |

---

## 13. Technical Notes

- **No build step** — pure HTML/CSS/JS frontend; open `index.html` directly or `python -m http.server 8080`
- **Python agents** must run from `agents/` directory (each file uses `os.chdir(Path(__file__).parent)`)
- **Vercel auto-deploys** on every push to `main`
- **Formspree** form ID `xwpbbzvy` hardcoded in `contact.html` and `sprint.html`
- **Grok API** uses OpenAI-compatible interface: `https://api.x.ai/v1/chat/completions`
- **Higgsfield CLI** is primary video tool; MuAPI credit still available as fallback
- **`yahwaylove.com`** → DIFFERENT business — do not reference as Andrew's site
- **DNA Scanner** is 100% client-side JS — works in demo without any API keys

---

## 14. Key File Reference

| File | Purpose |
|---|---|
| `AGENT_ARCHITECTURE.md` | Full 10-agent technical blueprint |
| `BUSINESS_AUDIT.md` | 405-line deliverability + scalability audit |
| `SYSTEM.md` | Canopy OS agent identity + routing table |
| `company.yaml` | Offer ladder, budget governance, API key status, tool inventory |
| `agents/.env.example` | All environment variables documented |
| `agents/README.md` | Agent usage documentation |
| `logo.svg` | Finalized YAHWAYLOVE logo — do not regenerate |
| `CLAUDE.md` | Claude Code context (this project's CLAUDE.md) |
| `AGENTS.md` | OpenCode context (agent definitions + tool permissions) |
| `CODEX.md` | Codex CLI context (codebase map + implementation tasks) |

---

*YAHWAYLOVE LLC — rocha@yahwaylove.com — Fort Worth, TX*  
*Context file generated May 9, 2026 — update after each major session*
