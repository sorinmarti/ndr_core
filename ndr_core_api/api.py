import json

import requests

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

        if field_config["type"] == "dictionary" and field_config["widget"] == "multi_search":
            param_str = f"&{api_param}="+",".join(get_params.getlist(field+"[]", []))
        else:
            param_str = f"&{api_param}="+get_params.get(field, "")
        api_request_str += param_str

    return api_request_str


def get_result(query):
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