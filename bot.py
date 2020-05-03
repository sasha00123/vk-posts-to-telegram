from telegram.ext import Updater, CallbackQueryHandler
from config import *
from publish import post
import logging
import json

from telegram import InlineKeyboardMarkup, InlineKeyboardButton

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.DEBUG)
logger = logging.getLogger(__name__)


def button(bot, update):
    # Handling button clicks under posts
    query = update.callback_query
    data = json.loads(query.data)

    # Post instantly or delay choice
    if "c" in data:
        keyboard = [
            [
                InlineKeyboardButton("Отправить ⚡", callback_data=json.dumps({
                    "i": data["i"],
                    "p": False
                })),
            ],
            [
                InlineKeyboardButton("Отложить 🕐", callback_data=json.dumps({
                    "i": data["i"],
                    "p": True
                })),
            ]
        ]
        markup = InlineKeyboardMarkup(keyboard)
        bot.edit_message_text(text=query.message.text,
                              chat_id=query.message.chat.id,
                              message_id=query.message.message_id,
                              reply_markup=markup)
        return

    # Some dark WaterMark processing magic.
    # I don't really get it either.)
    # You would rather not touch anything here, it might fail. Will try to decrypt it one day.
    if not "w" in data:
        keyboard = [[InlineKeyboardButton("No Watermark",
                                          callback_data=json.dumps({
                                              "i": data["i"],
                                              "p": data["p"],
                                              "w": False
                                          })),
                     InlineKeyboardButton("Left",
                                          callback_data=json.dumps({
                                              "i": data["i"],
                                              "p": data["p"],
                                              "w": "L"
                                          })),
                     InlineKeyboardButton("Right",
                                          callback_data=json.dumps({
                                              "i": data["i"],
                                              "p": data["p"],
                                              "w": "R"
                                          }))],
                    [InlineKeyboardButton("Cancel",
                                          callback_data=json.dumps({
                                              "i": data["i"],
                                              "c": True
                                          }))]]

        markup = InlineKeyboardMarkup(keyboard)
        bot.edit_message_text(text=query.message.text,
                              chat_id=query.message.chat.id,
                              message_id=query.message.message_id,
                              reply_markup=markup)
        return

    post(post_id=data["i"], postpone=data["p"], watermark=data["w"])
    bot.edit_message_text(text=query.message.text + "\nPOSTED!",
                          chat_id=query.message.chat.id,
                          message_id=query.message.message_id)


updater = Updater(token=TELEGRAM_TOKEN)
updater.dispatcher.add_handler(CallbackQueryHandler(button))

# Default template for Telegram Webhook & Heroku with python-telegram-bot
updater.start_webhook(listen="0.0.0.0",
                      port=PORT,
                      url_path=TELEGRAM_TOKEN)
updater.bot.set_webhook(f"https://{HEROKU_APP_NAME}.herokuapp.com/{TELEGRAM_TOKEN}")
updater.idle()
