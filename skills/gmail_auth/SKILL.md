## Purpose
Load OAuth2 Gmail credentials from disk for use in Gmail API calls.
Token file written once by `scripts/auth_setup.py` (interactive browser flow).

## Inputs
None.

## Outputs
`google.oauth2.credentials.Credentials` object.

## Dependencies
- `google-auth`
- `google-auth-oauthlib`
- Token JSON file at path configured in `core/settings.py`

## Public API
```python
from skills.gmail_auth.handler import get_gmail_credentials

creds = get_gmail_credentials()  # -> google.oauth2.credentials.Credentials
```

## Notes
Run `make auth-init` once to generate the token file. If token is expired,
`get_gmail_credentials()` refreshes it automatically using the stored refresh token.
