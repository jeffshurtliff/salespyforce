# -*- coding: utf-8 -*-
"""
:Module:            salespyforce.constants
:Synopsis:          Constants that are utilized throughout the package
:Created By:        Jeff Shurtliff
:Last Modified:     Jeff Shurtliff
:Modified Date:     25 Feb 2026
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final, ClassVar


# -----------------------------
# Versioning / meta
# -----------------------------
FALLBACK_SFDC_API_VERSION: Final[str] = '65.0'


# -----------------------------
# HTTP / networking defaults
# -----------------------------
DEFAULT_API_TIMEOUT_SECONDS: Final[int] = 30
DEFAULT_API_MAX_RETRIES: Final[int] = 3
VALID_HEADER_TYPES: Final[frozenset[str]] = frozenset({'default', 'articles'})


@dataclass(frozen=True)
class Headers:
    """Standard HTTP header names used by the package.

    .. versionadded:: 1.5.0

    This immutable namespace centralizes common header keys to avoid
    magic strings throughout the codebase and to reduce the risk of
    typographical errors. These values are intended for constructing
    outbound HTTP requests to the Salesforce REST API.
    """
    AUTHORIZATION: ClassVar[str] = 'Authorization'
    CONTENT_TYPE: ClassVar[str] = 'Content-Type'
    ACCEPT: ClassVar[str] = 'Accept'
    ACCEPT_ENCODING: ClassVar[str] = 'Accept-Encoding'
    ACCEPT_LANGUAGE: ClassVar[str] = 'Accept-Language'


@dataclass(frozen=True)
class AuthSchemes:
    """Authentication schemes that are leveraged with the HTTP ``Authorization`` header.
       (`Reference <https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Authentication>`__)

    .. versionadded:: 1.5.0
    """
    BEARER: ClassVar[str] = 'Bearer {token}'


@dataclass(frozen=True)
class ContentTypes:
    """Common HTTP ``Content-Type`` header values used by the package.

    .. versionadded:: 1.5.0

    This immutable namespace provides canonical MIME types used when
    sending or receiving data from the Salesforce REST API.
    """
    JSON: ClassVar[str] = 'application/json'


@dataclass(frozen=True)
class EncodingTypes:
    """Common HTTP ``Accept-Encoding`` header values.
       (`Reference <https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Accept-Encoding>`__)

    .. versionadded:: 1.5.0
    """
    GZIP: ClassVar[str] = 'gzip'
    COMPRESS: ClassVar[str] = 'compress'
    DEFLATE: ClassVar[str] = 'deflate'
    BR: ClassVar[str] = 'br'
    ZSTD: ClassVar[str] = 'zstd'
    DCB: ClassVar[str] = 'dcb'
    DCZ: ClassVar[str] = 'dcz'
    IDENTITY: ClassVar[str] = 'identity'
    WILDCARD: ClassVar[str] = '*'
    Q: ClassVar[str] = ';q={weight}'


@dataclass(frozen=True)
class Languages:
    """Common IETF language tags for use in the Accept-Language HTTP header.

    .. versionadded:: 1.5.0

    These represent commonly used Salesforce-supported locales.
    Additional valid IETF language tags may be supplied manually
    when constructing request headers.
    """
    EN_US: ClassVar[str] = 'en-US'
    EN_GB: ClassVar[str] = 'en-GB'
    FR_FR: ClassVar[str] = 'fr-FR'
    DE_DE: ClassVar[str] = 'de-DE'
    ES_ES: ClassVar[str] = 'es-ES'
    PT_BR: ClassVar[str] = 'pt-BR'
    JA_JP: ClassVar[str] = 'ja-JP'
    IT_IT: ClassVar[str] = 'it-IT'
    ZH_CN: ClassVar[str] = 'zh-CN'
    ZH_TW: ClassVar[str] = 'zh-TW'
    WILDCARD: ClassVar[str] = '*'
    Q: ClassVar[str] = ';q={weight}'


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
    SERVICES_DATA: ClassVar[str] = '/services/data'
    SERVICES_DATA_API: ClassVar[str] = SERVICES_DATA + '/{api_version}'
    SERVICES_DATA_API_SITE = SERVICES_DATA_API + '{site_segment}'
    QUERY: ClassVar[str] = SERVICES_DATA_API + '/query'
    SOBJECT: ClassVar[str] = SERVICES_DATA_API + '/sobjects/{sobject}'
    SOBJECT_BY_ID: ClassVar[str] = SOBJECT + '/{record_id}'
    CONNECT_COMMUNITIES_SITE: ClassVar[str] = '/connect/communities/{site_id}'
    CHATTER_FEEDS: ClassVar[str] = '/chatter/feeds'
    CHATTER_MY_NEWS_FEED: ClassVar[str] = CHATTER_FEEDS + '/news/me/feed-elements'
    CHATTER_USER_NEWS_FEED: ClassVar[str] = CHATTER_FEEDS + '/user-profile/{user_id}/feed-elements'
    CHATTER_GROUP_NEWS_FEED: ClassVar[str] = CHATTER_FEEDS + '/record/{group_id}/feed-elements'
    CHATTER_FEED_ELEMENTS: ClassVar[str] = '/chatter/feed-elements'
    CHATTER_FEED_ELEMENT_COMMENTS: ClassVar[str] = CHATTER_FEED_ELEMENTS + '/{feed_element_id}/capabilities/comments/items'


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
    Q: ClassVar[str] = 'q'
    TYPE: ClassVar[str] = 'type'
    BODY: ClassVar[str] = 'body'
    TEXT: ClassVar[str] = 'text'
    LIMIT: ClassVar[str] = 'limit'
    OFFSET: ClassVar[str] = 'offset'
    NEXT_RECORDS_URL: ClassVar[str] = 'nextRecordsUrl'
    FEED_ELEMENT_TYPE: ClassVar[str] = 'feedElementType'
    CREATED_BY_ID: ClassVar[str] = 'createdById'
    SUBJECT_ID: ClassVar[str] = 'subjectId'
    MESSAGE_SEGMENTS: ClassVar[str] = 'messageSegments'


# -----------------------------
# REST Payload Values
# -----------------------------
@dataclass(frozen=True)
class PayloadValues:
    """Standard and common payload values used in Salesforce REST requests.

    .. versionadded:: 1.5.0
    """
    FEED_ITEM: ClassVar[str] = 'FeedItem'
    TEXT: ClassVar[str] = 'text'


# -----------------------------
# Salesforce Object Fields
# -----------------------------
@dataclass(frozen=True)
class SObjectFields:
    """Standard and common field names and similar values relating to Salesforce objects.

    .. versionadded:: 1.5.0
    """
    HAS_READ_ACCESS: ClassVar[str] = 'HasReadAccess'
    HAS_EDIT_ACCESS: ClassVar[str] = 'HasEditAccess'
    HAS_DELETE_ACCESS: ClassVar[str] = 'HasDeleteAccess'
    VALID_ACCESS_CONTROL_FIELDS: ClassVar[frozenset[str]] = frozenset(
        {HAS_READ_ACCESS, HAS_EDIT_ACCESS, HAS_DELETE_ACCESS}
    )


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
PAYLOAD_VALUES: Final[PayloadValues] = PayloadValues()
SOBJECT_FIELDS: Final[SObjectFields] = SObjectFields()
