# OrderWindow — November 23 release record

Published **November 23, 2026**. Current native source-schema validation, the
complete controlled-output local suite and matching deployment succeeded. The
complete deployed source and initial stats were verified. The primary two-actor
walkthrough reached persisted `COMPLETED`. Six successful writes and the one
expected wrong-actor execution rejection all reached `FINALIZED`; the rejected
guard left the complete stored plan unchanged. Portal status is separate evidence.

| Item | Current evidence |
| --- | --- |
| Contract version / receipt schema | `1.0.0` / `orderwindow-v1` |
| Exact released source SHA-256 | `446ee9c880d8d927041249938ae45c23555fedc7f77b5ae37c1b543e9c8e4aba` |
| Public repository | https://github.com/zakazaka95/OrderWindow |
| Immutable source | https://github.com/zakazaka95/OrderWindow/blob/52adfb7ce4ea7533aa1db94ce7f81f8bb8443c93/OrderWindow.py — independently retrieved exact raw bytes match |
| Local suite on released source | 36 passing controlled-output tests |
| Native source-schema validation | Passed with the pinned v0.4.0 runner during this release |
| Constructor / transaction value | No constructor parameters; synthetic writes use 0 GEN value; network fees are separate |
| Network / chain ID / RPC | Studio Devnet / `61997` / `https://studio-dev.genlayer.com/api` |
| Contract | [0x51Fb8a926d289C9571b504332B04C3FeaF95D523](https://explorer-studio-dev.genlayer.com/address/0x51Fb8a926d289C9571b504332B04C3FeaF95D523) |
| Deployment transaction | [0x6cd36fcc0a3699372ce5866dd4556f56225ad513c6e209af7ecff3cd73ec987d](https://explorer-studio-dev.genlayer.com/tx/0x6cd36fcc0a3699372ce5866dd4556f56225ad513c6e209af7ecff3cd73ec987d) — successful execution |
| Complete tracked/deployed source comparison | Full source matches after CRLF-to-LF conversion and outer-whitespace trim; normalized SHA-256 `1b115b2154e7e505467e7200b90612e3f657922b8581b41bfbf3b02a6ece4363` |
| Initial persisted readback | `get_stats` retrieved successfully after deployment |
| First application write | [Plan opened successfully](https://explorer-studio-dev.genlayer.com/tx/0xff93bb0774dca64f441ba8d49d3977709e62c238a495b1d2f413116d308d4fff), preserving the exact two-actor specification |
| Demonstrated plan | Plan ID `0`; exact 600-second horizon, 3,600-second activation window and 60-second minimum gap |
| Complete semantic compilation | [Compilation succeeded](https://explorer-studio-dev.genlayer.com/tx/0x9dc21e804580ec68b3764a0b2f2fe120a1076121d72166640ff952ea4d87d19e); exact clause edge `from_id=2, to_id=1, max_seconds=-60` |
| Complete compiled receipt SHA-256 | `c0a1f77ac293e897175016b0ed98ce76550f1544a0f3a25a860bde1d060e625c` |
| Deterministic event windows | Build `[0, 540]` seconds; Publish `[60, 600]` seconds, relative to the activation origin |
| Owner activation | [Owner activated the exact compiled receipt](https://explorer-studio-dev.genlayer.com/tx/0xe401c2bd2f1d49862973d5c7d5a9285c32a841accd980452ab61511310292049), fixing the origin once |
| Build mark | [Assigned actor A recorded Build](https://explorer-studio-dev.genlayer.com/tx/0x97d3fa494f5cc03f6941b94726fce7000eae7cfaf638a7736cfb2d31b402c5fd) at offset `20` seconds |
| Expected wrong-actor guard | [Owner A's attempt to mark B's Publish event was rejected](https://explorer-studio-dev.genlayer.com/tx/0xe8ae87a1faa9d70aa3a6ec755cdb674a2db6c39746a1c50c787ac6709bb43f63); the complete stored plan was unchanged |
| Observed onchain guard reason | The execution receipt exposed `Only its assigned actor may mark an unrecorded event in an active plan.`; this is distinct from a generic read-only provider error |
| Distinct publisher mark | [Assigned actor B recorded Publish successfully](https://explorer-studio-dev.genlayer.com/tx/0xbd5d0f9f52cb93b03af14e01bdf3ac0d0e4f2751199753aa0ec592909f56ca55) at offset `349` seconds within the 600-second horizon; actual Build-to-Publish gap `329` seconds satisfies the 60-second minimum |
| Terminal persisted result | `COMPLETED`; both authenticated actors, transaction-time gap and residual-feasibility assertions passed; the exact origin and both marks remained unchanged on a later read |
| Transaction finality | All seven tracked transactions `FINALIZED`: six successful writes and one expected wrong-actor execution rejection with unchanged state; complete proof collected November 23 at 16:22:00 UTC |
| Portal contribution ID / status | `c043f6bc-5ab6-4d10-9883-1b1438371295` — [Pending review](https://portal.genlayer.foundation/my-submissions?q=OrderWindow), verified November 23, 2026, with four matching evidence items; no acceptance or award claimed |

## Minimal runner migration

The archived prepared source pinned v0.3.0. The current release changes only the
first two runner-header lines to the native-verified pin:

```text
# v0.4.0
# { "Depends": "py-genlayer:kzybg95x1gn21dw72m7hyg0maaap04n4nx55j9yt6fkdqxtz6bz0" }
```

The contract body, API and consensus/state logic are unchanged. All 36 local
tests passed on this released source, separately from native source-schema
validation. The archived prepared raw source SHA-256 was `73c85794f721379ac7fe812dec6b1e00a1240701d25a5e1888bef271acdf5818`; it is historical,
not the released source identified by the current hash above.

Raw file-byte hashes are distinct from any separately normalized complete
Explorer-source comparison. The complete comparison and normalization rule are
recorded above. Schema validation and initial stats alone do not establish a
successful application write, transaction-clock behavior or semantic correctness.

## Reproduce and interpret the evidence

The public [complete demonstration](evidence/demo-result.json),
[transaction list](evidence/transactions.json), [native schema result](evidence/native-schema.json)
and [complete source comparison](evidence/source-verification.json) bind the
actual deployed source and application results. The separate
[guard execution proof](evidence/guard-execution.json) preserves the observed
permission reason and equal before/after stored-state hashes.

The [RPC recovery record](evidence/rpc-recovery.json) distinguishes provider
rate-limit declines before a hash from tracked onchain outcomes. Nonces and
persisted state were reconciled before resuming; those offchain declines are not
additional failed contract calls or semantic decisions.

Use [STUDIO-TEST.md](STUDIO-TEST.md) with synthetic technical declarations,
normal consensus and zero transaction value. Require successful execution and
persisted application state, not acceptance alone. Preserve readable adverse
outcomes and distinguish local controlled-output tests, actual semantic results
and transaction finality. Neither a unit suite nor a small synthetic walkthrough
is a model-reliability benchmark or a production-readiness guarantee.

The complete walkthrough identifies the plan, compiled receipt and exact
activation hash, separate authenticated actors, each transaction-time mark and
the completed residual-feasible schedule. Marks are declarations by the
assigned address; they do not prove that an outside build or publication occurred.
Any actually demonstrated rejected guard must retain unchanged-state evidence.
