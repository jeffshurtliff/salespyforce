# -*- coding: utf-8 -*-
"""
:Module:            salespyforce.constants
:Synopsis:          Constants that are utilized throughout the package
:Created By:        Jeff Shurtliff
:Last Modified:     Jeff Shurtliff
:Modified Date:     22 Feb 2026
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final


# -----------------------------
# Versioning / meta
# -----------------------------
FALLBACK_SFDC_API_VERSION: Final[str] = "65.0"

# -----------------------------
# HTTP / networking defaults
# -----------------------------
DEFAULT_TIMEOUT_SECONDS: Final[int] = 30
DEFAULT_MAX_RETRIES: Final[int] = 3


@dataclass(frozen=True)
class Headers:
    """Standard HTTP header names used by the package.

    .. versionadded:: 1.5.0

    This immutable namespace centralizes common header keys to avoid
    magic strings throughout the codebase and to reduce the risk of
    typographical errors. These values are intended for constructing
    outbound HTTP requests to the Salesforce REST API.
    """
    AUTHORIZATION: str = "Authorization"
    CONTENT_TYPE: str = "Content-Type"
    ACCEPT: str = "Accept"


@dataclass(frozen=True)
class ContentTypes:
    """Common HTTP ``Content-Type`` header values used by the package.

    .. versionadded:: 1.5.0

    This immutable namespace provides canonical MIME types used when
    sending or receiving data from the Salesforce REST API.
    """
    JSON: str = "application/json"


# -----------------------------
# Salesforce REST endpoints
# -----------------------------
@dataclass(frozen=True)
class RestPaths:
    """Template paths for Salesforce REST API endpoints.

    .. versionadded:: 1.5.0

    This immutable namespace centralizes commonly used REST endpoint
    templates to avoid duplicating hard-coded paths throughout the
    codebase. The templates are designed to be formatted with runtime
    values such as ``api_version``, ``sobject``, and ``record_id``.
    """
    SERVICES_DATA: str = "/services/data"
    QUERY: str = "/services/data/v{api_version}/query"
    SOBJECT: str = "/services/data/v{api_version}/sobjects/{sobject}"
    SOBJECT_BY_ID: str = "/services/data/v{api_version}/sobjects/{sobject}/{record_id}"


# -----------------------------
# Query params / common keys
# -----------------------------
@dataclass(frozen=True)
class QueryParams:
    """Standard query parameter names used in Salesforce REST requests.

    .. versionadded:: 1.5.0

    This immutable namespace provides canonical parameter keys for
    constructing query strings when interacting with the Salesforce
    REST API. Centralizing these values helps prevent typographical
    errors and ensures consistent request construction.
    """
    Q: str = "q"
    LIMIT: str = "limit"
    OFFSET: str = "offset"
    NEXT_RECORDS_URL: str = "nextRecordsUrl"


# -----------------------------
# Exported namespaces
# -----------------------------
HEADERS: Final[Headers] = Headers()
CONTENT_TYPES: Final[ContentTypes] = ContentTypes()
REST_PATHS: Final[RestPaths] = RestPaths()
QUERY_PARAMS: Final[QueryParams] = QueryParams()
