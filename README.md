# OrderWindow

OrderWindow turns a small technical timing agreement into an exact, bounded difference-constraint graph. GenLayer validators independently translate every frozen clause; a deterministic solver decides whether the graph is consistent. After the owner accepts that exact receipt, assigned actors can record events only when a complete feasible future schedule still exists for every unfinished event.

This is a standalone contract primitive, with no frontend, token, escrow, payout or external execution. It is prepared locally and has not been deployed or submitted. See [DEPLOYMENT.md](DEPLOYMENT.md).

## The failure it prevents

Suppose a build must precede publication by at least 60 seconds, and both must be recorded within 120 seconds of activation. A build at second 90 is individually within the horizon, but leaves no legal publication time. OrderWindow rejects that mark. It does not wait for the later event to become impossible.

This can support small release coordination or machine workflow agreements where different actors make authenticated declarations. A mark proves that the assigned address declared an event onchain at that transaction time. It does **not** prove that a build, upload, delivery or other outside action actually happened.

## Where GenLayer matters

Participants can describe bounded relative timing in complete clauses instead of hand-authoring graph edges. Independently executing validators compile those meanings, including minimum delays and maximum gaps. They rebuild the complete consequential receipt from the same frozen inputs; canonical equality binds the original text, each clause's interpretation, normalized constraints, inspection coverage, deterministic closure, event windows and decision. An independent disagreement does not change contract storage.

The model does not select event times or decide feasibility. Floyd–Warshall computes all-pairs tight bounds and detects negative cycles. Real-model semantic correctness and agreement remain assumptions to evaluate on Studio; this repository's controlled-output tests do not establish them.

## Exact supported scope

- Two to five named technical events, each assigned a nonzero address, and one to five complete clauses.
- Unconditional conjunctions exactly equivalent to inclusive integer-second difference bounds. Each clause may emit at most four bounds, with an individual bound between -86,400 and 86,400 seconds.
- For example: “Publish is at least 60 seconds after Build.” Its edge is `t_build - t_publish <= -60`.
- Every event has the fixed implicit range `0 <= event_time <= horizon_seconds`. Event horizon and activation window are each 60–86,400 seconds.
- Strict comparisons, fractional or approximate durations, calendar dates, time zones, disjunctions, conditions and uncertain references must return `UNSUPPORTED` or `UNCERTAIN`. They may not be rounded, strengthened or partially omitted.
- A zero self-bound is allowed for an explicit tautology. Duplicate directed bounds normalize to the tightest bound, preserving their conjunction.
- One unsupported clause blocks the entire plan. Exact individual clauses with an uncertain combined meaning also block activation.

All strings are untrusted input. The full assembled prompt must fit both character and UTF-8 byte budgets. There is no slicing or prompt-level truncation. The classifier is instructed to inspect every complete event description and clause. This is not a guarantee that an AI is immune to malicious instructions.

## State and time

`DRAFT -> COMPILED -> ACTIVE -> COMPLETED` is the successful path. A semantically unsupported, inconclusive or infeasible result is terminal. Only technical/schema failures permit up to three attempts, stored individually; the owner cannot reroll a final semantic verdict. Nonterminal plans may be irreversibly retired by their owner.

The compile/activation cutoff is fixed at opening. Activation requires the owner, the exact accepted receipt hash and a transaction strictly before that cutoff. Activation fixes the origin once. The event horizon is measured from this origin, so consensus latency does not consume it and reactivation cannot slide it.

For a proposed mark, the deterministic solver fixes every prior mark to its actual offset, fixes the proposed mark to the current transaction offset, and requires every remaining event to occur at or after that same offset. It then tests the **entire** system, not just the proposed event's window. The horizon upper boundary is inclusive. Events cannot be backdated or repeated. Different actors may mark at the same integer second when the constraints allow it.

Successful writes advance a per-plan monotonic clock floor. Failed guards, rejected marks and views leave all storage untouched. `get_plan` returns stored history; `get_feasibility` distinguishes it from an elapsed activation window or an active schedule with no feasible future. Anyone may finalize an expired activation window or an infeasible active schedule using `expire_plan`. No events are invented during expiry.

## API

| Method | Purpose |
| --- | --- |
| `open_plan(title, purpose, events_json, clauses_json, horizon_seconds, activation_seconds)` | Freeze inputs and assign the next zero-based plan ID. |
| `compile_plan(plan_id)` | Owner requests full independent semantic compilation. |
| `activate_plan(plan_id, expected_receipt_hash)` | Owner accepts the exact feasible receipt and fixes the origin once. |
| `record_event(plan_id, event_id)` | Assigned actor records event 1–N at the transaction timestamp if full residual feasibility survives. |
| `retire_plan(plan_id)` | Owner irreversibly retires a nonterminal plan. |
| `expire_plan(plan_id)` | Anyone finalizes a missed activation cutoff or an impossible active residual schedule. |
| `get_plan`, `get_attempt` | Return stored complete plan/receipt history. |
| `get_feasibility`, `preview_event` | Return read-only diagnostics, without advancing time floors. |
| `get_stats` | Return version, counts and inspection bounds. |

An event JSON row has exactly `name`, `description` and `actor`. `clauses_json` is an array of complete strings. Boolean IDs, out-of-range IDs and bounds, malformed Unicode, exact duplicate event names and exact duplicate clauses are rejected.

## Reproduce local verification

Python 3.11+ and the standard library are sufficient for the isolated suite:

```sh
python -m unittest -v test_orderwindow.py
```

The 36 tests cover negative cycles, exact minimum/maximum gaps, all unfinished event lower bounds, same-second marks, completion, replay/actor checks, immutable activation, permissionless expiry, reverse clocks and rejected-write atomicity. They also mutate every receipt leaf, force independent semantic disagreement, exercise bounded technical retries, reject partial schemas, and inspect maximum-size escaped JSON/Unicode inputs without cutting text.

`testsupport.py` substitutes only a controlled SDK interface and model responses. These results establish local algorithm/state behavior, not deployment success, GenVM compatibility, model performance or production readiness. [STUDIO-TEST.md](STUDIO-TEST.md) gives the deployment and two-actor live verification procedure to perform later.

## Files and license

`OrderWindow.py` is the exact deployment candidate. The dependency is pinned in its first two lines. The MIT license applies to this package. There are no runtime services, private keys, network fetches or secret environment variables.
