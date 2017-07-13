import json
import re

from accessstats.client import ThriftClient

REGEX_ISSN = re.compile("^[0-9]{4}-[0-9]{3}[0-9xX]$")
REGEX_ISSUE = re.compile("^[0-9]{4}-[0-9]{3}[0-9xX][0-2][0-9]{3}[0-9]{4}$")
REGEX_ARTICLE = re.compile("^S[0-9]{4}-[0-9]{3}[0-9xX][0-2][0-9]{3}[0-9]{4}[0-9]{5}$")


def _code_type(code):

    if not code:
        return None

    if REGEX_ISSN.match(code):
        return 'issn'

    if REGEX_ISSUE.match(code):
        return 'issue'

    if REGEX_ARTICLE.match(code):
        return 'pid'


def _compute_downloads_per_year(query_result):

    result = []

    for item in query_result['aggregations']['access_year']['buckets']:
        result.append(
            (item['key'], int(item['access_total']['value']))
        )

    return result


def downloads_per_year(collection, code, raw=False):
    """
    This method retrieve the total of downloads per year.

    arguments
    collection: SciELO 3 letters Acronym
    code: (Journal ISSN, Issue PID, Article PID)

    return
    [
        ("2017", "20101"),
        ("2016", "11201"),
        ("2015", "12311"),
        ...
    ]
    """

    tc = ThriftClient()

    body = {"query": {"filtered": {}}}

    fltr = {}

    query = {
        "query": {
            "bool": {
                "must": [
                    {
                        "match": {
                            "collection": collection
                        }
                    }
                ]
            }
        }
    }

    aggs = {
        "aggs": {
            "access_year": {
                "terms": {
                    "field": "access_year",
                    "size": 0,
                    "order": {
                        "_term": "asc"
                    }
                },
                "aggs": {
                    "access_total": {
                        "sum": {
                            "field": "access_total"
                        }
                    }
                }
            }
        }
    }

    body['query']['filtered'].update(fltr)
    body['query']['filtered'].update(query)
    body.update(aggs)

    code_type = _code_type(code)

    if code_type:
        query["query"]["bool"]["must"].append({
            "match": {
                code_type: code
            }
        })

    query_parameters = [
        ('size', '0')
    ]

    query_result = tc.search(json.dumps(body), query_parameters)

    return query_result if raw is True else _compute_downloads_per_year(query_result)
