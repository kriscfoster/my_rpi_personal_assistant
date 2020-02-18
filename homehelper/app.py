import flask
import threading
import os
import slackeventsapi

import slackweb
import bedroomtv
import youtube
import surveillance

slack_signing_secret=os.environ.get('SLACK_SIGNING_SECRET')
approved_user_id=os.environ.get('APPROVED_USER_ID')

app=flask.Flask(__name__)
slack_events_adapter=slackeventsapi.SlackEventAdapter(slack_signing_secret, "/slack/events", app)

@slack_events_adapter.on('app_mention')
def app_mentioned(event_data):
  text=event_data['event']['text'].lower()
  channel_id=event_data['event']['channel']
  user_id=event_data['event']['user']

  if user_id != approved_user_id:
    message='You\'re not allowed to do that :police_car:'
    slackweb.post_message(channel_id, message)
  elif 'picture' in text:
    thread=threading.Thread(target=surveillance.send_image, args=[channel_id])
    thread.start()
  elif 'youtube' in text:
    thread=threading.Thread(target=youtube.send_stats, args=[channel_id])
    thread.start()
  elif 'tv state' in text:
    thread=threading.Thread(target=bedroomtv.send_state, args=[channel_id])
    thread.start()
  elif 'tv off' in text:
    thread=threading.Thread(target=bedroomtv.turn_off, args=[channel_id])
    thread.start()
  elif 'tv on' in text:
    thread=threading.Thread(target=bedroomtv.turn_on, args=[channel_id])
    thread.start()
  else:
    message='Sorry, didn\'t understand that :confused:'
    slackweb.post_message(channel_id, message)

if __name__ == '__main__':
  app.run()
