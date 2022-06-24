from django.db import models
from django.urls import reverse, NoReverseMatch


class NdrCorePage(models.Model):
    name = models.CharField(max_length=200,
                            help_text='The name of the page')

    label = models.CharField(max_length=200,
                             help_text='The label of the page')

    view_name = models.CharField(max_length=200,
                                 help_text='The name of the view')

    nav_icon = models.CharField(max_length=200,
                                help_text='The fontawesome nav icon')

    index = models.IntegerField(default=0)

    def url(self):
        try:
            reverse_url = reverse(f'main:{self.view_name}')
        except NoReverseMatch:
            reverse_url = '#'

        return reverse_url

    def __str__(self):
        return f"{self.name}: {self.label}"
