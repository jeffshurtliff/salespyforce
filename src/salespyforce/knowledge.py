# -*- coding: utf-8 -*-
"""
:Module:            salespyforce.knowledge
:Synopsis:          Defines the Knowledge-related functions associated with the Salesforce API
:Created By:        Jeff Shurtliff
:Last Modified:     Jeff Shurtliff
:Modified Date:     30 Jan 2026
"""

from . import errors
from .utils import log_utils

# Initialize logging
logger = log_utils.initialize_logging(__name__)


def check_for_existing_article(sfdc_object, title, sobject=None, return_id=False, return_id_and_number=False,
                               include_archived=False):
    """This method checks to see if an article already exists with a given title and returns its article number.
    (`Reference 1 <https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/dome_query.htm>`_,
    `Reference 2 <https://developer.salesforce.com/docs/atlas.en-us.knowledge_dev.meta/knowledge_dev/knowledge_development_soql_sosl_intro.htm>`_)

    .. version-changed:: 1.2.2
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
    """
    sobject = 'Knowledge__kav' if sobject is None else sobject
    query = f"SELECT Id,ArticleNumber FROM {sobject} WHERE Title = '{title}'"
    query += " AND PublishStatus != 'Archived'" if not include_archived else query
    response = sfdc_object.soql_query(query, replace_quotes=False)
    return_value = ''
    if response.get('totalSize') > 0:
        if return_id:
            return_value = response['records'][0]['Id']
        elif return_id_and_number:
            return_value = (response['records'][0]['Id'], response['records'][0]['ArticleNumber'])
        else:
            return_value = response['records'][0]['ArticleNumber']
    elif return_id_and_number:
        return_value = ('', '')
    return return_value


def get_article_id_from_number(sfdc_object, article_number, sobject=None, return_uri=False):
    """This method returns the Article ID when an article number is provided.
    (`Reference 1 <https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/dome_query.htm>`_,
    `Reference 2 <https://developer.salesforce.com/docs/atlas.en-us.knowledge_dev.meta/knowledge_dev/knowledge_development_soql_sosl_intro.htm>`_)

    :param sfdc_object: The instantiated SalesPyForce object
    :type sfdc_object: class[salespyforce.Salesforce]
    :param article_number: The Article Number to query
    :type article_number: str, int
    :param sobject: The Salesforce object to query (``Knowledge__kav`` by default)
    :type sobject: str, None
    :param return_uri: Determines if the URI of the article should be returned rather than the ID (``False`` by default)
    :type return_uri: bool
    :returns: The Article ID or Article URI, or a blank string if no article is found
    :raises: :py:exc:`ValueError`
    """
    sobject = 'Knowledge__kav' if sobject is None else sobject
    if sobject is None:
        raise ValueError('The sObject must be defined for the Article Type in order to query for the ID.')
    if len(str(article_number)) < 9:
        query = f"SELECT Id FROM {sobject} WHERE ArticleNumber LIKE '%0{article_number}'"
    else:
        query = f"SELECT Id FROM {sobject} WHERE ArticleNumber = '{article_number}'"
    response = sfdc_object.soql_query(query)
    if response.get('totalSize') > 0:
        if return_uri:
            return_value = response['records'][0]['attributes']['url']
        else:
            return_value = response['records'][0]['Id']
    else:
        return_value = ''
        print(f'No results were returned when querying for the article number {article_number}')
    return return_value


def get_articles_list(sfdc_object, query=None, sort=None, order=None, page_size=20, page_num=1):
    """This function retrieves a list of knowledge articles.
    (`Reference <https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/resources_knowledge_support_artlist.htm>`_)

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
    headers = sfdc_object._get_headers('articles')

    # Validate the sort field
    valid_sort_options = ['LastPublishedDate', 'CreatedDate', 'Title', 'ViewScore']
    if sort and sort not in valid_sort_options:
        errors.handlers.eprint(f'The sort value {sort} is not valid and will be ignored.')
        sort = None

    # Validate the order field
    if order and order.upper() not in ['ASC', 'DESC']:
        errors.handlers.eprint(f'The order value {order} is not valid and will be ignored.')
        order = None

    # Validate the page size field
    if page_size > 100:
        errors.handlers.eprint(f'The pageSize value exceeds the maximum and will default to 100.')
        page_size = 100

    # Validate the pageNumber field
    if page_num < 1:
        errors.handlers.eprint(f'The pageNumber value is not valid and will default to 1.')
        page_num = 1

    # Add values to the parameters dictionary if they have been defined
    params = {}
    if query:
        params['q'] = query
    if sort:
        params['sort'] = sort
    if order:
        params['order'] = order
    params['pageSize'] = page_size
    params['pageNumber'] = page_num

    # Perform the query
    return sfdc_object.get(f'/services/data/{sfdc_object.version}/support/knowledgeArticles',
                           params=params, headers=headers)


def get_article_details(sfdc_object, article_id, sobject=None):
    """This function retrieves details for a single knowledge article.
    (`Reference <https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/resources_knowledge_support_artdetails.htm>`_)

    :param sfdc_object: The instantiated SalesPyForce object
    :type sfdc_object: class[salespyforce.Salesforce]
    :param article_id: The Article ID for which to retrieve details
    :type article_id: str
    :param sobject: The Salesforce object to query (``Knowledge__kav`` by default)
    :type sobject: str, None
    :returns: The details for the knowledge article
    """
    # Define the headers
    headers = sfdc_object._get_headers('articles')

    # Perform the query and return the data
    sobject = 'Knowledge__kav' if sobject is None else sobject
    if sobject is not None:
        data = sfdc_object.get(f'/services/data/{sfdc_object.version}/sobjects/{sobject}/{article_id}')
    else:
        data = sfdc_object.get(f'/services/data/{sfdc_object.version}/support/knowledgeArticles/{article_id}',
                               headers=headers)
    return data


def get_validation_status(sfdc_object, article_id=None, article_details=None, sobject=None):
    """This function retrieves the Validation Status for a given Article ID.
    (`Reference <https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/resources_knowledge_support_artdetails.htm>`_)

    :param sfdc_object: The instantiated SalesPyForce object
    :type sfdc_object: class[salespyforce.Salesforce]
    :param article_id: The Article ID for which to retrieve details
    :type article_id: str, None
    :param article_details: The dictionary of article details for the given article
    :type article_details: dict, None
    :param sobject: The Salesforce object to query (``Knowledge__kav`` by default)
    :type sobject: str, None
    :returns: The validation status as a text string
    :raises: :py:exc:`RuntimeError`
    """
    if not any((article_id, article_details)):
        raise RuntimeError('The article ID or article details must be provided.')

    # Retrieve the article details if not already supplied
    if not article_details:
        article_details = get_article_details(sfdc_object, article_id, sobject)

    # Identify the validation status
    return article_details.get('ValidationStatus')


def get_article_metadata(sfdc_object, article_id):
    """This function retrieves metadata for a specific knowledge article.
    (`Reference <https://developer.salesforce.com/docs/atlas.en-us.knowledge_dev.meta/knowledge_dev/knowledge_REST_retrieve_article_metadata.htm>`_)

    :param sfdc_object: The instantiated SalesPyForce object
    :type sfdc_object: class[salespyforce.Salesforce]
    :param article_id: The Article ID for which to retrieve details
    :type article_id: str
    :returns: The article metadata as a dictionary
    :raises: :py:exc:`RuntimeError`
    """
    return sfdc_object.get(f'/services/data/{sfdc_object.version}/knowledgeManagement/articles/{article_id}')


def get_article_version(sfdc_object, article_id):
    """This function retrieves the version ID for a given master article ID.
    (`Reference <https://developer.salesforce.com/docs/atlas.en-us.knowledge_dev.meta/knowledge_dev/knowledge_REST_retrieve_article_version.htm>`_)

    :param sfdc_object: The instantiated SalesPyForce object
    :type sfdc_object: class[salespyforce.Salesforce]
    :param article_id: The Article ID for which to retrieve details
    :type article_id: str
    :returns: The version ID for the given master article ID
    :raises: :py:exc:`RuntimeError`
    """
    endpoint = f'/services/data/{sfdc_object.version}/knowledgeManagement/articleversions/masterVersions/{article_id}'
    return sfdc_object.get(endpoint)


def get_article_url(sfdc_object, article_id=None, article_number=None, sobject=None):
    """This function constructs the URL to view a knowledge article in Lightning or Classic.

    .. version-changed:: 1.2.0
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
    :raises: :py:exc:`ValueError`
    """
    sobject = 'Knowledge__kav' if sobject is None else sobject
    if not any((article_id, article_number)):
        raise ValueError('An article ID or an article number must be provided to retrieve the article URL.')
    if article_number and not article_id:
        article_id = get_article_id_from_number(sfdc_object, article_number, sobject)
    segment = '' if sfdc_object.base_url.endswith('/') else '/'
    if 'lightning' in sfdc_object.base_url or sobject == 'Knowledge__kav':
        article_url = f'{sfdc_object.base_url}{segment}lightning/r/Knowledge__kav/{article_id}/view'
    else:
        article_url = f'{sfdc_object.base_url}{segment}knowledge/publishing/articleDraftDetail.apexp?id={article_id}'
    return article_url


def create_article(sfdc_object, article_data, sobject=None, full_response=False):
    """This function creates a new knowledge article draft.
    (`Reference <https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/dome_sobject_create.htm>`_)

    :param sfdc_object: The instantiated SalesPyForce object
    :type sfdc_object: class[salespyforce.Salesforce]
    :param article_data: The article data used to populate the article
    :type article_data: dict
    :param sobject: The Salesforce object to query (``Knowledge__kav`` by default)
    :type sobject: str, None
    :param full_response: Determines if the full API response should be returned instead of the article ID (``False`` by default)
    :type full_response: bool
    :returns: The API response or the ID of the article draft
    :raises: :py:exc:`ValueError`, :py:exc:`TypeError`, :py:exc:`RuntimeError`
    """
    # Get the appropriate sObject to call
    sobject = 'Knowledge__kav' if sobject is None else sobject

    # Ensure the payload is in the appropriate format
    if not isinstance(article_data, dict):
        raise TypeError('The article data must be provided as a dictionary.')

    # Ensure that the required fields have been provided
    required_fields = ['Title', 'UrlName']
    for field in required_fields:
        if field not in article_data:
            raise ValueError(f'The following required field is missing from the article data: {field}')

    # Perform the API call
    response = sfdc_object.post(f'/services/data/{sfdc_object.version}/sobjects/{sobject}', payload=article_data)

    # Return the full response or just the article ID
    if not full_response:
        response = response.get('id')
    return response


def update_article(sfdc_object, record_id, article_data, sobject=None, include_status_code=False):
    """This function updates an existing knowledge article draft.
    (`Reference <https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/dome_update_fields.htm>`_)

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
    :raises: :py:exc:`ValueError`, :py:exc:`TypeError`, :py:exc:`RuntimeError`
    """
    # Get the appropriate sObject to call
    sobject = 'Knowledge__kav' if sobject is None else sobject

    # Ensure the payload is in the appropriate format
    if not isinstance(article_data, dict):
        raise TypeError('The article data must be provided as a dictionary.')

    # Ensure that the required fields have been provided
    required_fields = ['Title', 'UrlName']
    for field in required_fields:
        if field not in article_data:
            raise ValueError(f'The following required field is missing from the article data: {field}')

    # Perform the API call
    response = sfdc_object.patch(f'/services/data/{sfdc_object.version}/sobjects/{sobject}/{record_id}',
                                 payload=article_data)

    # Determine whether the call was successful
    successful = True if response.status_code == 204 else False

    # Return the success determination and optionally the status code
    if include_status_code:
        return successful, response.status_code
    return successful


def create_draft_from_online_article(sfdc_object, article_id, unpublish=False):
    """This function creates a draft knowledge article from an online article.
    (`Reference <https://developer.salesforce.com/docs/atlas.en-us.knowledge_dev.meta/knowledge_dev/actions_obj_knowledge.htm#createDraftFromOnlineKnowledgeArticle>`_)

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
        "inputs": [
            {
                "action": "EDIT_AS_DRAFT_ARTICLE",
                "unpublish": unpublish,
                "articleId": f"{article_id}"
            }
        ]
    }

    # Perform the API call
    endpoint = f'/services/data/{sfdc_object.version}/actions/standard/createDraftFromOnlineKnowledgeArticle'
    return sfdc_object.post(endpoint, payload)


def create_draft_from_master_version(sfdc_object, article_id=None, knowledge_article_id=None, article_data=None,
                                     sobject=None, full_response=False):
    """This function creates an online version of a master article.
    (`Reference <https://developer.salesforce.com/docs/atlas.en-us.198.0.knowledge_dev.meta/knowledge_dev/knowledge_REST_edit_online_master.htm>`_)

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
    :raises: :py:exc:`RuntimeError`
    """
    if not any((article_id, knowledge_article_id, article_data)):
        raise RuntimeError('Need to provide article ID, knowledge article ID, or article data.')

    # Get the appropriate sObject to call
    sobject = 'Knowledge__kav' if sobject is None else sobject

    # Get the knowledge article ID as needed
    if not knowledge_article_id:
        if not article_data:
            article_data = sfdc_object.get_article_details(article_id, sobject=sobject)
        knowledge_article_id = article_data.get('KnowledgeArticleId')

    # Perform the API call to retrieve the new draft ID
    endpoint = f'/services/data/{sfdc_object.version}/knowledgeManagement/articleVersions/masterVersions'
    response = sfdc_object.post(endpoint, {'articleId': knowledge_article_id})

    # Return the full response or the draft ID
    if not full_response:
        response = response.get('id')
    return response


def publish_article(sfdc_object, article_id, major_version=True, full_response=False):
    """This function publishes a draft knowledge article as a major or minor version.
    (`Reference <https://developer.salesforce.com/docs/atlas.en-us.knowledge_dev.meta/knowledge_dev/knowledge_REST_publish_master_version.htm>`_)

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
        "publishStatus": "Online"
    }
    if major_version:
        payload['versionNumber'] = 'NextVersion'

    # Perform the API call
    endpoint = f'/services/data/{sfdc_object.version}/knowledgeManagement/articleVersions/masterVersions/{article_id}'
    result = sfdc_object.patch(endpoint, payload)

    # Return the appropriate value depending on if a full response was requested
    if not full_response:
        result = True if result.status_code == 204 else False
    return result


def publish_multiple_articles(sfdc_object, article_id_list, major_version=True):
    """This function publishes multiple knowledge article drafts at one time.
    (`Reference <https://developer.salesforce.com/docs/atlas.en-us.knowledge_dev.meta/knowledge_dev/actions_obj_knowledge.htm#publishKnowledgeArticles>`_)

    :param sfdc_object: The instantiated SalesPyForce object
    :type sfdc_object: class[salespyforce.Salesforce]
    :param article_id_list: A list of Article IDs to be published
    :type article_id_list: list
    :param major_version: Determines if the published article should be a major version (``True`` by default)
    :type major_version: bool
    :returns: The API response from the POST request
    :raises: :py:exc:`RuntimeError`, :py:exc:`TypeError`, :py:exc:`ValueError`
    """
    # Define the endpoint URI
    endpoint = f'/services/data/{sfdc_object.version}/actions/standard/publishKnowledgeArticles'

    # Ensure there is at least one article ID to publish
    if not isinstance(article_id_list, list) or not isinstance(article_id_list[0], str):
        raise TypeError('A list of Article ID strings must be provided in order to publish multiple articles.')
    elif len(article_id_list) == 0:
        raise ValueError('No article ID strings were found in the article ID list variable.')

    # Define the action to perform
    action = 'PUBLISH_ARTICLE_NEW_VERSION' if major_version else 'PUBLISH_ARTICLE'

    # Construct the payload
    payload = {
        "inputs": [
            {
                "articleVersionIdList": article_id_list,
                "pubAction": action
            }
        ]
    }

    # Perform the API call
    return sfdc_object.post(endpoint, payload)


def assign_data_category(sfdc_object, article_id, category_group_name, category_name):
    """This function assigns a single data category for a knowledge article.
    (`Reference <https://itsmemohit.medium.com/quick-win-15-salesforce-knowledge-rest-apis-bb0725b2040e>`_)

    .. version-added:: 1.2.0

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
        "ParentId": article_id,
        "DataCategoryGroupName": category_group_name,
        "DataCategoryName": category_name
    }

    # Perform the API call
    endpoint = f'/services/data/{sfdc_object.version}/sobjects/Knowledge__DataCategorySelection'
    return sfdc_object.post(endpoint, payload)


def archive_article(sfdc_object, article_id):
    """This function archives a published knowledge article.
    (`Reference <https://developer.salesforce.com/docs/atlas.en-us.knowledge_dev.meta/knowledge_dev/knowledge_REST_archive_master_version.htm>`_)

    .. version-added:: 1.3.0

    :param sfdc_object: The instantiated SalesPyForce object
    :type sfdc_object: class[salespyforce.Salesforce]
    :param article_id: The ID of the article to archive
    :type article_id: str
    :returns: The API response from the POST request
    :raises: :py:exc:`RuntimeError`
    """
    # Define the payload for the API call
    payload = {
        "publishStatus": "Archived"
    }

    # Perform the API call
    endpoint = f'/services/data/{sfdc_object.version}/knowledgeManagement/articleVersions/masterVersions/{article_id}'
    return sfdc_object.patch(endpoint, payload)


def delete_article_draft(sfdc_object, version_id):
    """This function deletes an unpublished knowledge article draft.
    
    .. version-added:: 1.4.0
    
    :param sfdc_object: The instantiated SalesPyForce object
    :type sfdc_object: class[salespyforce.Salesforce]
    :param version_id: The 15-character or 18-character ``Id`` (Knowledge Article Version ID) value
    :type version_id: str
    :returns: The API response from the DELETE request
    :raises: :py:exc:`RuntimeError`
    """
    endpoint = f'/services/data/{sfdc_object.version}/sobjects/Knowledge__kav/{version_id}'
    return sfdc_object.delete(endpoint)
