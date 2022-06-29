import json
import os
import requests
from django.conf import settings

from ndr_core_api.ndr_core_api_helpers import get_api_config


def get_base_string(api_config, endpoint, page):
    base_string = f"{api_config['api_protocol']}://{api_config['api_host']}:{api_config['api_port']}/{endpoint}/?s={api_config['page_size']}&p={page}"
    return base_string


def create_advanced_search_string(endpoint, get_params):
    api_config = get_api_config()
    page_to_show = get_params.get("page", 1)
    api_request_str = get_base_string(api_config, endpoint, page_to_show)

    for field in api_config["search_fields"]:
        field_config = api_config["search_fields"][field]
        if "api_param" in field_config:
            api_param = field_config["api_param"]
        else:
            api_param = field

        param_str = ""
        if field_config["type"] == "dictionary" and field_config["widget"] == "multi_search":
            value_list = get_params.getlist(field+"[]", [])
            if len(value_list) > 0:
                param_str = f"&{api_param}="+",".join(value_list)
        else:
            value = get_params.get(field, "")
            if value != "":
                param_str = f"&{api_param}="+value
        api_request_str += param_str

    return api_request_str


def get_result(query):
    if get_api_config()["use_dummy_result"]:
        return dummy_get_result_list()

    try:
        # Timeouts: 2s until connection, 5s until result
        result = requests.get(query, timeout=(2, 5))
    except requests.exceptions.ConnectTimeout as e:
        return {"error": "The connection timed out"}
    except requests.exceptions.RequestException as e:
        return {"error": "Query could not be requested"}

    if result.status_code == 200:
        try:
            json_obj = json.loads(result.text)
            return json_obj
        except json.JSONDecodeError:
            return {"error": "Result could not be loaded"}
    else:
        return {"error": f"The server returned status code: {result.status_code}"}


def dummy_get_result_list():
    api_config = get_api_config()
    base_dummy_result = {
        "total": 181,
        "page": 2,
        "size": 10,
        "links": {
            "prev": None,
            "next": None,
            "self": ""
        },
        "hits": []
    }
    if api_config["dummy_result_file"] is not None:
        with open(os.path.join(settings.STATIC_ROOT, api_config["dummy_result_file"])) as f:
            dummy_search_line = json.load(f)
            for i in range(int(api_config["page_size"])):
                base_dummy_result["hits"].append(dummy_search_line)
            return base_dummy_result
    else:
        return base_dummy_result
