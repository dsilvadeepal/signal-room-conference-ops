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

- [x] Morning arrival and check-in surge
- [x] Post-lunch high-demand session friction
- [x] Late-afternoon improvement observed without a causal claim

**Metric and recommendation rules:**

- Operations pressure: `support_case_count / attendance * 100`; zero attendance appears as `N/A` and is omitted from the bubble chart.
- Attendee pulse score: the simulated average of 1–5 attendee micro-survey ratings for an entity during the selected 15-minute interval: `sum of submitted ratings / pulse_response_count`. Higher is better. The CSV contains only the synthetic aggregate and response count, not individual responses or PII.
- Pulse-score interpretation: low response counts should be treated as lower-confidence directional feedback, not a definitive measure of every attendee's experience.
- Attention rule 1: occupancy of at least 90% and queue time of at least 12 minutes for three consecutive intervals.
- Attention rule 2: app error rate of at least 5% and at least four support cases in one interval.
- Recommendation cards show evidence, owner (Event Operations Lead), timing (within 15 minutes), confidence, limitation, and “Verify and dispatch; not automated.”
- Late-afternoon improvement is observational; it is not attributed to an intervention.

## Vibe-coding build log

Capture only meaningful iterations. For each one, add a screenshot of the prompt and a screenshot of the resulting app or code change.

**Capture rule:** Take one screenshot of the relevant Codex conversation and one of the resulting artifact or test output for each iteration below. The summaries are factual build notes; replace the “prompt used” reference with the exact conversation screenshot rather than recreating a prompt later.

### Iteration 1: Product scope and UX contract

**Prompt used:**

Capture the conversation where the single-day conference scope, 2:30 p.m. opening state, Catalyst Theater signal story, and in-page investigation interaction were approved.

**What changed:**

Defined Signal Room as a synthetic, deterministic Streamlit data app—not an API, LLM, LangChain, or autonomous-agent project. Accepted one dashboard with two tabs and no routing.

**How I verified it:**

Reviewed the approved PRD and implementation plan before code work began.

**Screenshot placeholders:**

- [ ] Codex prompt
- [ ] Resulting schema or app view

### Iteration 2: Runnable Streamlit scaffold and dependency workflow

**Prompt used:**

Capture the request to start Task 1 and the decision to use `uv` for Python dependencies.

**What changed:**

Created the Streamlit shell, `pyproject.toml`, `uv.lock`, package structure, and a smoke test. Replaced a hand-managed requirements workflow with `uv sync` and `uv run`.

**How I verified it:**

Ran the smoke test and opened the local Streamlit server; no credentials were required.

**Screenshot placeholders:**

- [ ] Codex prompt
- [ ] First working app view

### Iteration 3: Deterministic synthetic data

**Prompt used:**

Capture the request to proceed to Task 2 and the generator/test implementation conversation.

**What changed:**

Generated 288 conference-signal records and 2,720 ordered journey events for 600 fictional attendees. Embedded the morning arrival surge, post-lunch Catalyst friction, and late-afternoon improvement story moments.

**How I verified it:**

Ran generator tests and generated the CSVs twice; the SHA-256 hashes matched, proving repeatability for the same seed.

**Screenshot placeholders:**

- [ ] Codex conversation
- [ ] CSV schema or deterministic-hash terminal output

### Iteration 4: Deterministic recommendation logic

**Prompt used:**

Capture the request to proceed to Task 3 and the known-answer analytics test conversation.

**What changed:**

Built pandas-based rules for operations pressure, three consecutive high-occupancy/high-queue intervals, and app-error/support-case signals. Recommendation copy includes an owner, timing, confidence, limitation, and a human decision boundary.

**How I verified it:**

Known-answer tests covered zero attendance, Catalyst Theater attention, normal-session monitoring, missing columns, and bounded evidence output.

**Screenshot placeholders:**

- [ ] Codex prompt
- [ ] Evidence and next-best-action panel

### Iteration 5: Live Event 360 interaction

**Prompt used:**

Capture the request to proceed to Task 4 and the bubble-chart/selection implementation conversation.

**What changed:**

Added a replay-time slider, KPI cards, status-colored Plotly bubbles, a no-selection state that visually calls out Catalyst Theater at 2:30 p.m., and a selected-entity trend chart. Refined the dashboard with a midnight operations theme, pulse-score help/confidence copy, a location-first filter, and explicit selection-clearing behavior.

**How I verified it:**

Figure tests verify that ineligible entities are excluded, bubble selection carries `entity_name` through Plotly custom data, and the selected entity’s trend is rendered. Capture the manual click-through after the task is complete.

**Screenshot placeholders:**

- [ ] Codex conversation
- [ ] Unselected 2:30 p.m. dashboard state
- [ ] Selected bubble with trend state

### Iteration 6: Product-language and interaction refinement

**Prompt used:**

Capture the conversations that questioned the pulse-score definition, technical `entity type` filter, dark-theme direction, and sticky bubble selection behavior.

**What changed:**

Defined pulse as a simulated average 1–5 micro-survey rating with a response-count confidence caveat. Replaced the technical primary filter with recognizable `Locations`, retained a plain-language `View` grouping, specified a midnight token system, and added `Clear selection` plus filter-scope clearing.

**How I verified it:**

Ran the full test suite after the changes. The selection-state test covers a selected bubble, empty chart selection, and a changed filter scope. Capture a manual dashboard check showing the help tooltip, a selected bubble, and `Clear selection`.

**Screenshot placeholders:**

- [ ] Codex conversation showing the product judgment
- [ ] Pulse help tooltip and low-confidence caveat
- [ ] Locations and View filters
- [ ] Selected state and Clear selection control

## Bugs and decisions

| Issue or decision | What happened | Resolution | What I learned |
| --- | --- | --- | --- |
| Streamlit could not import `signal_room` | `uv run pytest` passed because pytest used its configured `src/` path, but `uv run streamlit run app.py` raised `ModuleNotFoundError: No module named 'signal_room'`. | Added package build configuration to `pyproject.toml` and ran `uv sync`, which installed Signal Room into the local environment. | A passing test path does not automatically prove the production runtime can import the same package. Verify the actual app command. |
| Define attendee pulse score before the next dashboard slice | The dashboard shows a 1–5 pulse score, but the current documentation does not yet state what a score represents or how the synthetic aggregate is calculated. | Pending product/data iteration: document the simulated response scale and aggregation method, then add it to the data dictionary and dashboard help text. | A metric must be interpretable before it is used as a visual axis or decision signal. |
| Shift the dashboard to a midnight operations theme | The initial UX contract specified a light startup palette, but the desired product character is a dark, modern analytics experience. | Use midnight navy surfaces, bright neutral text, cobalt interaction, and the same coral/amber/mint status hierarchy; avoid pure black and retain text labels with every status color. | Theme changes need a complete token system—page, surfaces, borders, text, charts, and interaction—not only new bubble colors. |
|  |  |  |  |
|  |  |  |  |

## Learnings and observations

- What Codex accelerated: converting an approved product/UX contract into a runnable Streamlit scaffold, seeded CSV generator, known-answer tests, deterministic analytics functions, and Plotly dashboard components.
- Where product judgment was still necessary: The initial filter exposed `entity type`—a useful data-model field, but not a clear event-operator concept. Reframed it as a plain-language `View` grouping (All locations, Sessions, Shared services) and made recognizable location names—such as Catalyst Theater, Arrival Hub, and Support Bar—the primary `Locations` filter.
- What I learned about Streamlit and Plotly: pytest can pass while the Streamlit runtime still fails, so the real `uv run streamlit run app.py` path must be tested. Plotly selection needs explicit session-state rules and a visible clear action; users should not have to infer how to “unclick” a bubble.
- Why transparent, deterministic recommendations mattered here: every suggestion can show its thresholds, raw inputs, owner, timing, confidence, limitation, and human decision boundary. This is more appropriate than claiming an opaque model knows the root cause or can take action automatically.
- What I would add next with real data and appropriate human approval: completed-window event ingestion, appropriately consented attendee feedback, monitored data-quality checks, role-based access, and a human-approved workflow connection for operational dispatch.

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
