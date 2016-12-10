# ALL THIS IS DONE WITH A HEROKU SERVER, IF YOU'RE USING A SELF SIGNED CERTIFICATE YOU MAY NEED TO CHANGE SOME THINGS 


import os
import telegram
import requests
from telegram.ext import Updater
from flask import Flask, request, Response

# CONFIG
TOKEN = 'YOUR TELEGRAM TOKEN'
SLACK = 'YOUR SLACK TOKEN'
SLACK_WEBHOOK = 'YOUR SLACK INCOMING WEBHOOK URL'
HOST = 'YOUR HOST'

is_prod = os.environ.get('IS_HEROKU', None)

PORT = int(os.environ.get('PORT', '5000'))

# USE THIS IS YOU'RE USING A SELF SIGNEG CERT.
CERT = 'cert.pem'
CERT_KEY = 'private.key'
context = (CERT, CERT_KEY)


bot = telegram.Bot(TOKEN)
updater = Updater(TOKEN)
app = Flask(__name__)


@app.route("/")
def get():
    return Response("OK!")


@app.route('/' + TOKEN, methods=['POST'])
def webhook_handler():
    if request.method == "POST":
        # retrieve the message in JSON and then transform it to Telegram object
        update = telegram.Update.de_json(request.get_json(force=True), bot=bot)

        url = SLACK_WEBHOOK

        firstN = update.message.from_user.first_name
        lastN = update.message.from_user.last_name
        payload = {"text": "*{} {}:* {}".format(firstN, lastN, update.message.text)}

        send = requests.post(url, json=payload)

    return "OK"


@app.route("/" + SLACK, methods=['POST'])
def inbound():
    if request.form.get('token') == SLACK:
        username = request.form.get('user_name')
        text = request.form.get('text')
        inbound_message = "*{}:* {}".format(username, text)
        print(inbound_message)

        text = inbound_message

        if request.form.get('bot_id') == "YOUR BOT ID SO YOU SKIP DUPLICATES OR MESSAGES LOOPS":
            return "Bot"

        else:
            bot.sendMessage(chat_id="", text=text, parse_mode='Markdown')
    return Response(), 200


def setwebhook():
    updater.bot.setWebhook(webhook_url="https://URL:PORT/{}".format(TOKEN),  # certificate=open(CERT, 'rb')) UNCOMMENT THIS IF YOU'RE USING A S.S.C. SAME WITH PORT, OVERRIDE IT IF YOU'RE NOT USING A S.S.C.

if __name__ == '__main__':
    setwebhook()

    app.run(host='0.0.0.0',
            port=PORT,
            threaded=True,
            #ssl_context=context, UNCOMMENT THIS IF YOU'RE USING A S.S.C.
            debug=True)
