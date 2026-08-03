Not yet PASS. The substantive design is converged, but two accepted restatements still need executable recovery/type wording.

12. Measurement 17 correctly retracts the token-retirement claim. Repository evidence proves only that doctor builds a copied-credential home (`commands/doctor.md:157-168`; `tools/new-kimi-lane-home.ps1:410-414`). The narrowed finding—unnecessary copying and possible stranding if doctor stops before removal—stands.

**PASS.**

## Remaining amendment 1: malformed-lock recovery

P2 says a crash during truncate/rewrite leaves a malformed lock, correctly treated as held (`docs/superpowers/specs/2026-08-01-lane-credential-and-lock-design.md:165-171`). But its proposed recovery points to the P1 force-release, which requires the operator to confirm the complete recorded identity. A truncated or malformed record may not contain that identity. That makes the recovery path impossible in precisely the state it must recover.

Add a separate guarded malformed-lock override:

- If raw bytes are readable, doctor reports `MALFORMED`, byte length, and SHA-256.
- The human supplies that exact hash to the override.
- Under the exclusive handle, the tool re-hashes the current bytes and transitions to `state=free` only on an exact match.
- If the file is unreadable, the tool cannot override it; the user must first restore readability/ACL.
- The override remains visible and never unlinks the file.

This preserves the rule that unevaluable state is held while providing a compare-and-confirm recovery credential when owner identity is unavailable. Normal release must still match the complete owner/debate/nonce identity (`docs/superpowers/specs/2026-08-01-lane-credential-and-lock-design.md:179-185`).

**FIX — define a raw-hash-confirmed malformed-lock override distinct from identity-confirmed force-release.**

## Remaining amendment 2: `expires_at` is not “nonblank”

Measurement 18 gives `expires_at` type integer. “Present and nonblank” is executable for token strings but ambiguous for an integer; a truthiness implementation would reject `0`. More importantly, expiry being in the past is not structural corruption—the measurement-17 fixture deliberately had a past value.

Specify:

- `access_token`: present, string, nonempty after trimming.
- `refresh_token`: present, string, nonempty after trimming.
- `expires_at`: present and a JSON integer; no truthiness or freshness test.
- `scope`, `token_type`, and `expires_in`: not required.
- Doctor reports structural validity only, consistent with replacing its current unsupported “credential present and OAuth-sourced” verdict (`commands/doctor.md:161-168`).

The fixture currently contains only `access_token` (`evals/multi-model-verify/test_kimi_lane_home.py:310-317`), so adding representative `refresh_token` and integer `expires_at` in the same change remains required.

**FIX — replace “all three nonblank” with exact per-field type and emptiness rules.**

Everything else is restated without weakening: P1 retains exact full-identity idempotence, P2 retains persistent in-place exclusive transitions, and P3 removes doctor’s builder/provider-list path.

OVERALL VERDICT: FIX — convergence requires only the malformed-lock recovery rule and exact `expires_at` validation wording above; after those amendments, PASS.

## Final check

UNVERIFIED:

- Measurements 17 and 18 are external results recorded in this debate, not repository-verifiable evidence.
- The exact credential schema is absent from current repository fixtures; measurement 18 supplies it externally.
- Junction, refresh, deletion, absolute-key, login-coexistence, provider-list false-positive, and P2 Windows-handle behavior remain live-gate requirements.
- Durable flush and crash-during-rewrite behavior remain unverified on both PowerShell hosts.