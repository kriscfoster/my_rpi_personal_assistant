# my_rpi_personal_assistant
my_rpi is a personal assistant using a Raspberry Pi that you can interract with over Slack.

## features
* takes live picture.
* gets tv status (on/standby).
* turns tv on/off.
* gets YouTube channel stats.

## virtual environment

### setting up virtual environment
```python3 -m venv env```

### activating virtual environment
```source env/bin/activate```

### leaving virtual environment
```deactivate```

### installing from requirements file
```pip install -r requirements.txt```

## required environment variables
* ```SLACK_SIGNING_SECRET```
* ```SLACK_API_TOKEN```
* ```APPROVED_USER_ID```
* ```TV_IP_ADDRESS```
* ```SURVEILLANCE_IMAGES_BASE_PATH```
* ```YOUTUBE_API_TOKEN```
* ```YOUTUBE_CHANNEL_ID```