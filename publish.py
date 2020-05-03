from bson import ObjectId
from pymongo import MongoClient
from PIL import Image
import json
import requests
from config import *
from urllib.parse import urlencode
from datetime import datetime, timedelta


def get_publish_date():
    # Ask VK for postponed posts
    response = requests.get("{}/{}?{}".format(VK_BASE, "wall.get", urlencode({
        "access_token": VK_TOKEN,
        "v": "5.78",
        "filter": "postponed",
        "owner_id": -VK_GROUP_ID
    })))

    # If there was no posts -> Publish in 3 minutes
    num_postponed_posts = json.loads(response.text)["response"]["count"]
    if num_postponed_posts == 0:
        return (datetime.now() + timedelta(minutes=3)).timestamp()

    # Find last date & return
    postponed_posts = json.loads(response.text)["response"]["items"]
    postponed_posts.sort(key=lambda x: -x["date"])
    latest_post = postponed_posts[0]
    dt = datetime.fromtimestamp(latest_post["date"])

    return (dt + timedelta(hours=1)).timestamp()


def publish(post, watermark, publish_date=None):
    # Getting Vk Server to upload image
    # Would be better if there're was proper error handling.
    response = requests.get("{}/{}?{}".format(VK_BASE, "photos.getWallUploadServer", urlencode({
        "access_token": VK_TOKEN,
        "v": "5.78",
        "group_id": VK_GROUP_ID
    })))
    upload_url = json.loads(response.text)["response"]["upload_url"]

    links = []
    for image in [a for a in post["attachments"] if a["type"] == "photo"]:
        # Here saving attachment to file and saving a path to it.
        # Maybe there's a workaround with bytes, that was a quick work around.

        image_url = image["photo"]["sizes"][-1]["url"]
        path = "{}-{}.png".format(post["id"], image["photo"]["id"])

        with open(path, "wb") as file:
            file.write(requests.get(image_url).content)

        # Pasting watermark if required
        if watermark is not False:
            # Reading image
            base = Image.open(path)
            mark = Image.open("watermark.png")

            width, height = base.size
            w, h = mark.size

            # Creating empty canvas
            t = Image.new('RGBA', (width, height), (0, 0, 0, 0))
            t.paste(base, (0, 0))

            # Set appropriate position
            if watermark == "L":
                position = (15, height - 15 - h)
            else:
                position = (width - w - 15, height - 15 - h)

            # Pasting & Saving
            t.paste(mark, position, mask=mark)
            t.save(path)

        response = requests.post(upload_url, files={
            "photo": open(path, 'rb'),
        })
        os.remove(path)

        data = json.loads(response.text)
        data["access_token"] = VK_TOKEN
        data["v"] = "5.78"
        data["group_id"] = VK_GROUP_ID

        response = requests.post("{}/{}".format(VK_BASE, "photos.saveWallPhoto"), data=data)
        data = json.loads(response.text)["response"][0]

        # Uploaded to the server => Adding link to it
        links.append("photo{}_{}".format(data["owner_id"], data["id"]))
    data = {
        "owner_id": -VK_GROUP_ID,
        "from_group": 1,
        "message": post["text"],
        "attachments": ",".join(links),
        "access_token": VK_TOKEN,
        "v": "5.78",
    }
    if publish_date is not None:
        data["publish_date"] = publish_date
    response = requests.post("{}/{}".format(VK_BASE, "wall.post"), data=data)
    print(response.status_code)
    print(response.text)


def post(post_id, postpone, watermark):
    client = MongoClient(MONGO_DB_URL)
    db = client.get_database()
    posts = db.posts
    if postpone:
        publish(posts.find_one({"_id": ObjectId(post_id)}), publish_date=get_publish_date(), watermark=watermark)
    else:
        publish(posts.find_one({"_id": ObjectId(post_id)}), watermark=watermark)
