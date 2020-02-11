from picamera import PiCamera
from flask import Flask, request, jsonify
from slack import WebClient
import os
import time

slack_bot_token = os.environ.get('SLACK_BOT_TOKEN')
surveillance_images_base_path = os.environ.get('SURVEILLANCE_IMAGES_BASE_PATH')
surveillance_channel_name = os.environ.get('SURVEILLANCE_CHANNEL_NAME')
surveillance_channel_id = ''

slack_client = WebClient(slack_bot_token)
camera = PiCamera()

all_channels = slack_client.channels_list(exclude_archived=1)['channels']

for channel in all_channels:
    if channel['name'] == surveillance_channel_name:
        surveillance_channel_id = channel['id']

app = Flask(__name__)
@app.route('/image', methods=['GET', 'POST'])
def take_surveillance_image():
    millis = str(round(time.time() * 1000))
    surveillance_image_path = surveillance_images_base_path + millis + '.jpg'
    camera.capture(surveillance_image_path)

    slack_client.chat_postMessage(
      channel=surveillance_channel_id,
      text='surveillance image taken :camera_with_flash:'
    )

    slack_client.files_upload(
      channels=surveillance_channel_id,
      file=surveillance_image_path,
      title=surveillance_image_path
    )
    
    return 'surveillance photo uploaded :camera_with_flash'

if __name__ == '__main__':
    app.run()
