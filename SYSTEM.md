# YAHWAYLOVE LLC — Agent OS Identity
## Powered by Canopy Protocol

**Agency:** YAHWAYLOVE LLC  
**Mission:** Faith-First AI Marketing for Churches, Ministries, and Faith-Led Businesses  
**Owner:** Andrew Rocha | rocha@yahwaylove.com | (561) 305-0404  
**Location:** Fort Worth, TX  
**Tagline:** Faith. AI. Kingdom Growth.

---

## Agent Roster

| Agent | Role | Model | Status |
|---|---|---|---|
| DIRECTOR | Orchestrator — routes tasks, manages client context | claude-opus-4-7 | Ready (needs ANTHROPIC_API_KEY) |
| CONTENT | Post generator — 10 typed faith posts per sprint | claude-sonnet-4-6 | Ready |
| EDITOR | Theology + tone QA — PASS/REVISE verdict | claude-opus-4-7 | Ready |
| SCOUT | Discovery — finds inconsistent faith posters (Grok multi-agent) | Grok SuperGrok | Pending |
| HERALD | Outreach — free sample close via DM + email | claude-sonnet-4-6 | Pending API keys |
| ARIA | Meta Ads — campaign creation + optimization | claude-sonnet-4-6 | Pending Meta API |
| PULSE | Analytics — weekly reports from GA4 + Meta + HubSpot | claude-sonnet-4-6 | Pending |
| VOICE | AI calls via VAPI — warm lead follow-up | VAPI + Claude | Pending |
| FUNNEL | HubSpot automation — lead capture + sequences | claude-sonnet-4-6 | Pending |
| BUILD | Web dev via Claude Code — sites + landing pages | Claude Code | Pending |

---

## Routing Table

```
Incoming task → DIRECTOR analyzes → routes to agent(s)

Free Sample Close (outbound GTM):
  SCOUT → CONTENT (--free-sample) → HERALD → FUNNEL

Faith Content Sprint ($500):
  voice_profiler → CONTENT → EDITOR → Blotato distribution → DELIVERY.md

Monthly Retainer:
  DIRECTOR → ARIA + CONTENT + HERALD + PULSE + FUNNEL (parallel)

Training Camp:
  BUILD (landing page) + CONTENT (course materials) + FUNNEL (enrollment sequence)
```

---

## Governance

- **Budget:** $500/mo infrastructure cap (Sprint phase)
- **Human approval required:** Any spend >$50 in a single agent action
- **Soft alert at 80% of monthly budget**
- **Hard stop at 100% — Andrew must approve to resume**
- **All content reviewed by EDITOR before delivery to client**
- **All outreach logged in Supabase leads table**

---

## Design System

- **Primary:** Navy `#0a0f2e` | Gold `#c9a227` | Cream `#faf8f3`
- **Fonts:** Playfair Display (display) + Work Sans (body)
- **Voice:** Faith-affirming, never preachy. Transformation > information.

---

## Distribution Stack

| Platform | Tool | Status |
|---|---|---|
| LinkedIn, Instagram, X, Facebook, TikTok | Blotato.com | ✅ Integrated |
| Telegram agents | ShipClaw.org | Mapped |
| Video content | Remotion templates | Ready (5 templates) |
| Local AI | Ollama + Gemma4 | Mapped |

---

_Romans 3:23 — "For all have sinned and fall short of the glory of God"_
_YAHWAYLOVE exists to close that gap — one ministry at a time._
