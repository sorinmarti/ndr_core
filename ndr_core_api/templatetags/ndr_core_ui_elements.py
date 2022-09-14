import csv
import json
import os
from random import choice

from django import template
from django.template.base import FilterExpression
from django.template.loader import render_to_string
from django.templatetags.static import static

from django.conf import settings
from ndr_core_api.models import NdrCorePage
from ndr_core_api.ndr_core_api_helpers import get_api_config

register = template.Library()


@register.simple_tag(name='page_title')
def get_page_title(selected_page_name):
    try:
        page = NdrCorePage.objects.get(view_name=selected_page_name)
        return page.name
    except NdrCorePage.DoesNotExist:
        return "Page Not Found"


@register.inclusion_tag('ndr_core_api/elements/navigation.html')
def print_navigation():
    navigation = NdrCorePage.objects.all().order_by('index')
    return {'navigation': navigation}


@register.inclusion_tag('ndr_core_api/elements/navigation_bottom.html')
def print_navigation_bottom():
    navigation = NdrCorePage.objects.all().order_by('index')
    return {'navigation': navigation}


@register.inclusion_tag('ndr_core_api/elements/tag_list.html')
def print_tag_list(tag_file, selected_tag='all'):
    try:
        app_name = get_api_config()["app_name"]
        file_handle = open(os.path.join(settings.STATIC_ROOT, f'{app_name}', tag_file))
        rd = csv.reader(file_handle, delimiter="\t")
        choices = list()
        line = 0
        for row in rd:
            if line > 0:
                choices.append({
                    'label': row[1],
                    'value': row[0]
                })
            line += 1
        choices = sorted(choices, key=lambda tup: tup['label'])
        choices = [{'label': 'All', 'value': ''}, ] + choices
        return {'tag_list': choices, 'selected_tag': selected_tag}
    except IOError:
        return {'tag_list': []}


@register.inclusion_tag('ndr_core_api/elements/source_card.html')
def show_source_card(source_card_json):
    source_card_json['image_url'] = f'{get_api_config()["app_name"]}/images/sources/{source_card_json["image"]}'
    return {'source': source_card_json}


@register.inclusion_tag('ndr_core_api/elements/item_carousel.html')
def show_info_card(info_box_json):

    return {'css_category_class': 'text-primary',
            'category_title': "database",
            'card_title': info_box_json['title'],
            'continue_url': info_box_json['view'],
            'img_url': f'{get_api_config()["app_name"]}/images/{info_box_json["image"]}'}


@register.inclusion_tag('ndr_core_api/elements/person_card.html')
def show_person_tile(title, role, text, image_name, url):
    return {'title': title,
            'role': role,
            'text': text,
            'image_name': f'{get_api_config()["app_name"]}/images/{image_name}',
            'url': url}


@register.inclusion_tag('ndr_core_api/elements/info_bite.html')
def show_info_bite(info_bite):
    return info_bite


@register.inclusion_tag(f'{get_api_config()["app_name"]}/result_line_dpc.html')
def show_result_line_dpc(result_line):
    return {"result": result_line}


@register.inclusion_tag(f'{get_api_config()["app_name"]}/result_line_asiadir.html')
def show_result_line_asiadir(result_line):
    return {"result": result_line}


@register.inclusion_tag(f'{get_api_config()["app_name"]}/result_line_haka.html')
def show_result_line_haka(result_line):
    return {"result": result_line}


@register.tag(name="card")
def do_card(parser, token):
    try:
        tag_name, title_text, image, category, continue_link, data_link = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("Invalid arguments")

    nodelist = parser.parse(('end_card',))
    parser.delete_first_token()

    title_text = FilterExpression(title_text, parser)
    image = FilterExpression(image, parser)
    category = FilterExpression(category, parser)
    continue_link = FilterExpression(continue_link, parser)
    data_link = FilterExpression(data_link, parser)

    return CardNode(title_text, image, category, continue_link, data_link, nodelist)


class CardNode(template.Node):

    def __init__(self, title_text, image, category, continue_link, data_link, nodelist):
        self.title_text = title_text
        self.image = image
        self.category = category
        self.continue_link = continue_link
        self.data_link = data_link
        self.nodelist = nodelist

    def render(self, context):
        app_name = get_api_config()["app_name"]

        title_text = self.title_text.resolve(context) if self.title_text else 'Set a Title'
        image = self.image.resolve(context) if self.image else 'Set an Image'
        category = self.category.resolve(context) if self.category else 'Set a Category'
        continue_link = self.continue_link.resolve(context) if self.continue_link else 'Set a Continue Link'
        data_link = self.data_link.resolve(context) if self.data_link else 'Set a Data Link'

        rendered = render_to_string('ndr_core_api/elements/card.html',
                                    {
                                        'title': title_text,
                                        'image': static(f'{app_name}/images/{image}'),
                                        'category': category,
                                        'continue_link': continue_link,
                                        'data_link': data_link,
                                        'contents': self.nodelist.render(context)
                                    })
        return rendered


@register.tag(name="banner")
def do_banner(parser, token):
    try:
        tag_name, banner_title = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("Invalid arguments")

    nodelist = parser.parse(('end_banner',))
    parser.delete_first_token()

    banner_title = FilterExpression(banner_title, parser)

    return BannerNode(banner_title, nodelist, "jumbotron")


@register.tag(name="banner_small")
def do_small_banner(parser, token):
    try:
        tag_name, banner_title = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("Invalid arguments")

    nodelist = parser.parse(('end_banner_small',))
    parser.delete_first_token()

    banner_title = FilterExpression(banner_title, parser)

    return BannerNode(banner_title, nodelist, "jumbotron-small")


class BannerNode(template.Node):

    def __init__(self, banner_title, nodelist, css_class):
        self.banner_title = banner_title
        self.nodelist = nodelist
        self.css_lass = css_class

    def render(self, context):
        app_name = get_api_config()["app_name"]
        img_list = os.listdir(os.path.join(settings.STATIC_ROOT, f'{app_name}/images/jumbotron/'))
        random_img = choice(img_list)
        banner_title = self.banner_title.resolve(context) if self.banner_title else 'Set a Title'
        print(banner_title)
        rendered = render_to_string('ndr_core_api/elements/jumbotron.html',
                                    {
                                        'banner_title': banner_title,
                                        'banner_content': self.nodelist.render(context),
                                        'image_name': static(f'{app_name}/images/jumbotron/{random_img}'),
                                        'css_class': self.css_lass
                                    })
        return rendered


@register.tag(name="titled_text")
def do_titled_text(parser, token):
    try:
        tag_name, text_title = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("Invalid arguments")

    nodelist = parser.parse(('end_titled_text',))
    parser.delete_first_token()

    text_title = FilterExpression(text_title, parser)

    return TitledTextNode(text_title, nodelist)


class TitledTextNode(template.Node):

    def __init__(self, text_title, nodelist):
        self.text_title = text_title
        self.nodelist = nodelist

    def render(self, context):
        text_title = self.text_title.resolve(context) if self.text_title else 'Set a Title'
        rendered = render_to_string('ndr_core_api/elements/titled_text.html',
                                    {
                                        'text_title': text_title,
                                        'contents': self.nodelist.render(context)
                                    })
        return rendered


@register.filter
def pretty_json(value):
    return json.dumps(value, indent=4)


@register.simple_tag
def query_transform(request, to_remove):
    """usages: {% query_transform request page=1 %}"""
    updated = request.GET.copy()
    try:
        del (updated[to_remove])
    except KeyError:
        pass

    return "?" + updated.urlencode()