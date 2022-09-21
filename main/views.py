import csv
import json
import os
from operator import itemgetter

from django.contrib import messages
from django.shortcuts import render
from django.views import View

from django.conf import settings
from ndr_core_api.ndr_core_api_helpers import get_api_config
from ndr_core_api.views import AdvancedSearchView, get_list


class MyAdvancedSearchView(AdvancedSearchView):
    template_name = 'main/advanced_search.html'
    endpoint = "query"
    query_type = "advanced"

    def transform_result(self, hit):
        hit["full_name"] = ""
        print("RES2", hit["result_number"])
        if "name" in hit and "familyname" in hit["name"]:
            hit["full_name"] = hit["name"]["familyname"]
        if "name" in hit and "givennames" in hit["name"]:
            hit["full_name"] += ", " + hit["name"]["givennames"]


def show_include(request, study):
    app_name = get_api_config()["app_name"]
    print('include')

    previous_study = None
    next_study = None

    filenames = os.listdir(f'{app_name}/templates/main/studies')
    filenames.sort()
    current_index = filenames.index(study+".html")

    if current_index > 0:
        previous_study = filenames[current_index-1].split(".html")[0]
    else:
        previous_study = filenames[len(filenames)-1].split(".html")[0]

    if current_index < len(filenames)-1:
        next_study = filenames[current_index+1].split(".html")[0]
    else:
        next_study = filenames[0].split(".html")[0]

    return render(request, 'main/study.html', {'current': study,
                                               'previous': previous_study,
                                               'next': next_study})

class IncludeView(View):
    template_name = 'main/study.html'
    include_name = 'study'
    record_file = 'records.tsv'

    def get(self, request, *args, **kwargs):
        prev_include = None
        next_include = None
        current_include = None
        current_id = request.GET.get(self.include_name, None)

        try:
            choices = list()
            app_name = get_api_config()["app_name"]
            file_handle = open(os.path.join(settings.STATIC_ROOT, f'{app_name}', self.record_file), encoding='utf-8')
            csv_reader = csv.DictReader(file_handle, delimiter='\t')
            row_idx = 0
            for row in csv_reader:
                choices.append(row)
            choices = sorted(choices, key=lambda tup: tup['sorting'])

            if current_id is None:
                current_include = choices[0]
                if len(choices) > 1:
                    next_include = choices[1]
            else:
                current_include_idx = map(itemgetter('id'), choices).index(current_id)
                current_include = choices[current_include_idx]
                if current_include_idx > 0:
                    prev_include = choices[current_include_idx-1]
                if current_include_idx < len(choices):
                    next_include = choices[current_include_idx + 1]
        except IOError:
            messages.warning(request, 'Source file not found')

        return render(request, self.template_name, {'current_include': current_include,
                                                    'prev_include': prev_include,
                                                    'next_include': next_include})


def get_label_of():
    print(get_list('tags'))
