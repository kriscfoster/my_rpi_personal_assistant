from picamera import PiCamera
from flask import Flask, request, jsonify
from threading import Thread
from slack import WebClient
from slack import RTMClient
from slackeventsapi import SlackEventAdapter
from samsungtvws import SamsungTVWS

import os
import time
import requests

tv_ip_address = os.environ.get('TV_IP_ADDRESS')
youtube_api_token = os.environ.get('YOUTUBE_API_TOKEN')
slack_api_token = os.environ.get('SLACK_API_TOKEN')
slack_signing_secret = os.environ.get('SLACK_SIGNING_SECRET')
surveillance_images_base_path = os.environ.get('SURVEILLANCE_IMAGES_BASE_PATH')
approved_user_id = os.environ.get('APPROVED_USER_ID')
surveillance_channel_name = os.environ.get('SURVEILLANCE_CHANNEL_NAME')
surveillance_channel_id = ''
toggle_surveillance_mode = False

camera = PiCamera()
app = Flask(__name__)

slack_client = WebClient(slack_api_token)
slack_events_adapter = SlackEventAdapter(slack_signing_secret, "/slack/events", app)

all_channels = slack_client.channels_list(exclude_archived=1)['channels']

for channel in all_channels:
  if channel['name'] == surveillance_channel_name:
    surveillance_channel_id = channel['id']


def get_tv_state():
  response = requests.get('http://' + tv_ip_address + ':8001/api/v2/')
  state = response.json()['device']['PowerState']
  return state;

def send_surveillance_image(channel_id):
  millis = str(round(time.time() * 1000))
  surveillance_image_path = surveillance_images_base_path + millis + '.jpg'
  camera.capture(surveillance_image_path)

  slack_client.chat_postMessage(
    channel=channel_id,
    text='Surveillance picture taken, uploading it :computer:'
  )

  slack_client.files_upload(
    channels=channel_id,
    file=surveillance_image_path,
    title=surveillance_image_path
  )
    
  return 'surveillance photo uploaded :camera_with_flash'

def send_youtube_stats(channel_id):
  response = requests.get('https://www.googleapis.com/youtube/v3/channels?part=statistics&id=UCWkzkhQ3syxBjjAYwqCbzYg&key=' + youtube_api_token)
  subscriber_count = response.json()['items'][0]['statistics']['subscriberCount']
  view_count = response.json()['items'][0]['statistics']['viewCount']
  response_text = ':smiley: subscribers: *' + subscriber_count + '*\n' + ':eyes: views: *' + view_count + '*'
  slack_client.chat_postMessage(
    channel=channel_id,
    text=response_text
  )

@slack_events_adapter.on('app_mention')
def app_mentioned(event_data):
  text = event_data['event']['text']
  channel_id = event_data['event']['channel']
  user_id = event_data['event']['user']
  if user_id == approved_user_id:
    if 'picture' in text:
      slack_client.chat_postMessage(
          channel=channel_id,
          text='Sure, taking a picture for you now :camera_with_flash:'
      )
      thread = Thread(target=send_surveillance_image, args=[channel_id])
      thread.start()
    elif 'YouTube' in text:
      thread = Thread(target=send_youtube_stats, args=[channel_id])
      thread.start()
    elif 'surveillance on' in text:
      toggle_surveillance_mode = True
      slack_client.chat_postMessage(
        channel=channel_id,
        text=':video_camera: surveillance mode *ON*, movement detections will be sent to <#' + surveillance_channel_id + '>'
      )
    elif 'surveillance off' in text:
      toggle_surveillance_mode = False
      slack_client.chat_postMessage(
        channel=channel_id,
        text=':video_camera: surveillance mode *OFF*'
      )
    elif 'tv state' in text:
      tv_state = get_tv_state()
      slack_client.chat_postMessage(
        channel=channel_id,
        text=':tv: state is: *' + tv_state + '*'
      )
    elif 'tv off' in text:
      slack_client.chat_postMessage(
        channel=channel_id,
        text=':tv: turning tv *OFF*'
      )

      tv_state = get_tv_state()

      if tv_state == 'on':
        tv.shortcuts().power()

      slack_client.chat_postMessage(
        channel=channel_id,
        text=':tv: tv is *OFF*'
      )
    elif 'tv on' in text:
      slack_client.chat_postMessage(
        channel=channel_id,
        text=':tv: turning tv *ON*'
      )

      tv_state = get_tv_state()

      if tv_state == 'off':
        tv.shortcuts().power()

      slack_client.chat_postMessage(
        channel=channel_id,
        text=':tv: tv is *ON*'
      )
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
