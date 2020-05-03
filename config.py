import os
from decouple import config, Csv

# Telegram specific configs
TELEGRAM_TOKEN = config("TELEGRAM_TOKEN")
# Chat where to send posts. Might be any chat id.
TELEGRAM_USERNAME = config("TELEGRAM_USERNAME")

# VK.com specific configs
VK_TOKEN = config("VK_TOKEN")
VK_BASE = "https://api.vk.com/method"
VK_GROUP_TOKEN = config("VK_GROUP_TOKEN")
VK_GROUP_ID = config("VK_GROUP_ID")
# Where to search info - comma separated short names, publicXXXXXX, groupXXXXXX
DOMAINS = config("DOMAINS", cast=Csv(str))

# Data filled by HEROKU itself
# Should provision Mongo Database in add-ons.
# Also better to provision Runtime Metadata.
HEROKU_APP_NAME = config("HEROKU_APP_NAME")
MONGO_DB_URL = config("MONGODB_URI")
PORT = config("PORT", default=8443, cast=int)
