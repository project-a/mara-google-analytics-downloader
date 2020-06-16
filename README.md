# Mara Google Analytics Downloader

This package contains a google analytics downloader to be used with the mara ETL framework:

- Download a google analytics request to a database table

&nbsp;

## Installation

To use the library directly:

```
pip install git+https://github.com/hz-lschick/mara-google-analytics-downloader.git
```

&nbsp;

## Example

Here is a pipeline "ga_demo" which downloads to a table. This assumes you have a active google analytics account.
The analytics account access must be shared with the
email address for which you configured the credentials (see below).

```python
from mara_pipelines.pipelines import Pipeline, Task
from mara_pipelines.commands.sql import ExecuteSQL
from mara_google_analytics_downloader.mara_integration import DownloadGoogleAnalyticsFlatTable

pipeline = Pipeline(
    id='ga_demo',
    description='A small pipeline that demonstrates the google analytics download')

pipeline.add(Task(
    id='download_', description='Downloads a google analytics query into a flat table',
    commands=[
        ExecuteSQL(
                sql_statement=f"""
-- Creates the table where the google analytics data should end up in
DROP TABLE IF EXISTS public.ga_test;
CREATE TABLE public.ga_test (
    -- dimensions
    ga_date DATE,

    -- metrics
    ga_users BIGINT,
    ga_sessions BIGINT
)
""",
            echo_queries=False,
        ),
        DownloadGoogleAnalyticsFlatTable(

            # For help what to fill out here, check out the Google Analytics Query Explorer:
            #   https://ga-dev-tools.appspot.com/query-explorer/

            view_id='999999', # the google analytics view (profile) id, without the 'ga:' prefix
            start_date='7daysAgo', # the start date of the data to receive
            end_date='today', # the end date of the data to receive (default: today)
            dimensions=[ # the dimensions to receive (optional)
                'ga:date'
            ],
            metrics=[ # the metrics to receive
                'ga:users',
                'ga:sessions'
            ],
            target_table_name='public.ga_test', # table where the data should end up
            target_db_alias='dwh', # alias of the DB where the data should end up
        ),
    ]),
)
```

## Config

The downloader needs OAuth2 credentials, either use a service account or a user account.
* For service accounts, see https://gspread.readthedocs.io/en/latest/oauth2.html. All required information is in the
  downloaded json file.
* For user account credentials, see https://developers.google.com/analytics/devguides/reporting/core/v4/quickstart/service-py, Step 1.
  For getting the initial refresh token, you can use
  `flask mara_google_analytics_downloader.generate-user-refresh-token /path/to/downloaded/credential.json`

Credentials will need the scope `'https://www.googleapis.com/auth/analytics.readonly'`.

Example with OAuth2 credentials for a user account:

```python
from mara_app.monkey_patch import patch
import mara_google_analytics_downloader.config
patch(mara_google_analytics_downloader.config.ga_user_account_client_id)(lambda:"....client_id...")
patch(mara_google_analytics_downloader.config.ga_user_account_client_secret)(lambda:"...client_secret...")
patch(mara_google_analytics_downloader.config.ga_user_account_refresh_token)(lambda:"...initial_refresh_token...")
```

## Setup access to Google Analytics account to be downloaded

All sheets which should be accessed by the downloader must be shared with the email address associated with these
credentials. This email address is:

* for user account credentials: the email address of the user who created the credentials.
* for service accounts: the email address of the service account itself (e.g. "*@*.iam.gserviceaccount.com").
  This email address is e.g. included in the json file you can download.

## CLI

This package contains a small cli app which downloads a google analytics query and outputs it as csv.

You can use it stand alone, see `python -m mara_google_analytics_downloader --help ` for how to use it.
