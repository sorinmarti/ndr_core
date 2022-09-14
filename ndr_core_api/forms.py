import csv
import os

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field, Row, Column, Div, Button, BaseInput, Fieldset, HTML
from django import forms
from django.conf import settings
from django.utils.safestring import mark_safe

from ndr_core_api.ndr_core_api_helpers import get_api_config, get_search_field_config
from ndr_core_api.widgets import CustomSelect, CustomRange


class _NdrCoreSearchForm(forms.Form):

    def __init__(self, *args, **kwargs):
        self.api_config = get_api_config()
        super(forms.Form, self).__init__(*args, **kwargs)


class SimpleSearchForm(_NdrCoreSearchForm):
    search_term = forms.CharField(label='Search Term', max_length=100, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def helper(self):
        helper = FormHelper()
        helper.add_input(Submit('search', 'Search'))
        return helper


class AdvancedSearchForm(_NdrCoreSearchForm):

    repo_to_search = forms.Field()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.query_dict = {}
        if len(args) > 0:
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
                help_text = ""
                field_config = search_fields[field]

                if "required" in field_config:
                    required = field_config["required"]
                if "help_text" in field_config:
                    help_text = mark_safe(f'<small id="{field}Help" class="form-text text-muted">{field_config["help_text"]}</small>')

                if "type" in field_config:
                    if field_config["type"] == "string":
                        new_field = forms.CharField(required=required, help_text=help_text)
                    if field_config["type"] == "number":
                        new_field = forms.IntegerField(required=required, help_text=help_text)
                    if field_config["type"] == "boolean":
                        new_field = forms.BooleanField(required=required, help_text=help_text)
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
                        new_field = forms.CharField(required=required, widget=rangeWidget, help_text=help_text)
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
                                    new_field = forms.ChoiceField(widget=dict_widget, choices=choices, required=False, help_text=help_text)
                                if dict_config["type"] == "json":
                                    print(">> dictionary type 'json' not implemented yet")
                            else:
                                print(">> dictionary setting needs type")
                        else:
                            print(">> malformed dictionary setting")

                else:
                    new_field = forms.CharField(required=required, help_text=help_text)

                if new_field is not None:
                    self.fields[field] = new_field

    @property
    def helper(self):
        helper = FormHelper()
        helper.form_method = "GET"
        layout = helper.layout = Layout()

        for row in self.api_config["form_display"]:
            form_row = Div(css_class='form-row')
            for column in row:
                form_field = Field(column["name"], placeholder=column["name"].capitalize(), wrapper_class=f'col-md-{column["size"]}')
                form_row.append(form_field)

            layout.append(form_row)

        helper.form_show_labels = False

        select_html = '<select class="custom-select" name="repo_to_search">'
        for config in self.api_config["repositories"]:
            selected = ""
            if "repo_to_search" in self.query_dict and config == self.query_dict["repo_to_search"]:
                selected = " selected"
            select_html += f'<option value="{config}"{selected}>{self.api_config["repositories"][config]["label"]}</option>'
        select_html += '</select>'

        layout.append(
            Div(
                Div(
                    Div(
                        HTML(f'''<div class="input-group">
                          {select_html}
                          <div class="input-group-append">
                            <input type="submit" value="Search" name="search" class="btn btn-outline-secondary" type="button"Search>
                          </div>
                        </div>'''),
                        css_class="form-group"
                    ),
                    css_class="col-md-6 offset-md-6"
                ),
                css_class='form-row'
            )
        )

        return helper


class FilterForm(_NdrCoreSearchForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.query_dict = {}
        if len(args) > 0:
            self.query_dict = querydict_to_dict(args[0])

        if "tags[]" in self.query_dict:
            selection = self.query_dict["tags[]"]
            if selection == '':
                selection = []
            elif isinstance(selection, str):
                selection = [selection, ]
        else:
            selection = []

        choice_widget = CustomSelect(attrs={'list_name': 'tags', 'selection': selection, 'placeholder': 'All sub collections are selected. Filter them by type here.'}, )
        dict_config = {
            "type": "tsv",
            "file": "main/tag_list.tsv",
            "search_column": 0,
            "display_column": 1,
            "has_title_row": True
        }
        choices = get_choices_from_tsv(dict_config)
        filter_field = forms.ChoiceField(widget=choice_widget, choices=choices, required=False)
        self.fields['tags'] = filter_field

    @property
    def helper(self):
        helper = FormHelper()
        helper.form_method = "GET"
        helper.form_show_labels = False
        layout = helper.layout = Layout()

        form_row = Row(
            Column(
                Field('tags'),
                css_class=f'col-md-10'
            ),
            Column(
                Div(
                    MySubmit('filter', 'Filter'),
                    MySubmit('show_all', 'Show all'),
                    css_class="btn-group d-flex"
                ),
                css_class=f'col-md-2'
            ),
        )

        layout.append(form_row)
        return helper


class ContactForm(_NdrCoreSearchForm):

    def __init__(self, *args, **kwargs):
        super(ContactForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "POST"
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-sm-3'
        self.helper.field_class = 'col-sm-9'
        self.helper.add_input(MySubmit('submit', 'Send Message'))

    subject = forms.CharField(label='Subject',
                              initial="The Divisive Power of Citizenship - The French Case",
                              help_text="You can change the subject.",
                              required=True)
    email = forms.EmailField(label='Your E-Mail Address', help_text="We are going to reply to this e-mail address.", required=True)
    message = forms.CharField(label="Message",
                              help_text='Please be as specific as you can in your message. It will help us to answer your questions!',
                              widget=forms.Textarea)




class MySubmit(BaseInput):
    input_type = "submit"

    def __init__(self, *args, **kwargs):
        self.field_classes = "btn btn btn-outline-secondary w-100"
        super().__init__(*args, **kwargs)



def get_choices_from_tsv(dict_config):
    if "display_column" in dict_config and "search_column" in dict_config and "file" in dict_config:
        choices = list()
        with open(os.path.join(settings.STATIC_ROOT, dict_config["file"]), encoding='utf-8') as fd:
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
