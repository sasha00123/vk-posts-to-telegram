import telegram
from telegram import InlineKeyboardMarkup, InlineKeyboardButton

from config import *
from pymongo import MongoClient
import json


def offer(posts):
    bot = telegram.Bot(token=TELEGRAM_TOKEN)

    client = MongoClient(MONGO_DB_URL)
    db = client.get_database()

    post_list = db.posts
    print("Created bot instance")
    for i, post in enumerate(posts):
        id = str(post_list.insert_one(post).inserted_id)
        text = post["link"]
        conv = post["likes"]["count"] / post["views"]["count"]

        # Better to store in separate resource file.
        text += """
 Статистика:
    ❤: {} / {} / {}
    👁: {} / {}
    🚀 {}% / {}%
        """.format(post["likes"]["count"], int(post["mean"]["views"] * conv), int(post["mean"]["likes"]),
                   post["views"]["count"],  int(post["mean"]["views"]),
                   int(conv * 1000) / 10,  int(post["mean"]["conversion"] * 1000) / 10)

        keyboard = [
            [
                InlineKeyboardButton("Отправить ⚡", callback_data=json.dumps({
                    "i": id,
                    "p": False
                })),
            ],
            [
                InlineKeyboardButton("Отложить 🕐", callback_data=json.dumps({
                    "i": id,
                    "p": True
                })),
            ]
        ]

        markup = InlineKeyboardMarkup(keyboard)

        # Would be better to add some error-handling
        try:
            bot.send_message(chat_id=TELEGRAM_USERNAME,
                             text=text,
                             reply_markup=markup)
        except:
            continue
