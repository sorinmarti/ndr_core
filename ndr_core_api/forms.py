import csv
import os
from django import forms
from django.conf import settings
from ndr_core_api.ndr_core_api_helpers import get_api_config, get_search_field_config
from ndr_core_api.widgets import CustomSelect, CustomRange


class _NdrCoreSearchForm(forms.Form):

    def __init__(self, *args, **kwargs):
        self.api_config = get_api_config()
        super(forms.Form, self).__init__(*args, **kwargs)


class SimpleSearchForm(_NdrCoreSearchForm):
    search_term = forms.CharField(label='Search Term', max_length=100)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class AdvancedSearchForm(_NdrCoreSearchForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.query_dict = querydict_to_dict(args[0])

        if "advanced" in self.api_config["configurations"]:
            advanced_configuration = self.api_config["configurations"]["advanced"]
            search_fields = {}
            if "__all__" in advanced_configuration:
                search_fields = self.api_config["search_fields"]
            else:
                for field_name in advanced_configuration:
                    search_fields[field_name] = get_search_field_config(field_name)

            for field in search_fields:
                new_field = None
                required = False
                field_config = search_fields[field]
                print("FIELD", field_config)

                if "required" in field_config:
                    required = field_config["required"]

                if "type" in field_config:
                    if field_config["type"] == "string":
                        new_field = forms.CharField(required=required)
                    if field_config["type"] == "boolean":
                        new_field = forms.BooleanField(required=required)
                    if field_config["type"] == "number-range":
                        if f'startRange_{field}' in self.query_dict:
                            lower_number = self.query_dict[f'startRange_{field}']
                        else:
                            lower_number = field_config["number-range"]["min_number"]

                        if f'endRange_{field}' in self.query_dict:
                            upper_number = self.query_dict[f'endRange_{field}']
                        else:
                            upper_number = field_config["number-range"]["max_number"]

                        rangeWidget = CustomRange(attrs={'lower_number': str(lower_number),
                                                         'upper_number': str(upper_number)},)
                        new_field = forms.CharField(required=required, widget=rangeWidget)
                    if field_config["type"] == "dictionary":
                        dict_widget = forms.Select
                        if "dictionary" in field_config:
                            dict_config = field_config["dictionary"]
                            if "widget" in field_config:
                                if field_config["widget"] == "multi_search":
                                    if field+"[]" in self.query_dict:
                                        selection = self.query_dict[field+"[]"]
                                        if selection == '':
                                            selection = []
                                        elif isinstance(selection, str):
                                            selection = [selection, ]
                                    else:
                                        selection = []
                                    dict_widget = CustomSelect(attrs={'list_name': field, 'selection': selection},)
                            if "type" in dict_config:
                                if dict_config["type"] == "tsv":
                                    choices = get_choices_from_tsv(dict_config)
                                    new_field = forms.ChoiceField(widget=dict_widget, choices=choices, required=False)
                                if dict_config["type"] == "json":
                                    print(">> dictionary type 'json' not implemented yet")
                            else:
                                print(">> dictionary setting needs type")
                        else:
                            print(">> malformed dictionary setting")

                else:
                    new_field = forms.CharField(required=required)

                if new_field is not None:
                    self.fields[field] = new_field


def get_choices_from_tsv(dict_config):
    if "display_column" in dict_config and "search_column" in dict_config and "file" in dict_config:
        choices = list()
        with open(os.path.join(settings.STATIC_ROOT, dict_config["file"])) as fd:
            rd = csv.reader(fd, delimiter="\t")
            line = 0
            for row in rd:
                if line > 0 or (line == 0 and not dict_config["has_title_row"]):
                    choices.append((
                        row[dict_config["search_column"]],
                        row[dict_config["display_column"]]
                    ))
                line += 1
        choices = sorted(choices, key=lambda tup: tup[1])
        return choices
    else:
        print(">> dictionary config needs search- and display-column")
        return []


def querydict_to_dict(query_dict):
    data = {}
    for key in query_dict.keys():
        v = query_dict.getlist(key)
        if len(v) == 1:
            v = v[0]
        data[key] = v
    return data