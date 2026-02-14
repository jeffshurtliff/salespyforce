# Overview

SalesPyForce is a Python library designed to provide a comprehensive interface 
for interacting with the Salesforce API. It enables developers to programmatically 
access, manipulate, and manage Salesforce data and services through a cohesive 
and intuitive Python interface. This document provides a high-level overview of 
the library's purpose, architecture, and key components.[^1]

With this library, you can connect to a Salesforce org and perform tasks 
such as:

- Retrieving information about the Salesforce org including governor limits, 
  API versions, object details, and REST resources
- Creating, updating, and deleting records for standard and custom objects
- Verifying user access to specific records
- Executing SOQL (Salesforce Object Query Language) queries
- Executing SOSL (Salesforce Object Search Language) queries
- Working with knowledge articles (e.g., creating, updating, archiving, etc.)
- Interacting with Salesforce Chatter (e.g., retrieving news feeds, posting, etc.)

## Minimum Requirements

This library requires the following:

- Python version 3.9 or above (version 3.14 not yet officially supported)
- A Salesforce org (Production or Sandbox or Playground)
- A Salesforce user that has API privileges in the Salesforce org

## License and Support

SalesPyForce is available under the MIT License, which allows for free use, modification, 
and distribution with minimal restrictions. While the library is actively maintained and 
includes comprehensive testing, it is considered unofficial and is not endorsed or 
supported by [Salesforce Inc](https://salesforce.com).[^2]


[^1]: Overview introduction paragraph from [Devin.ai](https://app.devin.ai/wiki/jeffshurtliff/salespyforce)
[^2]: License and Support section from [Devin.ai](https://app.devin.ai/wiki/jeffshurtliff/salespyforce)
