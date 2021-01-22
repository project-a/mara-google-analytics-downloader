"""Google Analytics Download to to CSV on stdout

The csv is formatted as csv.excel dialect suitable for e.g. CSV loads into DBs.

No header is written.

Mainly to be used with mara to import a Google Analytics to a database table.
"""

import click
import sys
import random
import typing as t
import time

from apiclient.discovery import build

from mara_google_analytics_downloader import config as c
from mara_google_analytics_downloader.filter_parsing import ga_parse_filter



def detect_api(metrics: t.List[str], dimensions: t.List[str]) -> str:
    api = None
    for metric in metrics:
        current_api = None
        if metric.startswith('ga:'):
            current_api = 'ga'
        elif metric.startswith('mcf:'):
            current_api = 'mcf'
        else:
            raise ValueError(f'Could not detect API from metric {metric}. The metric must start with `ga:` or `mcf:`.')

        if not api:
            api = current_api
        elif api != current_api:
            raise ValueError(f'You can not use multiple APIs in your query. Make sure that all metrics and dimensions start with the same prefix e.g. `ga:` or `mcf:`.')

    for dimension in dimensions:
        current_api = None
        if dimension.startswith('ga:'):
            current_api = 'ga'
        elif dimension.startswith('mcf:'):
            current_api = 'mcf'
        else:
            raise ValueError(f'Could not detect API from dimension {dimension}. The dimension must start with `ga:` or `mcf:`.')

        if not api:
            api = current_api
        elif api != current_api:
            raise ValueError(f'You can not use multiple APIs in your query. Make sure that all metrics and dimensions start with the same prefix e.g. `ga:` or `mcf:`.')

    return api


@click.command()
@click.option('--view-id', help='Google Analytics View ID',
              required=True)
@click.option('--start-date', help='The start of a date range, e.g. 30daysAgo, 7daysAgo, today etc.',
              required=True)
@click.option('--end-date', help='The end of a date range, e.g. 30daysAgo, 7daysAgo, today etc.',
              required=True)
@click.option('--dimensions', help='A comma-separated list of dimensions to be used in the request',
              required=False)
@click.option('--metrics', help='A comma-separated list of metrics to be used in the request',
              required=True)
@click.option('--filters', help='A filter to be used in the request',
              required=False)
@click.option('--service-account-private-key-id', help='Service Account private_key_id',
              required=False)
@click.option('--service-account-private-key', help='Service Account private_key',
              required=False)
@click.option('--service-account-client-email', help='Service Account client_email',
              required=False)
@click.option('--service-account-client-id', help='Service Account client_id',
              required=False)
@click.option('--user-account-client-id', help='User Account client_id',
              required=False)
@click.option('--user-account-client-secret', help='User Account client_secret',
              required=False)
@click.option('--user-account-refresh-token', help='User Account refresh_token',
              required=False)
@click.option('--delimiter-char', help='A character that delimits the output fields.',
              default='\t',
              show_default="\\t",
              required=False)
@click.option('--add-view-id-column/--no-add-view-id-column',
              help='Adds a new column at the start with the view id',
              default=False,
              required=False)
@click.option('--fail-on-no-data/--no-fail-on-no-data',
              help='Toggle to fail if no data is received.',
              default=True,
              required=False)
def ga_download_to_csv(view_id: int,
                       start_date: str,
                       end_date: str,
                       metrics: str,
                       dimensions: str = None,
                       filters: str = None,
                       delimiter_char: str = '\t',
                       add_view_id_column: bool = False,
                       service_account_private_key_id: str = None,
                       service_account_private_key: str = None,
                       service_account_client_email: str = None,
                       service_account_client_id: str = None,
                       user_account_client_id: str = None,
                       user_account_client_secret: str = None,
                       user_account_refresh_token: str = None,
                       fail_on_no_data: bool = True
                       ):
    """Download google analytics data as CSV to stdout

    Needs google credentials, either from a service account or from a user account.

    The csv is formatted as csv.excel dialect suitable for e.g. CSV loads into DBs. No header is written.
    """
    if not view_id:
        raise RuntimeError("Need a view_id")
    if not start_date:
        raise RuntimeError("Need a start_date")
    if not end_date:
        raise RuntimeError("Need a end_date")
    if not metrics:
        raise RuntimeError("Need metrics")

    metrics_list = metrics.split(',') if metrics else []
    dimensions_list = dimensions.split(',') if dimensions else []
    api = detect_api(metrics_list, dimensions_list)

    # TODO: make sure we only get a single credential config overall and warn/abort if we have more than one
    #       (warn: no print to stdout allowed!)

    # add a fallback to the config if no value are given
    # config is only set if this command is invoked via flask with a MaraApp
    service_account_private_key_id = service_account_private_key_id or c.ga_service_account_private_key_id()
    service_account_private_key = service_account_private_key or c.ga_service_account_private_key()
    service_account_client_email = service_account_client_email or c.ga_service_account_client_email()
    service_account_client_id = service_account_client_id or c.ga_service_account_client_id()
    user_account_client_id = user_account_client_id or c.ga_user_account_client_id()
    user_account_client_secret = user_account_client_secret or c.ga_user_account_client_secret()
    user_account_refresh_token = user_account_refresh_token or c.ga_user_account_refresh_token()

    if user_account_client_id:
        credentials = _google_analytics_credentials_from_user_credentials(
            client_id=user_account_client_id,
            client_secret=user_account_client_secret,
            refresh_token=user_account_refresh_token,
        )
    elif service_account_client_id:
        credentials = _google_analytics_credentials_from_service_account_credentials(
            private_key_id=service_account_private_key_id,
            private_key=service_account_private_key,
            client_email=service_account_client_email,
            client_id=service_account_client_id,
        )
    else:
        raise RuntimeError("Need either credentials for a google user account or for a google service account")

    overall_tries = 0
    api_errors = 0
    start_index = 1
    stream = sys.stdout
    nrows = 0
    while True:
        try:
            if api == 'ga':
                # Builds the google analytics service object
                analytics = build('analyticsreporting', 'v4', credentials=credentials, cache_discovery=False)

                request_metrics = list(map(
                    lambda metric_name: {'expression': metric_name},
                    metrics.split(',')
                ))

                reuqest_dimensions = []
                if dimensions:
                    reuqest_dimensions = list(map(
                        lambda dimension_name: {'name': dimension_name},
                        dimensions.split(',')
                    ))

                reportRequest = {
                    'viewId': view_id,
                    'dateRanges': [{'startDate': start_date, 'endDate': end_date}],
                    'metrics': request_metrics,
                    'dimensions': reuqest_dimensions
                }

                if filters:
                    ga_parse_filter(reportRequest, filters)

                response = analytics.reports().batchGet(body={'reportRequests': [reportRequest]}).execute()
                break
            elif api == 'mcf':
                # Builds the google analytics service object
                analytics = build('analytics', 'v3', credentials=credentials, cache_discovery=False)

                request = analytics.data().mcf().get(
                    ids=f'ga:{view_id}',
                    start_date=start_date,
                    end_date=end_date,
                    metrics=metrics,
                    dimensions=dimensions,
                    filters=filters,
                    start_index=start_index
                )

                response = request.execute()

                nrows += write_mcf_response_as_csv_to_stream(response,
                                                             stream=stream,
                                                             delimiter_char=delimiter_char,
                                                             view_id=view_id if add_view_id_column else None,
                                                             write_header=False)

                stream.flush()

                if 'nextLink' in response: # if 'nextLink' is in response, the response is paged.
                    start_index = start_index + response.get('max-results',1000)
                    #print(f'Request next page with start_index={start_index}', file=sys.stderr, flush=True)
                else:
                    break
            else:
                raise NotImplementedError('Unexpected')
        except Exception as e:
            # some API down or so -> wait a bit and try again
            if overall_tries > 3:
                raise e
            print(f'Got exception, but will retry again: {e!r}', file=sys.stderr, flush=True)
            overall_tries += 1
            sleep_seconds = 20 * (overall_tries + 1)
            time.sleep(sleep_seconds)
            continue

    if api == 'ga':
        nrows += write_ga_response_as_csv_to_stream(response,
                                                    stream=stream,
                                                    delimiter_char=delimiter_char,
                                                    view_id=view_id if add_view_id_column else None,
                                                    write_header=False)

        stream.flush()

    if fail_on_no_data and nrows == 0:
        raise ValueError("Received no data rows, failing")


SCOPES = ['https://www.googleapis.com/auth/analytics.readonly']


# The next version of gspread will probably support google_auth_oauthlib instead of oauth2client but will
# still support the old credentials: https://github.com/burnash/gspread/pull/711
# but lets keep this functions private for now
def _google_analytics_credentials_from_service_account_credentials(
    private_key_id: str,
    private_key: str,
    client_email: str,
    client_id: str
):
    '''Returns the credentials for a service account
    '''
    import oauth2client
    from oauth2client.service_account import ServiceAccountCredentials
    from oauth2client import crypt

    # adapted from ServiceAccountCredentials._from_parsed_json_keyfile()
    service_account_email = client_email
    private_key_pkcs8_pem = private_key
    private_key_id = private_key_id
    client_id = client_id
    token_uri = oauth2client.GOOGLE_TOKEN_URI
    revoke_uri = oauth2client.GOOGLE_REVOKE_URI

    signer = crypt.Signer.from_string(private_key_pkcs8_pem)
    credentials = ServiceAccountCredentials(service_account_email, signer, scopes=SCOPES,
                                            private_key_id=private_key_id,
                                            client_id=client_id, token_uri=token_uri,
                                            revoke_uri=revoke_uri)
    credentials._private_key_pkcs8_pem = private_key_pkcs8_pem

    return credentials


def _google_analytics_credentials_from_user_credentials(
    client_id: str,
    client_secret: str,
    refresh_token: str
):
    '''Returns the credentials from user authenticated client_id, client_secret, refresh_token

    See https://developers.google.com/analytics/devguides/reporting/core/v4/quickstart/service-py for how to get
    such credentials including the initial refresh token
    '''
    # https://stackoverflow.com/a/42230541/1380673
    import oauth2client
    import oauth2client.client as client

    credentials = client.OAuth2Credentials(
        access_token=None,  # set access_token to None since we use a refresh token
        client_id=client_id,
        client_secret=client_secret,
        refresh_token=refresh_token,
        token_expiry=None,
        token_uri=oauth2client.GOOGLE_TOKEN_URI,
        user_agent=None,
        revoke_uri=oauth2client.GOOGLE_REVOKE_URI,
        scopes=SCOPES)
    return credentials


def write_ga_response_as_csv_to_stream(response,
                                       stream: t.TextIO,
                                       delimiter_char: str = '\t',
                                       view_id: str = None,
                                       write_header: bool = True):
    """Writes the Analytics Reporting API V4 response into a CSV stream.

    Header is written by default, see arg. write_header.

    Args:
    response: An Analytics Reporting API V4 response.
    stream: t.TextIO, sink where the processed content is written to (in Text mode, so sys.stdout is suitable)
    delimiter_char: str (default: '\t'), A character that delimits the output fields.
    view_id: str (default: None), If given the view id will be added as a first column. Column name: 'vid'
    write_header: bool (default: True), If a CSV header should be added at the start
    """

    import csv

    dialect = csv.excel
    dialect.delimiter = delimiter_char

    csv_writer = csv.writer(stream,dialect=dialect)

    n_rows = 0
    for report in response.get('reports', []):
        columnHeader = report.get('columnHeader', {})
        dimensionHeaders = columnHeader.get('dimensions', [])
        metricHeaders = columnHeader.get('metricHeader', {}).get('metricHeaderEntries', [])

    # write header
    if write_header:
        headerRow = []
        if view_id != None:
            headerRow.append('vid')
        for header in dimensionHeaders:
            headerRow.append(header)
        for metricHeader in metricHeaders:
            headerRow.append(metricHeader.get('name'))
        csv_writer.writerow(headerRow)

    # write rows
    for row in report.get('data', {}).get('rows', []):
        dimensions = row.get('dimensions', [])
        dateRangeValues = row.get('metrics', [])

        row = []

        if view_id != None:
            row.append(str(view_id))

        for header, dimension in zip(dimensionHeaders, dimensions):
            row.append(dimension)

        for i, values in enumerate(dateRangeValues):
            if i == 0: # note: we only support here one date range TODO maybe something to consider as a future feature
                for metricHeader, value in zip(metricHeaders, values.get('values')):
                    row.append(value)

        csv_writer.writerow(row)
        n_rows += 1

    return n_rows

def write_mcf_response_as_csv_to_stream(response,
                                        stream: t.TextIO,
                                        delimiter_char: str = '\t',
                                        view_id: str = None,
                                        write_header: bool = True):
    """Writes the Multi-Channel Funnels Reporting API V3 response into a CSV stream.

    Header is written by default, see arg. write_header.

    Args:
    response: An Multi-Channel Funnels Reporting API V3 response.
    stream: t.TextIO, sink where the processed content is written to (in Text mode, so sys.stdout is suitable)
    delimiter_char: str (default: '\t'), A character that delimits the output fields.
    view_id: str (default: None), If given the view id will be added as a first column. Column name: 'vid'
    write_header: bool (default: True), If a CSV header should be added at the start
    """

    import csv
    import json

    dialect = csv.excel
    dialect.delimiter = delimiter_char

    csv_writer = csv.writer(stream,dialect=dialect)

    n_rows = 0
    columnHeaders = response.get('columnHeaders', [])

    # write header
    if write_header:
        headerRow = []
        if view_id != None:
            headerRow.append('vid')
        for column_header in columnHeaders:
            headerRow.append(column_header.name)
        csv_writer.writerow(headerRow)

    # write rows
    for raw_row in response.get('rows', []):
        row = []

        if view_id != None:
            row.append(str(view_id))

        column_index = 0
        for cell in raw_row:
            column = columnHeaders[column_index]

            if column['dataType'] == 'MCF_SEQUENCE':
                row.append(json.dumps(cell['conversionPathValue']))
            else:
                row.append(cell['primitiveValue'])

            column_index += 1

        csv_writer.writerow(row)
        n_rows += 1

    return n_rows

if __name__ == '__main__':
    ga_download_to_csv(prog_name='mara_google_analytics_downloader')
