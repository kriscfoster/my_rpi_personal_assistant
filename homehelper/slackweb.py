import slack
import os

slack_api_token=os.environ.get('SLACK_API_TOKEN')
slack_client=slack.WebClient(slack_api_token)

def post_message(channel_id, message):
  slack_client.chat_postMessage(
    channel=channel_id,
    text=message
  )

def upload_file(channel_id, file, title):
  slack_client.files_upload(
    channels=channel_id,
    file=file,
    title=title
  )
