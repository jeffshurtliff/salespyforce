# salespyforce
A Python toolset for performing Salesforce API calls

<table>
    <tr>
        <td>Latest Stable Release</td>
        <td>
            <a href='https://pypi.org/project/salespyforce/'>
                <img alt="PyPI" src="https://img.shields.io/pypi/v/salespyforce">
            </a>
        </td>
    </tr>
    <tr>
        <td>Latest Beta/RC Release</td>
        <td>
            <a href='https://pypi.org/project/salespyforce/#history'>
                <img alt="PyPI" src="https://img.shields.io/badge/pypi-1.4.0.dev1-blue">
            </a>
        </td>
    </tr>
    <tr>
        <td>Build Status</td>
        <td>
            <a href="https://github.com/jeffshurtliff/salespyforce/blob/master/.github/workflows/pythonpackage.yml">
                <img alt="GitHub Workflow Status" 
                src="https://img.shields.io/github/actions/workflow/status/jeffshurtliff/salespyforce/pythonpackage.yml?branch=master">
            </a>
        </td>
    </tr>
    <tr>
        <td>Supported Versions</td>
        <td>
            <a href='https://pypi.org/project/salespyforce/'>
                <img alt="PyPI - Python Version" src="https://img.shields.io/pypi/pyversions/salespyforce">
            </a>
        </td>
    </tr>
    <tr>
        <td>Code Coverage</td>
        <td>
            <a href="https://codecov.io/gh/jeffshurtliff/salespyforce">
                <img src="https://codecov.io/gh/jeffshurtliff/salespyforce/branch/master/graph/badge.svg" />
            </a>
        </td>
    </tr>
    <tr>
        <td>Documentation</td>
        <td>
            <a href='https://salespyforce.readthedocs.io/en/latest/?badge=latest'>
                <img src='https://readthedocs.org/projects/salespyforce/badge/?version=latest' alt='Documentation Status' />
            </a>
        </td>
    </tr>
    <tr>
        <td>Security Audits</td>
        <td>
            <a href="https://github.com/marketplace/actions/python-security-check-using-bandit">
                <img alt="Bandit" src="https://img.shields.io/badge/security-bandit-yellow.svg">
            </a>
        </td>
    </tr>
    <tr>
        <td>License</td>
        <td>
            <a href="https://github.com/jeffshurtliff/salespyforce/blob/master/LICENSE">
                <img alt="License (GitHub)" src="https://img.shields.io/github/license/jeffshurtliff/salespyforce">
            </a>
        </td>
    </tr>
    <tr>
        <td style="vertical-align: top;">Issues</td>
        <td>
            <a href="https://github.com/jeffshurtliff/salespyforce/issues">
                <img style="margin-bottom:5px;" alt="GitHub open issues" src="https://img.shields.io/github/issues-raw/jeffshurtliff/salespyforce"><br />
            </a>
            <a href="https://github.com/jeffshurtliff/salespyforce/issues">
                <img alt="GitHub closed issues" src="https://img.shields.io/github/issues-closed-raw/jeffshurtliff/salespyforce">
            </a>
        </td>
    </tr>
    <tr>
        <td style="vertical-align: top;">Pull Requests</td>
        <td>
            <a href="https://github.com/jeffshurtliff/salespyforce/pulls">
                <img style="margin-bottom:5px;" alt="GitHub pull open requests" src="https://img.shields.io/github/issues-pr-raw/jeffshurtliff/salespyforce"><br />
            </a>
            <a href="https://github.com/jeffshurtliff/salespyforce/pulls">
                <img alt="GitHub closed pull requests" src="https://img.shields.io/github/issues-pr-closed-raw/jeffshurtliff/salespyforce">
            </a>
        </td>
    </tr>
</table>

## Overview
salespyforce is a Python toolkit focused on interacting with Salesforce APIs, with a primary `Salesforce` class 
that centralizes authentication, version selection, and access to helper feature sets (Chatter, Knowledge).

## Installation
The package can be installed via pip using the syntax below.

```sh
pip install salespyforce --upgrade
```

## Change Log
The change log can be found in the [documentation](https://salespyforce.readthedocs.io/en/latest/changelog.html).

## Usage
This section provides basic usage instructions for the package.

### Importing the package
Rather than importing the base package, it is recommended that you import the primary `Salesforce` class using the 
syntax below.

```python
from salespyforce import Salesforce
```

### Initializing a Salesforce object instance
The primary `Salesforce` object serves many purposes, the most important being to establish a connection to the 
Salesforce environment with which you intend to interact. As such, when initializing an instance of the `Salesforce` 
object, you will need to pass it the following information:
* The username and password of the API user
* The Organization ID of the Salesforce environment
* The Base URL and Endpoint URL
* The client ID, client secret, and security token

The `Salesforce` object can be initiated in two different ways:
* Passing the information directly into the object
* Leveraging a "helper" configuration file

#### Passing the information directly into the object
The environment and connection information can be passed directly into the `Salesforce` object when initializing it, 
as demonstrated in the example below.

```python
sfdc = Salesforce(
    username='admin.user@example.com',
    password='example123',
    org_id='4DJ000000CeMFYA0',
    base_url='https://example-dev-ed.lightning.force.com/',
    endpoint_url='https://example-dev-ed.my.salesforce.com/services/oauth2/token',
    client_id='3MVG9gTv.DiE8cKRIpEtSN_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX_TAoy1Zk_AKGukbqa4KbhM6nVYVUu6md',
    client_secret='7536F4A7865559XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX53797BEA88174713CC3C',
    security_token='2muXaXXXXXXXXXXXXXXXoVKxz'
)
```

#### Leveraging a "helper" configuration file
As an alternative to passing the connection information to the `Salesforce` class in the way demonstrated above, a
"helper" configuration file in `yaml` or `json` format can be leveraged instead and passed to the `Salesforce` class
when initializing the object.

This is an example of how the configuration file would be written in YAML format:

```yaml
# Helper configuration file for the SalesPyForce package

# Define how to obtain the connection information
connection:
    # Define the credentials
    username: admin.user@example.com
    password: example123

    # Define the org information
    org_id: 4DJ000000CeMFYA0
    base_url: https://example-dev-ed.lightning.force.com/
    endpoint_url: https://example-dev-ed.my.salesforce.com/services/oauth2/token

    # Define the API connection info
    client_key: 3MVG9gTv.DiE8cKRIpEtSN_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX_TAoy1Zk_AKGukbqa4KbhM6nVYVUu6md
    client_secret: 7536F4A7865559XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX53797BEA88174713CC3C
    security_token: 2muXaXXXXXXXXXXXXXXXoVKxz

# Define if SSL certificates should be verified when making API calls
ssl_verify: yes
```

The file can then be referenced using the `helper` argument when initializing the object instance, as shown below.

```python
HELPER_FILE = '/path/to/helper.yml'
sfdc = Salesforce(helper=HELPER_FILE)
```

## Documentation
The documentation is located here: [https://salespyforce.readthedocs.io/en/latest/](https://salespyforce.readthedocs.io/en/latest/)

## License
[MIT License](https://github.com/jeffshurtliff/salespyforce/blob/master/LICENSE)

## Reporting Issues
Issues can be reported within the [GitHub repository](https://github.com/jeffshurtliff/salespyforce/issues).

## Donations
If you would like to donate to this project then you can do so using [this PayPal link](https://www.paypal.com/cgi-bin/webscr?cmd=_donations&business=XDZ8M6UV6EFK6&item_name=SalesPyForce+Python+API&currency_code=USD).

## Disclaimer
This package is considered unofficial and is in no way endorsed or supported by [Salesforce Inc](https://www.salesforce.com).
