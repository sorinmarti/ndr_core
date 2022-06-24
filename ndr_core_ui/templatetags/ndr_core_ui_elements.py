import os
from random import choice

from django import template
from django.template.base import FilterExpression
from django.template.loader import render_to_string
from django.templatetags.static import static

from django.conf import settings
from ndr_core_ui.models import NdrCorePage

register = template.Library()


@register.simple_tag(name='page_title')
def get_page_title(selected_page_name):
    try:
        page = NdrCorePage.objects.get(view_name=selected_page_name)
        return page.name
    except NdrCorePage.DoesNotExist:
        return "Page Not Found"


@register.inclusion_tag('ndr_core_ui/elements/navigation.html')
def print_navigation():
    navigation = NdrCorePage.objects.all().order_by('index')
    return {'navigation': navigation}


@register.inclusion_tag('ndr_core_ui/elements/item_carousel.html')
def show_info_card(info_box_json):

    return {'css_category_class': 'text-primary',
            'category_title': "database",
            'card_title': info_box_json['title'],
            'continue_url': info_box_json['view'],
            'img_url': f'main/images/info_tiles/{info_box_json["image"]}'}


@register.inclusion_tag('ndr_core_ui/elements/person_card2.html')
def show_person_tile(title, role, text, image_name, url):
    return {'title': title,
            'role': role,
            'text': text,
            'image_name': f'ndr_core_ui/images/project_members/{image_name}',
            'url': url}


@register.inclusion_tag('ndr_core_ui/elements/info_bite.html')
def show_info_bite(info_bite):
    return info_bite


@register.inclusion_tag('ndr_core_ui/elements/result_line.html')
def show_result_line(result_line):
    return result_line


@register.tag(name="banner")
def do_banner(parser, token):
    try:
        tag_name, banner_title = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("Invalid arguments")

    nodelist = parser.parse(('endbanner',))
    parser.delete_first_token()

    banner_title = FilterExpression(banner_title, parser)

    return BannerNode(banner_title, nodelist)


class BannerNode(template.Node):

    def __init__(self, banner_title, nodelist):
        self.banner_title = banner_title
        self.nodelist = nodelist

    def render(self, context):
        img_list = os.listdir(os.path.join(settings.STATIC_ROOT, 'ndr_core_ui/images/headers/'))
        random_img = choice(img_list)
        banner_title = self.banner_title.resolve(context) if self.banner_title else 'Set a Title'
        print(banner_title)
        rendered = render_to_string('ndr_core_ui/elements/jumbotron.html',
                                    {
                                        'banner_title': banner_title,
                                        'banner_content': self.nodelist.render(context),
                                        'image_name': static(f'main/images/headers/{random_img}')
                                    })
        return rendered
