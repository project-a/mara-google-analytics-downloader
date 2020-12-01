from mara_google_analytics_downloader.static import METRICS, DIMENSIONS


def ga_parse_filter(report_request: dict, filters: str):
    """
    This function is parsing the URL filter syntax (v3)
        https://developers.google.com/analytics/devguides/reporting/core/v3/reference#filters
    to the JSON format filter syntax (v4)
        https://developers.google.com/analytics/devguides/reporting/core/v4/basics#filtering
        https://developers.google.com/analytics/devguides/reporting/core/v4/basics#filtering_2
    and adds the filter ot the report request.

    Args:
        report_request: the dict with the report request
        filter: the filter string
    """
    metric_filter_clauses = []
    dimension_filter_clauses = []

    # Reference: https://developers.google.com/analytics/devguides/reporting/core/v3/reference#filters
    if filters.find('(') >= 0 or filters.find(')') >= 0:
        raise Exception('Breakets in paramter --filters are not yet supported')


    for or_filter in filters.split(','):
        for and_filter in or_filter.split(';'):
            filter = and_filter

            # parse one filter (metric/dimension operator expression)
            metric_name = None
            dimension_name = None
            operator = None
            operator_not = False
            field_left = None
            field_right = None
            if filter.find('==') >= 0:
                field_left = filter[:filter.find('==')]
                field_right = filter[filter.find('==')+2:]
                operator = 'EXACT'
            elif filter.find('!=') > 0:
                field_left = filter[:filter.find('!=')]
                field_right = filter[filter.find('!=')+2:]
                operator = 'EXACT'
                operator_not = True
            elif filter.find('>') >= 0:
                field_left = filter[:filter.find('>')]
                field_right = filter[filter.find('>')+1:]
                operator = 'GREATER_THAN'
            elif filter.find('<') >= 0:
                field_left = filter[:filter.find('<')]
                field_right = filter[filter.find('<')+1:]
                operator = 'LESS_THAN'
            elif filter.find('>=') >= 0:
                field_left = filter[:filter.find('>=')]
                field_right = filter[filter.find('>=')+2:]
                operator = 'LESS_THAN'
                operator_not = True
            elif filter.find('<=') >= 0:
                field_left = filter[:filter.find('<=')]
                field_right = filter[filter.find('<=')+2:]
                operator = 'GREATER_THAN'
                operator_not = True
            elif filter.find('=@') >= 0:
                field_left = filter[:filter.find('=@')]
                field_right = filter[filter.find('=@')+2:]
                operator = 'PARTIAL'
            elif filter.find('!@') >= 0:
                field_left = filter[:filter.find('!@')]
                field_right = filter[filter.find('!@')+2:]
                operator = 'PARTIAL'
                operator_not = True
            elif filter.find('=~') >= 0:
                field_left = filter[:filter.find('=~')]
                field_right = filter[filter.find('=~')+2:]
                operator = 'REGEXP'
            elif filter.find('!~') >= 0:
                field_left = filter[:filter.find('!~')]
                field_right = filter[filter.find('!~')+2:]
                operator = 'REGEXP'
                operator_not = True
            else:
                raise Exception(f'Filter contains no or unknown operator: {filter}')

            if field_left in METRICS:
                # Reference: https://developers.google.com/analytics/devguides/reporting/core/v4/basics#filtering
                metric_filter_clauses.append({
                    'filters': [
                        {
                            'metricName': field_left,
                            'not': operator_not,
                            'operator': operator,
                            'comparisonValue': field_right
                        }
                    ]
                })
            elif field_left in DIMENSIONS:
                # Reference: https://developers.google.com/analytics/devguides/reporting/core/v4/basics#filtering_2
                dimension_filter_clauses.append({
                    'filters': [
                        {
                            'dimensionName': field_left,
                            'not': operator_not,
                            'operator': operator,
                            'expressions': [field_right]
                        }
                    ]
                })
            else:
                raise Exception(f'Unknown dimension/metric: {field_left}')

    if metric_filter_clauses:
        report_request.update({
            'metricFilterClauses': metric_filter_clauses
        })
    if dimension_filter_clauses:
        report_request.update({
            'dimensionFilterClauses': dimension_filter_clauses
        })
