# coding: utf-8
import unittest

from accessstats import queries


class AccessStatsQueriesTest(unittest.TestCase):

    def test_compute_documents_downloads_per_year(self):

        query_result = {
            "hits": {
                "hits": [],
                "total": 13,
                "max_score": 0.0
            },
            "timed_out": False,
            "took": 272,
            "aggregations": {
                "access_year": {
                    "buckets": [
                        {
                            "access_total": {
                                "value": 455.0
                            },
                            "key": "2016",
                            "doc_count": 7
                        },
                        {
                            "access_total": {
                                "value": 344.0
                            },
                            "key": "2017",
                            "doc_count": 6
                        }
                    ],
                    "doc_count_error_upper_bound": 0,
                    "sum_other_doc_count": 0
                }
            },
            "_shards": {
                "successful": 5,
                "failed": 0,
                "total": 5
            }
        }

        result = queries._compute_downloads_per_year(query_result)

        expected = [(u'2016', 455), (u'2017', 344)]

        self.assertEqual(expected, sorted(result))
