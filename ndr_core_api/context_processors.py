import json
import os
import random

from django.conf import settings

from ndr_core_api.ndr_core_api_helpers import get_api_config


def info_bite(request):
    f = open(os.path.join(settings.STATIC_ROOT, f'{get_api_config()["app_name"]}/data/bites.json'))
    data = json.load(f)
    bite = random.choice(data["bites"])
    if "image" in bite:
        bite["image"] = f'{get_api_config()["app_name"]}/images/info_bites/{bite["image"]}'
    return {"info_bite": bite}


def carousel_info(request):
    f = open(os.path.join(settings.STATIC_ROOT, f'{get_api_config()["app_name"]}/data/info_boxes.json'))
    info_tiles = json.load(f)
    return {"carousel_info": info_tiles["box_rows"]}
