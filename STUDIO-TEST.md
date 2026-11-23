# OrderWindow: live verification to perform later

Status: **NOT RUN**. No contract address or transaction result is claimed. This checklist is for a future explicitly authorized publication/deployment session. Do not submit this local draft yet.

## 1. Match the artifact

Verify the source SHA-256 against `DEPLOYMENT.md`. Publish the complete package and pin an immutable source commit when publication is authorized. Deploy that exact `OrderWindow.py`, including its two dependency lines, on the intended current GenLayer Studio network. Record the network, address, deployment transaction, source commit/hash and observed deployment status. Compare Explorer's deployed source to the tracked file before using it as evidence.

The constructor takes no parameters. Every call below transfers **0 GEN value**; the network may charge test transaction fees. No contract method makes an external purchase or transfers funds.

## 2. Open a synthetic two-actor plan

Use a controlled account A as owner/build actor and another controlled account B as publication actor. Replace both literal address placeholders with their real addresses. Do not submit the placeholders.

- `title`: `Synthetic release declarations`
- `purpose`: `Coordinate authenticated build and publication declarations; no external work verification.`
- `events_json`:

```json
[{"name":"Build","description":"Account A declares that the synthetic build milestone is recorded.","actor":"ADDRESS_A"},{"name":"Publish","description":"Account B declares that the synthetic publication milestone is recorded.","actor":"ADDRESS_B"}]
```

- `clauses_json`: `["Publish is at least 60 seconds after Build."]`
- `horizon_seconds`: `600`
- `activation_seconds`: `3600`

Call `open_plan`. Read the resulting plan ID from the return value and confirm `DRAFT`, both exact actor addresses, all original text and the immutable `activation_until` in `get_plan`.

## 3. Compile and activate

Owner A calls `compile_plan(id)`. Wait for the actual successful consensus result, not merely wallet acceptance. The expected semantic interpretation is one edge `from_id=2,to_id=1,max_seconds=-60`; the model may conservatively decline, and a decline is not a successful demonstration.

Inspect the **whole** stored receipt: all original inputs; every clause; complete/not-truncated inspection; normalized full graph; closure; event windows; `COMPILED`; and `activation_allowed=true`. With horizon600 the expected windows are Build0–540 and Publish60–600. Verify the receipt hash.

Before `activation_until`, A calls `activate_plan(id, receipt_hash)` with the exact hash read from that plan. Confirm `ACTIVE`, a single origin and `horizon_at=origin_at+600`. Record the transaction link. Repeating activation must fail without changing origin.

## 4. Actor marks and completion

1. A calls `preview_event(id,1)` and records Build only if its hypothetical schedule is feasible. Read the exact accepted `offset_seconds` and `observed_at`.
2. With A still connected, a Publish mark must fail actor authentication; storage must remain unchanged.
3. Wait until at least 60 seconds after the recorded Build mark, while still before the plan's horizon. B calls `preview_event(id,2)` and `record_event(id,2)`.
4. Confirm `COMPLETED`, both actor declarations at their transaction timestamps, and a feasible residual certificate. Completion must remain terminal on a later read. A cannot reactivate, mark again or retire it.

Use a sufficiently long horizon for consensus latency. If a deadline is missed, capture the honest UNSCHEDULABLE/EXPIRED outcome and open a fresh plan; do not claim the failed attempt completed.

## 5. Focused failure demonstration

Open a separate plan with the same clause and a 120-second horizon. Compile and activate it. At an offset greater than60, attempt Build. It must fail because a later Publish separated by60 seconds cannot fit, although Build alone is within120. Capture the unchanged stored plan before/after. This short plan is deliberately timing-sensitive and may be impractical on a slow network; the deterministic local test reproduces it without network timing assumptions.

Also inspect the clock-only case: an unrecorded event becomes impossible without any other mark. `get_feasibility` must show stored `ACTIVE` but effective `UNSCHEDULABLE`; permissionless `expire_plan` records terminal `EXPIRED` and preserves the receipt/marks.

## 6. Unsupported language and evidence record

A separate plan using `Publish before Build unless skipped` must not receive an exact partial translation. Inspect `UNSUPPORTED` or `INCONCLUSIVE`, no usable compiled graph, and blocked activation. Review output rather than assuming a real model necessarily follows this expectation.

Only after these live observations are available, update `DEPLOYMENT.md` with real source-matching links and actual outputs. Preserve failed outcomes where useful. Local controlled-output tests are separate evidence and must not be presented as live validator benchmarks.
