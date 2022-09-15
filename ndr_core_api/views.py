import csv
import json
import os
from smtplib import SMTPException

from django.contrib import messages
from django.core.mail import send_mail
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from django.conf import settings
from ndr_core_api.api import create_advanced_search_string, get_result
from ndr_core_api.ndr_core_api_helpers import get_api_config, get_search_field_config
from ndr_core_api.forms import SimpleSearchForm, AdvancedSearchForm, get_choices_from_tsv, ContactForm, FilterForm
from ndr_core_api.pagination import get_page_list
from ndr_core_api.ndr_core_api_helpers import get_api_config


class _NdrCoreSearchView(View):
    """ Base view for all configured ndr_core views. Provides access to the api-config"""

    template_name = None

    def __init__(self, *args, **kwargs):
        self.api_config = get_api_config()
        super().__init__(*args, **kwargs)

    def get_query_base(self):
        """Returns the base of each query URL in the form PROTOCOL://HOST:PORT"""
        return f"{self.api_config['api_protocol']}://{self.api_config['api_host']}:{self.api_config['api_host']}"


class DiscoverView(_NdrCoreSearchView):
    """ View to discover different datasets within a collection. They can be filtered by tags """
    def get(self, request, *args, **kwargs):
        if request.GET.get("tag", None) is not None:
            tag_to_load = request.GET.get("tag", None)
        else:
            tag_to_load = "all"

        return render(request, self.template_name, {})

    def get_list(self):
        """"""
        return {}


class SimpleSearchView(_NdrCoreSearchView):
    """ View to provide a simple search view with a single search field """
    form_class = SimpleSearchForm
    template_name = 'ndr_core_api/simple_search_form_template.html'
    result_line_template = 'ndr_core_api/simple_search_form_template.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class(request.GET)
        if form.is_valid():
            print("GET RESULT")
        return render(request, self.template_name, {'form': form})

    def compose_query(self, search_term, page=1, search_type="and"):

        return "" #self.get_query_base()


class AdvancedSearchView(_NdrCoreSearchView):
    """ View to provide a more detailed search with different fields """
    form_class = AdvancedSearchForm
    template_name = 'ndr_core_api/advanced_search_form_template.html'
    endpoint = "query"
    query_type = "basic"

    def get(self, request, *args, **kwargs):
        repository = None
        repository_title = None

        form = self.form_class()
        if request.method == "GET":
            form = self.form_class(request.GET)

            hit_list = None
            search_metadata = None
            if form.is_valid():
                if request.GET.get("search", None) is not None:
                    repository = form.cleaned_data["repo_to_search"]
                    repository_title = self.api_config["repositories"][repository]["label"]
                    query_type = self.query_type
                    if "query_type" in self.api_config["repositories"][repository]:
                        query_type = self.api_config["repositories"][repository]["query_type"]

                    query = create_advanced_search_string(repository, self.endpoint, query_type, request.GET)
                    result = get_result(repository, query)
                    if result is None:
                        messages.error(request, "The query could not be sent: unknown error")
                    else:
                        if "error" in result:
                            messages.error(request, result["error"])
                        else:
                            # Assuming the result is valid
                            if "hits" in result:
                                if int(result["total"]) == 0:
                                    messages.warning(request, "Your search didn't return any results")
                                hit_list = result["hits"]
                                self.transform_results(hit_list, result["page"], result["size"], result["total"])

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
        return render(request, self.template_name, {
            'form': form,
            'result': hit_list,
            'meta': search_metadata,
            'search_repo': repository,
            'search_repo_title': repository_title})

    def transform_results(self, hit_list, page, page_size, total_results):
        result_number = (page * page_size) - page_size + 1

        for hit in hit_list:
            hit["result_number"] = f"{result_number} of {total_results}"
            self.transform_result(hit)
            result_number += 1

    def transform_result(self, hit):
        pass


class FilterView(_NdrCoreSearchView):

    record_file = "records.csv"

    def get(self, request, *args, **kwargs):
        form = FilterForm()
        choices = list()

        if request.GET.get("show_all", None) is not None:
            return HttpResponseRedirect(request.path)

        if request.GET.get("filter", None) is not None:
            form = FilterForm(request.GET)

        if form.is_valid() or request.GET.get("filter", None) is None:
            try:
                app_name = get_api_config()["app_name"]
                file_handle = open(os.path.join(settings.STATIC_ROOT, f'{app_name}', self.record_file), encoding='utf-8')
                csv_reader = csv.DictReader(file_handle, delimiter=',', quotechar='"')
                selected_tags = request.GET.getlist("tags[]", None)
                all_tags = get_dict_list("tags")

                for row in csv_reader:
                    tag_search = row['tags']
                    row['tags'] = [{'tag': row["tags"], 'label': all_tags[row["tags"]]}, ]
                    if len(selected_tags) > 0:
                        for tag in selected_tags:
                            if tag in tag_search:
                                choices.append(row)
                                break
                    else:
                        choices.append(row)

                choices = sorted(choices, key=lambda tup: int(tup['sorting']), reverse=True)
            except IOError:
                print("source file not found")

            page_size = 5
            page = int(request.GET.get("page", 1))
            first_item = page_size * page - page_size
            last_item = first_item + page_size
            if last_item > len(choices):
                last_item = len(choices)

            search_metadata = {"total": len(choices),
                               "page": request.GET.get("page", '1'),
                               "size": page_size}
            search_metadata["num_pages"] = int(search_metadata["total"] / search_metadata["size"])
            if search_metadata["total"] % search_metadata["size"] > 0:
                search_metadata["num_pages"] += 1
            search_metadata["num_pages"] = str(search_metadata["num_pages"])
            search_metadata["pagelinks"] = get_page_list(request,
                                                         int(search_metadata["page"]),
                                                         int(search_metadata["num_pages"]))

            choices = choices[first_item:last_item]

        return render(request, self.template_name, {'results': choices, 'form': form, 'meta': search_metadata})


class ContactView(_NdrCoreSearchView):
    form_class = ContactForm
    template_name = 'ndr_core_api/contact_form.html'
    success_template_name = 'ndr_core_api/contact_form_sent.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            try:
                message = f'A message was sent through the contact form at {self.api_config["www-host"]}\n' \
                          f'\n' \
                          f'Subject: {form.cleaned_data["subject"]}\n' \
                          f'Reply-to: {form.cleaned_data["email"]}\n' \
                          f'Message: {form.cleaned_data["message"]}\n' \
                          f'\n' \
                          f'Do NOT reply directly to this message.'

                send_mail(
                    subject=f'Contact Message From {self.api_config["www-host"]}',
                    message=message,
                    from_email=self.api_config["contact-from-email"],
                    recipient_list=self.api_config["contact-recipients"],
                    fail_silently=False,
                )
                return render(request, self.success_template_name, {'email': form.cleaned_data['email']})
            except SMTPException:
                messages.error(request, 'Mail couldn\'t be sent')
                return render(request, self.template_name, {'form': form})

        return render(request, self.template_name, {'form': form})


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


def get_dict_list(list_name):
    field_config = get_search_field_config(list_name)
    choices = get_choices_from_tsv(field_config["dictionary"])
    result = dict()
    for choice in choices:
        result[choice[0]] = choice[1]
    return result


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
