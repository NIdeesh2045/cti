# Activity 12.2: TLS / Encryption-in-Transit

## Objective
Configure TLS encryption for MongoDB client-server communication and verify secure connections.

## Certificate Generation
Generated the following using OpenSSL:
- CA certificate and private key.
- MongoDB server certificate and private key.
- Client certificate and private key.
- Combined server and client PEM files.

The server and client certificates were signed by the generated CA.

## MongoDB Configuration
MongoDB was configured with:
- TLS mode: `requireTLS`
- Server certificate: `/certs/server.pem`
- CA certificate: `/certs/ca.crt`
- Host port: `27221`

## Verification
1. Unencrypted connection attempt was rejected.
2. Secure mongosh connection succeeded using the CA and client certificates.
3. Employee records were retrieved over TLS.
4. PyMongo 4.18.2 successfully connected using TLS.
5. The Python test returned `{'ok': 1.0}` and retrieved all three employee records.

## Files
- `test_tls.py` – PyMongo TLS verification.
- `output.txt` – Recorded TLS test results.
- `certs/` – Locally generated certificates and private keys.

## Security
Private keys and certificate files are excluded from Git using `.gitignore`. Do not commit private keys or passwords.

## Result
TLS encryption, certificate verification, and secure MongoDB access were successfully tested.
