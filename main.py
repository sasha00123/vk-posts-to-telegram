import json
from datetime import datetime, timedelta
from urllib.parse import urlencode
import requests
from config import *
from send import offer
import time


def main():
    all_posts = []
    for domain in DOMAINS:
        # Dirty way to handle 10 req/s limit.
        time.sleep(0.1)

        response = requests.get("{}/wall.get?{}".format(VK_BASE, urlencode({
            "access_token": VK_TOKEN,
            "v": "5.78",
            "domain": domain,
            "count": 50,
            "extended": 1,
        })))

        if response.status_code == 200:
            data = json.loads(response.text)

            if "error" in data:
                continue

            data = data["response"]
            posts = data["items"]

            # Counting mean values

            size_l = len([post for post in posts[:50] if 'likes' in post])
            size_v = len([post for post in posts[:50] if 'views' in post])

            if size_l > 0:
                mean_likes = list(sorted([post["likes"]["count"]
                                          for post in posts[:50] if 'likes' in post]))[size_l // 2]
            else:
                mean_likes = -1
            if size_v > 0:
                mean_views = list(sorted([post["views"]["count"]
                                          for post in posts[:50] if 'views' in post]))[size_v // 2]
            else:
                mean_views = -1
            if size_l > 0 and size_v > 0:
                mean_conversion = list(sorted([post["likes"]["count"] / post["views"]["count"]
                                               for post in posts[:50] if 'likes' in post and 'views' in post]))[
                    min(size_v, size_l) // 2]
            else:
                mean_conversion = -1

            # Filling all the necessary info
            for post in posts:
                delta = datetime.now() - datetime.fromtimestamp(post["date"])

                if not timedelta(hours=3) < delta < timedelta(hours=6, minutes=1) or "copy_history" in post \
                        or post["marked_as_ads"] or "http" in post["text"]:
                    post['conversion'] = 0
                    continue

                post["group_name"] = domain
                post["mean"] = {
                    "likes": mean_likes,
                    "views": mean_views,
                    "conversion": mean_conversion
                }
                post["conversion"] = post["likes"]["count"] / post["views"]["count"]
                post["link"] = "https://vk.com/wall-{}_{}".format(data["groups"][0]["id"], post["id"])
                all_posts.append(post)
        else:
            print("Ошибка! Статус: {}".format(response.status_code))

    # Find best posts
    all_posts = [post for post in all_posts if "mean" in post]
    all_posts.sort(key=lambda x: x["conversion"] / x["mean"]["conversion"], reverse=True)
    offer([post for post in all_posts if "mean" in post and post['conversion'] >= post['mean']['conversion']][:15])


if __name__ == "__main__":
    main()
