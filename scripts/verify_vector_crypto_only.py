#!/usr/bin/env python3
"""
Botlok v1.3.6 crypto-only vector verifier.

This script checks payload hash, key-id equality, approved alg, trusted-key lookup,
and Ed25519 signatures for the public test vectors. It deliberately does NOT enforce
full Botlok schema/profile validation. Its output includes schema_validation=not_enforced
so it is not mistaken for a complete reference verifier. Its canonical_payload() function is a profile-restricted shortcut equivalent to RFC 8785 only for the v0.1 ASCII-key, string/boolean-only payload profile; it is not a general JCS implementation.
"""
import json, base64, hashlib
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

ROOT = Path(__file__).resolve().parents[1]
VECTORS = ROOT / 'examples' / 'test-vectors'

def b64u_decode(s):
    return base64.urlsafe_b64decode(s + '=' * (-len(s) % 4))

def b64u(data):
    return base64.urlsafe_b64encode(data).decode('ascii').rstrip('=')

def no_duplicate_object_pairs_hook(pairs):
    out = {}
    for k, v in pairs:
        if k in out:
            raise ValueError(f'duplicate JSON member: {k}')
        out[k] = v
    return out

def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f, object_pairs_hook=no_duplicate_object_pairs_hook)

def canonical_payload(payload):
    for k, v in payload.items():
        if not isinstance(k, str):
            raise TypeError('payload key must be string')
        if not all(ord(c) < 128 for c in k):
            raise TypeError(f'payload key must be ASCII: {k!r}')
        if not (isinstance(v, str) or isinstance(v, bool)):
            raise TypeError(f'payload value for {k} must be string or boolean, got {type(v).__name__}')
    return json.dumps(payload, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode('utf-8')

def receipt_hash(payload):
    return b64u(hashlib.sha256(canonical_payload(payload)).digest())

def verify_sig(pub_b64, msg, sig_b64):
    try:
        Ed25519PublicKey.from_public_bytes(b64u_decode(pub_b64)).verify(b64u_decode(sig_b64), msg)
        return True
    except Exception:
        return False

def main():
    keys = load_json(VECTORS / 'TEST_KEYS_DO_NOT_USE.json')
    trusted_bot_keys = {keys['demo_bot']['key_id']: keys['demo_bot']['public_key_b64url']}
    ledger_keys = {keys['demo_ledger']['key_id']: keys['demo_ledger']['public_key_b64url']}
    duplicate_path = VECTORS / 'duplicate_member_rejected.json.txt'
    try:
        load_json(duplicate_path)
        print('duplicate_member_rejected.json.txt overall=UNEXPECTED_PASS duplicate_member=not_rejected schema_validation=not_enforced')
    except ValueError:
        print('duplicate_member_rejected.json.txt overall=INVALID duplicate_member=reject schema_validation=not_enforced')
    for path in sorted(VECTORS.glob('*.json')):
        if path.name == 'TEST_KEYS_DO_NOT_USE.json':
            continue
        r = load_json(path)
        payload = r['payload']
        computed_hash = receipt_hash(payload)
        hash_ok = computed_hash == r.get('receipt_hash')
        bot_sig = r.get('bot_sig', {})
        key_id_equal = payload.get('key_id') == bot_sig.get('key_id')
        alg_ok = bot_sig.get('alg') == 'Ed25519'
        if not key_id_equal:
            bot_result = 'key_id_mismatch'
        elif not alg_ok:
            bot_result = 'bad_alg'
        elif bot_sig.get('key_id') not in trusted_bot_keys:
            bot_result = 'missing_trusted_key'
        else:
            bot_pre = ('botlok-receipt-v0:' + r['receipt_hash']).encode('utf-8')
            bot_result = 'pass' if verify_sig(trusted_bot_keys[bot_sig['key_id']], bot_pre, bot_sig.get('sig','')) else 'fail'
        ledger = r.get('ledger')
        if not ledger:
            ledger_result = 'absent'
        elif ledger.get('alg') != 'Ed25519':
            ledger_result = 'bad_alg'
        elif ledger.get('key_id') not in ledger_keys:
            ledger_result = 'missing_trusted_key'
        else:
            led_pre = ('botlok-ledger-attestation-v0:' + r['receipt_hash'] + '|' + payload['receipt_id'] + '|' + ledger['ingest_ts']).encode('utf-8')
            ledger_result = 'pass' if verify_sig(ledger_keys[ledger['key_id']], led_pre, ledger.get('sig','')) else 'fail'
        overall = 'CRYPTO_CHECKS_PASS' if (hash_ok and bot_result == 'pass' and ledger_result in ['pass','absent']) else 'INVALID'
        if not hash_ok:
            print(f"{path.name} overall=INVALID payload_hash=fail bot_sig_diagnostic_for_original_receipt_hash={bot_result} ledger_sig_diagnostic_for_original_receipt_hash={ledger_result} schema_validation=not_enforced")
        elif overall == 'CRYPTO_CHECKS_PASS':
            print(f"{path.name} overall=CRYPTO_CHECKS_PASS payload_hash=pass bot_sig=pass ledger_signature_for_receipt_hash={ledger_result} schema_validation=not_enforced")
        else:
            print(f"{path.name} overall=INVALID payload_hash=pass bot_sig_diagnostic={bot_result} ledger_sig_diagnostic_for_receipt_hash={ledger_result} schema_validation=not_enforced")

if __name__ == '__main__':
    main()
