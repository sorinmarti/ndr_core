import json

from django.http import HttpResponse
from django.shortcuts import render
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from ndr_core_api.api import create_advanced_search_string
from ndr_core_api.ndr_core_api_helpers import get_api_config, get_search_field_config
from ndr_core_api.forms import SimpleSearchForm, AdvancedSearchForm, get_choices_from_tsv


class _NdrCoreSearchView(View):

    template_name = None

    def __init__(self, *args, **kwargs):
        self.api_config = get_api_config()
        super().__init__(*args, **kwargs)

    def get_query_base(self):
        """Returns the base of each query URL in the form PROTOCOL://HOST:PORT"""
        return f"{self.api_config['api_protocol']}://{self.api_config['api_host']}:{self.api_config['api_host']}"


class SimpleSearchView(_NdrCoreSearchView):
    form_class = SimpleSearchForm
    template_name = 'ndr_core_api/simple_search_form_template.html'
    result_line_template = 'ndr_core_api/simple_search_form_template.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():

            print("GET RESULT")
        return render(request, self.template_name, {'form': form})

    def compose_query(self, search_term, page=1, search_type="and"):

        return "" # self.get_query_base()


class AdvancedSearchView(_NdrCoreSearchView):
    form_class = AdvancedSearchForm
    template_name = 'ndr_core_api/advanced_search_form_template.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class(request.GET)
        if form.is_valid():
            print("GET RESULT")
            create_advanced_search_string(request.GET)
        else:
            print("FORM INVALID")
            print(form.errors)
        return render(request, self.template_name, {'form': form})


@csrf_exempt
def list_autocomplete2(request, list_name):
    if request.method == "GET":
        search_list = get_list(list_name)
        result_list = []
        search_term = request.GET.get("term", "")
        for item in search_list:
            print(item)
            if search_term.lower() in item[1].lower():
                result_list.append(item)
        return HttpResponse(json.dumps(result_list), content_type='application/json')

    return HttpResponse(json.dumps([]), content_type='application/json')


def get_list(list_name):
    field_config = get_search_field_config(list_name)
    choices = get_choices_from_tsv(field_config["dictionary"])
    return choices


@csrf_exempt
def list_autocomplete_single(request, list_name, selected_value):
    if request.method == "GET":
        choices = get_list(list_name)
        for item in choices:
            if selected_value == item[1]:
                return HttpResponse(json.dumps(item), content_type='application/json')
    return HttpResponse(json.dumps({}), content_type='application/json')


@csrf_exempt
def list_autocomplete_key_single(request, list_name, selected_value):
    if request.method == "GET":
        choices = get_list(list_name)
        for item in choices:
            if selected_value == item[0]:
                return HttpResponse(json.dumps(item), content_type='application/json')
    return HttpResponse(json.dumps({}), content_type='application/json')
