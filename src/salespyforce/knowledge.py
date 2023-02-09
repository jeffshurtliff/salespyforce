# -*- coding: utf-8 -*-
"""
:Module:            salespyforce.knowledge
:Synopsis:          Defines the Knowledge-related functions associated with the Salesforce API
:Created By:        Jeff Shurtliff
:Last Modified:     Jeff Shurtliff
:Modified Date:     09 Feb 2023
"""

from .utils import log_utils

# Initialize logging
logger = log_utils.initialize_logging(__name__)


def check_for_existing_article(sfdc_object, title, sobject=None, return_id=False, return_id_and_number=False):
    """This method checks to see if an article already exists with a given title and returns its article number.
    Reference: https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/dome_query.htm
    Reference: https://developer.salesforce.com/docs/atlas.en-us.knowledge_dev.meta/knowledge_dev/knowledge_development_soql_sosl_intro.htm

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

