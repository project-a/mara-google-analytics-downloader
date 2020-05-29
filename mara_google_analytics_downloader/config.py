"""Config for mara Google Analytics Downloader

You need to configure oauth2 credentials for either a google service or a google user account.
"""
import typing as t

def ga_service_account_private_key_id()-> t.Optional[str]:
    """Google Service Account private_key_id used to download the Google Analytics Data"""
    return None

def ga_service_account_private_key()-> t.Optional[str]:
    """Google Service Account private_key used to download the Google Analytics Data"""
    return None

def ga_service_account_client_email()-> t.Optional[str]:
    """Google Service Account client_email used to download the Google Analytics Data"""
    return None

def ga_service_account_client_id()-> t.Optional[str]:
    """Google Service Account client_id used to download the Google Analytics Data"""
    return None

def ga_user_account_client_id()-> t.Optional[str]:
    """Google User Account client_id used to download the Google Analytics Data"""
    return None

def ga_user_account_client_secret()-> t.Optional[str]:
    """Google User Account client_secret used to download the Google Analytics Data"""
    return None

def ga_user_account_refresh_token()-> t.Optional[str]:
    """Google User Account refresh_token used to download the Google Analytics Data"""
    return None
