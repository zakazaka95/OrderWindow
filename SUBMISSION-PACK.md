# OrderWindow submission draft

Prepared locally for a later week. **Do not publish, deploy or submit until the user says go.**

## Title

OrderWindow — Exact Timing Agreements with Residual-Feasible Event Marks

## Notes / Description

OrderWindow is a reusable timing primitive for technical workflows. A requester freezes two to five actor-assigned events and complete relative timing clauses. Independent GenLayer validators translate every clause into exact inclusive integer-second difference bounds and rebuild the full canonical receipt. A deterministic solver detects contradictions and derives event windows; unsupported or uncertain meanings block activation. The owner accepts the exact receipt hash and fixes one activation origin. Each actor records its event at the transaction time only if all prior marks and every unfinished event still admit a complete future schedule. Late declarations cannot strand another event. Plans complete, retire or expire irreversibly, with bounded technical retries and attempt history. Includes 36 local controlled-output tests, receipt tamper tests, documentation and a live verification checklist. Marks are actor declarations, not proof of outside work.

## Evidence to add after authorization

- Public repository containing this entire package.
- Immutable `OrderWindow.py` commit link matching the deployed source.
- Exact GenLayer Explorer contract address and deployment transaction.
- Honest live compile, activation and completed two-actor demo transactions, plus relevant failed guards.

No deployment, live model test or Portal submission has been performed for this draft. Use `STUDIO-TEST.md` before representing the primitive as live.
