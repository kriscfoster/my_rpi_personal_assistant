import samsungtvws
import os
import slackweb
import requests

tv_ip_address=os.environ.get('TV_IP_ADDRESS')

def get_state():
  response=requests.get('http://' + tv_ip_address + ':8001/api/v2/')
  state=response.json()['device']['PowerState']
  return state

def toggle_state():
  token_file=os.path.dirname(os.path.realpath(__file__)) + '/tv-token.txt'
  tv=samsungtvws.SamsungTVWS(host=tv_ip_address, port=8002, token_file=token_file)
  tv.shortcuts().power()

def send_state(channel_id):
  tv_state=get_state()
  message=':tv: tv state is *' + tv_state + '*'
  slackweb.post_message(channel_id, message)


def turn_off(channel_id):
  tv_state=get_state()

  message=''

  if tv_state == 'on':
    message=':tv: tv state is *on*, turning *off*'
  else:
    message=':tv: tv state is already *off*'

  slackweb.post_message(channel_id, message)

  if tv_state == 'on':
    toggle_state()
    message=':tv: tv turned *off*'
    slackweb.post_message(channel_id, message)

def turn_on(channel_id):
  tv_state=get_state()

  message=''

  if tv_state != 'on':
    message=':tv: tv state is *off*, turning *on*'
  else:
    message=':tv: tv state is already *on*'

  slackweb.post_message(channel_id, message)

  if tv_state != 'on':
    toggle_state()
    message=':tv: tv turned *on*'
    slackweb.post_message(channel_id, message)
