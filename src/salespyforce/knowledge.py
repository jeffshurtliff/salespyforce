# -*- coding: utf-8 -*-
"""
:Module:            salespyforce.knowledge
:Synopsis:          Defines the Knowledge-related functions associated with the Salesforce API
:Created By:        Jeff Shurtliff
:Last Modified:     Jeff Shurtliff
:Modified Date:     27 Feb 2026
"""

from __future__ import annotations

from typing import Optional, Union, Tuple

from . import errors
from . import constants as const
from .utils import log_utils

# Initialize logging
logger = log_utils.initialize_logging(__name__)


def check_for_existing_article(
        sfdc_object: "Salesforce",
        title: str,
        sobject: Optional[str] = None,
        return_id: bool = False,
        return_id_and_number: bool = False,
        include_archived: bool = False,
) -> Union[str, Tuple[str, str]]:
    """This method checks to see if an article already exists with a given title and returns its article number.
    (`Reference 1 <https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/dome_query.htm>`__,
    `Reference 2 <https://developer.salesforce.com/docs/atlas.en-us.knowledge_dev.meta/knowledge_dev/knowledge_development_soql_sosl_intro.htm>`__)

    .. versionchanged:: 1.2.2
       You can now specify whether archived articles are included in the query results.

    :param sfdc_object: The instantiated SalesPyForce object
    :type sfdc_object: class[salespyforce.Salesforce]
    :param title: The title of the knowledge article for which to check
    :type title: str
    :param sobject: The Salesforce object to query (``Knowledge__kav`` by default)
    :type sobject: str, None
    :param return_id: Determines if the Article ID should be returned (``False`` by default)
    :type return_id: bool
    :param return_id_and_number: Determines if Article ID and Article Number should be returned (``False`` by default)
    :type return_id_and_number: bool
    :param include_archived: Determines if archived articles should be included (``False`` by default)
    :type include_archived: bool
    :returns: The Article Number, Article ID, or both, if found, or a blank string if not found
    :raises: :py:exc:`TypeError`
    """
    # Prepare the SOQL query
    sobject = _validate_knowledge_sobject(sobject)
    query = f"""
        SELECT {const.SOBJECT_FIELDS.ID}, {const.SOBJECT_FIELDS.ARTICLE_NUMBER} 
        FROM {sobject} 
        WHERE {const.SOBJECT_FIELDS.TITLE} = '{title}'
    """
    if not include_archived:
        query += f" AND {const.SOBJECT_FIELDS.PUBLISH_STATUS} != '{const.SOBJECT_FIELD_VALUES.ARCHIVED}'"

    # Perform and parse the SOQL query
    response = sfdc_object.soql_query(query, replace_quotes=False)
    if response.get(const.RESPONSE_KEYS.TOTAL_SIZE) > 0:
        if return_id:
            return_value = response[const.RESPONSE_KEYS.RECORDS][0][const.SOBJECT_FIELDS.ID]
        elif return_id_and_number:
            return_value = (
                response[const.RESPONSE_KEYS.RECORDS][0][const.SOBJECT_FIELDS.ID],
                response[const.RESPONSE_KEYS.RECORDS][0][const.SOBJECT_FIELDS.ARTICLE_NUMBER],
            )
        else:
            return_value = response[const.RESPONSE_KEYS.RECORDS][0][const.SOBJECT_FIELDS.ARTICLE_NUMBER]
    elif return_id_and_number:
        return_value = ('', '')
    else:
        return_value = ''
    return return_value


def get_article_id_from_number(
        sfdc_object: "Salesforce",
        article_number: Union[str, int],
        sobject: Optional[str] = None,
        return_uri: bool = False,
) -> str:
    """This method returns the Article ID when an article number is provided.
    (`Reference 1 <https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/dome_query.htm>`__,
    `Reference 2 <https://developer.salesforce.com/docs/atlas.en-us.knowledge_dev.meta/knowledge_dev/knowledge_development_soql_sosl_intro.htm>`__)

    .. warning::
       The ability to retrieve the article URI/URL rather than the ID will be moved to a separate function in
       a future release.

    .. versionchanged:: 1.4.0
       A logic issue has been fixed and improved to make this function more robust and stable.

    :param sfdc_object: The instantiated SalesPyForce object
    :type sfdc_object: class[salespyforce.Salesforce]
    :param article_number: The Article Number to query
    :type article_number: str, int
    :param sobject: The Salesforce object to query (``Knowledge__kav`` by default)
    :type sobject: str, None
    :param return_uri: Determines if the URI of the article should be returned rather than the ID (``False`` by default)
    :type return_uri: bool
    :returns: The Article ID or Article URI, or a blank string if no article is found
    :raises: :py:exc:`TypeError`,
             :py:exc:`RuntimeError`
    """
    # Ensure the sobject is defined appropriately
    sobject = _validate_knowledge_sobject(sobject)

    # Construct the SOQL query to perform
    if not isinstance(article_number, str):
        article_number = str(article_number)
    query = f'SELECT {const.SOBJECT_FIELDS.ID} FROM {sobject} '
    if len(article_number) < 9:
        query += f"WHERE {const.SOBJECT_FIELDS.ARTICLE_NUMBER} LIKE '%0{article_number}'"
    else:
        query += f"WHERE {const.SOBJECT_FIELDS.ARTICLE_NUMBER} = '{article_number}'"

    # Perform the SOQL query and return the article number if found
    response = sfdc_object.soql_query(query)
    if response.get(const.RESPONSE_KEYS.TOTAL_SIZE) > 0:
        if return_uri:
            # TODO: Split out the return_uri functionality into a separate function and method
            warn_msg = ("The ability to retrieve the article URI/URL rather than the ID (return_uri parameter) will "
                        "be moved to a separate function/method in a future release")
            logger.warning(warn_msg)
            errors.handlers.display_warning(warn_msg)
            return_value = response[const.RESPONSE_KEYS.RECORDS][0][const.RESPONSE_KEYS.ATTRIBUTES][const.RESPONSE_KEYS.URL]
        else:
            return_value = response[const.RESPONSE_KEYS.RECORDS][0][const.SOBJECT_FIELDS.ID]
    else:
        return_value = ''
        warn_msg = f'No results were returned when querying for the article number {article_number}'
        logger.warning(warn_msg)
    return return_value


def get_articles_list(
        sfdc_object: "Salesforce",
        query: Optional[str] = None,
        sort: Optional[str] = None,
        order: Optional[str] = None,
        page_size: int = const.QUERY_PARAMS.DEFAULT_PAGE_SIZE,      # Default: 20
        page_num: int = const.QUERY_PARAMS.DEFAULT_PAGE_NUM,        # Default: 1
) -> list:
    """This function retrieves a list of knowledge articles.
    (`Reference <https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/resources_knowledge_support_artlist.htm>`__)

    .. versionchanged:: 1.4.0
       The errors now log as errors via the logger rather than to the stderr console.

    :param sfdc_object: The instantiated SalesPyForce object
    :type sfdc_object: class[salespyforce.Salesforce]
    :param query: A SOQL query with which to filter the results (optional)
    :type query: str, None
    :param sort: One of the following optional values: ``LastPublishedDate``, ``CreatedDate``, ``Title``, or ``ViewScore``
    :type sort: str, None
    :param order: Optionally define the ORDER BY as ``ASC`` or ``DESC``
    :type order: str, None
    :param page_size: The number of results per page (``20`` by default)
    :type page_size: int
    :param page_num: The starting page number (``1`` by default)
    :type page_num: int
    :returns: The list of retrieved knowledge articles
    """
    # Define the headers
    headers = sfdc_object._get_headers(const.HEADER_TYPE_ARTICLES)

    # Validate the sort parameter and ignore the value if it is invalid
    if sort and sort not in const.SOBJECT_FIELDS.VALID_KNOWLEDGE_SORT_FIELDS:
        logger.error(const._LOG_MESSAGES._INVALID_PARAM_VALUE_IGNORE.format(
            param=const.QUERY_PARAMS.SORT,
            value=sort
        ))
        sort = None

    # Validate the order parameter and ignore the value if it is invalid
    if order and order.upper() not in const.SOQL_QUERIES.VALID_ORDER_DIRECTIONS:
        logger.error(const._LOG_MESSAGES._INVALID_PARAM_VALUE_IGNORE.format(
            param=const.QUERY_PARAMS.ORDER,
            value=order
        ))
        order = None

    # Validate the page size parameter (Fall back to maximum value rather than default value if maximum is exceeded)
    if page_size > const.QUERY_PARAMS.MAX_PAGE_SIZE:
        logger.error(const._LOG_MESSAGES._PARAM_EXCEEDS_MAX_VALUE.format(
            param=const.QUERY_PARAMS.PAGE_SIZE,
            default=const.QUERY_PARAMS.MAX_PAGE_SIZE
        ))
        page_size = const.QUERY_PARAMS.MAX_PAGE_SIZE

    # Validate the pageNumber parameter and fall back to default value if it is invalid
    if page_num < const.QUERY_PARAMS.MIN_PAGE_NUM:
        logger.error(const._LOG_MESSAGES._INVALID_PARAM_VALUE_DEFAULT.format(
            param=const.QUERY_PARAMS.PAGE_NUM,
            default=const.QUERY_PARAMS.DEFAULT_PAGE_NUM
        ))
        page_num = const.QUERY_PARAMS.DEFAULT_PAGE_NUM

    # Add values to the parameters dictionary if they have been defined
    params = {}
    if query:
        params[const.QUERY_PARAMS.Q] = query
    if sort:
        params[const.QUERY_PARAMS.SORT] = sort
    if order:
        params[const.QUERY_PARAMS.ORDER] = order
    params[const.QUERY_PARAMS.PAGE_SIZE] = page_size
    params[const.QUERY_PARAMS.PAGE_NUM] = page_num

    # Perform the query
    # TODO: Determine what is returned by this API call and see if data should be pruned to just the list of articles
    # TODO: Replace the REST path below with a constant
    return sfdc_object.get(f'/services/data/{sfdc_object.version}/support/knowledgeArticles',
                           params=params, headers=headers)


def get_article_details(
        sfdc_object: "Salesforce",
        article_id: str,
        sobject: Optional[str] = None,
        use_knowledge_articles_endpoint: Optional[bool] = None,
):
    """This function retrieves details for a single knowledge article.
    (`Reference <https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/resources_knowledge_support_artdetails.htm>`__)

    .. versionchanged:: 1.4.0
       A logic issue was resolved and the new optional ``use_knowledge_articles_endpoint`` parameter can now be set to
       force the ``knowledgeArticles`` endpoint to be used for the GET request rather than the ``sobjects`` endpoint.

    :param sfdc_object: The instantiated SalesPyForce object
    :type sfdc_object: class[salespyforce.Salesforce]
    :param article_id: The Article ID for which to retrieve details
    :type article_id: str
    :param sobject: The Salesforce object to query (``Knowledge__kav`` by default)
    :type sobject: str, None
    :param use_knowledge_articles_endpoint: Optionally use the ``knowledgeArticles`` endpoint rather than ``sobjects``
                                            to retrieve the article details (``False`` by default)
    :type use_knowledge_articles_endpoint: bool, None
    :returns: The details for the knowledge article
    :raises: :py:exc:`RuntimeError`,
             :py:exc:`salespyforce.errors.exceptions.DataMismatchError`
    """
    # Define the headers based on the endpoint that will be utilized
    headers = sfdc_object._get_headers(const.HEADER_TYPE_ARTICLES) if use_knowledge_articles_endpoint else None

    # Ensure the sobject is defined appropriately
    sobject = _validate_knowledge_sobject(sobject, use_knowledge_articles_endpoint)

    # Define the endpoint to use in the GET request
    if use_knowledge_articles_endpoint:
        # TODO: Replace the REST path below with a constant
        endpoint = f'/services/data/{sfdc_object.version}/support/knowledgeArticles/{article_id}'
    else:
        sobject = const.SOBJECTS.KNOWLEDGE if not sobject else sobject
        # TODO: Replace the REST path below with a constant
        endpoint = f'/services/data/{sfdc_object.version}/sobjects/{sobject}/{article_id}'

    # Perform the query and return the data
    data = sfdc_object.get(endpoint, headers=headers)
    # TODO: Determine what is returned by this API call and see if data should be pruned to just the article details (for both endpoints)
    return data


def get_validation_status(
        sfdc_object: "Salesforce",
        article_id: Optional[str] = None,
        article_details: Optional[dict] = None,
        sobject: Optional[str] = None,
        use_knowledge_articles_endpoint: Optional[bool] = None,
) -> str:
    """This function retrieves the Validation Status for a given Article ID.
    (`Reference <https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/resources_knowledge_support_artdetails.htm>`__)

    .. versionchanged:: 1.5.0
       The `use_knowledge_articles_endpoint` parameter is now supported, which allows you to specify the
       REST path to utilize for the API query.

    .. versionchanged:: 1.4.0
       The function now returns an empty string rather than a ``None`` value if the ``ValidationStatus`` field
       is not found in the article details data, and a more specific exception class is used when input
       data is missing instead of the generic :py:exc:`RuntimeError` exception class.

    :param sfdc_object: The instantiated SalesPyForce object
    :type sfdc_object: class[salespyforce.Salesforce]
    :param article_id: The Article ID for which to retrieve details
    :type article_id: str, None
    :param article_details: The dictionary of article details for the given article
    :type article_details: dict, None
    :param sobject: The Salesforce object to query (``Knowledge__kav`` by default)
    :type sobject: str, None
    :param use_knowledge_articles_endpoint: Optionally use the ``knowledgeArticles`` endpoint rather than ``sobjects``
                                            to retrieve the article details (``False`` by default)
    :type use_knowledge_articles_endpoint: bool, None
    :returns: The validation status as a text string
    :raises: :py:exc:`RuntimeError`,
             :py:exc:`salespyforce.errors.exceptions.MissingRequiredDataError`
    """
    if not any((article_id, article_details)):
        error_msg = const._LOG_MESSAGES._MUST_BE_PROVIDED_ERROR.format(data='article ID or article details')
        logger.error(error_msg)
        raise errors.exceptions.MissingRequiredDataError(error_msg)

    # Retrieve the article details if not already supplied
    if not article_details:
        article_details = get_article_details(sfdc_object, article_id, sobject, use_knowledge_articles_endpoint)

    # Identify the validation status
    return article_details.get(const.SOBJECT_FIELDS.VALIDATION_STATUS, '')


def get_article_metadata(sfdc_object: "Salesforce", article_id: str):
    """This function retrieves metadata for a specific knowledge article.
    (`Reference <https://developer.salesforce.com/docs/atlas.en-us.knowledge_dev.meta/knowledge_dev/knowledge_REST_retrieve_article_metadata.htm>`__)

    :param sfdc_object: The instantiated SalesPyForce object
    :type sfdc_object: class[salespyforce.Salesforce]
    :param article_id: The Article ID for which to retrieve details
    :type article_id: str
    :returns: The article metadata as a dictionary
    :raises: :py:exc:`RuntimeError`
    """
    # TODO: Replace the REST path below with a constant and update :raises: with correct exceptions
    return sfdc_object.get(f'/services/data/{sfdc_object.version}/knowledgeManagement/articles/{article_id}')


def get_article_version(sfdc_object: "Salesforce", article_id: str):
    """This function retrieves the version ID for a given master article ID.
    (`Reference <https://developer.salesforce.com/docs/atlas.en-us.knowledge_dev.meta/knowledge_dev/knowledge_REST_retrieve_article_version.htm>`__)

    :param sfdc_object: The instantiated SalesPyForce object
    :type sfdc_object: class[salespyforce.Salesforce]
    :param article_id: The Article ID for which to retrieve details
    :type article_id: str
    :returns: The version ID for the given master article ID
    :raises: :py:exc:`RuntimeError`
    """
    # TODO: Replace the REST path below with a constant and update :raises: with correct exceptions
    endpoint = f'/services/data/{sfdc_object.version}/knowledgeManagement/articleversions/masterVersions/{article_id}'
    # TODO: Determine what is returned by this API call and see if data should be pruned to just the Version ID
    return sfdc_object.get(endpoint)


def get_article_url(
        sfdc_object: "Salesforce",
        article_id: Optional[str] = None,
        article_number: Union[Optional[str], Optional[int]] = None,
        sobject: Optional[str] = None,
) -> str:
    """This function constructs the URL to view a knowledge article in Lightning or Classic.

    .. versionchanged:: 1.2.0
       Changed when lightning URLs are defined and fixed an issue with extraneous slashes.

    :param sfdc_object: The instantiated SalesPyForce object
    :type sfdc_object: class[salespyforce.Salesforce]
    :param article_id: The Article ID for which to retrieve details
    :type article_id: str, None
    :param article_number: The article number for which to retrieve details
    :type article_number: str, int, None
    :param sobject: The Salesforce object to query (``Knowledge__kav`` by default)
    :type sobject: str, None
    :returns: The article URL as a string
    :raises: :py:exc:`salespyforce.errors.exceptions.MissingRequiredDataError`
    """
    sobject = _validate_knowledge_sobject(sobject)
    if not any((article_id, article_number)):
        exc_msg = 'An article ID or an article number must be provided to retrieve the article URL.'
        raise errors.exceptions.MissingRequiredDataError(exc_msg)
    if article_number and not article_id:
        article_id = get_article_id_from_number(sfdc_object, article_number, sobject)
    segment = '' if sfdc_object.base_url.endswith('/') else '/'
    if 'lightning' in sfdc_object.base_url or sobject == const.SOBJECTS.KNOWLEDGE:
        # TODO: Convert the URL below into a constant
        article_url = f'{sfdc_object.base_url}{segment}lightning/r/{sobject}/{article_id}/view'
    else:
        # TODO: Convert the URL below into a constant
        article_url = f'{sfdc_object.base_url}{segment}knowledge/publishing/articleDraftDetail.apexp?id={article_id}'
    return article_url


def create_article(
        sfdc_object: "Salesforce",
        article_data: dict,
        sobject: Optional[str] = None,
        full_response: bool = False,
):
    """This function creates a new knowledge article draft.
    (`Reference <https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/dome_sobject_create.htm>`__)

    :param sfdc_object: The instantiated SalesPyForce object
    :type sfdc_object: class[salespyforce.Salesforce]
    :param article_data: The article data used to populate the article
    :type article_data: dict
    :param sobject: The Salesforce object to query (``Knowledge__kav`` by default)
    :type sobject: str, None
    :param full_response: Determines if the full API response should be returned instead of the article ID (``False`` by default)
    :type full_response: bool
    :returns: The API response or the ID of the article draft
    :raises: :py:exc:`ValueError`,
             :py:exc:`TypeError`,
             :py:exc:`RuntimeError`
    """
    # Ensure the sobject is defined appropriately
    sobject = _validate_knowledge_sobject(sobject)

    # Ensure the payload is in the appropriate format
    _validate_article_data(article_data)

    # Ensure that the required fields have been provided
    _check_required_article_fields(article_data)

    # Define the endpoint and perform the API call
    endpoint = const.REST_PATHS.SOBJECT.format(
        api_version=sfdc_object.version,
        sobject=sobject,
    )
    response = sfdc_object.post(endpoint, payload=article_data)

    # Return the full response or just the article ID
    if not full_response:
        # TODO: Verify that the `id` value below is correct and shouldn't be `Id` instead
        response = response.get('id')
    return response


def update_article(
        sfdc_object: "Salesforce",
        record_id: str,
        article_data: dict,
        sobject: Optional[str] = None,
        include_status_code: bool = False,
):
    """This function updates an existing knowledge article draft.
    (`Reference <https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/dome_update_fields.htm>`__)

    :param sfdc_object: The instantiated SalesPyForce object
    :type sfdc_object: class[salespyforce.Salesforce]
    :param record_id: The ID of the article draft record to be updated
    :type record_id: str
    :param article_data: The article data used to update the article
    :type article_data: dict
    :param sobject: The Salesforce object to query (``Knowledge__kav`` by default)
    :type sobject: str, None
    :param include_status_code: Determines if the API response status code should be returned (``False`` by default)
    :type include_status_code: bool
    :returns: A Boolean indicating if the update operation was successful, and optionally the API response status code
    :raises: :py:exc:`ValueError`,
             :py:exc:`TypeError`,
             :py:exc:`RuntimeError`
    """
    # Ensure the sobject is defined appropriately
    sobject = _validate_knowledge_sobject(sobject)

    # Ensure the payload is in the appropriate format
    _validate_article_data(article_data)

    # Ensure that the required fields have been provided
    _check_required_article_fields(article_data)

    # Define the endpoint and perform the API call
    endpoint = const.REST_PATHS.SOBJECT_BY_ID.format(
        api_version=sfdc_object.version,
        sobject=sobject,
        record_id=record_id,
    )
    response = sfdc_object.patch(endpoint, payload=article_data)

    # Determine whether the call was successful
    successful = True if response.status_code == 204 else False

    # Return the success determination and optionally the status code
    if include_status_code:
        return successful, response.status_code
    return successful


def create_draft_from_online_article(sfdc_object: "Salesforce", article_id: str, unpublish: bool = False):
    """This function creates a draft knowledge article from an online article.
    (`Reference <https://developer.salesforce.com/docs/atlas.en-us.knowledge_dev.meta/knowledge_dev/actions_obj_knowledge.htm#createDraftFromOnlineKnowledgeArticle>`__)

    :param sfdc_object: The instantiated SalesPyForce object
    :type sfdc_object: class[salespyforce.Salesforce]
    :param article_id: The ID of the online article from which to create the draft
    :type article_id: str
    :param unpublish: Determines if the online article should be unpublished when the draft is created (``False`` by default)
    :type unpublish: bool
    :returns: The API response from the POST request
    :raises: :py:exc:`RuntimeError`
    """
    # Define the payload for the API call
    payload = {
        const.QUERY_PARAMS.INPUTS: [
            {
                const.QUERY_PARAMS.ACTION: const.PAYLOAD_VALUES.EDIT_AS_DRAFT,
                const.QUERY_PARAMS.UNPUBLISH: unpublish,
                const.QUERY_PARAMS.ARTICLE_ID: f"{article_id}"
            }
        ]
    }

    # Perform the API call
    # TODO: Replace the REST path below with a constant
    endpoint = f'/services/data/{sfdc_object.version}/actions/standard/createDraftFromOnlineKnowledgeArticle'
    return sfdc_object.post(endpoint, payload)


def create_draft_from_master_version(
        sfdc_object: "Salesforce",
        article_id: Optional[str] = None,
        knowledge_article_id: Optional[str] = None,
        article_data: Optional[dict] = None,
        sobject: Optional[str] = None,
        full_response: bool = False,
):
    """This function creates an online version of a master article.
    (`Reference <https://developer.salesforce.com/docs/atlas.en-us.198.0.knowledge_dev.meta/knowledge_dev/knowledge_REST_edit_online_master.htm>`__)

    .. versionchanged:: 1.5.0
       The :py:exc:`salespyforce.errors.exceptions.MissingRequiredDataError` exception class is now raised when
       required parameters are missing instead of the generic :py:exc:`RuntimeError` exception.

    :param sfdc_object: The instantiated SalesPyForce object
    :type sfdc_object: class[salespyforce.Salesforce]
    :param article_id: The Article ID from which to create the draft
    :type article_id: str, None
    :param knowledge_article_id: The Knowledge Article ID (``KnowledgeArticleId``) from which to create the draft
    :type knowledge_article_id: str, None
    :param article_data: The article data associated with the article from which to create the draft
    :type article_data: dict, None
    :param sobject: The Salesforce object to query (``Knowledge__kav`` by default)
    :type sobject: str, None
    :param full_response: Determines if the full API response should be returned instead of the article ID (``False`` by default)
    :type full_response: bool
    :returns: The API response or the ID of the article draft
    :raises: :py:exc:`salespyforce.errors.exceptions.MissingRequiredDataError`
    """
    if not any((article_id, knowledge_article_id, article_data)):
        error_msg = 'Need to provide article ID, knowledge article ID, or article data'
        logger.error(error_msg)
        raise errors.exceptions.MissingRequiredDataError(error_msg)

    # Ensure the sobject is defined appropriately
    sobject = _validate_knowledge_sobject(sobject)

    # Ensure the payload is in the appropriate format
    _validate_article_data(article_data)

    # Get the knowledge article ID as needed
    if not knowledge_article_id:
        if not article_data:
            article_data = sfdc_object.get_article_details(article_id, sobject=sobject)
        knowledge_article_id = article_data.get(const.SOBJECT_FIELDS.KNOWLEDGE_ARTICLE_ID)

    # Perform the API call to retrieve the new draft ID
    # TODO: Replace the REST path below with a constant
    endpoint = f'/services/data/{sfdc_object.version}/knowledgeManagement/articleVersions/masterVersions'
    response = sfdc_object.post(endpoint, {const.QUERY_PARAMS.ARTICLE_ID: knowledge_article_id})

    # Return the full response or the draft ID
    if not full_response:
        # TODO: Verify that the `id` value below is correct and shouldn't be `Id` instead
        response = response.get('id')
    return response


def publish_article(
        sfdc_object: "Salesforce",
        article_id: str,
        major_version: bool = True,
        full_response: bool = False,
):
    """This function publishes a draft knowledge article as a major or minor version.
    (`Reference <https://developer.salesforce.com/docs/atlas.en-us.knowledge_dev.meta/knowledge_dev/knowledge_REST_publish_master_version.htm>`__)

    :param sfdc_object: The instantiated SalesPyForce object
    :type sfdc_object: class[salespyforce.Salesforce]
    :param article_id: The Article ID to publish
    :type article_id: str
    :param major_version: Determines if the published article should be a major version (``True`` by default)
    :type major_version: bool
    :param full_response: Determines if the full API response should be returned (``False`` by default)
    :type full_response: bool
    :returns: A Boolean value indicating the success of the action or the API response from the PATCH request
    :raises: :py:exc:`RuntimeError`
    """
    # Define the payload for the API call
    payload = {
        const.QUERY_PARAMS.PUBLISH_STATUS: const.PAYLOAD_VALUES.ONLINE
    }
    if major_version:
        payload[const.QUERY_PARAMS.VERSION_NUMBER] = const.PAYLOAD_VALUES.NEXT_VERSION

    # Perform the API call
    # TODO: Replace the REST path below with a constant
    endpoint = f'/services/data/{sfdc_object.version}/knowledgeManagement/articleVersions/masterVersions/{article_id}'
    result = sfdc_object.patch(endpoint, payload)

    # Return the appropriate value depending on if a full response was requested
    if not full_response:
        result = True if result.status_code == 204 else False
    return result


def publish_multiple_articles(sfdc_object: "Salesforce", article_id_list: list, major_version: bool = True):
    """This function publishes multiple knowledge article drafts at one time.
    (`Reference <https://developer.salesforce.com/docs/atlas.en-us.knowledge_dev.meta/knowledge_dev/actions_obj_knowledge.htm#publishKnowledgeArticles>`__)

    .. versionchanged:: 1.5.0
       The :py:exc:`salespyforce.errors.exceptions.MissingRequiredDataError` exception class is now raised
       when required parameters are missing instead of a more generic exception.

    :param sfdc_object: The instantiated SalesPyForce object
    :type sfdc_object: class[salespyforce.Salesforce]
    :param article_id_list: A list of Article IDs to be published
    :type article_id_list: list
    :param major_version: Determines if the published article should be a major version (``True`` by default)
    :type major_version: bool
    :returns: The API response from the POST request
    :raises: :py:exc:`RuntimeError`,
             :py:exc:`salespyforce.errors.exceptions.MissingRequiredDataError`
    """
    # Define the endpoint URI
    # TODO: Replace the REST path below with a constant
    endpoint = f'/services/data/{sfdc_object.version}/actions/standard/publishKnowledgeArticles'

    # Ensure there is at least one article ID to publish
    validation_error = None
    if not isinstance(article_id_list, list) or not isinstance(article_id_list[0], str):
        validation_error = 'A list of Article ID strings must be provided in order to publish multiple articles.'
    elif len(article_id_list) == 0:
        validation_error = 'No article ID strings were found in the article ID list variable.'
    if validation_error:
        logger.error(validation_error)
        raise errors.exceptions.MissingRequiredDataError(validation_error)

    # Define the action to perform
    action = const.PAYLOAD_VALUES.PUBLISH_ARTICLE_NEW_VERSION if major_version else const.PAYLOAD_VALUES.PUBLISH_ARTICLE

    # Construct the payload
    payload = {
        const.QUERY_PARAMS.INPUTS: [
            {
                const.QUERY_PARAMS.ARTICLE_VERSION_ID_LIST: article_id_list,
                const.QUERY_PARAMS.PUBLISH_ACTION: action
            }
        ]
    }

    # Perform the API call
    return sfdc_object.post(endpoint, payload)


def assign_data_category(sfdc_object: "Salesforce", article_id: str, category_group_name: str, category_name: str):
    """This function assigns a single data category for a knowledge article.
    (`Reference <https://itsmemohit.medium.com/quick-win-15-salesforce-knowledge-rest-apis-bb0725b2040e>`__)

    .. versionadded:: 1.2.0

    :param sfdc_object: The instantiated SalesPyForce object
    :type sfdc_object: class[salespyforce.Salesforce]
    :param article_id: The ID of the article to update
    :type article_id: str
    :param category_group_name: The unique Data Category Group Name
    :type category_group_name: str
    :param category_name: The unique Data Category Name
    :type category_name: str
    :returns: The API response from the POST request
    :raises: :py:exc:`RuntimeError`
    """
    # Define the payload for the API call
    payload = {
        const.SOBJECT_FIELDS.PARENT_ID: article_id,
        const.SOBJECT_FIELDS.DATA_CATEGORY_GROUP_NAME: category_group_name,
        const.SOBJECT_FIELDS.DATA_CATEGORY_NAME: category_name
    }

    # Define the endpoint and perform the API call
    endpoint = const.REST_PATHS.SOBJECT.format(
        api_version=sfdc_object.version,
        sobject=const.SOBJECTS.KNOWLEDGE_DATA_CATEGORY_SELECTION,
    )
    return sfdc_object.post(endpoint, payload)


def archive_article(sfdc_object: "Salesforce", article_id: str):
    """This function archives a published knowledge article.
    (`Reference <https://developer.salesforce.com/docs/atlas.en-us.knowledge_dev.meta/knowledge_dev/knowledge_REST_archive_master_version.htm>`__)

    .. versionadded:: 1.3.0

    :param sfdc_object: The instantiated SalesPyForce object
    :type sfdc_object: class[salespyforce.Salesforce]
    :param article_id: The ID of the article to archive
    :type article_id: str
    :returns: The API response from the PATCH request
    :raises: :py:exc:`RuntimeError`
    """
    # Define the payload for the API call
    payload = {
        const.QUERY_PARAMS.PUBLISH_STATUS: const.PAYLOAD_VALUES.ARCHIVED
    }

    # Define the endpoint and perform the API call
    endpoint = const.REST_PATHS.ARTICLE_MASTER_VERSION_BY_ID.format(
        api_version=sfdc_object.version,
        article_id=article_id,
    )
    return sfdc_object.patch(endpoint, payload)


def delete_article_draft(sfdc_object: "Salesforce", version_id: str, sobject: Optional[str] = None,
                         use_knowledge_management_endpoint: bool = True):
    """This function deletes an unpublished knowledge article draft.
    
    .. versionchanged:: 1.5.0
       An optional ``sobject`` parameter can now be passed to specify the sObject against which to query.

    .. versionadded:: 1.4.0
    
    :param sfdc_object: The instantiated SalesPyForce object
    :type sfdc_object: class[salespyforce.Salesforce]
    :param version_id: The 15-character or 18-character ``Id`` (Knowledge Article Version ID) value
    :type version_id: str
    :param sobject: The Salesforce object to query (``Knowledge__kav`` by default)
    :type sobject: str, None
    :param use_knowledge_management_endpoint: Leverage the ``/knowledgeManagement/articleVersions/masterVersions/``
                                              endpoint rather than the ``/sobjects/Knowledge__kav/`` endpoint
                                              (``True`` by default)
    :type use_knowledge_management_endpoint: bool
    :returns: The API response from the DELETE request
    :raises: :py:exc:`RuntimeError`
    """
    # Ensure the sobject is defined appropriately
    sobject = _validate_knowledge_sobject(sobject)

    # Define the appropriate REST path and perform the API call
    if use_knowledge_management_endpoint:
        endpoint = const.REST_PATHS.ARTICLE_MASTER_VERSION_BY_ID.format(
            api_version=sfdc_object.version,
            article_id=version_id,
        )
    else:
        endpoint = const.REST_PATHS.SOBJECT_BY_ID.format(
            api_version=sfdc_object.version,
            sobject=sobject,
            record_id=version_id,
        )
    return sfdc_object.delete(endpoint)


def _validate_knowledge_sobject(
        _sobject: Optional[str] = None,
        _use_knowledge_articles_endpoint: Optional[bool] = None,
) -> str:
    """This function validates that a Knowledge sObject exists and supplies the default ``Knowledge__kav``
       object when missing.

    .. versionadded:: 1.5.0

    :param _sobject: The Knowledge sObject to validate
    :type _sobject: str, None
    :param _use_knowledge_articles_endpoint: Determines if the ``knowledgeArticles`` endpoint should be used rather
                                             than ``sobjects`` to retrieve the article details
    :type _use_knowledge_articles_endpoint: bool, None
    :returns: The provided sObject (or the default Knowledge sObject)
    :raises: :py:exc:`TypeError`,
             :py:exc:`salespyforce.errors.exceptions.DataMismatchError`
    """
    # Ensure that the sObject is a string
    if _sobject and not isinstance(_sobject, str):
        exc_msg = f'The sobject must be a string (provided: {type(_sobject)})'
        logger.error(exc_msg)
        raise TypeError(exc_msg)

    # Ensure there are no conflicting parameters
    if _sobject and _use_knowledge_articles_endpoint:
        if _sobject == const.SOBJECTS.KNOWLEDGE:
            _info_msg = (f'It is not necessary to define the sObject as {const.SOBJECTS.KNOWLEDGE} when leveraging '
                         'the knowledgeArticles endpoint')
            logger.info(_info_msg)
        else:
            _error_msg = 'You cannot use the knowledgeArticles endpoint with an explicitly defined sObject'
            logger.error(_error_msg)
            raise errors.exceptions.DataMismatchError(_error_msg)

    # Leverage the default sObject (Knowledge__kav) if a specific sObject was not provided
    elif not _sobject:
        _sobject = const.SOBJECTS.KNOWLEDGE
        logger.debug(const._LOG_MESSAGES._DEFAULT_SOBJECT_USED.format(sobject=_sobject))
    return _sobject


def _validate_article_data(_article_data: Optional[dict] = None, _required: bool = False) -> None:
    """This function validates the article data to ensure it is defined when required and hsa the appropriate type.

    .. versionadded:: 1.5.0

    :param _article_data: The article data to validate
    :type _article_data: dict, None
    :param _required: Indicates whether the article data is required (``False`` by default)
    :type _required: bool
    :returns: None
    :raises: :py:exc:`TypeError`,
             :py:exc:`salespyforce.errors.exceptions.DataMismatchError`
    """
    if _required and not _article_data:
        _error_msg = const._LOG_MESSAGES._MISSING_REQUIRED_DATA.format(data='article data')
        logger.error(_error_msg)
        raise errors.exceptions.MissingRequiredDataError(_error_msg)
    elif _article_data and not isinstance(_article_data, dict):
        logger.error(const._LOG_MESSAGES._ARTICLE_DATA_TYPE_ERROR)
        raise TypeError(const._LOG_MESSAGES._ARTICLE_DATA_TYPE_ERROR)


def _check_required_article_fields(_article_data: dict) -> None:
    """This function checks to ensure that the fields required to create or update an article are present.

    .. versionadded:: 1.5.0

    :param _article_data: The article data to validate
    :type _article_data: dict
    :returns: None
    :raises: :py:exc:`errors.exceptions.MissingRequiredDataError``
    """
    for _field in const.SOBJECT_FIELDS.REQUIRED_ARTICLE_CREATE_UPDATE_FIELDS:
        if _field not in _article_data:
            _error_msg = const._LOG_MESSAGES._MISSING_ARTICLE_FIELD_ERROR.format(field=_field)
            logger.error(_error_msg)
            raise errors.exceptions.MissingRequiredDataError(_error_msg)
