from picamera import PiCamera
from flask import Flask, request, jsonify
from slack import WebClient
from slack import RTMClient
import os
import time
from slackeventsapi import SlackEventAdapter

slack_api_token = os.environ.get('SLACK_API_TOKEN')
slack_signing_secret = os.environ.get('SLACK_SIGNING_SECRET')
surveillance_images_base_path = os.environ.get('SURVEILLANCE_IMAGES_BASE_PATH')
approved_user_id = os.environ.get('APPROVED_USER_ID')
surveillance_channel_name = os.environ.get('SURVEILLANCE_CHANNEL_NAME')
surveillance_channel_id = ''

slack_client = WebClient(slack_api_token)
slack_events_adapter = SlackEventAdapter(slack_signing_secret, "/slack/events", app)

all_channels = slack_client.channels_list(exclude_archived=1)['channels']

for channel in all_channels:
    if channel['name'] == surveillance_channel_name:
        surveillance_channel_id = channel['id']

camera = PiCamera()
app = Flask(__name__)

def send_surveillance_image(channel_id):
    slack_client.chat_postMessage(
        channel=channel_id,
        text='Sure, taking a picture for you now :camera_with_flash:'
    )

    millis = str(round(time.time() * 1000))
    surveillance_image_path = surveillance_images_base_path + millis + '.jpg'
    camera.capture(surveillance_image_path)

    slack_client.chat_postMessage(
      channel=channel_id,
      text='Surveillance picture taken, going to upload it :computer:'
    )

    slack_client.files_upload(
      channels=channel_id,
      file=surveillance_image_path,
      title=surveillance_image_path
    )
    
    return 'surveillance photo uploaded :camera_with_flash'

@slack_events_adapter.on("app_mention")
def app_mentioned(event_data):
    text = event_data['event']['text']
    channel_id = event_data['event']['channel']
    user_id = event_data['event']['user']
    if user_id == approved_user_id:
        if 'image' in text:
            send_surveillance_image(channel_id)
        else:
            slack_client.chat_postMessage(
              channel=channel_id,
              text='Sorry, didn\'t understand that :confused:'
            )
    else:
            slack_client.chat_postMessage(
              channel=channel_id,
              text='You\'re not allowed to do that :police_car:'
            )

if __name__ == '__main__':
    app.run()
