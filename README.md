# VK => Telegram => VK script

## About

### Features
- Find posts with best conversion
- Sends it to Telegram chat
- Allows to send / schedule post to the your own group
- Watermark support

### Maintenance
Repository is not actively maintained, it was just a project for personal usage.

## Instructions

#### First steps
- Set your own watermark.png
- Read config file carefully. You'll to provide some environment variables on Heroku
- Create Heroku app
- Provision required add-ons on Heroku (Mongo and Runtime Metadata)
- Set up Cron to main.py file (Using add-on on Heroku) to send posts

#### Deployment Script
- Deploy
- Swear
- Fix bugs
- Repeat

View logs on Heroku carefully. They help a lot.
