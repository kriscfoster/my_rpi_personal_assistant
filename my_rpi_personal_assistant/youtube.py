import requests
import slackweb
import os

youtube_api_token=os.environ.get('YOUTUBE_API_TOKEN')
youtube_channel_id=os.environ.get('YOUTUBE_CHANNEL_ID')

def send_stats(channel_id):
  response=requests.get('https://www.googleapis.com/youtube/v3/channels?part=statistics&id=' + youtube_channel_id + '&key=' + youtube_api_token)
  subscriber_count=response.json()['items'][0]['statistics']['subscriberCount']
  view_count=response.json()['items'][0]['statistics']['viewCount']
  response_text=':smiley: subscribers: *' + subscriber_count + '*\n' + ':eyes: views: *' + view_count + '*'
  slackweb.post_message(channel_id, response_text)
