# Botlok Receipt Schema v0.1 Candidate - v1.3.6 Public Candidate

Status: public release candidate for protocol review.  
Date: 2026-06-13.
Patch level: v1.3.6 reference-implementation-status candidate.  
Spec text license: CC-BY-4.0 candidate.  
Code, examples, and test vectors: Apache-2.0 candidate.  
Audience: protocol reviewers, grammY developers, Telegram bot implementers, and Botlok maintainers.

This document is the public candidate only. It intentionally excludes internal strategy, launch plans, probability estimates, founder notes, and outreach sequencing.

## 0. Abstract

Botlok defines signed receipts for selected Telegram bot runtime events. A Botlok receipt records what the wrapped runtime observed, what policy recorded, and what outbound action it attempted or suppressed. The purpose is to create a portable, externally shareable record that can be verified without raw message access or operator dashboard access.

Botlok v0.1 is Botlok-native and ACTA-inspired. It is not strict ACTA-wire-compatible. Stock ACTA verifiers should not be expected to verify Botlok v0.1-candidate receipts.

## 0.1 Reference implementation status

This document defines the Botlok v0.1-candidate public wire profile. It should not be read as a byte-for-byte description of the frozen M0 de-risk implementation.

The frozen M0 reference implementation at commit `8d6b77a` validates the core cryptographic and architectural model: canonical payload hashing, domain-separated Ed25519 signing, HMAC identifier commitments, durable local queueing, publish-later behavior, verify-before-attest ledger flow, and the proof-boundary model.

M0 does not yet emit this exact public wire profile. Known differences include:

- M0 uses numeric `event_ts` and ledger `ingest_ts` values; this public profile uses string values.
- M0 emits `previous_receipt_hash: null` at genesis; this public profile omits absent optional fields.
- M0 uses non-namespaced type strings: `IUR`, `PDR`, and `OAR`; this public profile uses `botlok:iur`, `botlok:pdr`, and `botlok:oar`.
- M0 uses per-type schema versions such as `IUR-0.2`, `PDR-0.1`, and `OAR-0.2`; this public profile uses `schema_version = "0.1-candidate"`.
- M0 has no `profile` field; this public profile uses `profile = "botlok-wire-v0.1-candidate"`.
- M0 uses `inputs_hash`, `args_hash`, and `content_hash`; this public profile uses commitment language and forbids public `content_commitment` / deterministic content hashes in v0.1.
- M0 OAR payloads may include a nested `flags` object and numeric `error_code`; this public profile restricts payload values to strings and booleans.
- M0 ledger verification does not yet enforce `payload.key_id == bot_sig.key_id`; this public candidate verifier does.

Aligning the reference implementation to this public wire profile is M1a work. The spec should be treated as the target public format, not as a dump of current M0 internal receipts.

## 1. Receipt type names

Public receipt type names are namespaced strings:

| Type | Alias | Meaning |
|---|---|---|
| `botlok:iur` | IUR | Inbound Update Receipt: what the wrapped Telegram bot runtime received or accepted as an inbound update. |
| `botlok:pdr` | PDR | Policy Decision Receipt: what policy recorded or decided. |
| `botlok:oar` | OAR | Outbound Action Receipt: what outbound Telegram API action the wrapped runtime observed, attempted, blocked, or suppressed. |

IUR/PDR/OAR are human-readable aliases. The namespaced strings are the public type names for new receipts.

## 2. Conformance language

The key words MUST, MUST NOT, REQUIRED, SHOULD, SHOULD NOT, MAY, and OPTIONAL in this document are to be interpreted as described in RFC 2119 and RFC 8174 when they appear in all capitals.

Botlok v0.1 receipts MUST NOT be labeled ACTA-compatible. They MAY be described as Botlok-native and ACTA-inspired. Strict ACTA wire compatibility is an open decision and would require changes to signature preimage, chain-hash scope, and encodings.

### 2.1 Candidate profile identifiers

For this v0.1 public candidate:

- `payload.schema_version` MUST equal `0.1-candidate`.
- `payload.profile` MUST equal `botlok-wire-v0.1-candidate`.

A strict v0.1 verifier MUST reject any other `schema_version` or `profile` unless explicitly configured for a later profile.

A verifier MUST reject a receipt with an unknown `schema_version`, unknown receipt `type`, unknown `profile`, unknown `alg`, unknown required-field semantics, or unknown conformance profile unless the verifier is explicitly configured to accept it.

In this sentence, "unknown required-field semantics" means unknown field meaning, unknown profile semantics, unknown structural behavior, or unknown conformance behavior. It does not mean unrecognized values of v0.1 opaque runtime-string fields. Opaque runtime strings are handled under Section 8.

### 2.2 Versioning and extension model

The v0.1 candidate has no extension mechanism. Unknown top-level payload fields MUST be rejected by strict v0.1 verifiers. Unknown top-level receipt-envelope fields and unknown fields inside `bot_sig` or `ledger` MUST be rejected by strict v0.1 verifiers. A future `extensions` object and critical/non-critical extension semantics are deferred to a later profile. Breaking schema families MUST use a new signature domain tag.

## 3. Proof boundary

### 3.1 What a signed Botlok record proves

A Botlok receipt whose checks pass proves:

- Record origin: the receipt was signed by the holder of a verifier-configured signing key.
- Payload integrity: the displayed or supplied payload hashes to the signed `receipt_hash`.
- Ledger signature for receipt hash, when present: a configured ledger key signed the ledger preimage for the `receipt_hash`, `payload.receipt_id`, and `ledger.ingest_ts`.

### 3.2 What it does not prove

A crypto-verified record does not prove:

- Telegram platform truth.
- Telegram delivery completeness.
- That every runtime path was instrumented.
- That the operator emitted every receipt they should have emitted.
- That the real-world action occurred.
- That a Telegram username is controlled by the signer.
- Operator legal identity.
- Fraud, safety classification, or legal liability.
- Payment finality, custody, settlement, refund status, or chargeback outcome.
- Chain continuity in M0/M1.
- Ledger independence unless separately verified.
- Timestamp truthfulness beyond the fact that a timestamp value was signed or ledger-signed.
- Freshness, audience, intended relying party, continued validity, revocation status, or suitability for a later dispute.

Plain language:

> A Botlok receipt means: this signed record was made by this key and is intact. It does not mean Telegram or the world agrees the underlying event happened.

### 3.3 Completeness boundary

Botlok v0.1 receipts are individually verifiable. They are not completeness guarantees. A missing receipt may mean no event occurred, the runtime was not instrumented, the receipt was not emitted, the queue failed, or the operator suppressed evidence. Chain-continuity features may detect some gaps in future versions; Botlok v0.1 does not prove complete instrumentation.

## 4. Verification Semantics Matrix

A verifier or receipt page MUST classify every displayed field by provenance. It MUST NOT display self-asserted, configured, operator-supplied, or unverified metadata under a generic verified badge unless the verification mechanism for that exact field is specified and has passed.

### 4.1 Default provenance rules

- Fields inside `payload` are bot-signed, but many are still signed runtime assertions rather than externally verified facts.
- Envelope crypto fields such as signature results are verifier-derived diagnostics.
- Ledger fields are ledger-signed only to the extent covered by the ledger attestation preimage.
- Operator labels are operator-supplied unless an external proof validates them.
- Commitment values are commitments only. They are not independently openable unless a disclosure mechanism is supplied and verified.

### 4.2 Display-field provenance table

| Field or UI value | Provenance | Required wording / display rule |
|---|---|---|
| `payload.receipt_id` | bot-signed internal identifier | Internal receipt identifier; not an access token. |
| `payload.type` | bot-signed | Signed receipt type. |
| `payload.schema_version` | bot-signed | Signed schema version string; must equal `0.1-candidate` in this candidate. |
| `payload.profile` | bot-signed | Signed profile string; must equal `botlok-wire-v0.1-candidate` in this candidate. |
| `payload.bot_id` | bot-signed + self-reported | Signed descriptive bot label; not Telegram identity proof. |
| `payload.environment` | bot-signed + self-reported | Signed runtime-declared environment; not independently true. |
| `payload.source_mode` | bot-signed + self-reported | Signed runtime-declared capture mode; not platform-verified. |
| `payload.event_ts` | bot-signed + self-reported | Signed runtime-declared event timestamp; clock truth not proven. |
| `payload.key_id` | bot-signed | Must equal `bot_sig.key_id`; not trusted except through verifier key map. |
| `payload.update_type` | bot-signed + self-reported | Signed runtime-reported update type; not platform-verified. |
| `payload.update_commitment` | bot-signed commitment only | Commitment only; not independently openable. |
| `payload.chat_commitment` | bot-signed commitment only | Commitment only; optional when unavailable; not independently openable. |
| `payload.user_commitment` | bot-signed commitment only | Commitment only; optional when unavailable; not independently openable. |
| `payload.raw_message_stored` | bot-signed + runtime self-report | Signed assertion about storage behavior; independent storage audit not proven. |
| `payload.rule_id` | bot-signed + runtime self-report | Signed policy rule label; not proof of external policy registry. |
| `payload.decision` | bot-signed + runtime self-report | Signed opaque runtime string in v0.1; do not infer enforcement. |
| `payload.reason_code` | bot-signed + runtime self-report | Signed opaque runtime string in v0.1. |
| `payload.enforcement_mode` | bot-signed + runtime self-report | Signed opaque runtime string in v0.1; v0.1 infers no enforcement from it. |
| `payload.policy_version` | bot-signed + runtime self-report | Signed policy version label; external policy contents not proven. |
| `payload.inputs_commitment` | bot-signed commitment only | Commitment only; not independently openable. |
| `payload.method` | bot-signed + runtime self-report | Signed wrapper-observed method name; not proof of Telegram delivery. |
| `payload.args_commitment` | bot-signed commitment only | Commitment to sanitized args; not exact wire bytes. |
| `payload.sanitizer_id` | bot-signed + runtime self-report | Signed sanitizer identifier; sanitizer semantics are draft/deferred. |
| `payload.sanitizer_version` | bot-signed + runtime self-report | Signed sanitizer version label; sanitizer semantics are draft/deferred. |
| `payload.policy_decision` | bot-signed + runtime self-report | Optional signed opaque runtime string in v0.1; v0.1 defines no PDR-to-OAR linkage. |
| `payload.outcome` | bot-signed + runtime self-report | Signed opaque runtime string in v0.1; not Telegram delivery. |
| `payload.retry_involved` | bot-signed + runtime self-report | Signed boolean assertion; independent retry audit not proven. |
| `payload.previous_receipt_hash` | bot-signed + self-reported linkage | Optional linkage field; not continuity/completeness proof. |
| `payload.content_commitment` | not allowed in v0.1 | Reserved/deferred field; if present, strict v0.1 verifiers reject the receipt. |
| `receipt_hash` | envelope value checked by verifier | Valid only if recomputed from displayed/supplied payload. |
| `bot_sig.alg` | envelope algorithm hint | Must match verifier-controlled allowed algorithm; Ed25519 only in v0.1. |
| `bot_sig.key_id` | envelope key lookup hint | Verified only after matching verifier-controlled trusted configuration. |
| `bot_sig.sig` | envelope signature bytes | Diagnostic over `receipt_hash`; not a truth claim by itself. |
| public-key fingerprint | verifier-derived | Fingerprint of the public key actually used. |
| `ledger.alg` | envelope ledger algorithm hint | Must match verifier-controlled allowed algorithm; Ed25519 only in v0.1. |
| `ledger.key_id` | envelope ledger-key lookup hint | Valid only through verifier-controlled ledger key map. |
| `ledger.ingest_ts` | ledger-signed only inside ledger preimage | Ledger timestamp value; clock accuracy not proven. |
| `ledger.sig` | ledger signature bytes | Signs only the ledger preimage defined in this spec. |
| ledger operator label | declared/configured unless registry-backed | Declared/configured; not independent unless verified. |
| chain continuity | verifier-derived if a continuity profile exists | v0.1/M1: unchecked only. |
| Telegram proof-of-control | verifier-derived only if proof validates | Absent unless explicit proof is present. |

## 5. Envelope model

A Botlok receipt has a signed payload plus envelope fields.

### 5.1 Normative envelope schema

A v0.1 receipt artifact MUST contain exactly these top-level fields unless a later explicitly configured profile says otherwise:

| Field | Required | Notes |
|---|---:|---|
| `payload` | yes | Signed evidence-bearing object. |
| `receipt_hash` | yes | Unpadded base64url SHA-256 of `JCS(payload)`. |
| `bot_sig` | yes | Bot runtime signature envelope. |
| `ledger` | no | Optional ledger signature envelope. |

A strict v0.1 verifier MUST reject unknown top-level receipt fields.

`bot_sig` MUST contain exactly:

| Field | Required | Notes |
|---|---:|---|
| `alg` | yes | Must equal `Ed25519`. |
| `key_id` | yes | Key lookup hint; must equal `payload.key_id`. |
| `sig` | yes | Ed25519 signature bytes encoded as unpadded base64url. |

If `ledger` is present, it MUST contain exactly:

| Field | Required | Notes |
|---|---:|---|
| `alg` | yes | Must equal `Ed25519`. |
| `key_id` | yes | Ledger key lookup hint. |
| `ingest_ts` | yes | Ledger-declared timestamp string. |
| `sig` | yes | Ledger signature bytes encoded as unpadded base64url. |

Unknown fields inside `bot_sig` or `ledger` MUST be rejected by strict v0.1 verifiers.

Presentation labels, public share tokens, UI status, and operator-facing notes MUST NOT be carried as top-level fields in the v0.1 receipt artifact. They belong in the receipt page projection or outside the receipt artifact.

## 6. Byte-level encoding and canonicalization

Implementations MUST apply these rules exactly:

- `JCS(payload)` means RFC 8785 canonical JSON serialized as UTF-8 bytes.
- Base64url means RFC 4648 URL-safe base64 without padding.
- Signature preimage strings are UTF-8 byte strings with no trailing newline.
- Ed25519 means pure Ed25519 as specified by RFC 8032, not Ed25519ph or Ed25519ctx.
- Signatures are 64 raw bytes encoded as unpadded base64url.
- Public keys are 32 raw bytes encoded as unpadded base64url.
- Receipts with duplicate JSON object member names MUST be rejected before canonicalization.
- Absent optional payload fields MUST be omitted. They MUST NOT be serialized as `null`, `undefined`, or sentinel strings such as `omitted`.

### 6.1 v0.1 JCS value-type profile

A valid v0.1 candidate public-wire signed payload MUST contain only JSON string and boolean values. Payload keys MUST be ASCII strings. Numbers, arrays, nested objects, `null`, and non-profile value types MUST be rejected by strict v0.1 verifiers.

This is a rule for the target public wire profile. The frozen M0 reference implementation currently emits non-profile values such as numeric timestamps and nested OAR flags; aligning that output to this profile is M1a work.

Full RFC 8785 edge-case coverage for numbers, nested objects, arrays, non-ASCII keys, and supplementary-plane ordering is deferred until a later profile ships matching vectors and a true RFC 8785 edge-case suite.

## 7. Hashes and signatures

```text
receipt_hash = b64url_no_pad(SHA-256(JCS(payload)))

bot_signature_preimage = UTF8("botlok-receipt-v0:" || receipt_hash)

ledger_signature_preimage = UTF8(
  "botlok-ledger-attestation-v0:" || receipt_hash || "|" ||
  payload.receipt_id || "|" || ledger.ingest_ts
)
```

`receipt_hash` uses the canonical payload only. It does not include `bot_sig`, `ledger`, public share tokens, or presentation labels.

The v0.1 candidate profile represents `payload.event_ts` and `ledger.ingest_ts` as strings. The frozen M0 reference currently represents those values as epoch-millisecond numbers; M1a aligns the reference implementation to the public profile.

`bot_sig.key_id` and `payload.key_id` MUST match byte-for-byte. If they differ, verification MUST fail before trusted-key lookup.

Verifiers MUST NOT trust the receipt-supplied `alg` or `key_id` except as hints into verifier-controlled trusted configuration. For v0.1, the only approved signature algorithm is `Ed25519`. The trusted key mapping binds `key_id -> algorithm -> public key -> allowed schema/profile`.

Public-key fingerprint formula:

```text
public_key_fingerprint = b64url_no_pad(SHA-256(raw_32_byte_public_key))
```

## 8. Common payload fields

A valid v0.1 Botlok payload MUST contain these common fields:

| Field | Required | Notes |
|---|---:|---|
| `schema_version` | yes | MUST equal `0.1-candidate` in this candidate. |
| `profile` | yes | MUST equal `botlok-wire-v0.1-candidate` in this candidate. |
| `environment` | yes | Runtime-declared string. |
| `bot_id` | yes | Signed descriptive bot label; not Telegram identity proof. |
| `key_id` | yes | Must equal `bot_sig.key_id`. |
| `receipt_id` | yes | Internal receipt identifier. |
| `type` | yes | `botlok:iur`, `botlok:pdr`, or `botlok:oar`. |
| `event_ts` | yes | Runtime-declared event timestamp string. |
| `previous_receipt_hash` | no | Optional signed self-reported linkage field. MUST be omitted at genesis or when unavailable. If present, MUST be an unpadded base64url receipt hash string. |

Missing required fields MUST make the receipt invalid for strict v0.1 verifiers. Optional fields that are absent MUST be omitted. They MUST NOT be serialized as `null`, `undefined`, or sentinel strings.

Unknown top-level payload fields MUST be rejected by strict v0.1 verifiers. v0.1 has no extension object.

`content_commitment` is not a v0.1 candidate payload field. It is reserved for a later profile and MUST NOT appear in v0.1 candidate payloads.

All non-commitment, non-structural payload string fields are signed opaque runtime strings in v0.1 unless this specification explicitly defines a closed value set. This includes decision, reason, outcome, policy, method, update type, source mode, rule ID, policy version, sanitizer ID, and sanitizer version strings. A strict verifier MUST NOT reject a receipt solely because it does not recognize those string values. A public page MUST display them as runtime-reported values and MUST NOT infer enforcement, delivery, safety, Telegram truth, platform verification, or registry membership from them.

## 9. Type-specific allowed fields and required fields

The following subsections define the complete allowed v0.1 fields for each receipt type. No payload fields other than the common fields in Section 8 and the type-specific fields listed in this section are permitted in v0.1. Fields marked required MUST be present. Optional fields that are absent MUST be omitted.

### 9.1 `botlok:iur`

A valid v0.1 `botlok:iur` payload MUST contain the common fields in Section 8 and:

| Field | Required | Notes |
|---|---:|---|
| `update_type` | yes | Runtime-reported update type. |
| `source_mode` | yes | Runtime-declared capture mode. |
| `update_commitment` | yes | Commitment to update material. |
| `raw_message_stored` | yes | Boolean runtime assertion. |
| `chat_commitment` | no | Optional; MUST be omitted when unavailable. |
| `user_commitment` | no | Optional; MUST be omitted when unavailable. |

Higher-capture-fidelity inbound receipts SHOULD use webhook raw-body capture. Long-polling receipts are derived from parsed update objects and may be unable to prove exact raw Telegram payload bytes. If the adapter encounters an unsafe numeric identifier after parsing, Botlok rejects the receipt rather than signing corrupted evidence.

### 9.2 `botlok:pdr`

A valid v0.1 `botlok:pdr` payload MUST contain the common fields in Section 8 and:

| Field | Required | Notes |
|---|---:|---|
| `rule_id` | yes | Runtime-reported rule label. |
| `decision` | yes | Signed opaque runtime string in v0.1. |
| `reason_code` | yes | Signed opaque runtime string in v0.1. |
| `enforcement_mode` | yes | Signed opaque runtime string in v0.1. |
| `policy_version` | yes | Runtime-reported policy version label. |
| `inputs_commitment` | yes | Commitment to policy inputs. |

A blocked or suppressed decision MUST NOT be shown as enforced. A PDR records what policy decided; v0.1 provides no mechanism by which a verifier could confirm that any downstream action was actually prevented or performed. Full action taxonomy and PDR-to-OAR linkage rules are deferred to M1a.

### 9.3 `botlok:oar`

A valid v0.1 `botlok:oar` payload MUST contain the common fields in Section 8 and:

| Field | Required | Notes |
|---|---:|---|
| `method` | yes | Telegram Bot API method name, e.g. `sendMessage`. |
| `args_commitment` | yes | Commitment to sanitized args; not exact wire bytes. |
| `sanitizer_id` | yes | Runtime-reported sanitizer identifier. |
| `sanitizer_version` | yes | Runtime-reported sanitizer version string. |
| `outcome` | yes | Signed opaque runtime string in v0.1. |
| `retry_involved` | yes | Boolean runtime assertion. |
| `policy_decision` | no | Optional signed opaque runtime string in v0.1. v0.1 defines no PDR-to-OAR linkage, so no link precondition governs its presence; PDR-to-OAR linkage is deferred to M1a. |

An OAR is a signed runtime assertion that the Botlok-wrapped runtime reported constructing or observing a logical outbound action according to the wrapper and sanitizer. It does not prove exact serialized HTTP wire bytes, Telegram delivery, or that the user saw the message.

Full sanitizer profile and full action-phase/outcome taxonomy are deferred to M1a.

## 10. `receipt_id` and public share tokens

`receipt_id` is an internal implementation identifier. It is not a security secret and it is not an access token.

A full receipt artifact includes the signed payload (including `payload.receipt_id`), `receipt_hash`, signatures, and optional ledger attestation. A public receipt page may display a projection of the receipt, but if it claims public verification it MUST provide a verifier path to the full artifact or enough data to verify the full artifact.

Public links MUST NOT use deterministic `receipt_id` as the public access key. Public sharing requires a separate `public_share_token` in M1a. Public share token implementation is not part of v0.1 candidate wire compatibility.

M1a requirements for public share tokens:

- At least 128 bits of CSPRNG entropy.
- Stored server-side only as a hash or keyed hash.
- Revocable.
- Not equal to `receipt_id`.
- Not included inside the signed payload.
- Not shown as evidence.

## 11. Chain continuity and `previous_receipt_hash`

`previous_receipt_hash` is an optional common payload field in v0.1. It MUST be omitted at genesis or when unavailable. If present, it is a signed self-reported local linkage field and MUST be an unpadded base64url receipt hash string. In M0/M1, it is not a completeness guarantee and the ledger does not verify continuity.

Public UI rule for v0.1/M1:

```text
Chain continuity: unchecked
```

A UI MUST NOT display `Chain continuity: pass` or `Chain continuity: gap` until a continuity verifier exists.

Future continuity profiles may define `chain_scope`, `bot_instance_id`, `sequence_no`, `restart_receipt`, persisted chain head, ledger-observed monotonicity, gap detection, and fork detection.

## 12. Privacy and commitments

### 12.1 Identifier commitments

M0 uses HMAC commitments for low-entropy Telegram identifiers.

```text
idKey = HMAC-SHA256(bot_signing_seed, "botlok-id-commitment-v0")
commitment = b64url_no_pad(HMAC-SHA256(idKey, "<kind>:<value>"))
```

These commitments hide low-entropy IDs from public enumeration and support equality correlation under the same commitment key. They are not public openings. An external verifier cannot independently confirm the committed Telegram ID without additional disclosure material controlled by the operator.

In v0.1, all commitment fields (update_commitment, inputs_commitment, args_commitment, and optional chat_commitment, user_commitment) are opaque signed strings. A strict v0.1 verifier validates only presence, JSON type, and signed integrity — not commitment algorithms or openings. The HMAC construction above describes how M0 produces commitments and is not a v0.1 verifier requirement.

Known limitation: because `idKey` is derived from the bot signing seed in M0, signing-key rotation changes the commitment key and breaks correlation across rotation.

Roadmap: use a separate or versioned commitment key, `commitment_key_id`, and optional selective disclosure.

### 12.2 Content commitments

Public receipts MUST NOT expose bare SHA-256 hashes of low-entropy message text, commands, captions, or callback data. Telegram bot traffic often includes short strings such as `/start`, `yes`, `confirm`, `buy`, or small callback payloads that are dictionary-guessable.

Public terminology uses `content_commitment`, not `content_hash`, for later profiles. In the v0.1 candidate, `content_commitment` is reserved/deferred and MUST NOT appear in v0.1 payloads. Public v0.1 receipts therefore omit content commitments.

The frozen M0 reference currently emits `content_hash` internally. That internal shape is not the public wire profile and is one reason M1a must align the reference output upward to this safer public profile.

Open Issue: define a later-profile content commitment and selective-disclosure mechanism without enabling cross-receipt dictionary attacks or unwanted cross-bot content matching.

## 13. PDR/OAR action semantics

The v0.1 action and decision fields listed in Section 9 are signed opaque runtime strings unless otherwise specified. A verifier MUST NOT infer Telegram delivery, enforcement, safety, or real-world occurrence from them.

A PDR `decision` is a signed policy record. It is not proof of enforcement, and v0.1 defines no linkage by which enforcement could be shown, so a verifier MUST NOT infer that any downstream action was prevented or performed.

An OAR `outcome` is a signed wrapper observation. If an OAR uses an outcome value that means the result is unknown or unconfirmed, a public page MUST display `action outcome unconfirmed` and MUST NOT present the action as successfully verified.

Full `action_phase`, `outcome`, `enforcement_actor`, retry taxonomy, and PDR-to-OAR linkage rules are deferred to M1a.

## 14. Ledger attestation and ledger operator

The v0.1 ledger signature is a diagnostic signature for the receipt hash. It signs only:

```text
"botlok-ledger-attestation-v0:" || receipt_hash || "|" || payload.receipt_id || "|" || ledger.ingest_ts
```

A v0.1 ledger signature attests only that the configured ledger key signed that preimage. It does not bind:

- the displayed `bot_sig` bytes;
- `bot_sig.key_id`;
- the full envelope;
- the trusted keyset;
- the verification profile;
- the currently displayed payload if its hash does not match `receipt_hash`;
- ledger operator independence;
- Telegram truth.

A ledger signature MUST NOT be displayed or described as proof that the displayed bot signature passed unless the attestation format explicitly signs that result.

Public UI wording SHOULD use `ledger_signature_for_receipt_hash`, not a generic `ledger verified` label.

If a receipt page shows ledger operator metadata, it MUST label it according to provenance:

```text
Ledger signature for receipt hash: pass / fail / absent
Ledger operator: declared/configured
Independence verification: not checked unless registry-backed
```

A structured ledger attestation object with verification profile, trusted keyset ID, bot signature hash, and ledger operator status is deferred to M1a.

## 15. Public verification page status

A public page MUST use layered verification language. It MUST NOT show a generic green `VERIFIED` badge that implies Telegram truth.

Recommended top-level language for passing receipts:

```text
SIGNED RECORD INTEGRITY: PASS
Payload hash: pass
Bot signature over receipt_hash: pass
Key source: trusted configuration / JWKS / registry / manual
Ledger signature for receipt_hash: pass / absent
Ledger independence: not checked unless registry-backed
Telegram identity binding: absent unless proven
Chain continuity: unchecked
Telegram delivery: not proven
World/event truth: not proven
```

Tampered payload rule:

If the displayed payload does not match `receipt_hash`, the public page MUST collapse to:

```text
INVALID - displayed payload does not match signed record
```

The page MUST NOT display green/pass-style bot-signature or ledger-attestation lines next to a tampered displayed payload. It MAY show diagnostic details below the invalid state, clearly stating that signatures, if valid, apply to the original `receipt_hash`, not to the tampered displayed payload.

## 16. Test vectors

This candidate includes target-profile test vectors under `examples/test-vectors/`:

- `valid_iur.json`
- `valid_pdr.json`
- `valid_oar.json`
- `tampered_payload_hash_mismatch.json`
- `invalid_bot_signature.json`
- `missing_trusted_key.json`
- `key_id_mismatch.json`
- `untrusted_but_valid_key.json`
- `duplicate_member_rejected.json.txt`
- `TEST_KEYS_DO_NOT_USE.json`
- `VERIFY_OUTPUT.txt`

The vectors follow these rules:

- no `null` values;
- absent optional fields are omitted;
- base64url is unpadded;
- `payload.key_id` equals `bot_sig.key_id` for all vectors except `key_id_mismatch.json`;
- genesis vectors omit `previous_receipt_hash`;
- tampered vector has invalid top-level status;
- ledger diagnostic output uses `ledger_signature_for_receipt_hash` wording.

The bundled verifier is intentionally crypto-only and not a full protocol validator. It is named `verify_vector_crypto_only.py` and prints `schema_validation=not_enforced`. Passing crypto checks do not, by themselves, make a receipt protocol-valid.

## 17. Relationship to ACTA and adjacent work

Botlok v0.1 is Botlok-native and ACTA-inspired. It is not strict ACTA-wire-compatible.

Known incompatibilities with current ACTA-style verifier assumptions include:

- Botlok signs a domain-separated preimage over the base64url `receipt_hash` string.
- Botlok M0 chain linkage differs from ACTA-style signed-receipt hashing.
- Botlok uses base64url encodings in this candidate.

ACTA alignment remains an open interoperability track. Botlok may later define or align with a Telegram-native ACTA profile after ACTA preimage ambiguity and Botlok wire-format choices are resolved.

## 18. Telegram profile roadmap (non-normative)

Planned Telegram-specific receipt semantics include:

- duplicate/webhook retry incident receipts;
- bot-to-bot loop and unknown-peer receipts;
- Stars payment-to-entitlement evidence;
- Telegram Business / Secretary action receipts;
- managed-bot lineage receipts;
- TON agentic-wallet intent-to-action receipts;
- AP2 `mandate_ref` bridge for runtime execution evidence.

These are roadmap items. They are not v0.1 conformance requirements.

## 19. M1a deferrals

The following are deliberately deferred to M1a public verification safety:

- align frozen M0 reference output to this public wire profile;
- structured ledger attestation object;
- public share-token implementation;
- full OAR sanitizer profile;
- full action-phase/outcome/enforcement taxonomy;
- public page implementation with layered checks;
- stronger test-vector suite;
- public receipt URL hardening;
- audience, freshness, challenge, replay, and expiry binding;
- full schema validator.

## 20. References

- RFC 2119: Key words for use in RFCs to Indicate Requirement Levels.
- RFC 8174: Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words.
- RFC 8785: JSON Canonicalization Scheme (JCS).
- RFC 8032: Edwards-Curve Digital Signature Algorithm (EdDSA), including Ed25519.
- RFC 4648: Base-N Encodings, including URL-safe base64.
- draft-farley-acta-signed-receipts: adjacent signed receipt work; Botlok v0.1 is not strict ACTA-compatible.
- grammY documentation: middleware and Bot API transformers.
- Telegram Bot API documentation.
