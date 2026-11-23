# OrderWindow Portal package

Published November 23, 2026. Category: Builder → Intelligent Contracts.
See [DEPLOYMENT.md](DEPLOYMENT.md) for observed publication, runtime and application evidence.

## Title

OrderWindow — Exact Timing Agreements with Residual-Feasible Event Marks

## Notes / Description

OrderWindow is a reusable timing primitive for technical workflows. A requester freezes two to five actor-assigned events and complete relative timing clauses. Independent GenLayer validators translate every clause into exact inclusive integer-second difference bounds and rebuild the full canonical receipt. A deterministic solver detects contradictions and derives event windows; unsupported or uncertain meanings block activation. The owner accepts the exact receipt hash and fixes one activation origin. Each actor records its event at the transaction time only if all prior marks and every unfinished event still admit a complete future schedule. Late declarations cannot strand another event. Plans complete, retire or expire irreversibly, with bounded technical retries and attempt history. Includes 36 local controlled-output tests, receipt tamper tests, documentation and a live verification checklist. Marks are actor declarations, not proof of outside work.

## Evidence

- GitHub Repository — https://github.com/zakazaka95/OrderWindow
- GitHub File — https://github.com/zakazaka95/OrderWindow/blob/52adfb7ce4ea7533aa1db94ce7f81f8bb8443c93/OrderWindow.py
- GenLayer Explorer Contract — https://explorer-studio-dev.genlayer.com/address/0x51Fb8a926d289C9571b504332B04C3FeaF95D523
- Other — https://explorer-studio-dev.genlayer.com/tx/0x9dc21e804580ec68b3764a0b2f2fe120a1076121d72166640ff952ea4d87d19e

The complete successful semantic compilation is linked above. Activation, actor
marks, any actual rejected guard and terminal completion are recorded separately
in DEPLOYMENT.md as observed.
The [complete public demonstration](evidence/demo-result.json) and
[expected guard proof](evidence/guard-execution.json) preserve the complete path
and distinguish six successful writes from the one intended rejected mark.

The description has 968 characters. Current native source-schema validation and
all 36 controlled-output tests pass. These checks are separate from deployment,
live-model and Portal results, which are recorded only as observed in DEPLOYMENT.md.
