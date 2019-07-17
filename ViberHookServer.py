from flask import Flask, Request, Response
from viberbot import Api
from viberbot.api.bot_configuration import BotConfiguration
from viberbot.api.messages import TextMessage, PictureMessage
import sched
import logging

from viberbot.api.viber_requests import (ViberConversationStartedRequest,
                                         ViberFailedRequest,
                                         ViberMessageRequest,
                                         ViberSubscribedRequest,
                                         ViberUnsubscribedRequest)

#Logging
logger = logging.getLogger(__name__)

#Constants
viber_bot_token = '49fd42821d67d3dd-8fa60f299b0fd824-2fc686a67f7a3354'
viber_bot_name = 'DLTC'
viber_bot_logo = 'logo.png'

#Initialization
app = Flask(__name__)
bot_configuration = BotConfiguration(
	name = viber_bot_name,
	avatar = viber_bot_logo,
	auth_token = viber_bot_token
)
viber = Api(bot_configuration)

@app.route('/', methods=['POST'])
def incoming():
    logger.debug("received request. post data: {0}".format(request.get_data()))

    #All messages must be signed (it is by default)
    if not viber.verify_signature(request.get_data(), request.headers.get('X-Viber-Content-Signature')):
        #Error if not signed
        return Response(status=403)

    viber_request = viber.parse_request(request.get_data())

    #Check type of request

    #Answer any message
    if isinstance(viber_request, ViberMessageRequest):
        text_message = TextMessage(text=random.choice(['Foo', 'Lumberjack', 'Спасибо Кириллу за Кириллицу!']))
        viber.send_messages(viber_request.sender.id, [text_message])

    #Thank user for subscription
    elif isinstance(viber_request, ViberSubscribedRequest):
        viber.send_messages(viber_request.sender.id, [TextMessage(text='Thaks for subscription!')])

    #Errors should never pass silently
    elif isinstance(viber_request, ViberFailedRequest):
        logger.warn("client failed receiving message. failure: {0}".format(viber_request))

    return Response(status=200)


def set_webhook(viber_bot):
    viber_bot.set_webhook('https://xxx.xxx.xxx.xxx:4443')
    logging.info("Web hook has been set")


if __name__ == "__main__":
    scheduler = sched.scheduler(time.time, time.sleep)
    scheduler.enter(5, 1, set_webhook, (viber,))
    t = threading.Thread(target=scheduler.run)
    t.start()
    
    app.run(host='0.0.0.0', port=4443, debug=True, ssl_context=context)