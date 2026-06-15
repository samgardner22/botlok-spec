# Botlok

Botlok is a Telegram-native signed-receipt format for bot and agent actions. It defines a compact, verifiable record of what a wrapped bot runtime observed, what policy decided, and what outbound action was constructed — signed with Ed25519 over a canonicalized payload.

This repository contains the v0.1-candidate public wire profile: the specification, test vectors, and a crypto-only reference verifier.

Scope. Botlok records and signs runtime assertions. It is evidence of what a bot reported, not proof of platform truth. A Botlok receipt does NOT prove Telegram delivery, Telegram identity, payment finality, or that the described real-world action occurred. The specification's proof-boundary section states these limits precisely.

Status. v0.1-candidate is the target public wire profile. The reference implementation (frozen, separate) currently emits a different internal shape; the spec's Reference Implementation Status section documents the differences identified so far. This is a candidate format under active development — not a finalized standard.

Botlok is inspired by the ACTA signed-receipts work but is NOT wire-compatible with it and should not be labeled ACTA-compatible.

Licensed under Apache 2.0.
