from django.conf import settings


def get_api_config():
    try:
        saved_api_config = getattr(settings, "NDR_CORE_API_CONFIG")
    except AttributeError:
        saved_api_config = {}

    set_default_config_value(saved_api_config, "app_name", "main")

    set_default_config_value(saved_api_config, "use_dummy_result", False)
    set_default_config_value(saved_api_config, "dummy_result_file", None)
    set_default_config_value(saved_api_config, "api_host", "localhost")
    set_default_config_value(saved_api_config, "api_protocol", "localhost")
    set_default_config_value(saved_api_config, "api_port", "localhost")
    set_default_config_value(saved_api_config, "search_fields",
                             {
                                "default_field": {
                                    "type": "string",
                                    "required": True
                                }
                             })
    set_default_config_value(saved_api_config, "configurations", {"advanced": "__all__"})

    return saved_api_config


def get_search_field_config(field_name):
    config = get_api_config()
    if field_name in config["search_fields"]:
        return config["search_fields"][field_name]
    raise ValueError(f"Field '{field_name}' not found")


def set_default_config_value(ndr_core_settings, name, value):
    if name not in ndr_core_settings:
        ndr_core_settings[name] = value
