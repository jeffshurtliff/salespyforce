# -*- coding: utf-8 -*-
"""
:Module:            salespyforce.constants
:Synopsis:          Constants that are utilized throughout the package
:Created By:        Jeff Shurtliff
:Last Modified:     Jeff Shurtliff
:Modified Date:     24 Feb 2026
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final


# -----------------------------
# Versioning / meta
# -----------------------------
FALLBACK_SFDC_API_VERSION: Final[str] = '65.0'

# -----------------------------
# HTTP / networking defaults
# -----------------------------
DEFAULT_API_TIMEOUT_SECONDS: Final[int] = 30
DEFAULT_API_MAX_RETRIES: Final[int] = 3
VALID_HEADER_TYPES: Final[set] = {'default', 'articles'}


@dataclass(frozen=True)
class Headers:
    """Standard HTTP header names used by the package.

    .. versionadded:: 1.5.0

    This immutable namespace centralizes common header keys to avoid
    magic strings throughout the codebase and to reduce the risk of
    typographical errors. These values are intended for constructing
    outbound HTTP requests to the Salesforce REST API.
    """
    AUTHORIZATION: str = 'Authorization'
    CONTENT_TYPE: str = 'Content-Type'
    ACCEPT: str = 'Accept'
    ACCEPT_ENCODING: str = 'Accept-Encoding'
    ACCEPT_LANGUAGE: str = 'Accept-Language'


@dataclass(frozen=True)
class AuthSchemes:
    """Authentication schemes that are leveraged with the HTTP ``Authorization`` header.
       (`Reference <https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Authentication>`__)

    .. versionadded:: 1.5.0
    """
    BEARER: str = 'Bearer {token}'


@dataclass(frozen=True)
class ContentTypes:
    """Common HTTP ``Content-Type`` header values used by the package.

    .. versionadded:: 1.5.0

    This immutable namespace provides canonical MIME types used when
    sending or receiving data from the Salesforce REST API.
    """
    JSON: str = 'application/json'


@dataclass(frozen=True)
class EncodingTypes:
    """Common HTTP ``Accept-Encoding`` header values.
       (`Reference <https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Accept-Encoding>`__)

    .. versionadded:: 1.5.0
    """
    GZIP: str = 'gzip'
    COMPRESS: str = 'compress'
    DEFLATE: str = 'deflate'
    BR: str = 'br'
    ZSTD: str = 'zstd'
    DCB: str = 'dcb'
    DCZ: str = 'dcz'
    IDENTITY: str = 'identity'
    WILDCARD: str = '*'
    Q: str = ';q={weight}'


@dataclass(frozen=True)
class Languages:
    """Common IETF language tags for use in the Accept-Language HTTP header.

    .. versionadded:: 1.5.0

    These represent commonly used Salesforce-supported locales.
    Additional valid IETF language tags may be supplied manually
    when constructing request headers.
    """
    EN_US: str = 'en-US'
    EN_GB: str = 'en-GB'
    FR_FR: str = 'fr-FR'
    DE_DE: str = 'de-DE'
    ES_ES: str = 'es-ES'
    PT_BR: str = 'pt-BR'
    JA_JP: str = 'ja-JP'
    IT_IT: str = 'it-IT'
    ZH_CN: str = 'zh-CN'
    ZH_TW: str = 'zh-TW'
    WILDCARD: str = '*'
    Q: str = ';q={weight}'


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
    SERVICES_DATA: str = '/services/data'
    QUERY: str = '/services/data/v{api_version}/query'
    SOBJECT: str = '/services/data/v{api_version}/sobjects/{sobject}'
    SOBJECT_BY_ID: str = '/services/data/v{api_version}/sobjects/{sobject}/{record_id}'


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
    Q: str = 'q'
    LIMIT: str = 'limit'
    OFFSET: str = 'offset'
    NEXT_RECORDS_URL: str = 'nextRecordsUrl'


# -----------------------------
# Exported namespaces
# -----------------------------
HEADERS: Final[Headers] = Headers()
AUTH_SCHEMES: Final[AuthSchemes] = AuthSchemes()
CONTENT_TYPES: Final[ContentTypes] = ContentTypes()
ENCODING_TYPES: Final[EncodingTypes] = EncodingTypes()
LANGUAGES: Final[Languages] = Languages()
REST_PATHS: Final[RestPaths] = RestPaths()
QUERY_PARAMS: Final[QueryParams] = QueryParams()
