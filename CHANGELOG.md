# Changelog

## 1.1.2 (2021-01-22)

- hotfix Google Analytics API did not work after version 1.1.0

## 1.1.1 (2021-01-22)

- fix mara integration broke when `add_view_id_column` was `False`

## 1.1.0 (2020-12-18)

- add support for requests to the Multi-Channel Funnel Reporting API
- fix broken mara html_doc_items when arg 'filters' is `None`

## 1.0.0 (2020-12-01)

- add all currently available dimensions and metrics from [Dimensions & Metrics Explorer](https://ga-dev-tools.appspot.com/dimensions-metrics-explorer/?)
- set shell entry point
- disable OAuth cache, fixes `ImportError: file_cache is unavailable' message

## 0.4.2 (2020-08-19)

- fix mara integration for parameter '--filters' when is empty

## 0.4.1 (2020-08-18)

- fix mara integration for parameter '--filters'

## 0.4.0 (2020-08-17)

- add support for paramter '--filters' _NOTE:_ Not all metrics/dimensions are supporeted yet! see [static.py](mara_google_analytics_downloader/static.py)

## 0.3.0 (2020-06-16)

- switch from data-integration (2.7.0) to mara-pipelines (3.0.0)

## 0.2.0 (2020-06-02)

- add parameter '--add-view-id-column'

## 0.1.0 (2020-05-29)

- initial version
