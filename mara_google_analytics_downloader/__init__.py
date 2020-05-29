def MARA_CONFIG_MODULES():
    from mara_google_analytics_downloader import config
    return [config]

def MARA_CLICK_COMMANDS():
    from mara_google_analytics_downloader.__main__ import ga_download_to_csv
    from mara_google_analytics_downloader.user_credential_helper import generate_user_refresh_token
    return [ga_download_to_csv, generate_user_refresh_token]
