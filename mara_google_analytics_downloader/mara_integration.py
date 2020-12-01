import shlex
from mara_pipelines import pipelines
from mara_pipelines.logging import logger
import mara_db.shell
import typing as t

from mara_google_analytics_downloader import config as c

__all__ = ['DownloadGoogleAnalyticsFlatTable']


class DownloadGoogleAnalyticsFlatTable(pipelines.Command):
    def __init__(self,
                 view_id: int,
                 start_date: str,
                 metrics: t.Iterable[str],
                 target_table_name: str,
                 target_db_alias: str = 'dwh',
                 end_date: str = 'today',
                 dimensions: t.Iterable[str] = None,
                 filters: str = None,
                 add_view_id_column: bool = False,
                 use_flask_command: bool = False,
                 fail_on_no_data: bool = False
                 ) -> None:
        """
        Executes a google analytics query and writes the result to a table

        This data will be the same as when you create a custom report with type 'Fact Table' in Google Analytics.

        Args:
            view_id: int, the Google Analytics view id, see https://ga-dev-tools.appspot.com/query-explorer/
            start_date: str, the start date of data to receive
            end_date: str, the end date of data to receive
            metrics: t.Iterable[str], the metrics to receive
            dimensions: t.Iterable[str] = None, the dimensions to receive
            filters: str=None, a filter string to be used in the query
            target_table_name: str, the schema qualified table name on the db_alias where the data should be inserted.
                               The table needs to exist.
            target_db_alias: str='dwh', the mara db alias where this data should be inserted
            add_view_id_column: bool=False, adds a new column at the beginning with the view id given in parameter view_id
            use_flask_command: bool=False, if true uses the downloader via flask, which needs an import to the main
                               module in the app.py import path to make the command available (any print() in that path
                               will fail the download). If True, the credentials needed in the downloader itself are
                               directly taken from the config, not passed in via commandline arguments.
            fail_on_no_data: bool=True, if true fail on no data rows received

        """
        self.view_id = view_id
        self.start_date = start_date
        self.end_date = end_date
        self.metrics = metrics
        self.dimensions = dimensions
        self.filters = filters
        self.target_table_name = target_table_name
        self.target_db_alias = target_db_alias
        self.delimiter_char = '\t'
        self.add_view_id_column = add_view_id_column
        self.use_flask_command = use_flask_command
        self.fail_on_no_data = fail_on_no_data

    def run(self) -> bool:
        logger.log(
            f'Loading google analytics data {self.view_id} ({self.dimensions} {self.metrics}) into {self.target_db_alias}.{self.target_table_name}...')
        if not super().run():
            logger.log(f'Error while loading google analytics data.')
            return False
        logger.log(f'Finished loading google analytics data.')
        return True

    def shell_command(self):
        return (ga_downloader_shell_command(self.view_id, self.start_date, self.end_date,
                                            self.metrics,dimensions=self.dimensions,
                                            filters=self.filters,
                                            delimiter_char=self.delimiter_char,
                                            add_view_id_column=self.add_view_id_column,
                                            use_flask_command=self.use_flask_command,
                                            fail_on_no_data=self.fail_on_no_data)
                + f'{_shell_linebreak_escape}| '
                + mara_db.shell.copy_from_stdin_command(self.target_db_alias, target_table=self.target_table_name,
                                                        null_value_string='', csv_format=True,
                                                        delimiter_char=self.delimiter_char))

    def html_doc_items(self) -> [(str, str)]:
        from mara_page import _
        from html import escape
        return [
            ('view id', _.pre[str(self.view_id)]),
            ('start date', _.pre[escape(self.start_date)]),
            ('end date', _.pre[escape(self.end_date)]),
            ('metrics', _.pre[escape(', '.join(self.metrics))]),
            ('dimensions', _.pre[escape(', '.join(self.dimensions if self.dimensions else []))]),
            ('filters', _.pre[escape(self.filters)]),
            ('add view id column', _.pre[str(self.add_view_id_column)]),
            ('target table name', _.pre[escape(self.target_table_name)]),
            ('target db', _.pre[escape(self.target_db_alias)]),
            ('Invocation', _.pre[_invocation(self.use_flask_command)]),
            ('Fail on no data', _.pre[str(self.fail_on_no_data)]),
        ]


def _invocation(use_flask):
    # import mara_google_analytics_downloader
    import mara_google_analytics_downloader.__main__
    main_module = mara_google_analytics_downloader.__name__
    flask_command_name = mara_google_analytics_downloader.__main__.ga_download_to_csv.callback.__name__.replace('_', '-')
    invocation = f'flask {main_module}.{flask_command_name}' if use_flask else main_module.replace('_', '-')
    return invocation


_shell_linebreak_escape = ' \\\n'
_indentions = ' ' * 5  # similar to what copy_from_stdin_command() does after a linebreak within the command


def ga_downloader_shell_command(view_id: int,
                                start_date: str,
                                end_date: str,
                                metrics: t.Iterable[str],
                                dimensions: t.Iterable[str] = None,
                                filters: str = None,
                                delimiter_char: str = '\t',
                                add_view_id_column: bool = False,
                                use_flask_command: bool = True,
                                fail_on_no_data: bool = True,
                                ):
    """
    Downloads google analytics data to a table

    Args:
        view_id: int, the Google Analytics view id, see https://ga-dev-tools.appspot.com/query-explorer/
        start_date: str, the start date of data to receive
        end_date: str, the end date of data to receive
        metrics: t.Iterable[str], the metrics to receive
        dimensions: t.Iterable[str] = None, the dimensions to receive
        filters: str=None, a filter string to be used in the query
        delimiter_char: str='\t', a character that delimits the output fields.
        add_view_id_column: bool=False, adds a new column at the beginning with the view id given in parameter view_id
        use_flask_command: bool=False, if true uses the downloader via flask, which needs an import in the flask app path
                           to make the command available and this can potentially print something which would make
                           the import fail. If True, the credentials are directly taken from the config,
                           not passed in via commandline arguments.
        fail_on_no_data: bool=True, if true fail on no data rows received
    """

    metrics_param = ','.join(metrics) if metrics else None
    dimensions_param = ','.join(dimensions) if dimensions else None

    command = []
    command.extend([
        _invocation(use_flask_command),
        _shell_linebreak_escape,
        _indentions,
        f" --view-id='{view_id}'",
        f' --add-view-id-column' if add_view_id_column else '--no-add-view-id-column',
        f" --start-date='{start_date}'",
        f" --end-date='{end_date}'",
        f' --metrics={metrics_param}',
        f' --dimensions={dimensions_param}',
        f" --delimiter-char='{delimiter_char}'",
        f' --fail-on-no-data' if fail_on_no_data else f' --no-fail-on-no-data'
    ])
    if filters:
        command.append(f" --filters='{filters}'")
    if not use_flask_command:
        if c.ga_service_account_client_id():
            command.extend([
                _shell_linebreak_escape,
                _indentions,
                f" --service-account-client-id='{c.ga_service_account_client_id()}'",
                f" --service-account-private-key-id='{c.ga_service_account_private_key_id()}'",
                f" --service-account-private-key='{c.ga_service_account_private_key()}'",
                f" --service-account-client-email='{c.ga_service_account_client_email()}'",
            ])
        elif c.ga_user_account_client_id():
            command.extend([
                _shell_linebreak_escape,
                _indentions,
                f" --user-account-client-id='{c.ga_user_account_client_id()}'",
                f" --user-account-client-secret='{c.ga_user_account_client_secret()}'",
                f" --user-account-refresh-token='{c.ga_user_account_refresh_token()}'",
            ])
        else:
            raise RuntimeError("Need either credentials for a google user account or for a google service account")

    return ''.join(command)
