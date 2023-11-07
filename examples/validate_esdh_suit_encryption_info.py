#!/usr/bin/env python3

import base64
from cwt import COSE, COSEKey

expected_plaintext_payload = b'This is a real firmware image.'

# See Section 6.2.5 Example (ECDH-ES + AES-KW)
# https://datatracker.ietf.org/doc/html/draft-ietf-suit-firmware-encryption#name-example-2
print("Example 2: ECDH-ES + AES-KW")

# 0. Load the Receiver's Private Key and Configure KDF Context
receiver_private_key_jwk = {
    "kty": "EC2",
    "crv": "P-256",
    "x": '5886CD61DD875862E5AAA820E7A15274C968A9BC96048DDCACE32F50C3651BA3',
    "y": '9EED8125E932CD60C0EAD3650D0A485CF726D378D1B016ED4298B2961E258F1B',
    "d": '60FE6DD6D85D5740A5349B6F91267EEAC5BA81B8CB53EE249E4B4EB102C476B3',
    "key_ops": ["deriveKey"],
    "alg": "ECDH-ES+A128KW",
    "kid": "kid-2",
}
print(f"Receiver's Private Key: {receiver_private_key_jwk}")
for key in ["x", "y", "d"]:
    receiver_private_key_jwk[key] = base64.b64encode(bytes.fromhex(receiver_private_key_jwk[key])).decode()
private_key = COSEKey.from_jwk(receiver_private_key_jwk)

# See Section 6.2.4 Context Information Structure
# https://datatracker.ietf.org/doc/html/draft-ietf-suit-firmware-encryption#name-context-information-structu
kdf_context = {
    "alg": "A128KW",
    "supp_pub": {
        "key_data_length": 128,
        "protected": {"alg": "ECDH-ES+A128KW"},
        "other": "SUIT Payload Encryption",
    },
}
print(f"KDF Context (NOTE: TO BE CONVERTED INTO ACTUAL VALUE): {kdf_context}")
print()

# 1. Load SUIT_Encryption_Info and the detached encrypted payload
filename_hex_suit_encryption_info = "suit-encryption-info-es-ecdh-aes-gcm.hex"
with open(filename_hex_suit_encryption_info, "r") as f:
    suit_encryption_info_hex = ''.join(f.read().splitlines())
print(f"SUIT_Encryption_Info (from {filename_hex_suit_encryption_info}):\n{suit_encryption_info_hex}")
suit_encryption_info_bytes = bytes.fromhex(suit_encryption_info_hex)

filename_diag_suit_encryption_info = "suit-encryption-info-es-ecdh-aes-gcm.diag"
with open(filename_diag_suit_encryption_info, "r") as f:
    print(f.read())

filename_encrypted_payload = "encrypted-payload-es-ecdh-aes-gcm.hex"
with open(filename_encrypted_payload, "r") as f:
    encrypted_payload_hex = ''.join(f.read().splitlines())
print(f"Encrypted Payload (from {filename_encrypted_payload}):\n{encrypted_payload_hex}")
encrypted_payload_bytes = bytes.fromhex(encrypted_payload_hex)

# 2. Decrypt the Encrypted Payload using SUIT_Encryption_Info
ctx = COSE.new()
result = ctx.decode(suit_encryption_info_bytes, keys=[private_key], context=kdf_context, detached_payload=encrypted_payload_bytes)
print(f"\nDecrypted Payload: {result}")
assert result == expected_plaintext_payload
print("Successfully decrypted")
