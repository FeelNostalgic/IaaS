# IaaS — End-to-End Encrypted Messaging on AWS

A Flask web app for sending private messages between registered users. Every message is
encrypted with the recipient's RSA public key and stored in a private S3 bucket; the
matching private key never leaves AWS KMS in plaintext. User metadata lives in MySQL.

> [!WARNING]
> This is an educational project. It has **no input validation, no real session
> management and two SQL-injection points**. Do not deploy it to production or put
> real data in it. See [Current status](#current-status).

## Quick start

```bash
git clone https://github.com/FeelNostalgic/IaaS.git
cd IaaS

python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env               # then edit it, see below
aws configure                      # AWS credentials via boto3's provider chain
mysql -u root -p < DB/schema.sql

python app.py                      # http://127.0.0.1:5000
```

Two values in `.env` have no defaults and the app refuses to start without them:

| Variable | What it is |
|---|---|
| `AWS_KMS_KEY_ID` | Key ID of an asymmetric KMS key used to generate every user's key pair. |
| `S3_BUCKET_NAME` | Bucket that stores all user objects. **Globally unique across all of AWS** — pick a free name. |

Create the KMS key once:

```bash
aws kms create-key --description "IaaS" --key-spec RSA_2048 --key-usage SIGN_VERIFY
```

The bucket is created automatically in `AWS_REGION` on the first user registration.

## How it works

```
Browser
  │
  ▼
app.py ──── Flask routes: /  /profile  /signup  /logout  /sendMessage
  │
  ├── UserController ──── register · login · logout · inbox
  │         │
  │         ├── Encrypter ──────── AWS KMS (key pairs) + RSA-OAEP + AES-128-EAX
  │         ├── S3Controller ───── AWS S3  (message objects, one prefix per user)
  │         └── DatabaseAPI ────── MySQL  (users table)
  │
  └── UsersFunctionality ─ send message · list recipients
```

### Cryptography

| Step | Operation |
|---|---|
| Register | KMS `generate_data_key_pair_without_plaintext` returns an RSA-2048 public key plus a private key that is *still KMS-wrapped*. The password is RSA-OAEP encrypted with the user's own public key. Both blobs go to MySQL. |
| Login | The stored password and wrapped private key are fetched; KMS unwraps the private key, which RSA-decrypts the password for comparison. |
| Send (large) | A random 128-bit AES key encrypts the message in `AES.MODE_EAX`. That AES key is RSA-OAEP encrypted with the *recipient's* public key. Four objects are uploaded: `message.bin`, `encrypted_aes_key.bin`, `nonce.bin`, `tag.bin`. |
| Read | Inverse: KMS unwraps the private key, RSA unwraps the AES key, AES verifies the tag and decrypts. |

Only the recipient can read a message: the server never holds a plaintext private key.

### S3 layout

```
<S3_BUCKET_NAME>/
└── alice/
    ├── 05-03-25-14-22-10-123456/
    │   ├── message.bin
    │   ├── encrypted_aes_key.bin
    │   ├── nonce.bin
    │   └── tag.bin
    └── bob/
        └── ...
```

## Current status

### Working

- [x] User registration, login and logout
- [x] RSA-2048 key pair per user, generated and unwrapped by AWS KMS
- [x] Hybrid AES-128-EAX + RSA-OAEP encryption for arbitrarily long messages
- [x] One S3 bucket with a per-user prefix; objects named by timestamp
- [x] Send a message to any registered user, read your own inbox
- [x] MySQL schema for users, public keys and wrapped private keys
- [x] Configuration externalized to environment variables (`.env`)

### Not working / known gaps

- [ ] **No input validation.** Empty or malformed usernames, passwords and full names
      are accepted (`TODO` markers in `Backend/userController.py`).
- [ ] **No real sessions.** `UserController` is a module-level singleton holding
      `is_logged_in` in memory. There are no cookies. Under a multi-worker server,
      one user's login leaks into another's request.
- [ ] **SQL injection.** `Backend/database.py` interpolates `username` into two
      queries with an f-string. The other five use `%s` parameters.
- [ ] **No CSRF protection**, and error responses return `None`, which renders an
      empty page instead of an error.
- [ ] **Tests require live infrastructure.** `Test/usersControllerTest.py` talks to
      real MySQL and real AWS and creates a real user. There are no unit tests and no
      mocks, so it cannot run in CI as written.
- [ ] **No CI, no migrations, no Dockerfile.**
- [ ] Registration creates the root bucket on every call and treats
      `BucketAlreadyOwnedByYou` as success, but a name collision with *another*
      account surfaces as a bare print.

## Project layout

| Path | Role |
|---|---|
| `app.py` | Flask app and the five HTTP routes. |
| `Backend/config.py` | Reads `.env` / environment. Single source of truth for all settings. |
| `Backend/database.py` | MySQL access layer (`DatabaseAPI`). |
| `Backend/encrypter.py` | KMS key pairs, RSA-OAEP, AES-128-EAX. |
| `Backend/s3Controller.py` | Bucket creation, upload and download. |
| `Backend/userController.py` | Registration, login, inbox. |
| `Backend/usersFunctionality.py` | Sending messages, listing recipients. |
| `Backend/errorEnums.py` | Error enums returned across layers. |
| `templates/`, `static/` | Jinja2 templates and a single stylesheet. No JS framework. |
| `DB/schema.sql` | `users` table. |
| `Test/usersControllerTest.py` | Integration tests — need live MySQL + AWS. |
| `Ejemplo python KWS/` | Standalone KMS proof-of-concept, independent of the app. |

## IAM permissions

The principal behind your AWS credentials needs:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["kms:GenerateDataKeyPairWithoutPlaintext", "kms:Decrypt"],
      "Resource": "arn:aws:kms:<region>:<account-id>:key/<AWS_KMS_KEY_ID>"
    },
    {
      "Effect": "Allow",
      "Action": ["s3:CreateBucket", "s3:PutObject", "s3:GetObject", "s3:ListBucket"],
      "Resource": "arn:aws:s3:::<S3_BUCKET_NAME>"
    }
  ]
}
```

## Tests

```bash
python -m unittest Test.usersControllerTest -v
```

Expect failures without a populated `.env`, a reachable MySQL, a valid KMS key and a
globally free bucket name. The tests are integration tests by design, not a safety net.

## Contributing

Issues and pull requests are welcome. Please open an issue before large changes so the
approach can be discussed. If you touch `Backend/config.py` or the schema, update
`.env.example` and the tables above in the same commit.

## License

MIT — see [LICENSE](LICENSE). Copyright © 2024 Francisco Aragonés.
