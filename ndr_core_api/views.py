import json

from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from ndr_core_api.api import create_advanced_search_string, get_result
from ndr_core_api.ndr_core_api_helpers import get_api_config, get_search_field_config
from ndr_core_api.forms import SimpleSearchForm, AdvancedSearchForm, get_choices_from_tsv
from ndr_core_api.pagination import get_page_list


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
        form = self.form_class(request.GET)
        if form.is_valid():
            print("GET RESULT")
        return render(request, self.template_name, {'form': form})

    def compose_query(self, search_term, page=1, search_type="and"):

        return "" # self.get_query_base()


class AdvancedSearchView(_NdrCoreSearchView):
    form_class = AdvancedSearchForm
    template_name = 'ndr_core_api/advanced_search_form_template.html'
    endpoint = "query"

    def get(self, request, *args, **kwargs):
        form = self.form_class(request.GET)
        hit_list = None
        search_metadata = None
        if form.is_valid():
            if request.GET.get("search", None) is not None:
                query = create_advanced_search_string(self.endpoint, request.GET)
                print(query)
                result = get_result(query)
                if result is None:
                    messages.error(request, "The query could not be sent: unknown error")
                else:
                    if "error" in result:
                        messages.error(request, result["error"])
                    else:
                        # Assuming the result is valid
                        if "hits" in result:
                            hit_list = result["hits"]
                            self.transform_results(hit_list)

                            search_metadata = {"total": result["total"],
                                               "page": result["page"],
                                               "size": result["size"]}
                            search_metadata["num_pages"] = int(search_metadata["total"] / search_metadata["size"])
                            if search_metadata["total"] % search_metadata["size"] > 0:
                                search_metadata["num_pages"] += 1
                            search_metadata["pagelinks"] = get_page_list(request,
                                                                         int(result["page"]),
                                                                         int(search_metadata["num_pages"]))

        else:
            pass
            # print(form.errors)
        return render(request, self.template_name, {'form': form, 'result': hit_list, 'meta': search_metadata})

    def transform_results(self, hit_list):
        for hit in hit_list:
            self.transform_result(hit)

    def transform_result(self, hit):
        pass


@csrf_exempt
def list_autocomplete2(request, list_name):
    if request.method == "GET":
        search_list = get_list(list_name)
        result_list = []
        search_term = request.GET.get("term", "")
        for item in search_list:
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
