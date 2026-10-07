# Signal Room Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a local, deterministic Streamlit conference-operations dashboard that turns simulated event signals into evidence-backed next-best actions.

**Architecture:** A seeded Python generator creates two versioned CSVs: 288 aggregated operating-signal snapshots and synthetic attendee journey events for 600 fictional attendees. pandas validates and derives metrics, statuses, and recommendations; Streamlit renders the two tabs; Plotly renders linked interactive visuals. Pure data and rule functions are tested with pytest before the UI consumes them.

**Tech Stack:** Python 3.11, Streamlit, pandas, Plotly, pytest, GitHub, optional Replit deployment.

**Spec:** `docs/superpowers/specs/2026-10-07-signal-room-design.md`

## Global Constraints

- Use only synthetic local CSVs; do not add credentials, APIs, databases, LLMs, LangChain, agents, D3, or executable workflows.
- `data/conference_signals.csv` contains exactly 288 rows: 36 windows from 9:00–9:15 a.m. through 5:45–6:00 p.m. for eight entities.
- `data/attendee_journeys.csv` contains 600 synthetic attendee IDs with an arrival, an exit, and two to four intermediate journey events each.
- Open Live Event 360 at 2:30 p.m. with no selected bubble; make Catalyst Theater visually prominent but do not preselect it.
- Calculate operations pressure as `support_case_count / attendance * 100`; zero attendance is `N/A` and excludes the entity from the bubble chart.
- Recommendations are informational only and display rule, inputs, owner, timing, confidence, limitation, and “Verify and dispatch; not automated.”
- Label all app and documentation views as simulated data. State observed late-afternoon improvement without claiming causation.

## Review Focus

- Missing required operational columns produce a readable validation error rather than a pandas traceback. Covered in Task 2.
- Zero attendance never creates an infinite rate or a plotted bubble. Covered in Task 3.
- Attention requires three correctly ordered consecutive intervals, not three arbitrary matching rows. Covered in Task 3.
- A filter scope with no records clears the recommendation and shows an empty state. Covered in Task 4 manual verification.
- Sankey flow totals are derived from ordered synthetic journeys, not inferred from the aggregate signal CSV. Covered in Task 6.

---

## UX contract and wireframes

**Product character:** Signal Room is a polished, light event-operations product. It should feel like a startup analytics tool for a busy event lead: spacious, calm, and immediately scannable rather than a dark command center or a generic spreadsheet dashboard.

**Visual tokens:** Use a cool near-white page background, deep navy text, cobalt for selected/interactable controls, coral for attention, amber for monitor, mint for healthy/improved, and text labels alongside every status color. Do not use color as the only status signal.

### Live Event 360 opening state

```text
┌────────────────────────────────────────────────────────────────────────────┐
│ Signal Room by Signal Foundry       Simulated event replay · 2:30 p.m.    │
│ Horizon Tech Summit                  [ Live Event 360 ] [ Journey & Ops ] │
├────────────────────────────────────────────────────────────────────────────┤
│ Event time: 9:00 ───────────────●────────────── 5:45                      │
│ [All entities ▼]  [All entity types ▼]                                    │
├───────────────┬───────────────┬───────────────┬────────────────────────────┤
│ Occupancy     │ Queue time    │ Pulse score   │ Support cases              │
│  ... %        │ ... min       │ ... / 5       │ ...                        │
├───────────────────────────────────────────────┬────────────────────────────┤
│                                               │ Select a signal            │
│  Attendee pulse score                         │ Catalyst Theater is marked │
│                                               │ Priority in the chart.     │
│               ● Catalyst Theater              │ No recommendation appears  │
│                                               │ until a bubble is selected.│
│  Bubble chart:                                 │                            │
│  x = pulse, y = operations pressure,          │                            │
│  size = people affected                       │                            │
│                                               │                            │
└───────────────────────────────────────────────┴────────────────────────────┘
```

- Default time is 2:30 p.m.; no bubble is selected.
- Catalyst Theater is the largest coral `Attention · Priority` bubble at that time. Its label must remain visible without hover.
- The right rail is an instructional empty state until a user selects a bubble.
- Filter or time changes clear an invalid prior selection and restore the empty state.

### Selected-signal and investigation state

```text
┌───────────────────────────────────────────────┬────────────────────────────┐
│ Bubble chart, selected Catalyst Theater        │ Attention · Catalyst Theater│
│                                                │ Rule: capacity + queue      │
│                                                │ Suggested owner: Event Ops  │
│                                                │ Within 15 minutes           │
│                                                │ [ Investigate this signal ] │
├───────────────────────────────────────────────┴────────────────────────────┤
│ Investigation: Catalyst Theater · 2:30 p.m.                                │
│ [Occupancy + queue timeline]      [Pulse, app error, support vs baseline] │
│ Trigger evidence: 2:00 · 2:15 · 2:30                                     │
│ Recommendation, confidence, limitation, and human decision boundary        │
└────────────────────────────────────────────────────────────────────────────┘
```

- Selecting a bubble populates the recommendation card; it does not immediately expand the investigation.
- The visible `Investigate this signal` button expands the investigation **within the same page**. It must not navigate to a new page.
- The evidence section shows raw metrics and triggering intervals before recommendation prose.
- Recommendations say “suggested next step,” never “automatic action,” “root cause,” or “this action will fix the issue.”

### Journey and Operations tab

```text
┌────────────────────────────────────────────────────────────────────────────┐
│ Journey and Operations        Same time/filter context and replay label    │
├───────────────────────────────────────────────┬────────────────────────────┤
│ Aggregated synthetic attendee flows            │ Selected entity health     │
│ Arrival → Session → Community → Exit           │ radial: occupancy, queue,  │
│                   ↘ Support → Exit             │ pulse, app, service load   │
└───────────────────────────────────────────────┴────────────────────────────┘
```

- The Sankey is labeled as a synthetic attendee-journey view.
- Without a selected entity, the radial area explains that the user should select a bubble on Live Event 360.
- The Sankey and radial profile retain the active event-time/filter context; they do not silently use a different scope.

### Navigation and shared state

- Use one Streamlit application with `st.tabs(["Live Event 360", "Journey and Operations"])`; do not use multipage routing, URL routing, or `st.switch_page` in v1.
- Place the event-time replay slider and entity filters above the tabs so they apply to both views.
- Store `selected_entity`, `selected_timestamp`, and `show_investigation` in Streamlit session state.
- A manual tab switch preserves a valid selected entity: Live Event 360 explains its recommendation; Journey and Operations uses it for the radial profile.
- A change to time, entity type, or entity filter clears the selection and investigation state before either tab rerenders. This prevents the second tab from showing a stale profile for a different snapshot.
- Selecting a bubble does not automatically navigate away from Live Event 360. The user chooses the Journey and Operations tab when they want the broader journey view.

### Responsive and accessibility requirements

- At narrow widths, stack the recommendation rail below the bubble chart and stack charts vertically.
- Use descriptive chart titles, metric units, status text, keyboard-operable buttons, and readable empty states.
- Keep interactive targets visually distinct; never make a chart hover state the only way to discover the priority signal.

---

## File structure

| Path | Responsibility |
| --- | --- |
| `app.py` | Streamlit entry point, session state, filters, tab layout, and in-page interaction orchestration. |
| `src/signal_room/data_generation.py` | Seeded generation and writing of both synthetic CSVs. |
| `src/signal_room/analytics.py` | Schema validation, derived metrics, status/rule evaluation, and investigation evidence. |
| `src/signal_room/journeys.py` | Ordered journey validation, Sankey flow aggregation, and radial-profile inputs. |
| `src/signal_room/visuals.py` | Plotly bubble, trend, Sankey, and radial figure construction. |
| `scripts/generate_data.py` | Command-line entry point that writes the two data files. |
| `tests/` | Known-answer tests for generator, analytics, and journey behavior. |
| `data/` | Versioned generated CSVs used by the local app and demo. |
| `README.md` | Setup, architecture, simulated-data disclosure, demo path, and optional Replit handoff. |

### Task 1: Bootstrap the runnable project

**Files:**
- Create: `.gitignore`, `requirements.txt`, `README.md`, `app.py`, `src/signal_room/__init__.py`, `tests/test_smoke.py`

**Interfaces:**
- Produces: an importable `signal_room` package and a runnable `app.py` entry point for later tasks.

- [x] **Step 1: Write the failing smoke test**

```python
def test_package_imports():
    import signal_room
```

- [x] **Step 2: Run the test to verify it fails**

Run: `python -m pytest tests/test_smoke.py -v`

Expected: FAIL because `signal_room` does not exist.

- [x] **Step 3: Add the minimal project configuration and package**

Create `requirements.txt` with Streamlit, pandas, Plotly, and pytest. Add `.gitignore` entries for `.venv/`, `.env`, `.streamlit/secrets.toml`, `__pycache__/`, and `.pytest_cache/`. Create an `app.py` that renders the Signal Room title and “Simulated event replay” label. Create the package initializer.

- [x] **Step 4: Verify the baseline**

Run: `python -m pytest tests/test_smoke.py -v` and `streamlit run app.py`.

Expected: smoke test passes; the local page loads without requiring credentials.

- [x] **Step 5: Commit the runnable baseline**

```bash
git add -- .gitignore requirements.txt README.md app.py src/signal_room/__init__.py tests/test_smoke.py
git commit -m "Build Signal Room project scaffold"
```

### Task 2: Generate and validate synthetic data

**Files:**
- Create: `src/signal_room/data_generation.py`, `scripts/generate_data.py`, `tests/test_data_generation.py`, `data/conference_signals.csv`, `data/attendee_journeys.csv`
- Modify: `README.md`

**Interfaces:**
- Produces: `generate_conference_signals(seed: int) -> pandas.DataFrame`, `generate_attendee_journeys(seed: int) -> pandas.DataFrame`, and `write_demo_data(output_dir: pathlib.Path, seed: int) -> tuple[pathlib.Path, pathlib.Path]`.
- Consumes: fixed conference schedule and entity constants defined in `data_generation.py`.

- [x] **Step 1: Write the failing generator and schema tests**

Test that the signal generator produces exactly 288 rows, 36 unique timestamps, eight entities per timestamp, and the required columns. Test that the journey generator produces exactly 600 distinct IDs, each with `arrival` first, `exit` last, and four through six total events.

- [x] **Step 2: Run the tests to verify they fail**

Run: `python -m pytest tests/test_data_generation.py -v`

Expected: FAIL because the generator functions do not exist.

- [x] **Step 3: Implement seeded signal and journey generation**

Use one fixed integer seed. Generate normal variation plus the 9:00–9:45 arrival surge, 2:00–3:15 Catalyst Theater friction, and late-afternoon observed improvement. Ensure the Catalyst snapshot at 2:30 has three consecutive qualifying capacity/queue windows and qualifying app-error/support values. Generate journey records whose ordered flows reflect increased Catalyst attendance and support events during the 2:00–3:15 interval.

- [x] **Step 4: Write the CSVs and verify deterministic output**

Run: `python scripts/generate_data.py` followed by `python -m pytest tests/test_data_generation.py -v`.

Expected: both CSVs are written under `data/`; all tests pass; rerunning with the same seed produces the same files.

- [x] **Step 5: Document and commit the data contract**

Add the two-file data explanation and simulated-data disclosure to `README.md`.

```bash
git add -- src/signal_room/data_generation.py scripts/generate_data.py tests/test_data_generation.py data/conference_signals.csv data/attendee_journeys.csv README.md
git commit -m "Generate deterministic conference data"
```

### Task 3: Implement metrics and rule-based recommendations

**Files:**
- Create: `src/signal_room/analytics.py`, `tests/test_analytics.py`

**Interfaces:**
- Produces: `validate_signal_data(signals: pandas.DataFrame) -> None`, `add_derived_metrics(signals: pandas.DataFrame) -> pandas.DataFrame`, `evaluate_rules(signals: pandas.DataFrame) -> pandas.DataFrame`, and `investigation_evidence(evaluated: pandas.DataFrame, entity_name: str, timestamp: pandas.Timestamp) -> dict[str, object]`.
- Consumes: `conference_signals.csv` columns from Task 2.

- [ ] **Step 1: Write failing known-answer tests**

Cover these cases:

- `support_case_count=4`, `attendance=80` yields operations pressure `5.0`.
- `attendance=0` yields `N/A` and `plot_eligible=False`.
- Catalyst rows at 2:00, 2:15, and 2:30 with occupancy at least 90% and queue at least 12 trigger the capacity-and-queue attention rule at 2:30 only.
- A 2:30 row with app error rate at least 5% and at least four support cases triggers the app-and-support attention rule.
- A normal session does not trigger attention.
- Missing required columns raise a readable `ValueError` listing the missing names.

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python -m pytest tests/test_analytics.py -v`

Expected: FAIL because analytics functions do not exist.

- [ ] **Step 3: Implement the analytics interfaces**

Sort rule evaluation by `entity_name` and `timestamp`. Add derived columns for `occupancy_rate`, `operations_pressure_per_100`, `plot_eligible`, `status`, `rule_id`, `next_best_action`, `owner`, `timing`, `confidence`, and `limitation`. The evidence dictionary must contain raw values, triggering timestamps, and the human decision boundary.

- [ ] **Step 4: Verify all rule behavior**

Run: `python -m pytest tests/test_analytics.py -v`.

Expected: all known-answer tests pass, including three-consecutive-window ordering and zero-attendance behavior.

- [ ] **Step 5: Commit the deterministic decision layer**

```bash
git add -- src/signal_room/analytics.py tests/test_analytics.py
git commit -m "Add deterministic signal recommendations"
```

### Task 4: Build Live Event 360 and selection behavior

**Files:**
- Create: `src/signal_room/visuals.py`
- Modify: `app.py`, `tests/test_smoke.py`

**Interfaces:**
- Produces: `build_bubble_chart(snapshot: pandas.DataFrame) -> plotly.graph_objects.Figure` and `build_trend_chart(entity_history: pandas.DataFrame) -> plotly.graph_objects.Figure`.
- Consumes: evaluated signal data from Task 3 and the user-selected replay timestamp.

- [ ] **Step 1: Extend the smoke test with figure tests**

Test that the bubble figure excludes `plot_eligible=False` rows, includes `entity_name` as Plotly custom data for selection, and assigns Catalyst Theater an attention marker at 2:30. Test that the trend figure includes the selected entity history.

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python -m pytest tests/test_smoke.py -v`

Expected: FAIL because the figure builders do not exist.

- [ ] **Step 3: Implement the Live Event 360 tab from the UX contract**

Use a 9:00 a.m.–5:45 p.m. 15-minute slider with default `2:30 p.m.`. Default to no selected entity. Build KPI cards with units, the bubble chart with pulse score on x, operations pressure on y, people affected as size, and explicit healthy/monitor/attention labels. Use `st.plotly_chart(..., on_select="rerun", selection_mode="points")`; read `entity_name` from custom data and persist it in Streamlit session state. Show a readable empty state when filters return no eligible bubbles.

- [ ] **Step 4: Verify selection manually and with tests**

Run: `python -m pytest tests/test_smoke.py -v` and `streamlit run app.py`.

Expected: the unselected 2:30 view highlights Catalyst Theater without selecting it; selecting a bubble updates the trend and clears or replaces the previous selection correctly.

- [ ] **Step 5: Commit the first end-to-end dashboard slice**

```bash
git add -- app.py src/signal_room/visuals.py tests/test_smoke.py
git commit -m "Build Live Event 360 dashboard"
```

### Task 5: Add investigation evidence and recommendation interaction

**Files:**
- Modify: `app.py`, `src/signal_room/analytics.py`, `tests/test_analytics.py`

**Interfaces:**
- Consumes: selected entity state from Task 4 and `investigation_evidence` from Task 3.
- Produces: a right-side recommendation card and an in-page investigation section.

- [ ] **Step 1: Write failing investigation-evidence tests**

Test that Catalyst at 2:30 returns both attention rules, the 2:00/2:15/2:30 trigger timestamps, owner `Event Operations Lead`, timing `Within 15 minutes`, and the exact human boundary text. Test that a normal session returns no dispatch recommendation.

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python -m pytest tests/test_analytics.py -v`

Expected: FAIL because the required evidence fields are absent or incomplete.

- [ ] **Step 3: Implement recommendation and in-page investigation UX from the selected-signal wireframe**

After a bubble selection, render the recommendation card in the right column. Use a visible `Investigate this signal` button in that card to reveal the in-page investigation section. Show the occupancy/queue timeline, baseline comparison for pulse/app errors/support cases, triggering intervals, raw values, confidence, limitation, owner, timing, and the exact non-automation statement.

- [ ] **Step 4: Verify the complete hero flow**

Run: `python -m pytest tests/test_analytics.py -v` and `streamlit run app.py`.

Expected: selecting Catalyst Theater at 2:30 populates the card; clicking `Investigate this signal` shows evidence without changing pages; normal sessions do not imply an unsupported action.

- [ ] **Step 5: Commit the investigation workflow**

```bash
git add -- app.py src/signal_room/analytics.py tests/test_analytics.py
git commit -m "Add recommendation investigation flow"
```

### Task 6: Build Journey and Operations

**Files:**
- Create: `src/signal_room/journeys.py`, `tests/test_journeys.py`
- Modify: `src/signal_room/visuals.py`, `app.py`

**Interfaces:**
- Produces: `validate_journey_data(journeys: pandas.DataFrame) -> None`, `build_journey_flows(journeys: pandas.DataFrame) -> pandas.DataFrame`, `build_sankey_chart(flows: pandas.DataFrame) -> plotly.graph_objects.Figure`, and `build_radial_chart(selected_snapshot: pandas.Series) -> plotly.graph_objects.Figure`.
- Consumes: ordered journey records from Task 2 and selected entity signal data from Task 4.

- [ ] **Step 1: Write failing journey tests**

Test that every journey begins with arrival and ends with exit, each Sankey flow comes from adjacent ordered events for the same attendee, and total flow counts equal the number of adjacent event pairs. Test that the radial chart uses occupancy, queue, pulse, app reliability, and service load values from the selected snapshot.

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python -m pytest tests/test_journeys.py -v`

Expected: FAIL because journey functions do not exist.

- [ ] **Step 3: Implement the second dashboard tab from the Journey and Operations wireframe**

Create the Journey and Operations tab. Render the Sankey from journey-event transitions, not operational estimates. Render the radial profile only after an entity selection; otherwise show a clear prompt to select a bubble on Live Event 360. Keep the same simulated-data label and selected-entity context across both tabs.

- [ ] **Step 4: Verify the journey view**

Run: `python -m pytest tests/test_journeys.py -v` and `streamlit run app.py`.

Expected: Sankey totals reconcile to the journey event log; selecting Catalyst Theater gives a consistent radial profile; no selection yields an explanatory empty state.

- [ ] **Step 5: Commit the second tab**

```bash
git add -- app.py src/signal_room/journeys.py src/signal_room/visuals.py tests/test_journeys.py
git commit -m "Add journey and operations view"
```

### Task 7: Polish, document, and prepare the submission

**Files:**
- Create: `.streamlit/config.toml`, `docs/data-dictionary.md`
- Modify: `README.md`, `app.py`, `docs/submission/week1-project-documentation-notes.md`

**Interfaces:**
- Produces: a readable local application, a data dictionary, and instructions for a reviewer to run or import the repository into Replit.

- [ ] **Step 1: Add final acceptance tests and copy checks**

Add tests that the generator contains the 2:30 Catalyst attention scenario, normal sessions do not alert, and no recommendation copy claims that a late-afternoon improvement was caused by an intervention.

- [ ] **Step 2: Run the tests to verify any final gaps**

Run: `python -m pytest -q`.

Expected: any missing acceptance behavior is reported before polish is marked complete.

- [ ] **Step 3: Apply the visual and documentation finish**

Add the initial light startup palette: cool near-white background, deep navy text, cobalt interaction state, coral attention, amber monitor, and mint healthy state. Add metric units, empty states, simulated-data/freshness labels, accessible status text, setup instructions, architecture summary, data dictionary, and optional Replit import steps. Update the submission tracker with actual prompts, screenshots, bugs, and learnings as they occur; do not invent evidence.

- [ ] **Step 4: Run final verification**

Run: `python -m pytest -q`, `git diff --check`, and `streamlit run app.py`.

Expected: all tests pass, no whitespace errors exist, the app opens locally, all filters remain consistent, and the five-minute Catalyst Theater demo path works.

- [ ] **Step 5: Commit the release-ready project**

```bash
git add -- .streamlit/config.toml docs/data-dictionary.md README.md app.py docs/submission/week1-project-documentation-notes.md tests/test_smoke.py tests/test_data_generation.py tests/test_analytics.py tests/test_journeys.py
git commit -m "Polish Signal Room for Week 1 submission"
```

## Plan self-review

- **Spec coverage:** Tasks 2–3 cover simulated data, deterministic calculations, rules, and safety; Tasks 4–6 cover both dashboard tabs and interactions; Task 7 covers visual quality, documentation, and submission evidence.
- **Review-focus coverage:** Task 2 owns schema failure behavior; Task 3 owns rate and consecutive-window rules; Task 4 owns empty filtered states; Task 6 owns journey-flow integrity; Task 7 owns non-causal wording.
- **Type consistency:** Tasks 3–6 use `pandas.DataFrame` for tabular data, `pandas.Series` for one selected snapshot, and `plotly.graph_objects.Figure` for every visualization.
- **Scope control:** No deployment, real-time ingestion, action execution, or AI-model feature is required before the local app and tests pass.
