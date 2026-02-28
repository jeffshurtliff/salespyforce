# -*- coding: utf-8 -*-
"""
:Module:            salespyforce.constants
:Synopsis:          Constants that are utilized throughout the package
:Created By:        Jeff Shurtliff
:Last Modified:     Jeff Shurtliff
:Modified Date:     28 Feb 2026
"""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Final, ClassVar, Mapping, Union


# -----------------------------
# Versioning / Meta
# -----------------------------
FALLBACK_SFDC_API_VERSION: Final[str] = '65.0'      # Used if querying the org for the version fails


# --------------------------------------
# Common Validation Criteria / Mapping
# --------------------------------------
SALESFORCE_ID_SUFFIX_ALPHABET: Final[str] = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ012345'
VALID_SALESFORCE_URL_PATTERN: Final[str] = r'^https://[a-zA-Z0-9._-]+\.salesforce\.com(/|$)'
YAML_BOOLEAN_MAPPING: Final[Mapping[Union[str, bool], bool]] = MappingProxyType({
    True: True,
    False: False,
    'yes': True,
    'no': False,
})


# -----------------------------
# Error Handling
# -----------------------------
_DEFAULT_WARNING_CATEGORY: Final[type[Warning]] = UserWarning


# -----------------------------
# Exception Classes
# -----------------------------
@dataclass(frozen=True)
class ExceptionClasses:
    """Constants utilized by the exception classes in the :py:mod:`salespyforce.errors.exceptions` module.

    .. versionadded:: 1.5.0
    """
    # Keyword arguments
    _DATA: str = 'data'
    _FEATURE: str = 'feature'
    _FIELD: str = 'field'
    _FILE: str = 'file'
    _IDENTIFIER: str = 'identifier'
    _INIT: str = 'init'
    _INITIALIZE: str = 'initialize'
    _MESSAGE: str = 'message'
    _OBJECT: str = 'object'
    _PARAM: str = 'param'
    _REQUEST_TYPE: str = 'request_type'
    _STATUS_CODE: str = 'status_code'
    _URL: str = 'url'
    _VAL: str = 'val'
    _VALUE: str = 'value'

    # Exception messages and message segments
    _API_CUSTOM_MSG: str = 'The {type} request failed with the following message:'
    _API_DEFAULT_MSG: str = 'The {type} request did not return a successful response.'
    _WITH_THE_FOLLOWING_SEGMENT: str = ' with the following'


# -----------------------------
# File Type Extensions
# -----------------------------
@dataclass(frozen=True)
class FileExtensions:
    """Common file extensions leveraged throughout the package.

    .. versionadded:: 1.5.0
    """
    # Without delimiter
    JPEG: str = 'jpeg'
    JSON: str = 'json'
    YAML: str = 'yaml'
    YML: str = 'yml'

    # With delimiter
    DOT_JPEG: str = f'.{JPEG}'
    DOT_JSON: str = f'.{JSON}'
    DOT_YAML: str = f'.{YAML}'
    DOT_YML: str = f'.{YML}'


# -------------------------------
# Helper Configuration Settings
# -------------------------------
@dataclass(frozen=True)
class HelperSettings:
    """Fields, values, and other constants relating to the helper configuration settings and
       the :py:mod:`salespyforce.utils.helper` module.

    .. versionadded:: 1.5.0
    """
    # Validation criteria
    VALID_HELPER_FILE_TYPES: ClassVar[frozenset[str]] = frozenset({'json', 'yml', 'yaml'})

    # Authentication and connection fields
    CONNECTION: str = 'connection'
    USERNAME: str = 'username'
    PASSWORD: str = 'password'
    ORG_ID: str = 'org_id'
    BASE_URL: str = 'base_url'
    ENDPOINT_URL: str = 'endpoint_url'
    CLIENT_KEY: str = 'client_key'
    CLIENT_SECRET: str = 'client_secret'
    SECURITY_TOKEN: str = 'security_token'
    CONNECTION_KEYS: ClassVar[frozenset[str]] = frozenset({
        USERNAME, PASSWORD, BASE_URL, ENDPOINT_URL,
        CLIENT_KEY, CLIENT_SECRET, ORG_ID, SECURITY_TOKEN,
    })

    # Other configuration fields
    SSL_VERIFY: str = 'ssl_verify'


# -----------------------------
# HTTP / Networking Defaults
# -----------------------------
DEFAULT_API_TIMEOUT_SECONDS: Final[int] = 30
DEFAULT_API_MAX_RETRIES: Final[int] = 3
HEADER_TYPE_DEFAULT: Final[str] = 'default'
HEADER_TYPE_ARTICLES: Final[str] = 'articles'
VALID_HEADER_TYPES: Final[frozenset[str]] = frozenset({
    HEADER_TYPE_DEFAULT,
    HEADER_TYPE_ARTICLES,
})


# -----------------------------
# HTTP / REST API Request Types
# -----------------------------
@dataclass(frozen=True)
class ApiRequestTypes:
    """Standard REST API Request types used by the package.

    .. versionadded:: 1.5.0
    """
    GET: str = 'GET'
    PATCH: str = 'PATCH'
    POST: str = 'POST'
    PUT: str = 'PUT'
    DELETE: str = 'DELETE'


# -----------------------------
# HTTP Header Fields / Names
# -----------------------------
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


# -----------------------------
# HTTP Authentication Schemes
# -----------------------------
@dataclass(frozen=True)
class AuthSchemes:
    """Authentication schemes that are leveraged with the HTTP ``Authorization`` header.
       (`Reference <https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Authentication>`__)

    .. versionadded:: 1.5.0
    """
    BEARER: ClassVar[str] = 'Bearer {token}'


# -----------------------------
# HTTP Content Types
# -----------------------------
@dataclass(frozen=True)
class ContentTypes:
    """Common HTTP ``Content-Type`` header values used by the package.

    .. versionadded:: 1.5.0

    This immutable namespace provides canonical MIME types used when
    sending or receiving data from the Salesforce REST API.
    """
    JSON: ClassVar[str] = 'application/json'


# -----------------------------
# HTTP Encoding Types
# -----------------------------
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


# -----------------------------
# HTTP Language Tags
# -----------------------------
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


# -------------------------------
# Salesforce REST API Endpoints
# -------------------------------
@dataclass(frozen=True)
class Urls:
    """Common URLs leveraged throughout the package.

    .. versionadded:: 1.5.0
    """
    # Common URLs
    LIGHTNING_RECORD_PAGE = '{base_url}/lightning/r/{sobject}/{record_id}/view'                             # Vars: base_url, sobject, record_id

    # Knowledge URLs
    CLASSIC_ARTICLE_DRAFT = '{base_url}/knowledge/publishing/articleDraftDetail.apexp?id={article_id}'     # Vars: base_url, article_id


# -------------------------------
# Salesforce REST API Endpoints
# -------------------------------
@dataclass(frozen=True)
class RestPaths:
    """Template paths for Salesforce REST API endpoints.

    .. versionadded:: 1.5.0

    This immutable namespace centralizes commonly used REST endpoint
    templates to avoid duplicating hard-coded paths throughout the
    codebase. The templates are designed to be formatted with runtime
    values such as ``api_version``, ``sobject``, and ``record_id``.
    """
    # General REST paths
    SERVICES_DATA: ClassVar[str] = '/services/data'
    SERVICES_DATA_API: ClassVar[str] = SERVICES_DATA + '/{api_version}'
    SERVICES_DATA_API_SITE = SERVICES_DATA_API + '{site_segment}'
    QUERY: ClassVar[str] = SERVICES_DATA_API + '/query'
    SOBJECT: ClassVar[str] = SERVICES_DATA_API + '/sobjects/{sobject}'
    SOBJECT_BY_ID: ClassVar[str] = SOBJECT + '/{record_id}'

    # Chatter REST paths
    CONNECT_COMMUNITIES_SITE: ClassVar[str] = '/connect/communities/{site_id}'
    # TODO: See if the constant below is missing the SERVICE_DATA_API prefix
    CHATTER_FEEDS: ClassVar[str] = '/chatter/feeds'
    CHATTER_MY_NEWS_FEED: ClassVar[str] = CHATTER_FEEDS + '/news/me/feed-elements'
    CHATTER_USER_NEWS_FEED: ClassVar[str] = CHATTER_FEEDS + '/user-profile/{user_id}/feed-elements'
    CHATTER_GROUP_NEWS_FEED: ClassVar[str] = CHATTER_FEEDS + '/record/{group_id}/feed-elements'
    # TODO: See if the constant below is missing the SERVICE_DATA_API prefix
    CHATTER_FEED_ELEMENTS: ClassVar[str] = '/chatter/feed-elements'
    CHATTER_FEED_ELEMENT_COMMENTS: ClassVar[str] = CHATTER_FEED_ELEMENTS + '/{feed_element_id}/capabilities/comments/items'

    # Knowledge REST paths
    _ARTICLE_ID = '/{article_id}'                                                                           # Vars: article_id
    _STANDARD_ACTIONS = '/actions/standard'
    _ACTION_CREATE_DRAFT_ONLINE = _STANDARD_ACTIONS + '/createDraftFromOnlineKnowledgeArticle'
    _ACTION_PUBLISH_KNOWLEDGE_ARTICLES = _STANDARD_ACTIONS + '/publishKnowledgeArticles'
    KNOWLEDGE_MANAGEMENT = SERVICES_DATA_API + '/knowledgeManagement'                                       # Vars: api_version
    KNOWLEDGE_MANAGEMENT_ARTICLES = KNOWLEDGE_MANAGEMENT + '/articles'                                      # Vars: api_version
    KNOWLEDGE_MANAGEMENT_ARTICLE_BY_ID = KNOWLEDGE_MANAGEMENT_ARTICLES + _ARTICLE_ID                        # Vars: api_version, article_id
    KNOWLEDGE_MANAGEMENT_ARTICLE_VERSIONS = KNOWLEDGE_MANAGEMENT + '/articleVersions'                       # Vars: api_version
    KNOWLEDGE_MANAGEMENT_MASTER_VERSIONS = KNOWLEDGE_MANAGEMENT_ARTICLE_VERSIONS + '/masterVersions'        # Vars: api_version
    ARTICLE_MASTER_VERSION_BY_ID: ClassVar[str] = KNOWLEDGE_MANAGEMENT_MASTER_VERSIONS + _ARTICLE_ID        # Vars: api_version, article_id
    KNOWLEDGE_ARTICLES: ClassVar[str] = SERVICES_DATA_API + '/support/knowledgeArticles'                    # Vars: api_version
    KNOWLEDGE_ARTICLES_BY_ID: ClassVar[str] = KNOWLEDGE_ARTICLES + _ARTICLE_ID                              # Vars: api_version, article_id
    CREATE_DRAFT_FROM_ONLINE_ARTICLE: ClassVar[str] = SERVICES_DATA_API + _ACTION_CREATE_DRAFT_ONLINE       # Vars: api_version
    PUBLISH_KNOWLEDGE_ARTICLES: ClassVar[str] = SERVICES_DATA_API + _ACTION_PUBLISH_KNOWLEDGE_ARTICLES      # Vars: api_version


# --------------------------------------
# REST API Query Parameters and values
# --------------------------------------
@dataclass(frozen=True)
class QueryParams:
    """Standard query and payload parameter names used in Salesforce REST requests.

    .. versionadded:: 1.5.0

    This immutable namespace provides canonical parameter keys for
    constructing query strings when interacting with the Salesforce
    REST API. Centralizing these values helps prevent typographical
    errors and ensures consistent request construction.
    """
    # Common parameter names
    Q: ClassVar[str] = 'q'
    BODY: ClassVar[str] = 'body'
    CREATED_BY_ID: ClassVar[str] = 'createdById'
    INPUTS: ClassVar[str] = 'inputs'
    LIMIT: ClassVar[str] = 'limit'
    NEXT_RECORDS_URL: ClassVar[str] = 'nextRecordsUrl'
    OFFSET: ClassVar[str] = 'offset'
    ORDER: ClassVar[str] = 'order'
    PAGE_NUM: ClassVar[str] = 'pageNumber'
    PAGE_SIZE: ClassVar[str] = 'pageSize'
    REF_ID: ClassVar[str] = 'refid'
    SORT: ClassVar[str] = 'sort'
    TEXT: ClassVar[str] = 'text'
    TYPE: ClassVar[str] = 'type'

    # Common parameter default values
    DEFAULT_PAGE_NUM: ClassVar[int] = 1
    DEFAULT_PAGE_SIZE: ClassVar[int] = 20

    # Common parameter threshold values
    MIN_PAGE_NUM: ClassVar[int] = 1
    MAX_PAGE_SIZE: ClassVar[int] = 100

    # Chatter parameter names / fields
    FEED_ELEMENT_TYPE: ClassVar[str] = 'feedElementType'
    MESSAGE_SEGMENTS: ClassVar[str] = 'messageSegments'
    SUBJECT_ID: ClassVar[str] = 'subjectId'

    # Knowledge parameter names / fields
    ACTION: ClassVar[str] = 'action'
    ARTICLE_ID: ClassVar[str] = 'articleId'
    ARTICLE_VERSION_ID_LIST: ClassVar[str] = 'articleVersionIdList'
    PUBLISH_ACTION: ClassVar[str] = 'pubAction'
    PUBLISH_STATUS: ClassVar[str] = 'publishStatus'
    UNPUBLISH: ClassVar[str] = 'unpublish'
    VERSION_NUMBER: ClassVar[str] = 'versionNumber'


# -----------------------------
# REST API Payload Values
# -----------------------------
@dataclass(frozen=True)
class PayloadValues:
    """Standard and common payload values used in Salesforce REST requests.

    .. versionadded:: 1.5.0
    """
    # Chatter payload values
    FEED_ITEM: ClassVar[str] = 'FeedItem'
    TEXT: ClassVar[str] = 'text'

    # Knowledge payload values
    ARCHIVED: ClassVar[str] = 'Archived'
    EDIT_AS_DRAFT: ClassVar[str] = 'EDIT_AS_DRAFT_ARTICLE'
    NEXT_VERSION: ClassVar[str] = 'NextVersion'
    ONLINE: ClassVar[str] = 'Online'
    PUBLISH_ARTICLE: ClassVar[str] = 'PUBLISH_ARTICLE'
    PUBLISH_ARTICLE_NEW_VERSION: ClassVar[str] = 'PUBLISH_ARTICLE_NEW_VERSION'


# -----------------------------
# REST API Response Keys
# -----------------------------
@dataclass(frozen=True)
class ResponseKeys:
    """Standard and common keys / fields for Salesforce REST API responses.

    .. versionadded:: 1.5.0
    """
    ATTRIBUTES: ClassVar[str] = 'attributes'
    RECORDS: ClassVar[str] = 'records'
    TOTAL_SIZE: ClassVar[str] = 'totalSize'
    URL: ClassVar[str] = 'url'


# -----------------------------
# Salesforce Objects
# -----------------------------
@dataclass(frozen=True)
class SObjects:
    """Salesforce object (i.e. sObject) API names.

    .. versionadded:: 1.5.0
    """
    KNOWLEDGE: ClassVar[str] = 'Knowledge__kav'
    KNOWLEDGE_DATA_CATEGORY_SELECTION: ClassVar[str] = 'Knowledge__DataCategorySelection'
    USER_RECORD_ACCESS: ClassVar[str] = 'UserRecordAccess'


# -----------------------------
# Salesforce Object Fields
# -----------------------------
@dataclass(frozen=True)
class SObjectFields:
    """Standard and common field names relating to Salesforce objects.

    .. versionadded:: 1.5.0
    """
    # Common field names
    CREATED_DATE: ClassVar[str] = 'CreatedDate'
    ID: ClassVar[str] = 'Id'
    PARENT_ID: ClassVar[str] = 'ParentId'
    RECORD_ID: ClassVar[str] = 'RecordId'
    USER_ID: ClassVar[str] = 'UserId'

    # Knowledge__kav field names
    ARTICLE_NUMBER: ClassVar[str] = 'ArticleNumber'
    KNOWLEDGE_ARTICLE_ID: ClassVar[str] = 'KnowledgeArticleId'
    LAST_PUBLISHED_DATE: ClassVar[str] = 'LastPublishedDate'
    PUBLISH_STATUS: ClassVar[str] = 'PublishStatus'
    TITLE: ClassVar[str] = 'Title'
    URL_NAME: ClassVar[str] = 'UrlName'
    VALIDATION_STATUS: ClassVar[str] = 'ValidationStatus'
    VIEW_SCORE: ClassVar[str] = 'ViewScore'

    # Knowledge__kav validation criteria
    REQUIRED_ARTICLE_CREATE_UPDATE_FIELDS: ClassVar[frozenset[str]] = frozenset({
        TITLE,
        URL_NAME,
    })
    VALID_KNOWLEDGE_SORT_FIELDS: ClassVar[frozenset[str]] = frozenset({
        LAST_PUBLISHED_DATE,
        CREATED_DATE,
        TITLE,
        VIEW_SCORE,
    })

    # Knowledge__DataCategorySelection field names
    DATA_CATEGORY_GROUP_NAME: ClassVar[str] = 'DataCategoryGroupName'
    DATA_CATEGORY_NAME: ClassVar[str] = 'DataCategoryName'

    # UserRecordAccess field names
    HAS_DELETE_ACCESS: ClassVar[str] = 'HasDeleteAccess'
    HAS_EDIT_ACCESS: ClassVar[str] = 'HasEditAccess'
    HAS_READ_ACCESS: ClassVar[str] = 'HasReadAccess'

    # UserRecordAccess validation criteria
    VALID_ACCESS_CONTROL_FIELDS: ClassVar[frozenset[str]] = frozenset({
        HAS_READ_ACCESS,
        HAS_EDIT_ACCESS,
        HAS_DELETE_ACCESS,
    })


# --------------------------------
# Salesforce Object Field Values
# --------------------------------
@dataclass(frozen=True)
class SObjectFieldValues:
    """Standard and common field values for Salesforce objects.

    .. versionadded:: 1.5.0
    """
    # Knowledge__kav
    ARCHIVED: ClassVar[str] = 'Archived'


# -----------------------------
# SOQL Query Syntax
# -----------------------------
@dataclass(frozen=True)
class SoqlQueries:
    """Standard query syntax for Salesforce SOQL queries.

    .. versionadded:: 1.5.0
    """
    # Ordering / Sorting
    ORDER_ASC: ClassVar[str] = 'ASC'
    ORDER_DESC: ClassVar[str] = 'DESC'
    VALID_ORDER_DIRECTIONS: ClassVar[frozenset[str]] = frozenset({
        ORDER_ASC,
        ORDER_DESC,
    })


# -----------------------------
# Log Messages
# -----------------------------
@dataclass(frozen=True)
class LogMessages:
    """Common log messages that are utilized in multiple locations throughout the package.

    .. versionadded:: 1.5.0
    """
    _ARTICLE_DATA_TYPE_ERROR: ClassVar[str] = 'The article data must be provided as a dictionary.'
    _DEFAULT_SOBJECT_USED: ClassVar[str] = 'The {sobject} sObject will be used as a specific sObject was not provided'
    _INVALID_PARAM_VALUE_DEFAULT: ClassVar[str] = 'The {param} value is not valid and will default to {default}'
    _INVALID_PARAM_VALUE_IGNORE: ClassVar[str] = "The {param} value '{value}' is not valid and will be ignored"
    _MISSING_ARTICLE_FIELD_ERROR: ClassVar[str] = 'The following required field is missing from the article data: {field}'
    _MISSING_REQUIRED_DATA: ClassVar[str] = '{data} is missing and must be provided as it is required'
    _MUST_BE_PROVIDED_ERROR: ClassVar[str] = 'The {data} must be provided.'
    _PARAM_EXCEEDS_MAX_VALUE: ClassVar[str] = 'The {param} value exceeds the maximum and will default to {default}'


# -----------------------------
# Exported namespaces
# -----------------------------

# Common (Public)
FILE_EXTENSIONS: Final[FileExtensions] = FileExtensions()
URLS: Final[Urls] = Urls()

# Common (Private)
_EXCEPTION_CLASSES: Final[ExceptionClasses] = ExceptionClasses()
_LOG_MESSAGES: Final[LogMessages] = LogMessages()

# Helper Utility
HELPER_SETTINGS: Final[HelperSettings] = HelperSettings()

# HTTP / API
API_REQUEST_TYPES: Final[ApiRequestTypes] = ApiRequestTypes()
AUTH_SCHEMES: Final[AuthSchemes] = AuthSchemes()
CONTENT_TYPES: Final[ContentTypes] = ContentTypes()
ENCODING_TYPES: Final[EncodingTypes] = EncodingTypes()
HEADERS: Final[Headers] = Headers()
LANGUAGES: Final[Languages] = Languages()
PAYLOAD_VALUES: Final[PayloadValues] = PayloadValues()
QUERY_PARAMS: Final[QueryParams] = QueryParams()
RESPONSE_KEYS: Final[ResponseKeys] = ResponseKeys()
REST_PATHS: Final[RestPaths] = RestPaths()

# Salesforce Objects (sObjects)
SOBJECTS: Final[SObjects] = SObjects()
SOBJECT_FIELDS: Final[SObjectFields] = SObjectFields()
SOBJECT_FIELD_VALUES: Final[SObjectFieldValues] = SObjectFieldValues()
SOQL_QUERIES: Final[SoqlQueries] = SoqlQueries()
