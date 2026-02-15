# Authentication

This guide explains how to authenticate to a Salesforce org when creating a
`salespyforce.Salesforce` client.

At this time, `salespyforce` authenticates using Salesforce's OAuth 2.0
username-password grant (`grant_type=password`) with:

- API username and password
- Security token
- Connected App client credentials (client ID and client secret)
- OAuth token endpoint URL

## Choose an Authentication Pattern

You can provide credentials in two supported ways:

- Pass values directly to the `Salesforce(...)` constructor
- Provide a helper configuration file (recommended)

Using a helper file keeps secrets out of source code and makes it easier to
reuse credentials across scripts and local tooling.

## Option 1: Pass Credentials as Constructor Parameters

Use this method when you need a quick script or one-off connection.

```python
from salespyforce import Salesforce

sfdc = Salesforce(
    username="admin.user@example.com",
    password="example123",
    org_id="4DJ000000CeMFYA0",
    base_url="https://example-dev-ed.lightning.force.com/",
    endpoint_url="https://example-dev-ed.my.salesforce.com/services/oauth2/token",
    client_id="3MVG9gTv.DiE8cKRIpEtSN_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
    client_secret="7536F4A7865559XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
    security_token="2muXaXXXXXXXXXXXXXXXoVKxz",
)
```

Required parameters for this method:

- `username`
- `password`
- `org_id`
- `base_url`
- `endpoint_url`
- `client_id`
- `client_secret`
- `security_token`

## Option 2 (Recommended): Use a Helper Configuration File

The helper file supports YAML (`.yml`/`.yaml`) and JSON (`.json`). For helper
files, the connection section should use `client_key` (not `client_id`) as
shown below.

Example helper file (`helper.yml`):

```yaml
# Helper configuration file for salespyforce
connection:
  username: admin.user@example.com
  password: example123
  org_id: 4DJ000000CeMFYA0
  base_url: https://example-dev-ed.lightning.force.com/
  endpoint_url: https://example-dev-ed.my.salesforce.com/services/oauth2/token
  client_key: 3MVG9gTv.DiE8cKRIpEtSN_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
  client_secret: 7536F4A7865559XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
  security_token: 2muXaXXXXXXXXXXXXXXXoVKxz

# Optional: defaults to true if omitted
ssl_verify: yes
```

Instantiate using the helper file:

```python
from salespyforce import Salesforce

sfdc = Salesforce(helper="/path/to/helper.yml")
```

You can also pass helper metadata in alternate forms:

- `Salesforce(helper=("/path/to/helper.json", "json"))`
- `Salesforce(helper={"path": "/path/to/helper.yml", "type": "yaml"})`

## Security Recommendations

- Prefer helper files over inline credentials.
- Keep helper files outside your repository.
- Add helper file names/paths to `.gitignore`.
- Restrict file permissions (for example, `chmod 600` on macOS/Linux).
- Use a dedicated Salesforce integration user with least-privilege permissions.
- Rotate client secrets and security tokens regularly.

## Interactive Prompt Behavior

If no `connection_info`, `helper`, or direct credential parameters are provided,
the client prompts for connection fields interactively in the terminal.

## Troubleshooting

If authentication fails:

- Verify the Connected App client ID/client secret are valid.
- Confirm the OAuth token endpoint URL is correct for your org.
- Confirm your security token is current.
- Confirm the API user has login/API access and is not locked.

## Future Authentication Support

:::{note}
Additional authentication methods are planned for future releases, such as
environment-variable-based configuration and additional OAuth 2.0 flows
(for example, JWT bearer and web server flow). External Client App-based
authentication options may also be added where applicable.
:::
