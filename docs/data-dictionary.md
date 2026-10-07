# Signal Room Data Dictionary

All data in Signal Room is synthetic and exists only for the local conference-replay demo. No row contains real attendee information or PII.

## `conference_signals.csv`

**Grain:** one entity during one 15-minute replay interval.

| Field | Definition |
| --- | --- |
| `timestamp` | Start of the 15-minute replay interval. |
| `entity_type` / `entity_name` | The session or shared service zone represented by the record. |
| `capacity` / `attendance` | Simulated available capacity and attendees present. |
| `avg_queue_minutes` | Simulated average wait time in minutes. |
| `attendee_pulse_score` | Simulated average 1–5 attendee micro-survey rating: sum of submitted ratings divided by `pulse_response_count`. Higher is better. |
| `pulse_response_count` | Number of simulated responses used for the pulse aggregate. Fewer than five responses means lower-confidence directional feedback, not a definitive experience measure. |
| `app_error_rate_pct` | Simulated percentage of relevant app interactions reporting an error. |
| `support_case_count` | Simulated support requests during the interval. |
| `people_affected` | Simulated estimate used only for bubble size. |

**Derived metric:** operations pressure is `support_case_count / attendance * 100`. It is `N/A` when attendance is zero.

## `attendee_journeys.csv`

**Grain:** one ordered synthetic event for one fictional attendee ID. `journey_stage` records arrival, session, community, support, or exit, so adjacent events can be aggregated into the Journey and Operations Sankey view.
