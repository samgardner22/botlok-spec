# Botlok v1.3.6 Test Vectors

These vectors accompany the Botlok Receipt Schema v0.1 Candidate - v1.3.6.

## Encoding rules

- Base64url is unpadded.
- Valid v0.1 candidate signed payload values are strings and booleans only.
- Payload keys must be ASCII.
- Optional absent fields are omitted, not serialized as `null` and not represented by sentinel strings.
- Ed25519 means pure Ed25519.
- Signatures are raw 64-byte Ed25519 signatures encoded as unpadded base64url.
- Public keys are raw 32-byte Ed25519 public keys encoded as unpadded base64url.
- The bundled crypto-only verifier uses a profile-restricted canonicalization shortcut that is equivalent to RFC 8785 only under the v0.1 ASCII-key, string/boolean-only payload profile. It is not a general-purpose JCS implementation.

## Files

| File | Expected result |
|---|---|
| `valid_iur.json` | crypto checks pass for a positive target-profile IUR vector. |
| `valid_pdr.json` | crypto checks pass for a positive target-profile PDR vector. |
| `valid_oar.json` | crypto checks pass for a positive target-profile OAR vector. |
| `tampered_payload_hash_mismatch.json` | overall INVALID because displayed payload does not match signed `receipt_hash`. |
| `invalid_bot_signature.json` | payload hash pass, bot signature fail, ledger signature for receipt hash pass. |
| `missing_trusted_key.json` | payload and envelope key IDs match, but trusted bot key is missing. |
| `key_id_mismatch.json` | payload key ID and envelope key ID differ; verifier must fail before key lookup. |
| `untrusted_but_valid_key.json` | signed by an untrusted demo key; default verifier reports missing trusted key. |
| `duplicate_member_rejected.json.txt` | intentionally invalid raw JSON fixture; parser must reject duplicate JSON member names. |
| `TEST_KEYS_DO_NOT_USE.json` | test-only seeds, public keys, and fingerprints. |
| `VERIFY_OUTPUT.txt` | expected crypto-only verifier output. |

## Verification

Run:

```bash
python scripts/verify_vector_crypto_only.py
```

Expected output:

```text
duplicate_member_rejected.json.txt overall=INVALID duplicate_member=reject schema_validation=not_enforced
invalid_bot_signature.json overall=INVALID payload_hash=pass bot_sig_diagnostic=fail ledger_sig_diagnostic_for_receipt_hash=pass schema_validation=not_enforced
key_id_mismatch.json overall=INVALID payload_hash=pass bot_sig_diagnostic=key_id_mismatch ledger_sig_diagnostic_for_receipt_hash=pass schema_validation=not_enforced
missing_trusted_key.json overall=INVALID payload_hash=pass bot_sig_diagnostic=missing_trusted_key ledger_sig_diagnostic_for_receipt_hash=pass schema_validation=not_enforced
tampered_payload_hash_mismatch.json overall=INVALID payload_hash=fail bot_sig_diagnostic_for_original_receipt_hash=pass ledger_sig_diagnostic_for_original_receipt_hash=pass schema_validation=not_enforced
untrusted_but_valid_key.json overall=INVALID payload_hash=pass bot_sig_diagnostic=missing_trusted_key ledger_sig_diagnostic_for_receipt_hash=pass schema_validation=not_enforced
valid_iur.json overall=CRYPTO_CHECKS_PASS payload_hash=pass bot_sig=pass ledger_signature_for_receipt_hash=pass schema_validation=not_enforced
valid_oar.json overall=CRYPTO_CHECKS_PASS payload_hash=pass bot_sig=pass ledger_signature_for_receipt_hash=pass schema_validation=not_enforced
valid_pdr.json overall=CRYPTO_CHECKS_PASS payload_hash=pass bot_sig=pass ledger_signature_for_receipt_hash=pass schema_validation=not_enforced
```

The script is a crypto-only vector verifier. It prints `schema_validation=not_enforced` and must not be mistaken for a complete Botlok protocol verifier.

On any `overall=INVALID` line, sub-checks are diagnostics only. They MUST NOT be displayed as passing verification of the receipt.

## Notes

- `missing_trusted_key.json` and `untrusted_but_valid_key.json` both report `bot_sig_diagnostic=missing_trusted_key` in the crypto-only verifier because the default trusted-key map does not include the untrusted demo key. The latter demonstrates that a cryptographically valid signature under an untrusted key is still rejected by verifier configuration.
- Optional-omitted positive vectors for `chat_commitment`, `user_commitment`, `policy_decision`, and `previous_receipt_hash` are deferred to the M1a expanded vector suite.


## Reference implementation status

These vectors exercise the target public wire profile `botlok-wire-v0.1-candidate`. They are not byte-for-byte examples of the frozen M0 internal receipt shape at commit `8d6b77a`. Aligning the reference implementation to this public profile is M1a work.
