# -*- coding: utf-8 -*-

# Sample Python code for youtube.playlistItems.list
# See instructions for running these code samples locally:
# https://developers.google.com/explorer-help/guides/code_samples#python

import os
# import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import dotenv


def yt_api_build():
    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    client_secrets_file = "../.misc/client_secret.json"

    # Get credentials and create an API client
    # flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
    #     client_secrets_file, scopes)
    # credentials = flow.run_console()
    return googleapiclient.discovery.build(
        'youtube', 'v3', developerKey=os.getenv('GOOGLE_DEVELOPER_KEY')
    )


if __name__ == "__main__":
    yt_api_build()