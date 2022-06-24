from ndr_core_api.ndr_core_api_helpers import get_api_config


def get_base_string(api_config, endpoint, page):
    base_string = f"{api_config['api_protocol']}://{api_config['api_host']}:{api_config['api_port']}/{endpoint}/?s={api_config['page_size']}&p={page}"
    return base_string

def create_advanced_search_string(get_params, page=1):
    api_config = get_api_config()
    api_request_str = get_base_string(api_config, "chapters", page)

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

    print("API-request", api_request_str)