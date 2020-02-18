from picamera import PiCamera
from flask import Flask, request, jsonify
from threading import Thread
from slack import RTMClient
from slackeventsapi import SlackEventAdapter
import slackweb
import bedroomtv
import youtube

import os
import time

surveillance_images_base_path=os.environ.get('SURVEILLANCE_IMAGES_BASE_PATH')
slack_signing_secret=os.environ.get('SLACK_SIGNING_SECRET')
approved_user_id=os.environ.get('APPROVED_USER_ID')

camera=PiCamera()
app=Flask(__name__)


slack_events_adapter=SlackEventAdapter(slack_signing_secret, "/slack/events", app)

def send_surveillance_image(channel_id):
  message='Sure, taking a picture for you now :camera_with_flash:'
  slackweb.post_message(channel_id, message)

  millis=str(round(time.time() * 1000))
  surveillance_image_path=surveillance_images_base_path + millis + '.jpg'
  camera.capture(surveillance_image_path)

  message='Surveillance picture taken, uploading it :computer:'
  slackweb.post_message(channel_id, message)
  slackweb.upload_file(channel_id, surveillance_image_path, surveillance_image_path)


@slack_events_adapter.on('app_mention')
def app_mentioned(event_data):
  text=event_data['event']['text']
  channel_id=event_data['event']['channel']
  user_id=event_data['event']['user']
  if user_id == approved_user_id:
    if 'picture' in text:
      thread=Thread(target=send_surveillance_image, args=[channel_id])
      thread.start()
    elif 'YouTube' in text:
      thread=Thread(target=youtube.send_stats, args=[channel_id])
      thread.start()
    elif 'tv state' in text:
      thread=Thread(target=bedroomtv.send_state, args=[channel_id])
      thread.start()
    elif 'tv off' in text:
      thread=Thread(target=bedroomtv.turn_off, args=[channel_id])
      thread.start()
    elif 'tv on' in text:
      thread=Thread(target=bedroomtv.turn_on, args=[channel_id])
      thread.start()
    else:
      message='Sorry, didn\'t understand that :confused:'
      slackweb.post_message(channel_id, message)
  else:
    message='You\'re not allowed to do that :police_car:'
    slackweb.post_message(channel_id, message)
if __name__ == '__main__':
  app.run()
