# Signal Room Product Design

**Status:** Approved for implementation

## 1. Product summary

**Signal Room** is a fictional event-operations analytics product by Signal Foundry. It helps an event experience and operations lead identify attendee friction, connect it to service pressure, inspect the supporting evidence, and review a bounded next-best action.

The v1 demonstration is set at the fictional Horizon Tech Summit. It uses simulated, aggregated data and never claims to represent real attendees, customers, or a real conference.

## 2. User, problem, and success

**Primary user:** An event experience and operations lead managing a multi-session technology conference.

**User problem:** The lead cannot manually inspect every session, venue zone, queue, and service signal. They need to find the issue that is affecting attendees now, understand the evidence, and decide what to investigate or address next.

**V1 success:** In a five-minute demo, the user can select the known high-demand-session issue, see its linked evidence, understand why it triggered, and see a clearly bounded next-best action.

**V1 non-goals:** Live data ingestion, attendee-level tracking, a second dashboard tab, Sankey or radial charts, authentication, a database, an API, an LLM, LangChain, an autonomous agent, or executable operational workflows.

## 3. Conference scenario and simulated data

The fictional Horizon Tech Summit runs for one day, 9:00 a.m. to 6:00 p.m. Each CSV row is a 15-minute aggregated snapshot for one operating entity.

| Item | V1 design |
| --- | --- |
| Time windows | 36: 9:00–9:15 a.m. through 5:45–6:00 p.m. |
| Operating entities | Five session locations and three shared service zones |
| Total records | 288 (`1 day × 36 intervals × 8 entities`) |
| Data source | Seeded synthetic generator that creates one versioned operational-signal CSV |
| Privacy posture | No real attendee, customer, employee, or event data |

**Session locations:** Momentum Hall, Catalyst Theater, Circuit Lab, Studio Two, Workshop Loft.

**Shared zones:** Arrival Hub, Community Commons, Support Bar.

### Required CSV columns

| Column | Meaning |
| --- | --- |
| `timestamp` | 15-minute event-time window |
| `entity_type` | `session_location` or `shared_zone` |
| `entity_name` | Operating entity name |
| `session_title` | Named agenda item when a session location is active |
| `session_track` | Agenda track when applicable |
| `capacity` | Maximum people accommodated in the entity |
| `attendance` | Aggregated attendees present |
| `check_ins` | Aggregated arrivals or scans during the interval |
| `avg_queue_minutes` | Average queue or wait time |
| `attendee_pulse_score` | Simulated average of 1–5 attendee micro-survey ratings for the entity and 15-minute interval: sum of submitted ratings divided by `pulse_response_count`; higher is better |
| `pulse_response_count` | Number of simulated pulse responses in the interval; fewer than five responses is lower-confidence directional feedback, not a definitive experience measure |
| `app_error_rate_pct` | Percentage of relevant app interactions reporting errors |
| `support_case_count` | Number of support requests in the interval |
| `people_affected` | Estimated people affected by the observed signal |

### Designed story moments

1. **Day 1 arrival surge:** Arrival Hub shows longer queues and increased service demand from 9:00 to 9:45 a.m.
2. **Post-lunch session friction:** Catalyst Theater has high occupancy, longer queues, a lower pulse score, app errors, and increased support cases from 2:00 to 3:15 p.m. The story represents a post-lunch programming shift, while the earlier event and lunch/networking periods provide a normal baseline.
3. **Late-afternoon improvement:** The relevant signals improve later in the day. The app presents this as an observed change and does not claim that any intervention caused it.

All other periods should vary plausibly but remain within normal operating ranges. The generated data must make each designed moment easy to find and deterministic with a fixed seed.

## 4. Product experience

### Dark-theme visual system

Signal Room uses a calm **midnight operations** theme, not pure black or a high-noise command-center aesthetic. The page background is midnight navy `#0B1020`; cards and charts sit on raised navy surfaces `#141B2D` and `#1C2540`; borders use `#283554`; primary and secondary text use `#F4F7FB` and `#AAB6CF`. Cobalt `#6EA8FE` identifies selected or interactive controls, coral `#FF6B7A` identifies attention, amber `#F6C85F` identifies monitor, and mint `#5DDBB4` identifies healthy or improved conditions. Status words and icons remain visible alongside color, and Plotly charts must use the same dark surfaces, light axes, and muted gridlines.

### Live Event 360 dashboard

The dashboard answers: **Where should I look now?**

- The opening state is 2:30 p.m. with no bubble selected. Catalyst Theater is visually prominent as the largest attention-colored bubble and has a visible priority label; this invites the user to investigate it without preselecting it. The 2:30 p.m. snapshot is the third consecutive 15-minute interval of the post-lunch-session signal, making its attention status and recommendation evidence-backed.
- A 15-minute event-time replay slider from 9:00 a.m. through 5:45 p.m. controls the displayed snapshot; the final snapshot represents the 5:45–6:00 p.m. window. In a real deployment, it would expose only completed time windows; in this simulated demo, it also allows replay of the full day. A plain-language `View` control optionally groups locations as Sessions or Shared services, while the primary `Locations` filter lets the user select recognizable names such as Catalyst Theater, Arrival Hub, or Support Bar.
- KPI cards for occupancy, average queue time, attendee pulse, app error rate, and support cases. Each KPI shows its unit. The pulse KPI help text says “Average 1–5 attendee pulse rating; higher is better.” and the page states that lower response counts mean lower confidence.
- A clickable Plotly bubble chart:
  - X-axis: attendee pulse score from 1.0 to 5.0.
  - Y-axis: operations pressure, shown as support cases per 100 attendees.
  - Bubble size: people affected.
  - Bubble color and status label: healthy, monitor, or attention.
- The right-side chart is always visible. Before selection, **Overall conference pulse** shows combined occupancy and attendance-weighted average queue time for the current filters across the event day.
- Selecting a bubble replaces the overall trend with **Location performance over time: [location]** and shows that location’s status.
- The selected location’s Evidence and next-best-action section appears below the two charts. It states the triggered rule, inputs, proposed response, confidence, and limitation.
- The investigation view for the selected location contains:
  - a 15-minute timeline of occupancy and queue time;
  - a comparison of pulse score, app error rate, and support cases against the selected entity's day baseline;
  - the three consecutive intervals or current interval that triggered the rule; and
  - the deterministic recommendation, confidence, and limitation.

## 5. Deterministic findings and next-best actions

All metrics, status labels, and recommendations are calculated in pandas. The interface must show the rule and the source values used. The app may describe an observed pattern but must not claim causation.

**Operations-pressure calculation:** `support_case_count ÷ attendance × 100`. When attendance is zero, operations pressure is `N/A`; that entity is omitted from the bubble chart for that time window and the interface explains that there is insufficient attendance to calculate a comparable rate.

### Proposed v1 rules for review

| Status | Trigger | Next-best action | Action owner, timing, and confidence |
| --- | --- | --- | --- |
| Attention | Occupancy is at least 90% and average queue time is at least 12 minutes for three consecutive intervals | Open simulated overflow viewing and publish a session-routing update | Event Operations Lead, within 15 minutes; high when all three intervals are present |
| Attention | App error rate is at least 5% and support cases are at least 4 in an interval | Publish a simulated status update and staff a concierge point | Event Operations Lead, within 15 minutes; high when both signals are present |
| Monitor | A prior attention signal has queue time below 7 minutes, support cases below 3, and occupancy below 85% for two consecutive intervals | Monitor recovery; do not add a new intervention | No dispatch; medium when two recovery intervals are present |
| Insufficient evidence | No matching data, fewer than two intervals, or fewer than five pulse responses | State the limitation and do not recommend an intervention | No dispatch; low |

Every recommendation must display the suggested owner, suggested timing, and the human decision boundary: "Verify and dispatch; not automated." The high-demand Catalyst Theater story must trigger the first and second attention rules. A normal session must not trigger an attention recommendation.

## 6. Technical design

| Layer | Product | Responsibility |
| --- | --- | --- |
| Development partner | Codex | Assist with code generation, explanation, debugging, and iteration; not part of the deployed app |
| Runtime | Python and Streamlit | Application layout, filters, state, and local execution |
| Data and rules | pandas | CSV loading, validation, derived metrics, status classification, and next-best actions |
| Visual layer | Plotly | Bubble chart and linked trend |
| Testing | pytest | Known-answer tests for data generation, metrics, classifications, and recommendations |
| Version control | Git and GitHub | Private repository, reviewable branches, and submission code link |
| Optional hosting | Replit | Import and run the GitHub project after the stable local build is verified |

The implementation must use only local files. No credentials or secrets are needed for v1.

## 7. Quality, safety, and failure behavior

- Label the app and README as using simulated data.
- Show a freshness label such as `Simulated event replay · data through 2:30 p.m.` that updates with the replay slider.
- Validate required CSV columns before calculating metrics. Show a readable error if the file is missing or invalid.
- Show a clear empty state when filters return no records.
- Prevent divide-by-zero errors for capacity and response-count calculations.
- Keep filters, KPI cards, bubble selection, overall conference pulse, location trend, and evidence panel consistent with the same selected scope.
- Use status labels and text in addition to color.
- Never expose a real external action button; recommendations are informational only.

## 8. Demo and submission evidence

The intended video story is the 2:30 p.m. Catalyst Theater post-lunch issue: select its bubble, inspect the trend and evidence, and explain the deterministic recommendation.

The project documentation must include the problem statement, simulated-data description, relevant Codex prompts, meaningful iterations or bugs, screenshots of the build process and final app, and lessons learned.

## 9. Review decisions

The v1 product decisions are approved for implementation. Late-afternoon improvement is presented as an observed change, not evidence that an intervention caused it.

## 10. Acceptance criteria

- [ ] The generated CSV contains exactly 288 rows and all required columns.
- [ ] The 2:30 p.m. Catalyst Theater scenario is visible through the filters and triggers the intended attention recommendation.
- [ ] The opening state shows the filter-aware Overall conference pulse; selecting a bubble switches to that location’s trend and evidence panel.
- [ ] Operations pressure is calculated as support cases per 100 attendees; zero-attendance entities are shown as `N/A` and omitted from the bubble chart.
- [ ] The opening state shows 2:30 p.m. with no bubble selected and makes Catalyst Theater visually prominent through size, attention status, and a priority label.
- [ ] Selecting Catalyst Theater shows its recommendation and investigation metrics within the same dashboard page.
- [ ] A normal session shows either healthy or monitor status and does not trigger an attention recommendation.
- [ ] Empty or insufficient-data scopes produce a readable limitation state.
- [ ] The app runs locally with documented setup steps and can be demonstrated in five minutes or less.
