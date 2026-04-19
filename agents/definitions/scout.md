# SCOUT — Discovery Agent
## Grok Multi-Agent Architecture

**Role:** Identify faith leaders posting inconsistently on LinkedIn/Facebook  
**Model:** Grok 3 (SuperGrok) — real-time X/web search + multi-agent coordination  
**Trigger:** Manual (Sprint phase) → Automated cron (Retainer phase)  
**Output:** `raw/prospect_list.json` → feeds HERALD outbound queue

---

## Grok Multi-Agent Architecture

SCOUT runs 3 sub-agents simultaneously via SuperGrok:

| Sub-Agent | Name | Role |
|---|---|---|
| Orchestrator | Grok | Routes queries, synthesizes findings |
| Web + X Search | Harper | Scans LinkedIn, Facebook, X for faith posters |
| Fact Checker | Benjamin | Verifies contact info, posting frequency |

Result: 272 sources in 37 seconds (Ruben Hassid pattern, SuperGrok $30/mo)

---

## Discovery Criteria

A prospect qualifies if they match ALL of:
1. Faith leader (pastor, ministry director, church admin, faith-led business owner)
2. Posts publicly on LinkedIn or Facebook
3. Posting frequency < 2x per week (inconsistent = opportunity)
4. Audience > 500 followers (worth the outreach)
5. Recent post < 30 days ago (still active, not abandoned)

---

## Search Queries (Harper runs these in parallel)

```
LinkedIn:
  "pastor" site:linkedin.com last_post_days:30
  "church" "ministry" site:linkedin.com -"posted 1 day" -"posted 2 days"
  "faith-led" OR "Christian business" site:linkedin.com

Facebook:
  Faith leader pages with < 2 posts/week (requires Meta API in retainer phase)
  
X (Twitter):
  "pastor" OR "ministry" -"promoted" filter:verified since:2026-03-19
```

---

## Output Format

```json
{
  "prospect_id": "P-2026-04-19-001",
  "name": "Pastor James Carter",
  "church": "Cornerstone Fellowship",
  "location": "Dallas, TX",
  "linkedin_url": "https://linkedin.com/in/pastorjamescarter",
  "followers": 1240,
  "last_post_date": "2026-04-05",
  "posts_last_30_days": 2,
  "sample_voice": "James Carter's content is scripture-heavy with personal stories. Warm, pastoral tone. Uses 'beloved' frequently. Posts are 150-200 words.",
  "niche": "adult congregation",
  "priority": "HIGH",
  "scout_date": "2026-04-19",
  "status": "pending_outreach"
}
```

---

## Sprint Phase (Manual SCOUT)

No API required. Andrew runs SCOUT manually:

1. Search LinkedIn for: `"pastor" "church" "ministry"` — filter by people
2. Look at posting frequency on their profile
3. Copy name, church, URL, sample posts into `raw/prospect_list.json`
4. Run `python agents/scout_agent.py --analyze --prospect [linkedin_url]`
   → Script fetches public posts, extracts voice signals, scores prospect
5. Top 10 prospects → CONTENT generates free sample posts
6. HERALD sends the DM

---

## Full Automation (Retainer Phase)

```bash
python agents/scout_agent.py --run --limit 50 --niche "adult congregation"
```

Runs all 3 Grok sub-agents, outputs 50 ranked prospects to `raw/prospect_list.json`
Automatically triggers CONTENT for top 10 (score ≥ 8.0)

---

## Integration Points

- **CONTENT:** Passes `sample_voice` for post generation context
- **HERALD:** Passes `linkedin_url` + `name` + `church` for DM targeting
- **FUNNEL:** All prospects logged to Supabase `leads` table
- **PULSE:** Tracks outreach → response → conversion rates weekly
