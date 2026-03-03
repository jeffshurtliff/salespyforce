# -*- coding: utf-8 -*-
# bandit: skip=B101
"""
:Module:            tests.integration.test_connection
:Synopsis:          Integration smoke test for Salesforce client connectivity
:Created By:        Jeff Shurtliff
:Last Modified:     Jeff Shurtliff (via GPT-5.3-Codex)
:Modified Date:     02 Mar 2026
"""

import pytest


@pytest.mark.integration
def test_salesforce_integration_client_has_base_url(salesforce_integration):
    """This function validates that integration fixture authentication returns a client."""
    assert isinstance(salesforce_integration.base_url, str)
    assert salesforce_integration.base_url
