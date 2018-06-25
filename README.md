# slack-parrot
dont let your memes be dreams

a clone of mimic

### Setup and Installation
* Make a new bot user in your Slack workspace and get yourself a Slack API token (see https://api.slack.com/bot-users)
* Clone the repo
* `pip install -r requirements.txt` in your preferred environment
* Add a file called `slackbot_settings.py
    * Add the setting `API_TOKEN = 'your_token_here'`
* Run the `parrot.py` in the background of your cloud instance with nohup or something
