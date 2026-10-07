# Signal Room Product Design

**Status:** Draft for product and engineering review

## 1. Product summary

**Signal Room** is a fictional event-operations analytics product by Signal Foundry. It helps an event experience and operations lead identify attendee friction, connect it to service pressure, inspect the supporting evidence, and review a bounded next-best action.

The v1 demonstration is set at the fictional Horizon Tech Summit. It uses simulated, aggregated data and never claims to represent real attendees, customers, or a real conference.

## 2. User, problem, and success

**Primary user:** An event experience and operations lead managing a multi-session technology conference.

**User problem:** The lead cannot manually inspect every session, venue zone, queue, and service signal. They need to find the issue that is affecting attendees now, understand the evidence, and decide what to investigate or address next.

**V1 success:** In a five-minute demo, the user can select the known high-demand-session issue, see its linked evidence, understand why it triggered, and see a clearly bounded next-best action.

**V1 non-goals:** Live data ingestion, attendee-level tracking, authentication, a database, an API, an LLM, LangChain, an autonomous agent, or executable operational workflows.

## 3. Conference scenario and simulated data

The fictional Horizon Tech Summit runs for one day, 9:00 a.m. to 6:00 p.m. Each CSV row is a 15-minute aggregated snapshot for one operating entity.

| Item | V1 design |
| --- | --- |
| Time windows | 36: 9:00–9:15 a.m. through 5:45–6:00 p.m. |
| Operating entities | Five session locations and three shared service zones |
| Total records | 288 (`1 day × 36 intervals × 8 entities`) |
| Data sources | Seeded synthetic generator that creates versioned operational-signal and attendee-journey CSVs |
| Privacy posture | No real attendee, customer, employee, or event data; journey IDs are synthetic |

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
| `attendee_pulse_score` | Aggregated satisfaction pulse from 1.0 to 5.0 |
| `pulse_response_count` | Number of pulse responses in the interval |
| `app_error_rate_pct` | Percentage of relevant app interactions reporting errors |
| `support_case_count` | Number of support requests in the interval |
| `people_affected` | Estimated people affected by the observed signal |

### Attendee journey records

The Sankey visual uses a second synthetic event-log CSV rather than inferring individual movement from aggregated operational data. It represents 600 fictional attendees with synthetic IDs and ordered journey events. Each attendee has an arrival event, an exit event, and two to four intermediate events, resulting in approximately 2,400 to 3,600 journey records.

| Column | Meaning |
| --- | --- |
| `attendee_id` | Synthetic, non-identifying attendee ID |
| `timestamp` | Event-time of the journey touchpoint |
| `journey_stage` | `arrival`, `session`, `community`, `support`, or `exit` |
| `entity_name` | Venue zone or session location associated with the touchpoint |
| `session_title` | Agenda item when the touchpoint is a session |
| `outcome` | Simulated completion, support-needed, or rerouted outcome |

### Designed story moments

1. **Day 1 arrival surge:** Arrival Hub shows longer queues and increased service demand from 9:00 to 9:45 a.m.
2. **Post-lunch session friction:** Catalyst Theater has high occupancy, longer queues, a lower pulse score, app errors, and increased support cases from 2:00 to 3:15 p.m. The story represents a post-lunch programming shift, while the earlier event and lunch/networking periods provide a normal baseline.
3. **Late-afternoon improvement:** The relevant signals improve later in the day. The app presents this as an observed change and does not claim that any intervention caused it.

All other periods should vary plausibly but remain within normal operating ranges. The generated data must make each designed moment easy to find and deterministic with a fixed seed.

## 4. Product experience

### Live Event 360 tab

The default tab answers: **Where should I look now?**

- The opening state is 2:30 p.m. with no bubble selected. Catalyst Theater is visually prominent as the largest attention-colored bubble and has a visible priority label; this invites the user to investigate it without preselecting it. The 2:30 p.m. snapshot is the third consecutive 15-minute interval of the post-lunch-session signal, making its attention status and recommendation evidence-backed.
- A 15-minute event-time replay slider from 9:00 a.m. through 5:45 p.m. controls the displayed snapshot; the final snapshot represents the 5:45–6:00 p.m. window. In a real deployment, it would expose only completed time windows; in this simulated demo, it also allows replay of the full day. Entity type and entity filters further narrow the view.
- KPI cards for occupancy, average queue time, attendee pulse, app error rate, and support cases. Each KPI shows its unit.
- A clickable Plotly bubble chart:
  - X-axis: attendee pulse score from 1.0 to 5.0.
  - Y-axis: operations pressure, shown as support cases per 100 attendees.
  - Bubble size: people affected.
  - Bubble color and status label: healthy, monitor, or attention.
- Selecting a bubble populates the right-side recommendation panel and updates all linked details on the page.
- A linked time trend shows occupancy, queue time, support cases, and pulse score for the selected entity across the relevant day.
- An Evidence and next-best-action panel states the triggered rule, inputs, proposed response, confidence, and limitation.
- Clicking the recommendation panel opens an investigation view for the selected entity. It contains:
  - a 15-minute timeline of occupancy and queue time;
  - a comparison of pulse score, app error rate, and support cases against the selected entity's day baseline;
  - the three consecutive intervals or current interval that triggered the rule; and
  - the deterministic recommendation, confidence, and limitation.

### Journey and Operations tab

The second tab answers: **How are the event journey and operational health connected?**

- A Sankey-style summary of actual ordered flows in the synthetic attendee journey records: arrival, session attendance, community engagement, support interaction, and exit.
- A radial health profile for the selected entity across occupancy, queue time, attendee pulse, app reliability, and service load.
- A selected-entity summary consistent with the first tab's filters and status.

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
| Runtime | Python and Streamlit | Application layout, filters, state, tabs, and local execution |
| Data and rules | pandas | CSV loading, validation, derived metrics, status classification, and next-best actions |
| Visual layer | Plotly | Bubble chart, linked trend, Sankey summary, and radial health profile |
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
- Keep filters, KPI cards, bubble selection, trend, radial profile, Sankey summary, and evidence panel consistent with the same selected scope.
- Use status labels and text in addition to color.
- Never expose a real external action button; recommendations are informational only.

## 8. Demo and submission evidence

The intended video story is the 2:30 p.m. Catalyst Theater post-lunch issue: select its bubble, inspect the trend and evidence, explain the deterministic recommendation, then show Journey and Operations.

The project documentation must include the problem statement, simulated-data description, relevant Codex prompts, meaningful iterations or bugs, screenshots of the build process and final app, and lessons learned.

## 9. Review decisions

The v1 product decisions are approved for implementation. Late-afternoon improvement is presented as an observed change, not evidence that an intervention caused it.

## 10. Acceptance criteria

- [ ] The generated CSV contains exactly 288 rows and all required columns.
- [ ] The 2:30 p.m. Catalyst Theater scenario is visible through the filters and triggers the intended attention recommendation.
- [ ] Selecting its bubble updates the linked trend and evidence panel.
- [ ] Operations pressure is calculated as support cases per 100 attendees; zero-attendance entities are shown as `N/A` and omitted from the bubble chart.
- [ ] The opening state shows 2:30 p.m. with no bubble selected and makes Catalyst Theater visually prominent through size, attention status, and a priority label.
- [ ] Selecting Catalyst Theater populates its recommendation; clicking that recommendation opens its investigation metrics within the same dashboard page.
- [ ] A normal session shows either healthy or monitor status and does not trigger an attention recommendation.
- [ ] Empty or insufficient-data scopes produce a readable limitation state.
- [ ] The app runs locally with documented setup steps and can be demonstrated in five minutes or less.
