import os
import subprocess

from mara_google_analytics_downloader.mara_integration import ga_downloader_shell_command
from . import local_config


# NOTE
#   Test is missing for paramter
#     --filters
#     --delimiter-char
#     --add-view-id-column/--no-add-view-id-column
#     --fail-on-no-data/--no-fail-on-no-data


def test_simple_query_1():
    TEST_FILE = 'tests/test_shell_ga.simple_query_1.csv'
    dimensions = ['ga:date']
    metrics = ['ga:sessions']

    if os.path.isfile(TEST_FILE):
        os.remove(TEST_FILE)

    command = ga_downloader_shell_command(
        view_id=local_config.VIEW_ID,
        start_date=local_config.START_DATE,
        end_date=local_config.END_DATE,
        metrics=metrics,
        dimensions=dimensions,
        use_flask_command=False
    )

    command = f'{command} > {TEST_FILE}'

    print(command)

    (exitcode, output) = subprocess.getstatusoutput(command)
    print(output)
    assert exitcode == 0
    assert not output
    assert os.path.isfile(TEST_FILE)
