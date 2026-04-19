# YAHWAYLOVE — CONTENT Agent Stack

Faith Content Sprint pipeline. Takes a pastor's intake form and delivers
10 posts in their exact voice, reviewed for theology and tone, in under 48 hours.

---

## Setup

```bash
cd agents/
pip install anthropic python-dotenv
cp .env.example .env
# Add your ANTHROPIC_API_KEY to .env
```

---

## The 3 Agents

| File | Role | Input | Output |
|---|---|---|---|
| `voice_profiler.py` | Taste Interviewer | Formspree JSON or CLI interview | `profiles/pastor_name.md` |
| `content_agent.py` | CONTENT — post generator | `pastor.md` profile | `posts/[sprint_id]/raw_posts.md` |
| `editor_agent.py` | EDITOR — theology + tone QA | `raw_posts.md` | `reviewed_posts.md` + `editor_report.md` |

---

## Workflows

### Full Sprint from Formspree Form (most common)

When a pastor fills out the form at `yahwaylove.com/sprint`, Formspree emails
the submission to `rocha@yahwaylove.com`. Save the form data as a JSON file, then:

```bash
# Save the form submission as form.json (see format below)
python sprint_runner.py --form form.json
```

This runs all 3 agents end-to-end and produces a `DELIVERY.md` file ready to email.

### Free Sample Close (outbound GTM)

```bash
# Generate 1 post for a pastor you're cold-outreaching:
python sprint_runner.py --form form.json --free-sample
```

Produces a single post you can DM with the message:
_"We wrote this for your church. Post it if you like it. If you want more, let's talk."_

### From an Existing Profile

```bash
python sprint_runner.py --profile profiles/john_smith.md --topic "trusting God in uncertainty"
```

### Individual Agent Calls

```bash
# Build voice profile only (interactive CLI):
python voice_profiler.py --interactive --output profiles/pastor.md

# Generate posts from profile:
python content_agent.py --profile profiles/john_smith.md --topic "James 1"

# Run editor on existing sprint:
python editor_agent.py --sprint SPRINT-2026-04-19-JS

# Build delivery doc only:
python sprint_runner.py --sprint SPRINT-2026-04-19-JS --deliver
```

---

## Form JSON Format

When Formspree sends a webhook or you export the form data, save it like this:

```json
{
  "name": "Pastor John Smith",
  "church": "Grace Community Church",
  "email": "john@gracechurch.org",
  "topic": "We've been in James 1 and I want something for young adults going through hard seasons",
  "style": "Conversational & relatable",
  "location": "Austin, TX"
}
```

Fields map directly from the sprint form at `yahwaylove.com/sprint`.

---

## File Structure

```
agents/
  sprint_runner.py      ← Run this for full pipeline
  voice_profiler.py     ← Taste Interviewer (builds pastor.md)
  content_agent.py      ← Generates 10 posts
  editor_agent.py       ← Theology + tone QA
  .env                  ← Your API keys (not committed)
  .env.example          ← Template
  README.md             ← This file

  profiles/
    john_smith.md       ← Voice profiles (one per pastor)
    pastor_name.md      ← Auto-named from form data

  posts/
    SPRINT-2026-04-19-JS/
      raw_posts.md      ← CONTENT output (unreviewed)
      editor_report.md  ← EDITOR verdict per post
      reviewed_posts.md ← Approved posts (delivery-ready)
      intake_summary.md ← What went in
      DELIVERY.md       ← Final email-ready document
```

---

## Prompt Engineering Notes

### voice_profiler.py
Uses `claude-opus-4-5` for the Taste Interviewer — highest reasoning quality for
capturing nuanced voice patterns. The pastor.md profile is the most critical file
in the entire pipeline. Garbage in = posts that don't sound like the pastor.

### content_agent.py
Uses `claude-sonnet-4-6` for post generation — fast and high quality.
10 posts generated in a single call for consistency across the batch.
Free sample mode generates 1 post (Post 1: Scripture Reflection) only.

### editor_agent.py
Uses `claude-opus-4-5` for review — needs strong reasoning to catch theological errors.
Produces inline revisions for any post that fails — CONTENT doesn't need to re-run.
A second `claude-sonnet-4-6` call extracts the final clean posts from the report.

---

## The Free Sample Close

The `--free-sample` flag powers the YAHWAYLOVE outbound GTM flow:

1. SCOUT identifies a faith leader posting inconsistently (< 2x/week)
2. Andrew fills out a quick form.json from their public profile
3. `sprint_runner.py --form form.json --free-sample` generates 1 post
4. Andrew sends it via DM: _"We wrote this for your church. Post it if you like it."_
5. If they engage → pitch the $500 Sprint
6. If they buy the Sprint → pitch the retainer

**No API calls needed for the DM step. Just Claude.ai Pro + manual outreach.**

---

## Current Status

- [x] `voice_profiler.py` — complete
- [x] `content_agent.py` — complete
- [x] `editor_agent.py` — complete
- [x] `sprint_runner.py` — complete
- [ ] Awaiting `ANTHROPIC_API_KEY` to run end-to-end
- [ ] First test run: use Andrew as the "pastor" to validate voice profile quality
- [ ] SCOUT integration (automated LinkedIn/Facebook discovery) — Phase 2

---

_Andrew Rocha | YAHWAYLOVE LLC | rocha@yahwaylove.com | Romans 3:23_
