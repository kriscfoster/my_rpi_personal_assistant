import os
import time
import picamera

import slackweb

surveillance_images_base_path=os.environ.get('SURVEILLANCE_IMAGES_BASE_PATH')

camera=picamera.PiCamera()

def send_image(channel_id):
  message='Sure, taking a picture for you now :camera_with_flash:'
  slackweb.post_message(channel_id, message)

  millis=str(round(time.time() * 1000))
  surveillance_image_path=surveillance_images_base_path + millis + '.jpg'
  camera.capture(surveillance_image_path)

  message='Surveillance picture taken, uploading it :computer:'
  slackweb.post_message(channel_id, message)
  slackweb.upload_file(channel_id, surveillance_image_path, surveillance_image_path)
