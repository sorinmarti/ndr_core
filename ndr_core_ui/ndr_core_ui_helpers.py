from django.conf import settings


def get_api_config():
    try:
        saved_api_config = getattr(settings, "NDR_CORE_UI_CONFIG")
    except AttributeError:
        saved_api_config = {}

    set_default_config_value(saved_api_config, "header_title", "NDR Core Database")
    set_default_config_value(saved_api_config, "header_author", "NDR Core")
    set_default_config_value(saved_api_config, "header_description", "NDR Core Database Instance")

    set_default_config_value(saved_api_config, "website_title", "NDR Core Database")

    set_default_config_value(saved_api_config, "main_view", "ndr_core_ui:index")
    set_default_config_value(saved_api_config, "search_view", "ndr_core_ui:search")

    set_default_config_value(saved_api_config, "footer_text", "(c) 2022, NDR Core")

    return saved_api_config


def set_default_config_value(ndr_core_settings, name, value):
    if name not in ndr_core_settings:
        ndr_core_settings[name] = value
