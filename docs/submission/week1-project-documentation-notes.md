# Week 1 Project Documentation Notes

Use this working file while building Signal Room. Write rough notes as they happen; turn the completed sections into the Google Doc near submission time.

## Submission checklist

- [ ] Google Doc includes the project overview, dataset, vibe-coding screenshots, prompts, iterations or bugs, and learnings.
- [ ] Video demo is five minutes or less and shows the working app live.
- [ ] GitHub repository link is accessible to the reviewer and included in the submission form.
- [ ] Submission is made through the Week 1 form.

## Project overview

**Working title:** Signal Room by Signal Foundry

**GitHub repository:** https://github.com/dsilvadeepal/signal-room-conference-ops

**Tech stack:** Python, Streamlit, pandas, Plotly, pytest, GitHub, optional Replit deployment.

**One-sentence problem statement:**

Signal Room helps an event experience and operations lead identify attendee friction, connect it to service pressure, inspect the evidence, and review a bounded next-best action.

**Who the app helps:**

An event experience and operations lead managing a multi-session technology conference.

**What the app does:**

A Streamlit dashboard presents simulated event-time signals, highlights attention-worthy bubbles, and reveals linked evidence, a synthetic attendee journey, and deterministic recommendations after a user selects a signal.

**What the app does not do:**

It uses only synthetic data and local CSVs. It does not ingest live data, track real attendees, use an API, LLM, or agent, execute an action, or claim causal effects.

## Dataset and methodology

**Data sources:** Simulated conference operations signals and synthetic attendee journey events.

**Data grain:** One 15-minute snapshot for one session location or shared service zone.

**Scale:** One day, 9:00 a.m. to 6:00 p.m.; 288 operational-signal records plus approximately 2,400 to 3,600 journey events for 600 fictional attendees.

**Columns and definitions:**

**Operational-signal CSV:** `timestamp`, `entity_type`, `entity_name`, `session_title`, `session_track`, `capacity`, `attendance`, `check_ins`, `avg_queue_minutes`, `attendee_pulse_score`, `pulse_response_count`, `app_error_rate_pct`, `support_case_count`, and `people_affected`.

**Attendee-journey CSV:** `attendee_id`, `timestamp`, `journey_stage`, `entity_name`, `session_title`, and `outcome`. All IDs are synthetic; ordered journey events support the Sankey view.

**Designed story moments:**

- [ ] Morning arrival and check-in surge
- [ ] Post-lunch high-demand session friction
- [ ] Late-afternoon improvement observed without a causal claim

**Metric and recommendation rules:**

- Operations pressure: `support_case_count / attendance * 100`; zero attendance appears as `N/A` and is omitted from the bubble chart.
- Attention rule 1: occupancy of at least 90% and queue time of at least 12 minutes for three consecutive intervals.
- Attention rule 2: app error rate of at least 5% and at least four support cases in one interval.
- Recommendation cards show evidence, owner (Event Operations Lead), timing (within 15 minutes), confidence, limitation, and “Verify and dispatch; not automated.”
- Late-afternoon improvement is observational; it is not attributed to an intervention.

## Vibe-coding build log

Capture only meaningful iterations. For each one, add a screenshot of the prompt and a screenshot of the resulting app or code change.

### Iteration 1: Dataset and scope

**Prompt used:**

<!-- Paste the relevant Codex prompt. -->

**What changed:**

<!-- What you accepted, changed, or rejected. -->

**How I verified it:**

<!-- What you checked. -->

**Screenshot placeholders:**

- [ ] Codex prompt
- [ ] Resulting schema or app view

### Iteration 2: Streamlit app scaffold

**Prompt used:**

<!-- Paste the relevant Codex prompt. -->

**What changed:**

<!-- What you accepted, changed, or rejected. -->

**How I verified it:**

<!-- What you checked. -->

**Screenshot placeholders:**

- [ ] Codex prompt
- [ ] First working app view

### Iteration 3: Linked visual interaction

**Prompt used:**

<!-- Paste the relevant Codex prompt. -->

**What changed:**

<!-- What you accepted, changed, or rejected. -->

**How I verified it:**

<!-- Confirm that selecting a bubble updates the linked evidence. -->

**Screenshot placeholders:**

- [ ] Codex prompt
- [ ] Selected bubble with linked evidence

### Iteration 4: Deterministic recommendations

**Prompt used:**

<!-- Paste the relevant Codex prompt. -->

**What changed:**

<!-- Explain why recommendations are rule-based and bounded. -->

**How I verified it:**

<!-- Check a known issue and a normal scenario. -->

**Screenshot placeholders:**

- [ ] Codex prompt
- [ ] Evidence and next-best-action panel

### Iteration 5: Visual refinement and quality checks

**Prompt used:**

<!-- Paste the relevant Codex prompt. -->

**What changed:**

<!-- Note design improvements, bug fixes, empty states, or readability improvements. -->

**How I verified it:**

<!-- Record the final visual and functional check. -->

**Screenshot placeholders:**

- [ ] Before or issue state
- [ ] Final dashboard state

## Bugs and decisions

| Issue or decision | What happened | Resolution | What I learned |
| --- | --- | --- | --- |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |

## Learnings and observations

- What Codex accelerated:
- Where product judgment was still necessary:
- What I learned about Streamlit and Plotly:
- Why transparent, deterministic recommendations mattered here:
- What I would add next with real data and appropriate human approval:

## Final screenshots for the Google Doc

- [ ] Full Live Event 360 dashboard
- [ ] Selected high-demand session bubble
- [ ] Linked trend and evidence panel
- [ ] Next-best-action recommendation
- [ ] Journey and Operations view
- [ ] Vibe-coding process screenshots from the build log

## Video demo outline

- [ ] Introduce the user problem and simulated-data disclaimer.
- [ ] Show the Live Event 360 dashboard and filters.
- [ ] Select the high-demand-session bubble.
- [ ] Explain the linked evidence and deterministic next-best action.
- [ ] Show the Journey and Operations tab.
- [ ] Explain how Codex supported the build and one lesson learned.
