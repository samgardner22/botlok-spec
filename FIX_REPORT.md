# Botlok v1.3.6 Fix Report

Status: public candidate patch after an external code-claim accuracy read.
Date: 2026-06-13.

## Summary

v1.3.6 does not change the cryptographic design from v1.3.5. It adds a reference-implementation-status correction so the public candidate is honest about the gap between the frozen M0 de-risk implementation and the target public wire profile.

## Changes

1. Added a Reference Implementation Status section to the public SPEC.
2. Renamed the public profile from `botlok-core-m0` to `botlok-wire-v0.1-candidate`.
3. Rehashed and re-signed all target-profile test vectors after the profile rename.
4. Clarified that v0.1-candidate defines a target public wire profile, not current frozen M0 output.
5. Listed known M0 differences:
   - numeric `event_ts` / `ingest_ts`;
   - `previous_receipt_hash: null` at genesis;
   - non-namespaced `IUR` / `PDR` / `OAR` type strings;
   - per-type schema versions such as `IUR-0.2`, `PDR-0.1`, `OAR-0.2`;
   - no `profile` field;
   - `content_hash`, `inputs_hash`, `args_hash`;
   - nested OAR `flags`;
   - numeric `error_code`;
   - M0 ledger does not yet enforce `payload.key_id == bot_sig.key_id`.
6. Clarified that M1a aligns the reference implementation to the public wire profile.
7. Updated the test-vector README and verifier labels for v1.3.6.

## What did not change

The following remain deferred to M1a:

- structured ledger attestation object;
- public share-token implementation;
- public receipt page build;
- full schema validator;
- OAR sanitizer profile;
- action taxonomy;
- chain continuity;
- selective disclosure;
- audience/freshness/replay binding;
- alignment of reference implementation output to the public wire profile.

## Current status

The v1.3.6 public candidate is suitable for protocol review as a target public wire profile, following confirmation that the Reference Implementation Status note accurately captures the M0/code differences.
