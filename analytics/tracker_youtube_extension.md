# YouTube Tracking Extension

**Purpose:** YouTube-specific metrics, fields, and tracking guidelines for YouTube Shorts probe.  
**Base schema:** [analytics/schema.md](../schema.md)  
**Integration:** Extends existing NODE_NULL_TRACKER with YouTube-specific fields

---

## YouTube-Specific Fields

### Additional Columns for Posts Tab

Add these columns when tracking YouTube Shorts:

| Field | Type | Description | Capture Window |
|-------|------|-------------|----------------|
| `title` | string | Video title (required on YouTube) | At publish |
| `thumbnail_style` | string | Thumbnail design variant | At publish |
| `impressions` | integer | YouTube Studio impressions count | 2h, 24h, 48h |
| `ctr` | decimal | Click-through rate on thumbnail (%) | 2h, 24h, 48h |
| `avg_percentage_viewed` | decimal | YouTube's "Average percentage viewed" metric | 24h, 48h |
| `traffic_source` | string | Primary source (Browse, Suggested, Search, External) | 24h |
| `audience_retention_graph` | string | Link to retention graph screenshot | 24h |

### YouTube Title Format

**Pattern:** `[Hook text] — [Mechanism/system name]`

**Examples:**
- `What happens when AI gets too good at junior dev work? — AI Displacement`
- `You're already living in a social credit system — Distributed Reputation`
- `Why does every app feel like a slot machine? — Attention Economy`

---

## YouTube Studio Metrics Map

### Standard Metrics (same as other platforms)

| Platform Metric | YouTube Studio Name | Notes |
|----------------|---------------------|-------|
| Views | Views | Total views |
| Avg view duration | Average view duration | In seconds |
| Completion % | N/A | Calculate: (Avg % viewed) |
| Shares | Shares | Includes all share types |
| Comments | Comments | Total comment count |

### YouTube-Specific Metrics

| Metric | YouTube Studio Name | Calculation/Notes |
|--------|---------------------|-------------------|
| Impressions | Impressions | How many times thumbnail was shown |
| CTR | Click-through rate | (Views / Impressions) × 100 |
| Loop % | N/A | Estimate from retention graph end spike |
| Saves | Saves to playlists | YouTube-specific save type |

### Retention Graph Analysis

YouTube provides more detailed retention data than TikTok:

1. **Capture screenshot** of retention graph at 24h window
2. **Identify drop-off points:**
   - Hook effectiveness (0-3s)
   - Mid-video holds (10-15s)
   - End loop potential (23-28s)
3. **Store link** in `audience_retention_graph` field

---

## Capture Windows (YouTube-specific)

YouTube analytics update on different cadences:

| Metric | Availability | Recommended Capture |
|--------|--------------|---------------------|
| Views, CTR | Near real-time | 2h, 24h, 48h |
| Avg % viewed | ~1-2h delay | 24h, 48h |
| Traffic source | ~2-6h delay | 24h |
| Retention graph | ~6-12h delay | 24h |
| Saves | ~12-24h delay | 48h |

**Rule:** Always capture at consistent windows within experiment blocks.

---

## YouTube Shorts Algorithm Considerations

### YouTube vs TikTok Differences

| Factor | TikTok | YouTube Shorts |
|--------|--------|----------------|
| Initial distribution | FYP (For You Page) | Browse, Suggested |
| Completion weight | Very high | High |
| Loop detection | Direct metric | Inferred from retention graph |
| External links | Discouraged | Pinned comments allowed |
| Title requirement | Optional caption | Required title field |

### Optimization Notes

1. **Thumbnail matters more on YouTube:**
   - CTR is a primary ranking signal
   - Test thumbnail variants per vertical

2. **Title framing matters:**
   - YouTube search/browse uses titles
   - TikTok uses on-screen text + captions

3. **Pinned comment strategy:**
   - YouTube allows clickable links in pinned comments
   - Use for landing page → email capture funnel

---

## Email Funnel Tracking (YouTube-specific)

### UTM Tracking

Use UTM parameters in pinned comment links:

```
https://forge.crisiscore.systems?utm_source=youtube&utm_medium=shorts&utm_campaign=probe&utm_content=video_01
```

**Structure:**
- `utm_source=youtube`
- `utm_medium=shorts`
- `utm_campaign=probe`
- `utm_content=video_[NN]` (video number)

### Email Funnel Metrics Tab

Create new tab in NODE_NULL_TRACKER: **Email Funnel**

| Field | Description | Capture Method |
|-------|-------------|----------------|
| `video_id` | Video number (01-09) | Manual |
| `publish_date` | Video publish date | Manual |
| `views_48h` | Total views at 48h | YouTube Studio |
| `landing_page_visits` | UTM-tracked visits | Google Analytics / Plausible |
| `email_signups` | Total signups from this video | ConvertKit / email platform |
| `signup_rate` | (Signups / Views) × 100 | Calculated |
| `email_1_opens` | Opens on Welcome email | Email platform |
| `email_5_opens` | Opens on Product Offer email | Email platform |
| `product_conversions` | Purchases from this video's cohort | Gumroad + attribution |
| `conversion_rate` | (Conversions / Signups) × 100 | Calculated |
| `revenue` | Total revenue from cohort | Gumroad |

---

## Derived Metrics (YouTube-specific)

### Retention Score (YouTube-adjusted)

Use YouTube's "Average percentage viewed" as primary retention metric:

$$\text{RetentionScore} = \text{AvgPercentageViewed}$$

(No need to calculate from duration; YouTube provides it directly)

### Engagement Score (YouTube-adjusted)

$$\text{EngagementScore} = \left(\frac{\text{Comments} + \text{Shares} + \text{Saves}}{\text{Views}}\right) \times 1000$$

### Thumbnail Performance Index

$$\text{ThumbnailIndex} = \text{CTR} \times \text{RetentionScore}$$

Higher index = effective thumbnail + strong content hold.

---

## YouTube-Specific Decision Thresholds

### Win Criteria (per video)

- Avg % viewed ≥ 40%
- CTR ≥ 3% (YouTube Shorts benchmark)
- Engagement score ≥ 20
- Email signup rate ≥ 5% (views → signups)

### Neutral Criteria

- Avg % viewed 30-40%
- CTR 2-3%
- Engagement score 10-20
- Email signup rate 2-5%

### Loss Criteria (kill signal)

- Avg % viewed < 30%
- CTR < 2%
- Engagement score < 10
- Email signup rate < 2%

### Funnel-Specific Kill Criteria

- <100 views after 48h (3 consecutive videos)
- Platform flags content
- Comments indicate brand confusion
- Email platform warns about spam complaints

---

## Thumbnail Variant Tracking

Test 2-3 thumbnail styles per vertical:

### Thumbnail Styles

| Style ID | Description |
|----------|-------------|
| `T1_question` | Question text + abstract visual |
| `T2_contrast` | Bold statement + split-screen |
| `T3_minimal` | Single word + stark visual |

Track which style performs best via CTR + retention combination.

---

## YouTube-Specific Invalid Conditions

Mark video `INVALID` if:

- Video unlisted/deleted after initial publish
- Major title/thumbnail change >6h after publish
- YouTube flags video (age-restriction, limited ads, etc.)
- Promoted via external traffic (non-organic)
- Re-uploaded due to processing errors

---

## Integration with Existing Schema

This extension **adds to** (not replaces) the base schema from [analytics/schema.md](../schema.md).

**All base fields still required:**
- Date, Platform, Vertical, Hook Type
- Duration, Visual Style, Voice Style
- Views 1h, Views 24h
- Shares, Saves, Comments
- Notes, Decision

**YouTube extension adds:**
- Title, Thumbnail Style
- Impressions, CTR
- Avg % viewed (replaces manual retention calculation)
- Traffic Source, Retention Graph Link

---

## Next Steps

1. Create **Email Funnel** tab in NODE_NULL_TRACKER
2. Set up UTM tracking in Google Analytics / Plausible
3. Configure email platform (ConvertKit) webhook → tracker automation
4. Test full capture workflow with video 01 before scaling
