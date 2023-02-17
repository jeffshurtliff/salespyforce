# -*- coding: utf-8 -*-
"""
:Module:            salespyforce.knowledge
:Synopsis:          Defines the Knowledge-related functions associated with the Salesforce API
:Created By:        Jeff Shurtliff
:Last Modified:     Jeff Shurtliff
:Modified Date:     17 Feb 2023
"""

from .utils import log_utils

# Initialize logging
logger = log_utils.initialize_logging(__name__)


def check_for_existing_article(sfdc_object, title, sobject=None, return_id=False, return_id_and_number=False):
    """This method checks to see if an article already exists with a given title and returns its article number.
    (`Reference 1 <https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/dome_query.htm>`_,
    `Reference 2 <https://developer.salesforce.com/docs/atlas.en-us.knowledge_dev.meta/knowledge_dev/knowledge_development_soql_sosl_intro.htm>`_)

    :param sfdc_object: The instantiated SalesPyForce object
    :param title: The title of the knowledge article for which to check
    :type title: str
    :param sobject: The Salesforce object to query (``Knowledge__kav`` by default)
    :type sobject: str, None
    :param return_id: Determines if the Article ID should be returned (``False`` by default)
    :type return_id: bool
    :param return_id_and_number: Determines if Article ID and Article Number should be returned (``False`` by default)
    :type return_id_and_number: bool
    :returns: The Article Number, Article ID, or both, if found, or a blank string if not found
    """
    sobject = 'Knowledge__kav' if sobject is None else sobject
    query = f"SELECT Id,ArticleNumber FROM {sobject} WHERE Title = '{title}'"
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
    Reference: https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/dome_query.htm
    Reference: https://developer.salesforce.com/docs/atlas.en-us.knowledge_dev.meta/knowledge_dev/knowledge_development_soql_sosl_intro.htm

    :param sfdc_object: The instantiated SalesPyForce object
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
        # TODO: Use an eprint function
        print(f'The sort value {sort} is not valid and will be ignored.')
        sort = None

    # Validate the order field
    if order and order.upper() not in ['ASC', 'DESC']:
        # TODO: Use an eprint function
        print(f'The order value {order} is not valid and will be ignored.')
        order = None

    # Validate the page size field
    if page_size > 100:
        # TODO: Use an eprint function
        print(f'The pageSize value exceeds the maximum and will default to 100.')
        page_size = 100

    # Validate the pageNumber field
    if page_num < 1:
        # TODO: Use an eprint function
        print(f'The pageNumber value is not valid and will default to 1.')
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
