from django import template

from ndr_core_ui.ndr_core_ui_helpers import get_ui_config

register = template.Library()


@register.simple_tag(name='config_value')
def get_config_value(value):
    ndr_core_ui_config = get_ui_config()
    if value in ndr_core_ui_config:
        return ndr_core_ui_config[value]
    return "No Value Found"
